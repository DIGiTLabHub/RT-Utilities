from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from collections.abc import Iterable

from .citations import Citation, normalize_url


_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def _iter_paragraphs(doc_root: ET.Element) -> Iterable[ET.Element]:
    return doc_root.findall(".//w:p", _NS)


def _paragraph_text(paragraph: ET.Element) -> str:
    return "".join(t.text or "" for t in paragraph.findall(".//w:t", _NS))


def extract_citations(docx_path: str, stop_at_references: bool = True) -> list[Citation]:
    citations, _ = extract_citations_with_warnings(docx_path, stop_at_references=stop_at_references)
    return citations


def extract_citations_with_warnings(
    docx_path: str,
    stop_at_references: bool = True,
) -> tuple[list[Citation], list[str]]:
    rels_path = "word/_rels/document.xml.rels"
    doc_path = "word/document.xml"

    with zipfile.ZipFile(docx_path, "r") as z:
        rels_xml = z.read(rels_path)
        doc_xml = z.read(doc_path)

    rels_root = ET.fromstring(rels_xml)
    rel_map = {
        rel.attrib.get("Id"): rel.attrib.get("Target")
        for rel in rels_root
        if rel.attrib.get("Id")
    }

    doc_root = ET.fromstring(doc_xml)
    seen_numbers: set[int] = set()
    number_to_url: dict[int, str] = {}
    citations: list[Citation] = []
    warnings: list[str] = []

    for p in _iter_paragraphs(doc_root):
        text = _paragraph_text(p).strip()
        if stop_at_references and text.lower().startswith("references"):
            break

        for hl in p.findall(".//w:hyperlink", _NS):
            r_id = hl.attrib.get(f"{{{_NS['r']}}}id")
            url = rel_map.get(r_id)
            if not url:
                continue
            hl_text = "".join(t.text or "" for t in hl.findall(".//w:t", _NS))
            nums: list[str] = re.findall(r"\[(\d+)\]", hl_text)
            for num_str in nums:
                num = int(num_str)
                normalized = normalize_url(url)
                if num in number_to_url and number_to_url[num] != normalized:
                    warnings.append(
                        f"Ambiguous URL for citation [{num}]: {number_to_url[num]} vs {normalized}"
                    )
                    continue
                number_to_url[num] = normalized
                if num in seen_numbers:
                    continue
                seen_numbers.add(num)
                citations.append(Citation(number=num, url=normalized))

    return citations, warnings
