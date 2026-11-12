# Static source observations from 50 sampled MCP server packages

Exploratory static source-code review of 50 MCP server packages selected from an npm candidate set, read at cited file and line locations. Scan date 2026-10-20. Published tarballs were downloaded and extracted in isolation; no package code, `npm install`, or lifecycle scripts were run. The observations are code markers, not runtime emissions, behavior, intent, or vulnerability findings.

## How the sample was drawn

The 50 packages are the candidates with the highest recorded last-month downloads after manual exclusions. They are not the 50 most-downloaded MCP servers in the candidate set, so this is an exploratory study of a defined sample.

- `ranked.json` records 0 downloads for 434 of its 571 candidates, and many of those zeros are failed lookups. For example, it records 0 for `chrome-devtools-mcp`, but the npm downloads API reports 8,032,928 downloads for that package from 20 September to 19 October 2026.
- Queried again on 3 November 2026, the API returned counts for 200 of the 434 zero entries, and 157 of those had more downloads than the smallest sampled package (1,377).
- 69 candidates ranked above that package were excluded by hand, and the reason for each exclusion was not recorded. Many are SDKs or adapters that the stated rule excludes, but some describe themselves as MCP servers, such as `@akutishevsky/lunchmoney-mcp` and `@ankimcp/anki-mcp-server`.
- The searches returned 703 unique packages. `ranked.json` lists 571. The materials do not explain the difference.

Every count in this report holds for the 50 packages in [packages.txt](packages.txt), and only for them. A representative sample would need verified download counts and a recorded reason for every exclusion.

The per-package table below shows the scanner's raw flags, before the hand review. Its "Undocumented" column lists hosts outside the documentation baseline below; after the hand review, 8 packages name such a host, as the headline findings say.

## Documentation baseline

A host counts as documented when its registrable domain appears, as a web address or a quoted domain, in the package's main README or in five `package.json` fields, or when the host contains the package's scope. The main README is a `README.md`, `readme.md`, `Readme.md`, `README.MD`, `README` or `readme.markdown` file at the package root. The five fields are `homepage`, `description`, `author`, `repository` and `bugs`. For an unscoped package, the scope is the first hyphen-separated part of its name. READMEs in other languages, other shipped documents, documents the README links to outside the package, and other `package.json` fields are outside this baseline.

A wider baseline counts every README file in the package in any language, every other document shipped for the user, and every `package.json` field. It leaves out instruction files bundled for the AI app. Under it, 7 of the 8 packages remain. `@alisaitteke/photoshop-mcp` drops out. Its 1.7.37 main README names neither `hey.sideguard.io` nor `openrouter.ai`, and it links `docs/anonymous-usage-analytics.md`, a note the package doesn't ship. The package's `README.de.md`, `README.es.md`, `README.ja.md`, `README.tr.md` and `README.zh-CN.md` name both hosts. If bundled instruction files also count, `hostinger-api-mcp` drops out as well, leaving 6, since `skills/migrate-to-hosting/SKILL.md` holds the same `curl -s https://api.ipify.org` instruction. The 5 packages with analytics or telemetry markers stay 5, because that count comes from code. [docs-check.json](docs-check.json) gives each flagged host's disposition and each tarball's integrity hash.

## Headline findings

- **8 of 50 (16%) include a third-party endpoint in source that neither the main README nor the five `package.json` fields name.** Under the wider documentation baseline, the count is 7.
- **5 of 50 (10%) include source markers associated with analytics or telemetry.** 2 main READMEs say nothing about those markers (`figma-developer-mcp`, `exa-mcp-server`); 1 shows only a config key (`nx-mcp`); 2 mention it.
- **20 of 50 (40%) contain process-spawning markers** (`child_process` import or `execSync`/`spawnSync`/`execFileSync`).
- **16 of 50 (32%) contain home-directory resolution markers.**
- **24 of 50 (48%) read environment-variable names commonly used for API keys, tokens, or secrets.**
- 2 packages ship without a README in the tarball (`@sentry/mcp-server`, `@supabase/mcp-server-supabase`).
- One package's source defines `panel_add_mcp`, a tool whose code can add MCP-server entries to the user's `~/.claude.json` (`comfyui-mcp`).

None of these observations is an accusation. Many reflect ordinary engineering choices. The cited files and lines let readers inspect the source marker; a static marker does not establish behavior in an individual installation or run.

