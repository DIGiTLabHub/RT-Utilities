"""Pipeline orchestration."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from .bib_writer import BibEntry, entry_from_metadata, render_bib
from .citations import Citation
from .docx_parser import extract_citations_with_warnings
from .enrich import Metadata, enrich_url
from .latex_writer import (
    convert_docx_to_latex,
    ensure_bibliography,
    ensure_natbib,
    remove_references_section,
    replace_citations,
)
from .verify import verify_docx_vs_tex


def convert_docx(
    input_path: str,
    output_dir: str,
    base_name: str | None = None,
    strict: bool = False,
    no_network: bool = False,
    deterministic: bool = False,
) -> None:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = base_name or Path(input_path).stem

    citations, parse_warnings = extract_citations_with_warnings(input_path, stop_at_references=True)
    if strict and parse_warnings:
        raise ValueError("Strict mode: ambiguous citations found")

    latex = convert_docx_to_latex(input_path)
    latex = remove_references_section(latex)
    latex = ensure_natbib(latex)
    latex = replace_citations(latex)
    latex = ensure_bibliography(latex, base)
    latex = latex.rstrip() + "\n\\end{document}\n"

    tex_path = out_dir / f"{base}.tex"
    _ = tex_path.write_text(latex, encoding="utf-8")

    entries, warnings = _build_bib_entries(citations, no_network=no_network)
    bib_path = out_dir / f"{base}.bib"
    _ = bib_path.write_text(render_bib(entries), encoding="utf-8")

    warnings_path = out_dir / "warnings.txt"
    all_warnings = warnings + parse_warnings
    _ = warnings_path.write_text(
        "\n".join(sorted(set(all_warnings))) if all_warnings else "No warnings.",
        encoding="utf-8",
    )

    verification_path = out_dir / "verification.txt"
    _ = verification_path.write_text(verify_docx_vs_tex(input_path, tex_path), encoding="utf-8")

    report = {
        "input": input_path,
        "output": str(out_dir),
        "deterministic": deterministic,
        "citations": [asdict(c) for c in citations],
    }
    _ = (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def enrich_bib(output_dir: str, use_scholar: bool = True) -> None:
    out_dir = Path(output_dir)
    bib_path = next(out_dir.glob("*.bib"), None)
    if not bib_path:
        raise FileNotFoundError("No .bib file found in output directory")

    content = bib_path.read_text(encoding="utf-8")
    entry_re: re.Pattern[str] = re.compile(r"@(\w+)\{([^,]+),([^@]+)\}", re.DOTALL)

    entries: list[BibEntry] = []
    warnings: list[str] = []

    matches = cast(list[tuple[str, str, str]], entry_re.findall(content))
    for entry_type, key, body in matches:
        fields: dict[str, str] = {}
        for m in re.finditer(r"\n\s*(\w+)\s*=\s*\{([^}]*)\}\s*,?", body):
            fields[m.group(1).lower()] = m.group(2)
        url: str | None = fields.get("url")
        meta: Metadata | None = enrich_url(url) if url else None
        if meta:
            if "title" not in fields:
                fields["title"] = meta.title or ""
            if "author" not in fields:
                fields["author"] = meta.author or ""
            if "year" not in fields:
                fields["year"] = meta.year or ""
            if "journal" not in fields:
                fields["journal"] = meta.journal or ""
            if "doi" not in fields:
                fields["doi"] = meta.doi or ""

        if use_scholar:
            warnings.append("Scholar enrichment not implemented in CLI; use external workflow.")

        entry = BibEntry(
            key=key,
            entry_type=entry_type,
            title=fields.get("title") or f"Website: {urlparse(url).netloc}" if url else "Untitled",
            author=fields.get("author") or None,
            year=fields.get("year") or None,
            journal=fields.get("journal") or fields.get("publisher"),
            doi=fields.get("doi") or None,
            url=url,
            extra={k: v for k, v in fields.items() if k not in {"title", "author", "year", "journal", "publisher", "doi", "url", "urldate"}},
        )
        entries.append(entry)

    _ = bib_path.write_text(render_bib(entries), encoding="utf-8")

    warnings_path = out_dir / "warnings.txt"
    existing = warnings_path.read_text(encoding="utf-8") if warnings_path.exists() else ""
    if warnings:
        _ = warnings_path.write_text(
            (existing + "\n" + "\n".join(sorted(set(warnings)))).strip() + "\n",
            encoding="utf-8",
        )


def verify_outputs(input_path: str, output_dir: str) -> None:
    out_dir = Path(output_dir)
    tex_path = next(out_dir.glob("*.tex"), None)
    if not tex_path:
        raise FileNotFoundError("No .tex file found in output directory")
    report = verify_docx_vs_tex(input_path, tex_path)
    _ = (out_dir / "verification.txt").write_text(report, encoding="utf-8")


def _build_bib_entries(
    citations: list[Citation],
    no_network: bool = False,
) -> tuple[list[BibEntry], list[str]]:
    entries: list[BibEntry] = []
    warnings: list[str] = []
    for citation in citations:
        meta = enrich_url(citation.url) if not no_network else None
        if meta is None:
            meta = Metadata(url=citation.url)
        entry, entry_warnings = entry_from_metadata(citation.number, citation.url, meta)
        entries.append(entry)
        warnings.extend(entry_warnings)
    return entries, warnings
