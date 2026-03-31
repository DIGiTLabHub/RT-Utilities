# CLI Spec: drdoc2tex

## Overview
`drdoc2tex` is a CLI tool that converts a ChatGPT Deep Research DOCX into LaTeX and BibTeX using the workflow described in `DeepResearchDoc2Tex.md`.

The CLI is split into three subcommands to keep the core conversion deterministic and to make enrichment optional.

## Commands

### 1) convert
Convert DOCX to LaTeX/BibTeX using a deterministic pipeline.

```
```

Required behavior:
- Parse DOCX into a normalized document model.
- Extract `[n] → URL` citation mapping.
- Remove the references section at the end of the DOCX.
- Convert to LaTeX and replace citations with `\cite{key-N}`.
- Generate `refs.bib` keyed by `key-N` (minimal metadata allowed).
- Write `warnings.txt` and `verification.txt`.

Options:
- `-o, --output-dir PATH` (required)
- `--base-name NAME` (default: input filename stem)
- `--strict` (fail on ambiguous mapping)
- `--no-network` (disable any network calls)
- `--deterministic` (stable sorting, stable keys, no heuristics)

Outputs:
- `OUTPUT_DIR/main.tex` (or `{base}.tex`)
- `OUTPUT_DIR/refs.bib` (or `{base}.bib`)
- `OUTPUT_DIR/warnings.txt`
- `OUTPUT_DIR/verification.txt`
- `OUTPUT_DIR/report.json` (optional)

### 2) enrich
Enrich BibTeX entries using external metadata sources.

```
```

Required behavior:
- Read existing `.bib` and fill missing `title`, `author`/`organization`, and `year`.
- Use ordered strategies: Scholar → DOI → publisher.
- Preserve keys and existing fields unless replacements are authoritative.
- Write updated `.bib` and append to `warnings.txt`.

Options:
- `--no-scholar` (skip Google Scholar)
- `--max-requests N` (rate limit)
- `--cache-dir PATH`

### 3) verify
Verify DOCX vs LaTeX citations.

```
```

Required behavior:
- Extract citations from DOCX (excluding the references section).
- Extract `\cite{}` keys from LaTeX.
- Compare and report missing/extra citations.
- Update `verification.txt` and `warnings.txt`.

### 4) verify-bib
Verify BibTeX URLs and DOIs one by one.

```
drdoc2tex verify-bib PATH/TO/file.bib
```

Required behavior:
- For each entry, check `url` (HTTP 200–399) and `doi` via `https://doi.org/<doi>`.
- Follow redirects (cap at 5).
- Write failures to `bib-non-found-alert.txt`.

## Exit Codes
- `0`: success
- `1`: runtime error
- `2`: verification failures
- `3`: strict mode failures

## Determinism Rules
- Stable key format: `key-N` (N = citation number in DOCX).
- Stable output ordering in `.bib` and reports.
- No network access when `--no-network` is set.

## File Layout (Recommended)
```
src/drdoc2tex/
  cli.py
  pipeline.py
  docx_parser.py
  citations.py
  latex_writer.py
  bib_writer.py
  enrich.py
  verify.py
```
