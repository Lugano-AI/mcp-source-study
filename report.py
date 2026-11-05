#!/usr/bin/env python3
"""Write REPORT.md from results.json plus the hand review in review.json."""
import json, pathlib, datetime

HERE = pathlib.Path(__file__).resolve().parent
results = json.load(open(HERE / "results.json"))
review = json.load(open(HERE / "review.json"))
n = len(results)
dl = sum(r["downloads_last_month"] for r in results)
by = {r["package"]: r for r in results}

tele = review["telemetry"]
undoc = review["third_party_endpoints_not_in_readme"]
exec_ = sorted(r["package"] for r in results if r["summary"]["exec"])
home = sorted(r["package"] for r in results if r["summary"]["home_dir"])
secrets = sorted(r["package"] for r in results if r["summary"]["secret_env"])
no_readme = sorted(r["package"] for r in results if not r.get("readme", True))

undisclosed = [k for k, v in tele.items() if v["readme_disclosure"] == "none"]
partial = [k for k, v in tele.items() if v["readme_disclosure"].startswith("config key")]

def pct(x):
    return f"{100 * x / n:.0f}%"

lines = []
w = lines.append
w("# Static source observations from 50 sampled MCP server packages")
w("")
w(f"Static source-code review of {n} MCP server packages selected from an npm candidate set, "
  f"read at cited file and line locations. Scan date {review['reviewed_on']}. Published tarballs "
  "were downloaded and extracted in isolation; no package code, `npm install`, or lifecycle scripts were run. "
  "The observations are code markers, not runtime emissions, behavior, intent, or vulnerability findings.")
w("")
w("## Correction, 3 November 2026")
w("")
w("An audit on 3 November 2026 found that this report describes its sample wrongly. The method below says the 50 packages are "
  "the highest-ranked candidates by last-month downloads. The ranking file does not support that.")
w("")
w("- `ranked.json` records 0 downloads for 434 of its 571 candidates, and many of those zeros are failed lookups. "
  "For example, it records 0 for `chrome-devtools-mcp`, but the npm downloads API reports 8,032,928 downloads for that package "
  "from 20 September to 19 October 2026.")
w("- We queried the 434 zero entries again on 3 November. The API returned counts for 200 of them, and 157 of those had more "
  "downloads than the smallest sampled package (1,377).")
w("- 69 candidates ranked above that package were excluded by hand, and the reason for each exclusion was not recorded. "
  "Many are SDKs or adapters that the stated rule excludes, but some describe themselves as MCP servers, "
  "such as `@akutishevsky/lunchmoney-mcp` and `@ankimcp/anki-mcp-server`.")
w("- The method says the searches returned 703 unique packages. `ranked.json` lists 571. The materials do not explain the difference.")
w("")
w("So these 50 packages are not the 50 most-downloaded MCP servers in the candidate set. Every count in this report is still "
  "correct for the 50 packages in [packages.txt](packages.txt), and only for them. A corrected sample needs verified download "
  "counts and a recorded reason for every exclusion.")
w("")
w("The scanner's rules are also wider than this report first said. It reads eight file types (.js, .mjs, .cjs, .jsx, .ts, .tsx, "
  ".mts and .cts). Its process marker also matches `execFileSync`. It skips test, example, documentation, `.github` and "
  "`node_modules` directories and `.d.ts` files, and it checks only the first 20,000 characters of each line. See [scan.py](scan.py).")
w("")
w('The per-package table below shows the scanner\'s raw flags. Its "Hosts in code" and "Undocumented" columns come before the hand review; after it, 7 packages name a third-party endpoint their README omits, as the headline findings say.')
w("")
w("## Headline findings")
w("")
w(f"- **{len(undoc)} of {n} ({pct(len(undoc))}) include a third-party endpoint in source that the sampled README does not name.**")
w(f"- **{len(tele)} of {n} ({pct(len(tele))}) include source markers associated with analytics or telemetry.** {len(undisclosed)} sampled READMEs "
  "say nothing about those markers "
  f"({', '.join('`'+k+'`' for k in undisclosed)}); {len(partial)} shows only a config key ({', '.join('`'+k+'`' for k in partial)}); "
  f"{len(tele) - len(undisclosed) - len(partial)} document it.")
