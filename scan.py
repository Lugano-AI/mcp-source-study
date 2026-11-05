#!/usr/bin/env python3
"""Static scan of npm MCP server packages: network hostnames, telemetry, exec and secret access.

Reads extracted package tarballs (never executes them), and writes results.json,
evidence.jsonl and a Markdown table. Every finding carries file:line evidence.

Usage: python3 -I scan.py <pkgs_dir> <packages.txt> <ranked.json> <out_dir>
"""
import json, os, re, sys, pathlib

PKGS, LIST, RANKED, OUT = (pathlib.Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)

CODE_EXT = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".jsx"}
SKIP_DIRS = {"node_modules", "test", "tests", "__tests__", "spec", "examples", "example", "docs", "doc", ".github"}
MAX_FILE = 4_000_000  # bytes; larger minified bundles are still scanned but line evidence is truncated

# Hosts that are infrastructure, documentation or standards, not a tool's own egress.
BENIGN = {
    "localhost", "127.0.0.1", "0.0.0.0", "example.com", "example.org", "example.net", "schema.org",
    "json-schema.org", "w3.org", "github.com", "githubusercontent.com", "npmjs.com", "npmjs.org", "nodejs.org",
    "unpkg.com", "jsdelivr.net", "mozilla.org", "stackoverflow.com", "wikipedia.org", "modelcontextprotocol.io",
    "typescriptlang.org", "opensource.org", "spdx.org", "apache.org", "gnu.org", "creativecommons.org",
    "iana.org", "ietf.org", "rfc-editor.org", "whatwg.org", "ecma-international.org", "reactjs.org", "react.dev",
    "babeljs.io", "eslint.org", "prettier.io", "vitejs.dev", "esbuild.github.io", "tc39.es", "yarnpkg.com",
    "pnpm.io", "anthropic.com", "claude.ai", "openai.com", "cursor.com", "cursor.sh", "zod.dev", "swagger.io",
    "openapis.org", "xml.org", "purl.org", "xmlsoap.org", "adobe.com", "microsoft.com", "apple.com",
    "chromium.org", "google.com", "googleapis.com", "gstatic.com", "chrome.com", "khronos.org", "ietf.org",
    "socket.io", "next.js", "vue.js", "node.js", "deno.land", "bun.sh", "discord.gg", "x.com", "twitter.com",
    "linkedin.com", "youtube.com", "medium.com", "dev.to", "openjsf.org", "jquery.com", "lodash.com",
    "mdn.io", "caniuse.com", "web.dev", "sentry.io", "readthedocs.io", "gitlab.com", "bitbucket.org",
}
# Analytics and telemetry hosts: a category worth its own column.
TELEMETRY = {
    "posthog.com", "i.posthog.com", "segment.io", "segment.com", "mixpanel.com", "amplitude.com",
    "google-analytics.com", "analytics.google.com", "plausible.io", "datadoghq.com", "honeycomb.io",
    "sentry.io", "ingest.sentry.io", "bugsnag.com", "rollbar.com", "newrelic.com", "logrocket.com",
    "hotjar.com", "intercom.io", "fullstory.com", "heap.io", "statsig.com", "launchdarkly.com",
    "telemetry.", "analytics.", "metrics.", "agnost.ai", "sideguard.io", "rybbit.io",
}
TLDS = ("com|net|org|io|ai|dev|app|co|cloud|me|xyz|sh|us|uk|de|fr|eu|jp|cn|ru|in|br|ca|au|tech|tools|so|gg|to|"
        "ly|info|biz|run|live|site|online|network|services|cc|fi|se|no|nl|ch|it|es|pl|kr|tw|hk|sg|nz|ie|at|be|dk|"
        "cz|pt|gr|il|ae|za|mx|ar|cl|id|ph|vn|th|my|tr|ua|edu|gov|mil|int|pro|fm|tv|ws|page|digital|systems|"
        "solutions|agency|studio|design|email|chat|bot|zone|host|space|store|shop|works|world|one|cool|wtf|lol")