## Telemetry and analytics

| Package | Downloads/mo | Source observation | README |
|---|---:|---|---|
| `figma-developer-mcp` | 336,096 | `us.i.posthog.com` — Source contains a PostHog host and hardcoded project key; the cited code includes FRAMELINK_TELEMETRY=off and DO_NOT_TRACK opt-outs plus redaction logic. | none |
| `n8n-mcp` | 305,791 | `telemetry.n8n-mcp.com` — Source names a first-party telemetry endpoint. | links a privacy and telemetry note (PRIVACY.md) in the project's GitHub repository that names the host and how to opt out; the package doesn't ship the note |
| `nx-mcp` | 236,569 | `www.google-analytics.com` — Source contains Google Analytics Measurement Protocol references with fields including user_id, editor, OS, app, and Nx versions. | config key only (disableTelemetry); the README does not describe what the telemetry code would send or where |
| `exa-mcp-server` | 64,791 | `api.agnost.ai` — Source contains an Agnost MCP analytics SDK call; the cited call site disables tool inputs, outputs, and errors. | none |
| `@alisaitteke/photoshop-mcp` | 40,281 | `hey.sideguard.io` — Source names a Rybbit analytics host. | the main README says anonymous usage analytics run by default and can be turned off, and links docs/anonymous-usage-analytics.md, a note in the project's GitHub repository that names the Rybbit host; the main README names neither hey.sideguard.io nor openrouter.ai, and the package doesn't ship the note; the package's README.de.md, README.es.md, README.ja.md, README.tr.md and README.zh-CN.md name both hosts |

## Third-party endpoints not named in the main README

| Package | Downloads/mo | Source observation |
|---|---:|---|
| `@upstash/context7-mcp` | 2,640,895 | login.microsoftonline.com: source contains code that fetches Entra JWKS (signing keys) to validate JWTs; Entra is not mentioned in the main README |
| `hostinger-api-mcp` | 741,258 | api.ipify.org: a bundled skill contains the instruction `curl -s https://api.ipify.org`; the address appears only in that skill text, not in code that calls it |
| `@sentry/mcp-server` | 462,862 | ai-gateway.vercel.sh, openrouter.ai, api.vercel.com: source includes bundled AI SDK provider defaults; the package ships without a README |
| `figma-developer-mcp` | 336,096 | us.i.posthog.com (see telemetry) |
| `nx-mcp` | 236,569 | www.google-analytics.com (see telemetry) |
| `comfyui-mcp` | 117,113 | api.atlascloud.ai, api.x.ai, api.z.ai: source names model-provider endpoints that the main README does not name (Kimi, MiniMax, OpenRouter, Civitai, Ollama, Grok, and GLM are named) |
| `exa-mcp-server` | 64,791 | api.agnost.ai (see telemetry) |
| `@alisaitteke/photoshop-mcp` | 40,281 | hey.sideguard.io, openrouter.ai: source names a Rybbit analytics host and the OpenRouter API; the main README names neither host, and the package's READMEs in five other languages name both (see telemetry) |

## Additional static observations

- `comfyui-mcp`: Source defines `panel_add_mcp`, whose code can add new MCP-server entries to the user's ~/.claude.json.
- `@sentry/mcp-server`: No README in the published tarball; package.json was the documentation baseline checked in this study.
- `@supabase/mcp-server-supabase`: No README in the published tarball.

## Static source markers in the 50-package sample

The `exec`, `home dir`, `secrets in env`, and `eval` columns are markers found in static source. A blank cell means the scan did not record that marker; it is not a runtime result.

