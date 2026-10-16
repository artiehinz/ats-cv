## Start with Codex

Copy this prompt to start with Codex:

```text
git clone https://github.com/artiehinz/ats-cv.git
cd ats-cv
# For an existing local copy instead: git pull --ff-only

Read `AGENTS.md`, `REVIEW.md`, and `.agents/skills/rebuild-cv/SKILL.md` first.

1. Find my original CV under `source/` or `old_cv/` and preserve it unchanged. Before editing tracked YAML with personal information, confirm I am working in a dedicated private clone/repository or an ignored private project.
2. Ask for the target role, work preferences, and any missing factual clarifications. Treat the original CV as evidence: replace placeholders with a complete verified inventory, keep unresolved facts in `REVIEW.md`, and never infer dates, degrees, metrics, credentials, or tools.
3. Keep a full master inventory and create a focused variant for the target role. Do not hide keywords or content.
4. Run `uv sync --locked`, the unit tests, and builds for both `motion` and `master`. Inspect every QA PNG, `report.json`, `extracted.txt`, and `extracted-layout.txt`; use an independent reader when available. Verify links, visible URL text, and name/headline/contact reading order.
5. Return the PDF paths and unresolved questions. Do not upload, publish, share, or submit any document or source material without my explicit permission.
```

# Convert an old CV into an ATS-friendly resume with Codex

Place an old CV locally, let Codex read it as evidence, and convert
owner-verified facts into structured YAML. RenderCV then produces a modern,
ATS-friendly PDF, while local checks and page previews support review. The
workflow does not promise universal ATS compatibility or automatic factual
correctness.

## How it works

1. Put the original CV in `old_cv/` or `source/`; both are private and ignored.
2. Start Codex with the prompt above.
3. Provide or confirm facts and resolve questions before changes are approved.
4. Codex updates the master inventory and optional job-specific variants.
5. Build the PDF and inspect its QA report, extracted text, and previews before use.

## Privacy

Use `source/` or `old_cv/` for original resumes and other private evidence.
Those directories are local input only and ignored by Git (apart from their
README files). Do not publish, submit, or upload source material without the
owner’s explicit permission.

Ignoring inputs and `out/` does not make tracked YAML private. Before replacing
the generic placeholders in `content/`, `variants/`, or `REVIEW.md` with a real
person's information, work in a private repository or a separate ignored local
project. `.gitignore` cannot untrack files that Git already
knows about. Check `git status` and the staged diff before sharing a repository.

## Setup and validation

Python 3.12+ and uv are required. The pinned dependencies are recorded in
`pyproject.toml` and `uv.lock`.

```sh
uv sync --locked
uv run python -m unittest discover -s tests -v
uv run python scripts/cv.py build --variant motion
uv run python scripts/cv.py build --variant master
```

On Windows PowerShell, use the same commands with
`$env:PYTHONUTF8='1'` set for the session. If the `uv` command is not on PATH,
use `python -m uv sync --locked` and replace `uv run` with `python -m uv run`.
This does not install anything globally.

Each build writes `resume.pdf`, `resume.md`, `resume.typ`, and prepared YAML to
`out/<variant>/`, with QA artifacts under `out/<variant>/qa/`. Inspect every
page PNG and read the QA report plus both extraction outputs before using a
document.

`out/personal/` is only an optional custom local convention; it is not produced
by this generic template. Public template builds remain under `out/<variant>/`.

The local validation workflow has been executed for this template, but every
build remains a draft: tests and QA do not verify facts, guarantee ATS
interpretation, or approve a resume for submission.

For an optional independent text-reader check, install `pdfminer.six` in your
own environment if it is not already available, then run:

```sh
python -c "from pdfminer.high_level import extract_text; print(extract_text('out/motion/resume.pdf'))"
```

Compare the name, headline, contact order, visible URLs, employer/date grouping,
and links against the PDF. The built-in native and layout extraction files are
two views from the same MuPDF-based checker; Poppler or PDFMiner is an
independent reader when locally available. Neither is a commercial ATS test or
a job-match assessment.

## Where to edit

| Path | Purpose |
| --- | --- |
| `content/master.yaml` | Complete editable placeholder inventory |
| `variants/master.yaml` | Full-inventory profile |
| `variants/motion.yaml` | Focused two-page example profile |
| `design/blue.yaml` | Typography, colour, spacing, and entry layout |
| `source/` | Local private evidence; ignored except its README |
| `old_cv/` | Local original-resume input; ignored except its README |
| `REVIEW.md` | Owner confirmations and unresolved questions |
| `.agents/skills/rebuild-cv/SKILL.md` | Project-local Codex editing/build workflow |

Replace placeholders only with owner-confirmed information. Keep unused but
verified material in the master inventory; make application-specific selections
and wording in a variant. See `AGENTS.md`, `REVIEW.md`, and `TESTING.md` for
the operating rules.

## Project-local Codex skill

The included `rebuild-cv` skill guides source-aware edits, local test/build
execution, PNG and QA inspection, and clear warnings about factual and ATS
limits. It does not authorize publishing, submission, or exposing private
source files.