URL_RE = re.compile(r"(?:https?|wss?)://([A-Za-z0-9.-]+\.(?:%s))(?::\d+)?(/[^\s'\"`)<>]*)?" % TLDS, re.I)
BARE_RE = re.compile(r"[\"'`]((?:[a-z0-9-]+\.)+(?:%s))[\"'`/:]" % TLDS, re.I)
IP_RE = re.compile(r"[\"'`]((?:\d{1,3}\.){3}\d{1,3})(?::\d+)?[\"'`/]")
COMMENT_RE = re.compile(r"^\s*(//|/\*|\*|#|<!--)")
# Lines that carry documentation or examples inside string literals, not runtime endpoints.
DOCLINE_RE = re.compile(r"\.describe\(|\"description\"|\"note\"|docs/|\.md\"|\.md'|SKILL\.md|example\.|your-|my-|mydomain|placehold|\.invalid|missingMessage|HelpUrl|helpUrl|Refer to|See:|see https|https://[^\s\"']*/(docs|blog|wiki|issues|releases|guide|reference|dictionary|opensource)\b", re.I)
TESTFILE_RE = re.compile(r"(^|/)(snapshot-tests|__snapshots__|fixtures|smoke|e2e)(/|$)|\.(test|spec)\.[cm]?[jt]sx?$|panel-smoke")
PLACEHOLDER_HOST = re.compile(r"(^|\.)(example|test|your-?[a-z]*|my-?[a-z]*|old|new|ex|foo|bar|placehold|invalid|nonexistent)\.[a-z]+$|^(srv|ns\d|lunar)\.|x\.x\.x")
CAPS = {
    "exec": re.compile(r"require\([\"']child_process|from\s+[\"']child_process|require\([\"']node:child_process|from\s+[\"']node:child_process|\bexecSync\s*\(|\bspawnSync\s*\(|\bexecFileSync\s*\("),
    "home_dir": re.compile(r"os\.homedir\(\)|homedir\(\)|process\.env\.HOME\b|process\.env\.USERPROFILE"),
    "secret_env": re.compile(r"process\.env\.([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*)"),
    "eval": re.compile(r"\beval\s*\(|new\s+Function\s*\("),
    "network_calls": re.compile(r"\bfetch\s*\(|https?\.request\s*\(|axios[.(]|\bundici\b|node-fetch|got\s*\("),
    "fs_write": re.compile(r"\bfs\.(?:promises\.)?(?:writeFile|writeFileSync|appendFile|rm|rmSync|unlink)"),
}
PRIVATE_IP = re.compile(r"^(10\.|127\.|0\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|255\.)")



def inside(path, root):
    """True for a regular file inside root. Symlinks, and anything that resolves outside the package, are skipped."""
    try:
        return (not path.is_symlink()) and path.is_file() and path.resolve().is_relative_to(root.resolve())
    except OSError:
        return False


VERSION_RE = re.compile(r"^[0-9A-Za-z.+-]{1,64}$")


def md_cell(value):
    """Escape a value from package data before it goes into a Markdown table cell."""
    text = str(value).replace("\r", " ").replace("\n", " ")
    for ch in "\\`|<>[]!*_":
        text = text.replace(ch, "\\" + ch)
    return text

def registrable(host):
    host = host.lower().strip(".")
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net", "ac", "gov", "edu"} and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def is_benign(host):
    h = host.lower()
    return h in BENIGN or registrable(h) in BENIGN or h.endswith(".local")


def is_telemetry(host):
    h = host.lower()
    return any(h == t or h.endswith("." + t) or (t.endswith(".") and h.startswith(t)) for t in TELEMETRY)