| Package | Version | Downloads/mo | Hosts in code | Undocumented | Telemetry | exec | home dir | secrets in env | eval |
|---|---|---:|---:|---|---|---|---|---:|---|
| `@storybook/mcp` | 10.6.2 | 9,140,670 | 1 | opencollective.com |  |  |  |  |  |
| `@upstash/context7-mcp` | 4.4.4 | 2,640,895 | 5 | microsoftonline.com |  |  |  | 4 |  |
| `hostinger-api-mcp` | 3.3.1 | 741,258 | 4 | ipify.org |  | yes | yes | 1 |  |
| `@notionhq/notion-mcp-server` | 2.5.2 | 699,166 | 3 | git.io |  |  |  | 3 | yes |
| `firecrawl-mcp` | 3.33.4 | 625,831 | 5 |  |  |  |  | 4 |  |
| `@azure/mcp` | 3.0.0 | 558,323 | 0 |  |  | yes | yes |  |  |
| `@zereight/mcp-gitlab` | 2.3.4 | 526,272 | 3 | chatgpt.com, claude.com |  | yes | yes | 8 |  |
| `@sentry/mcp-server` | 0.42.0 | 462,862 | 10 | ai-sdk.dev, logtape.org, openrouter.ai, slsa.dev … | docs.sentry.io, sentry.sentry.io | yes | yes | 4 | yes |
| `@ui5/mcp-server` | 0.3.2 | 362,686 | 3 |  |  |  | yes |  |  |
| `@supabase/mcp-server-supabase` | 0.14.0 | 352,071 | 4 |  |  |  |  | 1 |  |
| `figma-developer-mcp` | 0.13.2 | 336,096 | 1 | posthog.com | us.i.posthog.com |  |  |  |  |
| `n8n-mcp` | 2.94.3 | 305,791 | 7 |  | telemetry.n8n-mcp.com | yes |  | 8 | yes |
| `xcodebuildmcp` | 2.7.0 | 253,777 | 1 |  |  | yes | yes |  |  |
| `@serdnaley/metabase-mcp` | 0.2.0 | 240,728 | 0 |  |  |  |  | 2 | yes |
| `nx-mcp` | 0.25.0 | 236,569 | 3 | google-analytics.com | www.google-analytics.com | yes | yes | 2 | yes |
| `@google-cloud/observability-mcp` | 0.2.3 | 195,702 | 0 |  |  |  | yes |  | yes |
| `openinputbridge-mcp` | 0.1.1 | 190,641 | 0 |  |  | yes |  |  |  |
| `@mastra/mcp-docs-server` | 1.3.8 | 157,845 | 1 |  |  |  | yes |  |  |
| `@ericthered926/duckduckgo-mcp-server` | 0.6.0 | 138,436 | 0 |  |  |  |  |  |  |
| `@metamask/device-mcp` | 0.5.0 | 123,616 | 0 |  |  | yes | yes |  |  |
| `comfyui-mcp` | 0.52.206 | 117,113 | 31 | atlascloud.ai, chatgpt.com, civitai.com, githubcopilot.com … |  | yes | yes | 33 |  |
| `@drawio/mcp` | 1.10.0 | 116,312 | 3 |  |  | yes | yes |  | yes |
| `@winor30/mcp-server-datadog` | 1.8.0 | 113,345 | 1 | datadoghq.com | app.datadoghq.com |  |  | 2 |  |
| `@transcend-io/mcp-server-admin` | 1.1.3 | 88,742 | 0 |  |  |  |  |  |  |
| `@shortcut/mcp` | 0.25.0 | 76,505 | 1 |  |  |  |  | 1 |  |
| `@eslint/mcp` | 0.3.15 | 71,334 | 0 |  |  |  |  |  |  |
| `@turbopuffer/turbopuffer-mcp` | 2.7.0 | 70,801 | 1 |  |  | yes |  |  |  |
| `@vantasdk/vanta-mcp-server` | 1.2.0 | 70,088 | 1 |  |  |  |  | 1 |  |
| `@claude-flow/mcp` | 3.1.1 | 66,131 | 0 |  |  |  |  |  |  |
| `@primer/mcp` | 1.1.1 | 65,900 | 0 |  |  | yes |  |  |  |
| `exa-mcp-server` | 3.4.2 | 64,791 | 5 | agnost.ai | api.agnost.ai |  |  | 1 | yes |
| `pptx-viewer-mcp` | 2.8.6 | 61,783 | 0 |  |  |  |  |  |  |
| `@benborla29/mcp-server-mysql` | 2.0.9 | 49,410 | 0 |  |  |  |  | 2 |  |
| `@alisaitteke/photoshop-mcp` | 1.7.37 | 40,281 | 2 | openrouter.ai, sideguard.io | hey.sideguard.io | yes | yes | 1 | yes |
| `@taiga-ai/mcp-server` | 0.31.0 | 36,925 | 1 |  |  |  |  |  | yes |
| `@imgly/codesign-mcp` | 0.4.2 | 34,980 | 4 |  |  | yes | yes | 1 |  |
| `@ivotoby/openapi-mcp-server` | 1.16.1 | 31,394 | 0 |  |  |  |  | 2 |  |
| `@phantom/mcp-server` | 1.2.9 | 28,216 | 6 |  |  | yes |  | 1 |  |
| `@iobroker/mcp-server` | 1.2.3 | 24,484 | 0 |  |  | yes |  |  |  |
| `@primeng/mcp` | 22.1.2 | 22,598 | 2 |  |  |  |  |  |  |
| `@coinbase/cds-mcp-server` | 9.29.0 | 20,133 | 1 |  |  | yes |  |  |  |
| `@mantine/mcp-server` | 9.7.3 | 19,904 | 1 |  |  |  |  |  |  |
| `@zapier/zapier-sdk-mcp` | 0.27.9 | 15,948 | 0 |  |  |  |  |  |  |
| `@browserless.io/mcp` | 1.39.0 | 11,839 | 14 | celonis.com, chatgpt.com, devin.ai, grok.com … |  | yes |  | 4 | yes |
| `@nexus2520/jira-mcp-server` | 1.2.0 | 10,528 | 0 |  |  |  |  | 1 |  |
| `@ahrefs/mcp` | 0.0.11 | 9,311 | 1 |  |  |  |  | 1 |  |
| `@openbnb/mcp-server-airbnb` | 0.3.0 | 8,457 | 3 |  |  |  |  |  |  |
| `@kazuph/mcp-fetch` | 1.6.3 | 7,031 | 0 |  |  |  | yes |  |  |
| `@burtthecoder/mcp-shodan` | 1.0.34 | 1,828 | 2 |  |  |  |  | 1 |  |
| `@agent-infra/mcp-server-filesystem` | 1.2.29 | 1,377 | 0 |  |  | yes | yes |  |  |


