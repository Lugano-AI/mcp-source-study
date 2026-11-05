# MCP source study

We read the published source of 50 MCP server packages, the add-ons that give AI apps tools, and checked the hosts each package's code names against its README and package.json. We never installed or ran any of them.

The essay is at [lugano.ai/research/mcp-access-study](https://lugano.ai/research/mcp-access-study/). [REPORT.md](REPORT.md) is the full report. It opens with a correction, dated 3 November 2026, about how the sample was drawn. Read that first.

## What's here

- `scan.py`: the static scanner.
- `report.py`: rebuilds the report tables from the scan results.
- `packages.txt`: the 50 packages.
- `ranked.json`: the download ranking behind the sample. Many of its zeros are failed lookups (see the correction).
- `results.json`, `summary.json`, `headline.json`, `table.md`: per-package results and the counts.
- `review.json`: the hand review of every host-flagged package.
- `evidence.jsonl`: the file and line behind every observation.

## Rerun it

Download and extract the packages yourself, each in its own directory, without installing them. Then:

```
python3 -I scan.py <extracted_pkgs_dir> packages.txt ranked.json .
python3 -I report.py
```

A rerun on fresh downloads may not match exactly, since package versions keep changing.

## What it can't tell you

A code marker isn't a runtime request, a behavior, intent or a vulnerability. The sample is flawed, so the counts hold for these 50 packages only.

## License

Apache License 2.0. See [LICENSE](LICENSE). Copyright 2026 Lugano AI Holdings LLC.
