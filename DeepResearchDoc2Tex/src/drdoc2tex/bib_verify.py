from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import requests


@dataclass
class BibEntry:
    key: str
    url: str | None
    doi: str | None


def parse_bib_entries(content: str) -> list[BibEntry]:
    entry_re: re.Pattern[str] = re.compile(r"@(\w+)\{([^,]+),([^@]+)\}", re.DOTALL)
    entries: list[BibEntry] = []
    for match in entry_re.finditer(content):
        key = str(match.group(2))
        body = str(match.group(3))
        url = _extract_field(body, "url")
        doi = _extract_field(body, "doi")
        entries.append(BibEntry(key=key, url=url, doi=doi))
    return entries


def _extract_field(body: str, name: str) -> str | None:
    match = re.search(rf"\n\s*{re.escape(name)}\s*=\s*\{{([^}}]+)\}}", body, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()


def verify_bib_file(bib_path: Path, timeout: int = 20) -> list[str]:
    content = bib_path.read_text(encoding="utf-8")
    entries = parse_bib_entries(content)

    failures: list[str] = []
    for entry in entries:
        failures.extend(_verify_entry(entry, timeout=timeout))
    return failures


def _verify_entry(entry: BibEntry, timeout: int = 20) -> list[str]:
    failures: list[str] = []
    if entry.url:
        ok, reason = _check_url(entry.url, timeout=timeout)
        if not ok:
            failures.append(f"{entry.key} | url | {entry.url} | {reason}")

    if entry.doi:
        doi_url = f"https://doi.org/{entry.doi}"
        ok, reason = _check_url(doi_url, timeout=timeout)
        if not ok:
            failures.append(f"{entry.key} | doi | {entry.doi} | {reason}")

    if not entry.doi and not entry.url:
        failures.append(f"{entry.key} | url | <missing> | no url or doi present")

    return failures


def _check_url(url: str, timeout: int = 20) -> tuple[bool, str]:
    headers = {"User-Agent": "drdoc2tex/1.0"}
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        if response.status_code >= 400:
            response = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers)
        if response.history and len(response.history) > 5:
            return False, "too many redirects"
        if 200 <= response.status_code < 400:
            return True, "ok"
        return False, f"status {response.status_code}"
    except requests.RequestException as exc:
        return False, str(exc)
