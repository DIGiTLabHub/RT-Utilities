# a handy utility for creating handout from a pdf slides

Helper: running example

Install dependencies:

```bash
python3 -m pip install pypdf reportlab
```

Basic usage (3 slides per page, header, page numbers on by default):

```bash
python3 handout.py slides.pdf handout.pdf
```

Two slides per page with custom header and larger note lines:

```bash
python3 handout.py slides.pdf handout.pdf --slides-per-page 2 --header "Weekly Sync" --line-spacing 30
```

Disable the page number footer:

```bash
python3 handout.py slides.pdf handout.pdf --no-page-number
```