## Method

1. Candidates came from four npm registry searches (`mcp server`, `mcp-server`, `keywords:mcp`, `model context protocol server`): 703 unique packages.
2. Candidates were ranked by last-month downloads from `api.npmjs.org`. Clients, SDKs, frameworks, adapters, transports, and platform binaries were excluded manually. The 50 remaining candidates with the highest recorded counts are listed in [packages.txt](packages.txt). Most recorded counts were zero (see How the sample was drawn), so this is an exploratory, defined sample, not a claim about all MCP packages or npm globally.
3. Each sampled package's published tarball was downloaded from the registry and extracted into an isolated directory. No `npm install`, lifecycle scripts, or package code were run.
4. [scan.py](scan.py) reads every `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.mts` and `.cts` file outside test, example, documentation, `.github` and `node_modules` directories, skips `.d.ts` and `.map` files, and checks only the first 20,000 characters of each line. It records scheme URLs in non-comment code (excluding lines that carry documentation text or example domains), analytics hosts, `child_process` use and `execSync`, `spawnSync` or `execFileSync` calls, home-directory resolution, and names read from the environment. The documentation baseline above decides which hosts count as documented.
5. Every flagged package was then read at the cited location. [review.json](review.json) records the manual review, including dropped false positives and reasons.

## Limits

- Static only. A host or capability marker in code is not proof of a runtime request, behavior, or vulnerability; requests can also be assembled from strings the scanner cannot join.
- The main README is a proxy for documentation. Vendors may document endpoints elsewhere, including READMEs in other languages in the same package (see Documentation baseline).
- Bundled dependencies inside the tarball are scanned; transitive dependencies installed at runtime are not.
- Capability flags describe source patterns and possible code paths, not what happens in a given session.
- The sample is 50 packages selected from a 703-package candidate set. Rankings reflect one month of npm downloads and change quickly.

## Reproduce

Run [scan.py](scan.py) against an already extracted package directory, then regenerate with [report.py](report.py):

```bash
python3 -I scan.py <extracted_pkgs_dir> packages.txt ranked.json .
python3 -I report.py
```

Data and review files: [packages.txt](packages.txt) (sample), [ranked.json](ranked.json) (download counts), [results.json](results.json) (source markers per package), [evidence.jsonl](evidence.jsonl) (cited file and line records), [review.json](review.json) (manual review), [docs-check.json](docs-check.json) (documentation check of the flagged hosts), [summary.json](summary.json) (scanner counts before hand review), and [table.md](table.md).
