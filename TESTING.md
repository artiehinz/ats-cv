# Testing and validation

Use Python 3.12+ and uv. Run these commands from the project root:

```sh
uv sync --locked
uv run python -m unittest discover -s tests -v
uv run python scripts/cv.py build --variant motion
uv run python scripts/cv.py build --variant master
```

The unit tests cover generic composition, selection validation, and
invisible-character rejection. They do not render a PDF or validate a commercial
ATS interpretation. A build validates the prepared input with the pinned
renderer and writes a PDF, extracted text, report, and page PNGs to
`out/<variant>/qa/`.

Inspect every PNG and read `report.json`, `extracted.txt`, and
`extracted-layout.txt`. Confirm name/headline/contact reading order, exact
fields, visible URL text, employer/date grouping, active link annotations, and
the absence of unreadable glyphs. The native and layout files are both produced
by the MuPDF-based checker. Poppler adds a second extraction check when
installed; PDFMiner is another optional independent reader:

```sh
python -c "from pdfminer.high_level import extract_text; print(extract_text('out/motion/resume.pdf'))"
```

`pdfminer.six` is optional and not bundled or installed automatically. Passing
tests or QA does not verify facts, commercial ATS interpretation, job match, or
readiness for submission.
