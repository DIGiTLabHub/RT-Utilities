# DeepResearchDoc2Tex

## Purpose
Convert a ChatGPT Deep Research DOCX into a LaTeX `article` (`.tex`) and a BibTeX bibliography (`.bib`) without rewriting or shortening the content. Preserve structure, wording, and citation semantics while translating formatting into LaTeX.

## Scope
- In scope: DOCX ingestion, structural preservation, citation extraction, web retrieval for citation metadata, BibTeX generation, LaTeX emission, warnings/reporting.
- Out of scope: Content editing, summarization, and automatic fact-checking.

## Assumptions
- Input is a DOCX produced by ChatGPT Deep Research.
- Citations appear as bracketed numeric tokens (e.g., `[1]`) and are hyperlinks to URLs/DOIs.
- Document may contain headings, paragraphs, lists, quotes, tables, images, and code blocks.
- If assumptions fail, continue with best-effort conversion and emit warnings.

## Inputs
- Primary: DOCX file path (e.g., `@deep-research02.docx`).
- Optional: Output directory, output base name, citation style override (default numeric), and a flag for strictness (strict vs best-effort).

## Outputs
- `output.tex` (or `{inputBase}.tex`): compilable LaTeX `article` document.
- `references.bib` (or `{inputBase}.bib`): BibTeX entries for all unique citations.
- Optional: `citations.json` (or LaTeX comment block) mapping citation numbers to keys/URLs for debugging.
- `warnings.txt`: unresolved citations, missing links, ambiguous cases.

## Pipeline (Required Steps)
1. Read DOCX and extract document structure and inline formatting.
2. Identify and parse linked numeric citations in the text; record `[n] → URL` mapping.
3. Clean the DOCX content by removing the references section at the end, while preserving all in-body citations (`[n]`, `[n,m]`, `[n–m]`).
4. Convert the cleaned DOCX content into LaTeX `article` with required packages/definitions.
5. Normalize citation links and replace them with `\cite{key-number-index}` in the LaTeX output.
6. Retrieve citation metadata from the web for each citation in order of appearance.
7. Generate BibTeX entries keyed by `key-number-index` and write the `.bib` file.
8. Run the citation enhancement loop (Scholar → DOI → publisher) for missing fields.
9. Run verification between DOCX and `.tex`, then write `warnings.txt`.

## Citation Parsing Rules
- Recognize bracketed numbers: `[12]` as citations.
- Support multiple citations:
  - Adjacent: `[1][2]`
  - Comma-separated: `[1,2]`, `[1, 2, 5]`
  - Ranges: `[1-3]` or `[1–3]` (expand to 1,2,3)
- Citations can appear within headings, list items, captions, or inline emphasis.
- Citations must be linked to a URL/DOI when available. If no link is present, mark as unresolved and include in warnings.
- Maintain a deterministic mapping from citation number to BibTeX key. Repeated citations reuse the same key.
- BibTeX key format for this workflow: `key-number-index` (example: `key-12`).

## Citation Normalization
- Canonicalize URLs when possible (strip trackers, normalize scheme, remove fragment if irrelevant).
- Treat DOI links as the same source even if URL differs (normalize DOI as canonical identifier when present).
- If one citation number maps to multiple distinct URLs, treat as ambiguity and warn; choose the first occurrence unless strict mode is enabled.

## Web Retrieval for Citations
- Use a web search/fetch step to retrieve bibliographic metadata from linked URLs/DOIs.
- Prefer authoritative sources (publisher pages, official docs, DOI landing pages).
- Do not follow infinite redirects; cap redirect depth and record the final canonical URL.
- Record `urldate` for all entries.
- If metadata retrieval fails or is incomplete, fall back to minimal entries and log a warning.
- Keep retrieval deterministic: same inputs should yield the same chosen metadata source when possible.
- Metadata fields to attempt (in priority order): `title`, `author`/`organization`, `year`/`date`, `journal`/`publisher`, `doi`, `url`.
- DOI handling:
  - Prefer a canonical DOI value without the `https://doi.org/` prefix.
  - If DOI is the only identifier, treat it as the primary key for deduplication.
- Missing metadata:
  - If `author` is missing, use `organization` or a `key` field for sorting stability.
  - If `title` is missing, use a conservative placeholder derived from the domain.

## Citation Enhancement (Post-Processing)
Use this block to improve existing `.tex`/`.bib` outputs after the first conversion pass.

### When to Run
- Run if any BibTeX entries are missing `title`, `author`/`organization`, or `year`.
- Run if warnings report missing metadata or access-denied sources.

### Enhancement Strategies (Ordered)
1. **Google Scholar BibTeX**
   - Search the exact paper title.
   - Open the result, select **Cite** → **BibTeX**.
   - Replace or enrich the existing BibTeX entry fields.
