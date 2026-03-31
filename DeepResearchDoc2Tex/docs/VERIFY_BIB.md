# BibTeX Link/DOI Verification

## Purpose
Provide a repeatable process to verify every BibTeX entry in a `.bib` file by checking:
- URL accessibility (for web sources)
- DOI resolvability (for journal/conference/book entries)

Each entry must be verified one by one. If verification fails, record it in `bib-non-found-alert.txt`.

## Inputs
- A `.bib` file (example: `deep-research02.bib`)

## Outputs
- `bib-non-found-alert.txt`: one line per failed entry with key and reason

## Verification Rules
1. **URL check**
   - If `url` exists, fetch it and confirm an HTTP 200–399 response.
   - Follow redirects (cap at 5).
   - If status is 4xx/5xx or request fails, mark as non‑found.

2. **DOI check**
   - If `doi` exists, resolve via `https://doi.org/<doi>`.
   - Accept 200–399 responses.
   - If DOI fails to resolve, mark as non‑found.

3. **Entry classification**
   - If a DOI exists, it must pass even if URL fails.
   - If no DOI exists, URL must pass.
   - If both exist, both should pass; failures are recorded separately.

## Failure Recording Format
Append to `bib-non-found-alert.txt`:
```
<bibkey> | <field> | <value> | <reason>
```

Example:
```
key-39 | doi | 10.1145/3711896.3736963 | doi.org returned 403
key-21 | url | https://liner.com/review/medgemma-technical-report | 404 not found
```

## Minimal Manual Procedure
For each BibTeX entry:
1. Open the `url` in a browser; verify it loads.
2. If `doi` exists, open `https://doi.org/<doi>`; verify it resolves.
3. Record any failure in `bib-non-found-alert.txt`.

## Optional Automation Notes
You can automate with a script that:
- Parses the `.bib` file
- Performs URL and DOI checks
- Writes `bib-non-found-alert.txt`

Keep requests rate‑limited and deterministic.
