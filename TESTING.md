# Testing and validation

Use Python 3.12+ and uv. Run these commands from the project root:

```sh
uv sync
uv run python -m unittest discover -s tests -v
uv run python scripts/cv.py build --variant motion
uv run python scripts/cv.py build --variant master
```

The tests cover generic composition, selection validation, invisible-character
rejection, and PDF diagnostics. A build validates the prepared input with the
pinned renderer and writes a PDF, extracted text, report, and page PNGs to
`out/<variant>/qa/`.

Inspect every PNG and read `report.json`, `extracted.txt`, and
`extracted-layout.txt`. Poppler adds a second extraction check when installed.
Passing tests or QA does not verify facts, ATS interpretation, or readiness for
submission.