2. **DOI Landing Page**
   - Use the DOI to fetch metadata from the publisher or Crossref landing page.
3. **Publisher Page Metadata**
   - Use the canonical publisher page metadata (journal, authors, year).

### Enhancement Loop
- Repeat strategies until all citations have `title`, `author`/`organization`, and `year`, or until no new metadata is found.
- Log every failed retrieval attempt with the citation index in `warnings.txt`.

### Update Rules
- Keep BibTeX keys stable; only update fields, do not change keys unless deduplication requires it.
- Preserve `url` and `urldate` in all entries.
- If multiple sources disagree, prefer the most authoritative (publisher > DOI registry > secondary sources).
- Record all updates and remaining gaps in `warnings.txt`.

## BibTeX Generation Rules
- One BibTeX entry per unique source.
- Preferred fields when available: `author`, `title`, `year`, `journal`/`publisher`, `doi`, `url`, `urldate`.
- If only a URL is available (or metadata retrieval fails), use a conservative fallback (e.g., `@misc`) and include `url` and `urldate`.
- BibTeX key scheme must be deterministic and collision-resistant.
  - Example rule: `source{n}` or `authorYearShortTitle` with a numeric suffix on collision.
- Dedupe entries by canonical URL or DOI.

## LaTeX Conversion Rules
- Output a compilable `article` document with a minimal, justified package set.
- Use a numeric citation style to render `[n]` (document the exact mechanism).
- All linked citations must be converted to `\cite{key-number-index}` in the LaTeX source.
- Preserve structure and ordering:
  - Headings and section hierarchy
  - Paragraphs
  - Lists (ordered/unordered)
  - Block quotes
  - Code blocks (verbatim/monospace)
  - Tables (simple tables should be converted; complex tables may fall back to a placeholder with warning)
  - Images (include placeholders or figure environments if extraction is not supported)
- Preserve inline emphasis (bold/italic) and links.
- Escape LaTeX-special characters: `% $ & _ # { } ~ ^ \`.
- Do not editorialize or reflow content beyond required LaTeX normalization.

## Error Handling and Warnings
- Non-fatal: missing citation links, malformed URLs, unresolvable metadata, complex tables/images.
- Fatal (strict mode): inconsistent citation number mappings, unreadable DOCX, LaTeX output generation failure.
- Always emit `warnings.txt` summarizing all issues and chosen fallbacks.

## Acceptance Criteria
- `.tex` compiles without errors using standard LaTeX toolchains.
- All citations in the DOCX appear in the LaTeX output at the same positions.
- Every unique citation has a BibTeX entry in `.bib`.
- No content is omitted or rewritten; structure is preserved.
- Warnings list all unresolved/ambiguous cases.

## Edge Cases and Required Behavior
- Citation token present but no hyperlink: preserve token, emit warning, optionally assign a placeholder key.
- Hyperlink present but empty/malformed: preserve token, emit warning, do not fabricate metadata.
- Duplicate citations: same URL across different numbers should map to one BibTeX entry and shared key.
- Same number pointing to different URLs: warn and use first occurrence unless strict mode is enabled.
- Out-of-order or skipped numbering: preserve literal numbering and warn only if inconsistent mappings are found.
- Mixed separators and range notation: expand ranges deterministically; normalize separator spacing.
- Citations inside emphasized text or headings: maintain formatting and insert citation command inline.
- Non-ASCII text, smart quotes, em-dashes, ligatures: preserve characters; normalize only if needed for LaTeX safety.
- Long URLs: allow line breaking in LaTeX or use appropriate URL formatting to avoid overfull boxes.

## Determinism and Reproducibility
- Same input must produce identical `.tex` and `.bib` outputs.
- Citation key generation must be deterministic.
- Warning order and content must be stable.

## Minimum Viable Fidelity
- Correct structure and citation mapping are mandatory.
- Formatting details (e.g., exact spacing or line breaks) may vary if they do not change meaning.

## Nice-to-Have Fidelity
- Preserve exact list spacing and paragraph breaks.
- Map DOCX styles to LaTeX macros when possible.

## Verification Checklist
- [ ] DOCX ingested and parsed without loss of structure
- [ ] All citations detected and mapped
- [ ] `.bib` entries generated and deduplicated
- [ ] LaTeX output compiles and matches content order
- [ ] Warnings produced for all unresolved cases
- [ ] Verification pass compares DOCX vs `.tex` and confirms no missing references

## Verification Pass (DOCX vs LaTeX)
After generation, run a dedicated check to ensure all DOCX references appear as `\cite{}` in LaTeX.

### Required Checks
- Extract all linked numeric citations from DOCX (by citation number and URL).
- Extract all `\cite{}` keys from LaTeX.
- Map DOCX citation numbers to BibTeX keys and verify every DOCX citation is represented in LaTeX.
- Report any missing or extra references in `warnings.txt`.
