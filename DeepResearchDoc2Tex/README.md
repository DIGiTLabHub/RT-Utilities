# DeepResearchDoc2Tex

## Purpose
Convert a ChatGPT Deep Research DOCX into a LaTeX article (`.tex`) and a BibTeX bibliography (`.bib`) without rewriting or shortening the content. Preserve structure, wording, and citation semantics while translating formatting into LaTeX.

This repo also defines a workflow spec in `DeepResearchDoc2Tex.md` that describes how to:
- Extract citations from a DOCX
- Map them to BibTeX keys
- Convert to LaTeX with `\cite{}`
- Enrich BibTeX entries via web sources
- Verify DOCX vs LaTeX reference coverage

## How to Use the Skill (Workflow)
1. Place your input DOCX in this folder (example: `deep-research02.docx`).
2. Follow the pipeline defined in `DeepResearchDoc2Tex.md`:
   - Parse citations and URLs from the DOCX
   - Remove the references section at the end
   - Convert to LaTeX and replace citations with `\cite{key-N}`
   - Build a `.bib` keyed by `key-N`
   - Run citation enhancement (Scholar → DOI → publisher)
   - Run verification (DOCX vs `.tex`) and review `warnings.txt`
3. Outputs:
   - `*.tex` LaTeX document
   - `*.bib` bibliography
   - `warnings.txt` and `verification.txt`

## Python Tool (CLI) Skeleton
This repo includes a CLI skeleton in `src/drdoc2tex` and a CLI spec in `docs/CLI_SPEC.md`.

### Setup
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CLI (stub)
```
python -m drdoc2tex.cli convert INPUT.docx -o OUTPUT_DIR
python -m drdoc2tex.cli enrich OUTPUT_DIR
python -m drdoc2tex.cli verify INPUT.docx OUTPUT_DIR
python -m drdoc2tex.cli verify-bib PATH/TO/file.bib
```

## Files
- `DeepResearchDoc2Tex.md`: Skill/workflow specification
- `deep-research02.docx`: Example input
- `deep-research02.tex`: Generated LaTeX output
- `deep-research02.bib`: Generated BibTeX output
- `warnings.txt`: Missing metadata and unresolved citations
- `verification.txt`: DOCX vs LaTeX citation check result

## Notes
- The DOCX is the source of truth; preserve text and structure.
- Citations must be represented as `\cite{key-N}` in LaTeX.
- Use deterministic keys and keep them stable across enhancement passes.
