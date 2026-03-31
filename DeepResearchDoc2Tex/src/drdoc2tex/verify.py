from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .citations import key_for_number, normalize_url


_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def verify_docx_vs_tex(docx_path: str, tex_path: str | Path) -> str:
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
    numbers: set[int] = set()
    stop = False
    for p in doc_root.findall(".//w:p", _NS):
        text = "".join(t.text or "" for t in p.findall(".//w:t", _NS)).strip()
        if text.lower().startswith("references"):
            stop = True
        if stop:
            break
        for hl in p.findall(".//w:hyperlink", _NS):
            r_id = hl.attrib.get(f"{{{_NS['r']}}}id")
            url = rel_map.get(r_id)
            if not url:
                continue
            _ = normalize_url(url)
            hl_text = "".join(t.text or "" for t in hl.findall(".//w:t", _NS))
            nums: list[str] = re.findall(r"\[(\d+)\]", hl_text)
            for num_str in nums:
                numbers.add(int(num_str))

    tex = Path(tex_path).read_text(encoding="utf-8")
    tex_keys: set[str] = set()
    matches: list[str] = re.findall(r"\\cite\{([^}]+)\}", tex)
    for match in matches:
        for key in match.split(","):
            tex_keys.add(key.strip())

    missing: list[str] = [str(n) for n in sorted(numbers) if key_for_number(n) not in tex_keys]
    extra: list[str] = [key for key in sorted(tex_keys) if not key.startswith("key-")]

    if not missing and not extra:
        return "Verification OK: all DOCX citations are present in LaTeX."
    lines: list[str] = []
    if missing:
        lines.append("Missing citations in LaTeX: " + ", ".join(missing))
    if extra:
        lines.append("Extra citations in LaTeX: " + ", ".join(extra))
    return "\n".join(lines)
