from __future__ import annotations

import re
import subprocess

from .citations import key_for_number


def convert_docx_to_latex(docx_path: str) -> str:
    result = subprocess.run(
        ["pandoc", docx_path, "-t", "latex", "-s"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def remove_references_section(latex: str) -> str:
    markers = [
        r"\\section\{References",
        r"\\subsection\{References",
        r"\\section\{References \(Verified",
        r"\\subsection\{References \(Verified",
    ]
    for marker in markers:
        match = re.search(marker, latex)
        if match:
            return latex[: match.start()].rstrip() + "\n"
    return latex


def ensure_natbib(latex: str) -> str:
    if "\\usepackage[numbers]{natbib}" in latex:
        return latex
    return latex.replace("\\begin{document}", "\\usepackage[numbers]{natbib}\n\\begin{document}", 1)


def replace_citations(latex: str) -> str:
    # Replace pandoc href citations: \href{url}{{[}1{]}}
    pattern = re.compile(r"\\href\{[^}]+\}\{\{\[\}(\d+)\{\]\}\}")

    def repl(match: re.Match[str]) -> str:
        return f"\\cite{{{key_for_number(int(match.group(1)))}}}"

    latex = pattern.sub(repl, latex)

    # Replace bare [n] occurrences
    bare_pat = re.compile(r"(?<!\\cite\{)\[(\d+)\]")
    latex = bare_pat.sub(lambda m: f"\\cite{{{key_for_number(int(m.group(1)))}}}", latex)
    return latex


def ensure_bibliography(latex: str, bib_name: str) -> str:
    if "\\bibliographystyle" in latex:
        return latex
    return latex.rstrip() + f"\n\\bibliographystyle{{unsrtnat}}\n\\bibliography{{{bib_name}}}\n"
