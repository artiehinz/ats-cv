#!/usr/bin/env python3
"""Compose a CV, invoke local RenderCV, and inspect the exported PDF.

The checks are layout/text diagnostics, not an ATS score or factual verification.
All paths are resolved relative to this project; no network APIs are called here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path
from typing import Any

import yaml
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
PINNED_RENDERER = "2.8"
INVISIBLE = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return value


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def assemble(master: dict, variant: dict, style: dict) -> dict:
    """Select visible content without modifying the complete master inventory."""
    cv = copy.deepcopy(master["cv"])
    cv.update(copy.deepcopy(variant.get("cv_overrides", {})))
    sections = copy.deepcopy(master["cv"]["sections"])
    for target, selection in variant.get("section_selections", {}).items():
        source = master["cv"]["sections"][selection["source"]]
        indices = selection["indices"]
        if not indices or len(indices) != len(set(indices)):
            raise ValueError(f"Empty or repeated selection in {target}")
        if any(not isinstance(i, int) or i < 0 or i >= len(source) for i in indices):
            raise ValueError(f"Invalid source entry index in {target}")
        sections[target] = [copy.deepcopy(source[i]) for i in indices]
    sections.update(copy.deepcopy(variant.get("section_overrides", {})))
    order = variant.get("section_order", list(sections))
    if not order or len(set(order)) != len(order):
        raise ValueError("Section order must be nonempty and contain no duplicates")
    missing = set(order) - set(sections)
    if missing:
        raise ValueError(f"Unknown sections: {sorted(missing)}")
    cv["sections"] = {key: sections[key] for key in order}
    if any(INVISIBLE.search(s) for s in strings(cv)):
        raise ValueError("Invisible formatting characters found in CV content; review and remove")
    return {"cv": cv, **copy.deepcopy(style)}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for ch in "–—−":
        text = text.replace(ch, "-")
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(text.lower().split())


def expected_fields(payload: dict) -> list[str]:
    cv = payload["cv"]
    fields = [cv["name"], cv["email"], *cv["sections"].keys()]
    for section in cv["sections"].values():
        for item in section:
            if isinstance(item, dict):
                for key in ("company", "position", "institution", "date"):
                    if item.get(key):
                        fields.append(str(item[key]))
    return list(dict.fromkeys(fields))


def inspect_pdf(pdf: Path, payload: dict, report_dir: Path, max_pages: int = 2,
                previews: bool = True) -> dict:
    """Check extraction, key fields, headings, bounds, fonts, and obvious hidden text.

    This deliberately does not claim complete invisibility/occlusion detection,
    semantic employer/date parsing, truth checking, or employer-ATS certification.
    """
    report_dir.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    with fitz.open(pdf) as doc:
        if doc.needs_pass:
            raise ValueError("Encrypted PDF cannot be checked without a password")
        native = "\n".join(page.get_text(sort=False) for page in doc)
        ordered = "\n".join(page.get_text(sort=True) for page in doc)
        (report_dir / "extracted.txt").write_text(native, encoding="utf-8")
        (report_dir / "extracted-layout.txt").write_text(ordered, encoding="utf-8")
        text = normalize(native)
        if not text:
            errors.append("PDF has no extractable text")
        missing = [s for s in expected_fields(payload) if normalize(s) not in text]
        if missing:
            errors.append("Missing expected fields: " + "; ".join(missing))
        positions = [text.find(normalize(h)) for h in payload["cv"]["sections"]]
        if all(p >= 0 for p in positions) and positions != sorted(positions):
            errors.append("Section headings are not in the expected extraction order")
        if len(doc) > max_pages:
            warnings.append(f"{len(doc)} pages exceeds the target of {max_pages}; edit content before shrinking type")
        if pdf.stat().st_size > 2_500_000:
            warnings.append("PDF exceeds the project's conservative 2.5 MB file-size target")
        if "\ufffd" in native:
            errors.append("Replacement characters found in extracted text")
        if INVISIBLE.search(native):
            warnings.append("Zero-width formatting characters found in extracted text")
        fonts: dict[int, dict] = {}
        for number, page in enumerate(doc, 1):
            small, white, out = 0, 0, 0
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        if not span["text"].strip():
                            continue
                        if span["size"] < 9.5:
                            small += 1
                        if span.get("color") == 0xFFFFFF or span.get("alpha", 255) == 0:
                            white += 1
                        bounds = fitz.Rect(span["bbox"])
                        area = page.rect + (-1, -1, 1, 1)
                        if not area.contains(bounds):
                            out += 1
            if small:
                warnings.append(f"Page {number}: {small} text spans below 9.5 pt")
            if white:
                errors.append(f"Page {number}: {white} white/transparent text spans; inspect on white background")
            if out:
                errors.append(f"Page {number}: {out} text spans extend beyond page bounds")
            if any(t.get("type") == 3 for t in page.get_texttrace()):
                errors.append(f"Page {number}: non-painted text detected")
            for font in page.get_fonts(full=True):
                xref = font[0]
                if xref not in fonts:
                    embedded = bool(doc.extract_font(xref)[3]) if xref else False
                    fonts[xref] = {"name": font[3], "embedded": embedded}
                    if not embedded:
                        warnings.append(f"Font is not embedded: {font[3]}")
            if previews:
                page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False).save(report_dir / f"page-{number}.png")
        pages = len(doc)
    poppler = shutil.which("pdftotext")
    secondary_missing: list[str] = []
    if poppler:
        for mode, filename in (([], "poppler.txt"), (["-layout"], "poppler-layout.txt")):
            result = subprocess.run([poppler, *mode, str(pdf), "-"], capture_output=True,
                                    text=True, encoding="utf-8", timeout=30, check=True)
            (report_dir / filename).write_text(result.stdout, encoding="utf-8")
            if not mode:
                secondary_missing = [s for s in expected_fields(payload)
                                     if normalize(s) not in normalize(result.stdout)]
        if secondary_missing:
            warnings.append("Poppler did not preserve some expected fields; inspect its text outputs")
    else:
        warnings.append("Poppler not installed: independent extraction check skipped")
    report = {"status": "fail" if errors else "pass_with_warnings" if warnings else "pass",
              "pages": pages, "bytes": pdf.stat().st_size, "errors": errors, "warnings": warnings,
              "missing_fields": missing, "poppler_available": bool(poppler),
              "poppler_missing_fields": secondary_missing, "fonts": list(fonts.values()),
              "limits": "Text/layout diagnostics only; visual review and factual review remain required. Not an ATS score."}
    (report_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def prepare(variant_name: str) -> tuple[dict, Path, int]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", variant_name):
        raise ValueError("Variant must be a simple filename stem such as motion or art-director")
    master = load_yaml(ROOT / "content/master.yaml")
    variant = load_yaml(ROOT / f"variants/{variant_name}.yaml")
    style = load_yaml(ROOT / "design/blue.yaml")
    payload = assemble(master, variant, style)
    out = ROOT / "out" / variant_name
    out.mkdir(parents=True, exist_ok=True)
    path = out / "Artie_Hinz_CV.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    return payload, out, int(variant.get("max_pages", 2))


def build(variant_name: str) -> dict:
    payload, out, max_pages = prepare(variant_name)
    try:
        installed = importlib.metadata.version("rendercv")
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError("RenderCV is not installed. Run uv sync, then use uv run python scripts/cv.py build") from exc
    if installed != PINNED_RENDERER:
        raise RuntimeError(f"Expected RenderCV {PINNED_RENDERER}, found {installed}; run uv sync")
    executable = shutil.which("rendercv")
    if not executable:
        raise RuntimeError("rendercv CLI is missing from PATH; run this script with uv run")
    sources = [ROOT / "content/master.yaml", ROOT / f"variants/{variant_name}.yaml", ROOT / "design/blue.yaml"]
    input_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    # Build in staging: a failed render cannot overwrite the last generated PDF.
    with tempfile.TemporaryDirectory(prefix=".render-", dir=out) as temp:
        stage = Path(temp)
        command = [executable, "render", str(out / "Artie_Hinz_CV.yaml"),
                   "--pdf-path", str(stage / "Artie_Hinz_CV.pdf"),
                   "--typst-path", str(stage / "Artie_Hinz_CV.typ"),
                   "--markdown-path", str(stage / "Artie_Hinz_CV.md"),
                   "--dont-generate-html", "--dont-generate-png"]
        subprocess.run(command, cwd=stage, check=True, timeout=180)
        pdf = stage / "Artie_Hinz_CV.pdf"
        if not pdf.is_file():
            raise RuntimeError("RenderCV did not produce the expected PDF; inspect its validation output")
        report = inspect_pdf(pdf, payload, stage / "qa", max_pages)
        # Keep the PDF and its diagnostics even when QA fails so the failure can be inspected.
        # This is a draft build directory, never an automatic application/submission destination.
        for suffix in ("pdf", "typ", "md"):
            item = stage / f"Artie_Hinz_CV.{suffix}"
            if item.exists():
                shutil.copy2(item, out / item.name)
        if (out / "qa").exists():
            shutil.rmtree(out / "qa")
        shutil.copytree(stage / "qa", out / "qa")
    (out / "rendered-input.yaml").write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    build_record = {"renderer": installed, "variant": variant_name,
                    "inputs": input_hashes,
                    "qa_status": report["status"], "approval": "DRAFT: owner and visual approval still required"}
    (out / "build.json").write_text(json.dumps(build_record, indent=2) + "\n", encoding="utf-8")
    print(f"PDF: {out / 'Artie_Hinz_CV.pdf'}\nQA: {out / 'qa/report.json'}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "build", "check", "watch"])
    parser.add_argument("--variant", default="motion")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            _, out, _ = prepare(args.variant)
            print(f"Prepared {out / 'Artie_Hinz_CV.yaml'}; no PDF rendered")
            return 0
        if args.command == "check":
            out = ROOT / "out" / args.variant
            # Check against the payload that was actually rendered, not newly edited sources.
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", args.variant):
                raise ValueError("Invalid variant name")
            payload = load_yaml(out / "rendered-input.yaml")
            max_pages = int(load_yaml(ROOT / f"variants/{args.variant}.yaml").get("max_pages", 2))
            report = inspect_pdf(out / "Artie_Hinz_CV.pdf", payload, out / "qa", max_pages)
        elif args.command == "build":
            report = build(args.variant)
        else:
            print("Watching content, variants, and design. Ctrl+C stops.")
            previous = None
            while True:
                paths = [p for d in ("content", "variants", "design") for p in (ROOT / d).glob("*.yaml")]
                signature = tuple((str(p), p.stat().st_mtime_ns) for p in sorted(paths))
                if signature != previous:
                    previous = signature
                    try:
                        report = build(args.variant)
                        print(json.dumps(report, indent=2, ensure_ascii=False))
                    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, yaml.YAMLError, KeyError) as exc:
                        print(f"Build error: {exc}", file=sys.stderr)
                time.sleep(1)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if report["errors"] else 0
    except KeyboardInterrupt:
        return 0
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, yaml.YAMLError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
