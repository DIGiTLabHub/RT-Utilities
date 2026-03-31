from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from urllib.parse import urlparse

from .citations import key_for_number
from .enrich import Metadata


@dataclass
class BibEntry:
    key: str
    entry_type: str
    title: str
    author: str | None = None
    year: str | None = None
    journal: str | None = None
    doi: str | None = None
    url: str | None = None
    extra: dict[str, str] = field(default_factory=dict)


def entry_from_metadata(number: int, url: str, meta: Metadata) -> tuple[BibEntry, list[str]]:
    warnings: list[str] = []
    key = key_for_number(number)

    title = meta.title
    if not title:
        title = f"Website: {urlparse(url).netloc}"
        warnings.append(f"Missing title for citation [{number}] {url}")

    year = meta.year
    if not year:
        warnings.append(f"Missing year for citation [{number}] {url}")

    entry_type = "article" if (meta.author or meta.journal) else "misc"
    entry = BibEntry(
        key=key,
        entry_type=entry_type,
        title=title,
        author=meta.author,
        year=year,
        journal=meta.journal,
        doi=meta.doi,
        url=url,
    )
    return entry, warnings


def render_bib(entries: list[BibEntry]) -> str:
    today = date.today().isoformat()
    lines: list[str] = []
    for entry in entries:
        entry_type = entry.entry_type or "misc"
        lines.append(f"@{entry_type}{{{entry.key},")
        lines.append(f"  title = {{{entry.title}}},")
        if entry.author:
            lines.append(f"  author = {{{entry.author}}},")
        if entry.year:
            lines.append(f"  year = {{{entry.year}}},")
        if entry.journal:
            field = "journal" if entry_type == "article" else "publisher"
            lines.append(f"  {field} = {{{entry.journal}}},")
        for key, value in entry.extra.items():
            if key in {"title", "author", "year", "journal", "publisher", "doi", "url", "urldate"}:
                continue
            lines.append(f"  {key} = {{{value}}},")
        if entry.doi:
            lines.append(f"  doi = {{{entry.doi}}},")
        if entry.url:
            lines.append(f"  url = {{{entry.url}}},")
        lines.append(f"  urldate = {{{today}}},")
        lines.append("}")
        lines.append("")
    return "\n".join(lines)