w(f"- **{len(exec_)} of {n} ({pct(len(exec_))}) contain process-spawning markers** (`child_process` import or `execSync`/`spawnSync`/`execFileSync`).")
w(f"- **{len(home)} of {n} ({pct(len(home))}) contain home-directory resolution markers.**")
w(f"- **{len(secrets)} of {n} ({pct(len(secrets))}) read environment-variable names commonly used for API keys, tokens, or secrets.**")
w(f"- {len(no_readme)} packages ship without a README in the tarball ({', '.join('`'+k+'`' for k in no_readme)}).")
w("- One package's source defines `panel_add_mcp`, a tool that writes new MCP-server entries to the user's `~/.claude.json` (`comfyui-mcp`).")
w("")
w("None of these observations is an accusation. Many reflect ordinary engineering choices. The cited files and lines let readers inspect the source marker; "
  "a static marker does not establish behavior in an individual installation or run.")
w("")
w("## Telemetry and analytics")
w("")
w("| Package | Downloads/mo | Source observation | README |")
w("|---|---:|---|---|")
for k, v in sorted(tele.items(), key=lambda kv: -by[kv[0]]["downloads_last_month"]):
    w(f"| `{k}` | {by[k]['downloads_last_month']:,} | `{v['host']}` — {v['what']} | {v['readme_disclosure']} |")
w("")
w("## Third-party endpoints not named in the sampled README")
w("")
w("| Package | Downloads/mo | Source observation |")
w("|---|---:|---|")
for k, v in sorted(undoc.items(), key=lambda kv: -by[kv[0]]["downloads_last_month"]):
    for item in v:
        w(f"| `{k}` | {by[k]['downloads_last_month']:,} | {item} |")
w("")
w("## Additional static observations")
w("")
for k, v in review["notable"].items():
    w(f"- `{k}`: {v}")
w("")
w("## Static source markers in the 50-package sample")
w("")
w("The `exec`, `home dir`, `secrets in env`, and `eval` columns are markers found in static source. A blank cell means the scan did not record that marker; it is not a runtime result.")
w("")
w((HERE / "table.md").read_text())
w("")
w("## Method")
w("")
w("1. Candidates came from four npm registry searches (`mcp server`, `mcp-server`, `keywords:mcp`, `model context protocol server`): 703 unique packages.")
w("2. Candidates were ranked by last-month downloads from `api.npmjs.org`. Clients, SDKs, frameworks, adapters, transports, and platform binaries were excluded manually. The 50 highest-ranked remaining candidates are listed in [packages.txt](packages.txt); this is a defined sample, not a claim about all MCP packages or npm globally.")
w("3. Each sampled package's published tarball was downloaded from the registry and extracted into an isolated directory. No `npm install`, lifecycle scripts, or package code were run.")
w("4. [scan.py](scan.py) reads every `.js`, `.mjs`, `.cjs`, `.ts`, and `.tsx` file outside test and docs directories and records scheme URLs in non-comment code (excluding lines that carry documentation text or example domains), analytics hosts, `child_process` use, home-directory resolution, and names read from the environment. A host counts as documented when its registrable domain appears in the README or `package.json`, or matches the package's scope.")
w("5. Every flagged package was then read at the cited location. [review.json](review.json) records the manual review, including dropped false positives and reasons.")
w("")
w("## Limits")
w("")
w("- Static only. A host or capability marker in code is not proof of a runtime request, behavior, or vulnerability; requests can also be assembled from strings the scanner cannot join.")
w("- The README is a proxy for documentation. Vendors may document endpoints elsewhere.")
w("- Bundled dependencies inside the tarball are scanned; transitive dependencies installed at runtime are not.")
w("- Capability flags describe source patterns and possible code paths, not what happens in a given session.")
w("- The sample is 50 packages selected from a 703-package candidate set. Rankings reflect one month of npm downloads and change quickly.")
w("")
w("## Reproduce")
w("")
w("Run [scan.py](scan.py) against an already extracted package directory, then regenerate with [report.py](report.py):")
w("")
w("```bash")
w("python3 -I scan.py <extracted_pkgs_dir> packages.txt ranked.json .")
w("python3 -I report.py")
w("```")
w("")
w("Data and review files: [packages.txt](packages.txt) (sample), [ranked.json](ranked.json) (download counts), [results.json](results.json) (source markers per package), [evidence.jsonl](evidence.jsonl) (cited file and line records), [review.json](review.json) (manual review), [summary.json](summary.json), and [table.md](table.md).")
(HERE / "REPORT.md").write_text("\n".join(lines) + "\n")
json.dump({"packages": n, "downloads_last_month": dl, "third_party_not_in_readme": len(undoc), "telemetry": len(tele),
           "telemetry_undisclosed": len(undisclosed), "telemetry_config_key_only": len(partial), "exec": len(exec_),
           "home_dir": len(home), "secret_env": len(secrets), "no_readme": len(no_readme)},
          open(HERE / "headline.json", "w"), indent=1)
print(open(HERE / "headline.json").read())
