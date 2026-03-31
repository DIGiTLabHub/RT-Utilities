import argparse
import sys
from pathlib import Path
from dataclasses import dataclass

from .bib_verify import verify_bib_file
from .pipeline import convert_docx, enrich_bib, verify_outputs


@dataclass
class Args:
    command: str
    input: str | None = None
    output_dir: str | None = None
    base_name: str | None = None
    strict: bool = False
    no_network: bool = False
    deterministic: bool = False
    no_scholar: bool = False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="drdoc2tex")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="Convert DOCX to LaTeX/BibTeX")
    _ = convert.add_argument("input", help="Input DOCX file")
    _ = convert.add_argument("-o", "--output-dir", required=True, help="Output directory")
    _ = convert.add_argument("--base-name", help="Base name for outputs")
    _ = convert.add_argument("--strict", action="store_true", help="Fail on ambiguous mapping")
    _ = convert.add_argument("--no-network", action="store_true", help="Disable network calls")
    _ = convert.add_argument("--deterministic", action="store_true", help="Stable keys and ordering")

    enrich = subparsers.add_parser("enrich", help="Enrich BibTeX entries")
    _ = enrich.add_argument("output_dir", help="Output directory containing .bib")
    _ = enrich.add_argument("--no-scholar", action="store_true", help="Skip Google Scholar")
    _ = enrich.add_argument("--max-requests", type=int, default=50, help="Max network requests")
    _ = enrich.add_argument("--cache-dir", help="Cache directory for network results")

    verify = subparsers.add_parser("verify", help="Verify DOCX vs LaTeX citations")
    _ = verify.add_argument("input", help="Input DOCX file")
    _ = verify.add_argument("output_dir", help="Output directory containing .tex")

    verify_bib = subparsers.add_parser("verify-bib", help="Verify BibTeX links and DOIs")
    _ = verify_bib.add_argument("bib_path", help="Path to .bib file")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args(namespace=Args(command=""))
    try:
        if args.command == "convert":
            convert_docx(
                args.input or "",
                args.output_dir or "",
                base_name=args.base_name,
                strict=args.strict,
                no_network=args.no_network,
                deterministic=args.deterministic,
            )
        elif args.command == "enrich":
            enrich_bib(args.output_dir or "", use_scholar=not args.no_scholar)
        elif args.command == "verify":
            verify_outputs(args.input or "", args.output_dir or "")
        elif args.command == "verify-bib":
            bib_path = Path(getattr(args, "bib_path", "") or "")
            failures = verify_bib_file(bib_path)
            alert_path = bib_path.parent / "bib-non-found-alert.txt"
            content = "\n".join(failures) if failures else "No failures."
            _ = alert_path.write_text(content, encoding="utf-8")
        return 0
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - safety net
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