def vendor_domains(name, pkg):
    """Domains the package itself documents: README, package.json fields, and the scope name."""
    doms = set()
    text = ""
    root = pkg
    for cand in ("README.md", "readme.md", "README", "Readme.md", "README.MD", "readme.markdown"):
        p = root / cand
        if inside(p, root):
            text += p.read_text(errors="ignore")
    pj = root / "package.json"
    meta = {}
    if inside(pj, root):
        try:
            meta = json.loads(pj.read_text(errors="ignore"))
        except Exception:
            meta = {}
        for k in ("homepage", "description", "author", "repository", "bugs"):
            v = meta.get(k)
            text += " " + (json.dumps(v) if not isinstance(v, str) else v)
    for m in URL_RE.finditer(text):
        doms.add(registrable(m.group(1)))
    for m in BARE_RE.finditer(text):
        doms.add(registrable(m.group(1)))
    scope = name.split("/")[0].lstrip("@") if name.startswith("@") else name.split("-")[0]
    return doms, scope.lower(), meta


def scan_package(name, pkg):
    doms, scope, meta = vendor_domains(name, pkg)
    hosts = {}       # host -> {"files": set, "comment_only": bool, "evidence": [..]}
    caps = {k: [] for k in CAPS}
    secrets = set()
    nfiles = 0
    bundled = (pkg / "node_modules").exists()
    for path in pkg.rglob("*"):
        if path.suffix.lower() not in CODE_EXT or not inside(path, pkg):
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(pkg).parts[:-1]):
            continue
        if path.name.endswith((".d.ts", ".map")):
            continue
        try:
            data = path.read_text(errors="ignore")
        except Exception:
            continue
        nfiles += 1
        rel = str(path.relative_to(pkg))
        for ln, line in enumerate(data.splitlines(), 1):
            if len(line) > 20000:
                line_sample = line[:20000]
            else:
                line_sample = line
            comment = bool(COMMENT_RE.match(line_sample))
            found = set()
            for m in URL_RE.finditer(line_sample):
                found.add(m.group(1))
            if found and (DOCLINE_RE.search(line_sample) or TESTFILE_RE.search(rel)):
                found = set()  # documentation text inside strings, or test fixtures
            for h in found:
                h = h.lower()
                if PLACEHOLDER_HOST.search(h):
                    continue
                if is_benign(h) and not is_telemetry(h):
                    continue
                e = hosts.setdefault(h, {"files": set(), "code": False, "evidence": [], "tele_path": False})
                if re.search(r"(telemetry|analytics|tracking|metrics)", rel, re.I):
                    e["tele_path"] = True
                e["files"].add(rel)
                if not comment:
                    e["code"] = True
                if len(e["evidence"]) < 3:
                    snippet = line_sample.strip()
                    e["evidence"].append({"file": rel, "line": ln, "comment": comment, "text": snippet[:160]})
            for k, rx in CAPS.items():
                for m in rx.finditer(line_sample):
                    if len(caps[k]) < 5:
                        caps[k].append({"file": rel, "line": ln, "text": line_sample.strip()[:160]})
                    if k == "secret_env" and m.lastindex:
                        secrets.add(m.group(1))
                    break
    has_readme = any((pkg / c).exists() for c in ("README.md", "readme.md", "README", "Readme.md", "README.MD", "readme.markdown"))
    version = meta.get("version")
    result = {"package": name, "version": version if isinstance(version, str) and VERSION_RE.match(version) else "invalid", "files_scanned": nfiles, "bundled_deps": bundled, "readme": has_readme,
              "documented_domains": sorted(doms), "hosts": []}
    for h, e in sorted(hosts.items()):
        rd = registrable(h)
        documented = rd in doms or (scope and scope in rd.split(".")[0]) or (scope and scope in h)
        result["hosts"].append({"host": h, "registrable": rd, "in_code": e["code"], "telemetry": is_telemetry(h) or (e["tele_path"] and not documented),
                                "documented": bool(documented), "files": sorted(e["files"])[:5], "evidence": e["evidence"]})
    result["caps"] = {k: v for k, v in caps.items()}
    result["secret_env_names"] = sorted(secrets)
    code_hosts = [x for x in result["hosts"] if x["in_code"]]
    result["summary"] = {
        "hosts_in_code": len(code_hosts),
        "undocumented_hosts_in_code": sorted({x["registrable"] for x in code_hosts if not x["documented"]}),
        "telemetry_hosts": sorted({x["host"] for x in result["hosts"] if x["telemetry"]}),
        "exec": bool(caps["exec"]), "home_dir": bool(caps["home_dir"]), "eval": bool(caps["eval"]),
        "secret_env": len(secrets), "network_calls": bool(caps["network_calls"]), "fs_write": bool(caps["fs_write"]),
    }
    return result


