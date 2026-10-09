## Start with Codex

Copy this prompt to start with Codex:

```sh
git clone https://github.com/artiehinz/ats-cv.git
cd ats-cv
# For an existing local copy instead: git pull --ff-only

Read `AGENTS.md`, `REVIEW.md`, and `.agents/skills/rebuild-cv/SKILL.md` first. Run `uv sync`, `uv run python -m unittest discover -s tests -v`, `uv run python scripts/cv.py build --variant motion`, and `uv run python scripts/cv.py build --variant master`. Inspect every QA PNG plus `report.json`, `extracted.txt`, and `extracted-layout.txt`. I will provide and confirm facts, and approve changes. Use local source evidence only; never invent facts. Use variants for tailoring, preserve private inputs, and do not publish or submit anything without my explicit permission. Treat `source/` and `old_cv/` as local private inputs: keep their contents out of Git except their README files.
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

## Setup and validation

Python 3.12+ and uv are required. The pinned dependencies are recorded in
`pyproject.toml` and `uv.lock`.

```sh
uv sync
uv run python -m unittest discover -s tests -v
uv run python scripts/cv.py build --variant motion
uv run python scripts/cv.py build --variant master
```

Each build writes `resume.pdf`, `resume.md`, `resume.typ`, the prepared YAML,
and QA artifacts under `out/<variant>/`. Inspect every page PNG and read the
QA report plus both extraction outputs before using a document.

The local validation workflow has been executed for this template, but every
build remains a draft: tests and QA do not verify facts, guarantee ATS
interpretation, or approve a resume for submission.

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
