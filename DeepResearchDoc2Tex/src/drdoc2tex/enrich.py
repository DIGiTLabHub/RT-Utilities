from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

import requests

from .citations import normalize_url


@dataclass
class Metadata:
    title: str | None = None
    author: str | None = None
    year: str | None = None
    journal: str | None = None
    doi: str | None = None
    url: str | None = None


def _extract_doi_from_url(url: str) -> str | None:
    match = re.search(r"10\.\d{4,9}/[^\s<>]+", url)
    return match.group(0) if match else None


def _parse_crossref(data: Mapping[str, object]) -> Metadata:
    item = cast(Mapping[str, object], data.get("message", {}))
    title_list = cast(Sequence[str], item.get("title", []))
    title = title_list[0] if title_list else None
    authors = cast(Sequence[Mapping[str, object]], item.get("author", []))
    author = None
    if authors:
        author = " and ".join(
            " ".join(part for part in [cast(str | None, a.get("family")), cast(str | None, a.get("given"))] if part)
            for a in authors
        )
    year = None
    issued = cast(Sequence[Sequence[object]], cast(Mapping[str, object], item.get("issued", {})).get("date-parts", []))
    if issued and issued[0]:
        year = str(issued[0][0])
    journal = None
    container = cast(Sequence[str], item.get("container-title", []))
    if container:
        journal = container[0]
    doi = cast(str | None, item.get("DOI"))
    url = cast(str | None, item.get("URL"))
    return Metadata(title=title, author=author, year=year, journal=journal, doi=doi, url=url)


def fetch_crossref(doi: str, timeout: int = 20) -> Metadata | None:
    try:
        resp = requests.get(f"https://api.crossref.org/works/{doi}", timeout=timeout)
        if resp.status_code != 200:
            return None
        data = cast(Mapping[str, object], resp.json())
        return _parse_crossref(data)
    except requests.RequestException:
        return None


def _extract_meta(html: str, names: list[str]) -> str | None:
    for name in names:
        pattern = rf'<meta[^>]+name=["\"]{re.escape(name)}["\"][^>]+content=["\"]([^"\"]+)["\"]'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        pattern = rf'<meta[^>]+property=["\"]{re.escape(name)}["\"][^>]+content=["\"]([^"\"]+)["\"]'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def fetch_html_metadata(url: str, timeout: int = 20) -> Metadata | None:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "drdoc2tex/1.0"})
        if resp.status_code != 200:
            return None
        html = resp.text
    except requests.RequestException:
        return None

    title = _extract_meta(html, ["citation_title", "dc.title", "og:title"])
    author = _extract_meta(html, ["citation_author", "dc.creator"])
    year = _extract_meta(html, ["citation_year", "citation_date", "dc.date"])
    journal = _extract_meta(html, ["citation_journal_title", "citation_conference_title"])
    doi = _extract_meta(html, ["citation_doi", "dc.identifier"])
    if doi and doi.startswith("doi:"):
        doi = doi.replace("doi:", "").strip()

    return Metadata(title=title, author=author, year=_year_only(year), journal=journal, doi=_clean_doi(doi), url=url)


def _year_only(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"(\d{4})", value)
    return match.group(1) if match else None


def _clean_doi(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if value.startswith("http"):
        doi = _extract_doi_from_url(value)
        return doi or value
    return value


def enrich_url(url: str) -> Metadata:
    url = normalize_url(url)
    doi = _extract_doi_from_url(url)
    if doi:
        crossref = fetch_crossref(doi)
        if crossref:
            return crossref
    html_meta = fetch_html_metadata(url)
    if html_meta:
        return html_meta
    return Metadata(url=url)
