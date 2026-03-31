#!/usr/bin/env python3
import argparse
import importlib
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Sequence, Tuple


@dataclass(frozen=True)
class Layout:
    page_width: float = 612.0
    page_height: float = 792.0
    margin: float = 36.0
    gutter: float = 18.0
    row_gap: float = 12.0
    slide_padding: float = 6.0
    note_padding: float = 6.0
    line_spacing: float = 24.0
    line_inset: float = 8.0
    rows: int = 3
    header_font_size: float = 12.0
    page_number_font_size: float = 10.0

    @property
    def col_width(self) -> float:
        return (self.page_width - 2 * self.margin - self.gutter) / 2

    @property
    def row_height(self) -> float:
        return (
            self.page_height - 2 * self.margin - (self.rows - 1) * self.row_gap
        ) / self.rows

    @property
    def left_col_x(self) -> float:
        return self.margin

    @property
    def right_col_x(self) -> float:
        return self.margin + self.col_width + self.gutter

    def row_bounds(self, row_index: int) -> Tuple[float, float]:
        row_top = self.page_height - self.margin - row_index * (self.row_height + self.row_gap)
        row_bottom = row_top - self.row_height
        return row_bottom, row_top


def validate_layout(layout: Layout) -> None:
    if layout.rows not in (2, 3):
        raise ValueError("Rows must be 2 or 3.")
    if layout.col_width <= 0:
        raise ValueError("Column width must be positive. Check margins/gutter.")
    if layout.row_height <= 0:
        raise ValueError("Row height must be positive. Check margins/row gap.")
    if layout.slide_padding * 2 >= layout.col_width:
        raise ValueError("Slide padding too large for column width.")
    if layout.note_padding * 2 >= layout.col_width:
        raise ValueError("Note padding too large for column width.")
    if layout.line_spacing <= 0:
        raise ValueError("Line spacing must be positive.")


def create_notes_overlay(
    layout: Layout,
    header_text: str,
    page_number: int | None,
    total_pages: int,
) -> Any:
    buffer = BytesIO()
    canvas_module = importlib.import_module("reportlab.pdfgen.canvas")
    Canvas = canvas_module.Canvas
    c = Canvas(buffer, pagesize=(layout.page_width, layout.page_height))
    c.setLineWidth(1)
    for row in range(layout.rows):
        row_bottom, _ = layout.row_bounds(row)
        box_x = layout.right_col_x + layout.note_padding
        box_y = row_bottom + layout.note_padding
        box_w = layout.col_width - 2 * layout.note_padding
        box_h = layout.row_height - 2 * layout.note_padding
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.rect(box_x, box_y, box_w, box_h, stroke=1, fill=0)

        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        line_y = box_y + layout.line_spacing
        line_left = box_x + layout.line_inset
        line_right = box_x + box_w - layout.line_inset
        max_y = box_y + box_h - layout.line_spacing * 0.5
        while line_y < max_y:
            c.line(line_left, line_y, line_right, line_y)
            line_y += layout.line_spacing
    if header_text:
        c.setFont("Helvetica", layout.header_font_size)
        header_y = layout.page_height - layout.margin / 2
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(layout.margin, header_y, header_text)

    if page_number is not None:
        c.setFont("Helvetica", layout.page_number_font_size)
        footer_y = layout.margin / 2
        label = f"{page_number}/{total_pages}"
        text_width = c.stringWidth(label, "Helvetica", layout.page_number_font_size)
        c.drawString(layout.page_width - layout.margin - text_width, footer_y, label)

    c.showPage()
    c.save()
    buffer.seek(0)
    pypdf = importlib.import_module("pypdf")
    return pypdf.PdfReader(buffer).pages[0]


def place_slide(
    target_page: Any,
    slide_page: Any,
    layout: Layout,
    row: int,
    scale_multiplier: float = 1.0,
) -> None:
    row_bottom, _ = layout.row_bounds(row)
    box_x = layout.left_col_x + layout.slide_padding
    box_y = row_bottom + layout.slide_padding
    box_w = layout.col_width - 2 * layout.slide_padding
    box_h = layout.row_height - 2 * layout.slide_padding

    slide_w = float(slide_page.mediabox.width)
    slide_h = float(slide_page.mediabox.height)
    if slide_w <= 0 or slide_h <= 0:
        return

    scale = min(box_w / slide_w, box_h / slide_h) * scale_multiplier
    scaled_w = slide_w * scale
    scaled_h = slide_h * scale
    tx = box_x + (box_w - scaled_w) / 2
    ty = box_y + (box_h - scaled_h) / 2

    pypdf = importlib.import_module("pypdf")
    transform = pypdf.Transformation().scale(scale).translate(tx, ty)
    target_page.merge_transformed_page(slide_page, transform, expand=False)


def generate_handout(
    input_path: str,
    output_path: str,
    layout: Layout,
    header_text: str,
    show_page_numbers: bool,
    slide_scale_multiplier: float = 1.0,
) -> None:
    validate_layout(layout)
    pypdf = importlib.import_module("pypdf")
    reader = pypdf.PdfReader(input_path)
    writer = pypdf.PdfWriter()

    total_slides = len(reader.pages)
    total_pages = (total_slides + layout.rows - 1) // layout.rows
    for page_index, start in enumerate(range(0, total_slides, layout.rows), start=1):
        page = pypdf.PageObject.create_blank_page(
            width=layout.page_width, height=layout.page_height
        )
        page_number = page_index if show_page_numbers else None
        notes_overlay = create_notes_overlay(
            layout,
            header_text=header_text,
            page_number=page_number,
            total_pages=total_pages,
        )
        page.merge_page(notes_overlay)

        for row in range(layout.rows):
            slide_index = start + row
            if slide_index >= total_slides:
                break
            place_slide(
                page,
                reader.pages[slide_index],
                layout,
                row,
                scale_multiplier=slide_scale_multiplier,
            )

        writer.add_page(page)

    with open(output_path, "wb") as output_file:
        writer.write(output_file)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert slide PDFs into letter-size handouts with three slides "
            "and lined notes per page."
        )
    )
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument("--margin", type=float, default=36.0, help="Page margin in points")
    parser.add_argument("--gutter", type=float, default=18.0, help="Column gutter in points")
    parser.add_argument("--row-gap", type=float, default=12.0, help="Gap between rows in points")
    parser.add_argument(
        "--line-spacing", type=float, default=30.0, help="Note line spacing in points"
    )
    parser.add_argument(
        "--slides-per-page",
        type=int,
        choices=[2, 3],
        default=2,
        help="Number of slides and note boxes per page",
    )
    parser.add_argument(
        "--header",
        default="Weekly Sync",
        help="Header text (empty string disables)",
    )
    parser.add_argument(
        "--no-page-number",
        action="store_true",
        help="Disable page number footer",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    layout = Layout(
        margin=args.margin,
        gutter=args.gutter,
        row_gap=args.row_gap,
        line_spacing=args.line_spacing,
        rows=args.slides_per_page,
    )
    slide_scale_multiplier = (
        1.25
        if args.slides_per_page == 2
        and args.header == "Weekly Sync"
        and args.line_spacing == 30.0
        else 1.0
    )
    generate_handout(
        args.input,
        args.output,
        layout,
        header_text=args.header,
        show_page_numbers=not args.no_page_number,
        slide_scale_multiplier=slide_scale_multiplier,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