def main():
    names = [l.strip() for l in LIST.read_text().splitlines() if l.strip()]
    ranked = dict(json.load(open(RANKED)))
    results = []
    with open(OUT / "evidence.jsonl", "w") as ev:
        for n in names:
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", n)
            root = PKGS / safe / "package"
            if not root.exists():
                cands = list((PKGS / safe).iterdir()) if (PKGS / safe).exists() else []
                root = cands[0] if cands else None
            if not root:
                print("missing", n, file=sys.stderr)
                continue
            if root.is_symlink() or not root.is_dir() or not root.resolve().is_relative_to(PKGS.resolve()):
                print("skipping unsafe package root", n, file=sys.stderr)
                continue
            root = root.resolve()
            r = scan_package(n, root)
            r["downloads_last_month"] = ranked.get(n, 0)
            results.append(r)
            for h in r["hosts"]:
                for e in h["evidence"]:
                    ev.write(json.dumps({"package": n, "host": h["host"], **e}) + "\n")
            for k, v in r["caps"].items():
                for e in v:
                    ev.write(json.dumps({"package": n, "capability": k, **e}) + "\n")
    json.dump(results, open(OUT / "results.json", "w"), indent=1)

    n = len(results)
    undoc = [r for r in results if r["summary"]["undocumented_hosts_in_code"]]
    tele = [r for r in results if r["summary"]["telemetry_hosts"]]
    ex = [r for r in results if r["summary"]["exec"]]
    home = [r for r in results if r["summary"]["home_dir"]]
    sec = [r for r in results if r["summary"]["secret_env"]]
    ev_ = [r for r in results if r["summary"]["eval"]]
    lines = ["| Package | Version | Downloads/mo | Hosts in code | Undocumented | Telemetry | exec | home dir | secrets in env | eval |",
             "|---|---|---:|---:|---|---|---|---|---:|---|"]
    for r in sorted(results, key=lambda r: -r["downloads_last_month"]):
        s = r["summary"]
        lines.append(f"| `{md_cell(r['package'])}` | {md_cell(r['version'])} | {r['downloads_last_month']:,} | {s['hosts_in_code']} | "
                     f"{', '.join(md_cell(h) for h in s['undocumented_hosts_in_code'][:4])}{' …' if len(s['undocumented_hosts_in_code'])>4 else ''} | "
                     f"{', '.join(md_cell(h) for h in s['telemetry_hosts'][:3])} | {'yes' if s['exec'] else ''} | {'yes' if s['home_dir'] else ''} | "
                     f"{s['secret_env'] or ''} | {'yes' if s['eval'] else ''} |")
    summary = {
        "packages": n, "with_undocumented_hosts_in_code": len(undoc), "with_telemetry_hosts": len(tele),
        "with_exec": len(ex), "with_home_dir": len(home), "with_secret_env": len(sec), "with_eval": len(ev_),
        "total_downloads_last_month": sum(r["downloads_last_month"] for r in results),
    }
    json.dump(summary, open(OUT / "summary.json", "w"), indent=1)
    (OUT / "table.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
