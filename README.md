# Artie Hinz — local, Codex-editable CV starter

A file-based CV project built around RenderCV 2.8, not a hosted resume builder.
Your original PDF is preserved; editable data, application variants, design, and
validation code are separate. No GitHub account, database, Docker container, or
resume-service account is required for the build.

## Private source-resume workflow

The imported `source/` files are the preserved private evidence for this starter
project. For a future conversion, put an original resume in `old_cv/`; Codex can
read it and convert its contents into this RenderCV-based project. `old_cv/` is
local input only and is ignored by Git (except its README). The preserved
`source/original.pdf` and `source/original.txt` are also ignored, so neither
source-resume path is committed accidentally.

**Current validation state:** the pinned RenderCV 2.8 environment has been
resolved locally, the no-network test suite passes, and the motion and master
variants have been rendered and visually reviewed with their QA reports. Builds
remain drafts: visual checks do not verify facts, guarantee ATS interpretation,
or approve a CV for submission. Re-run the commands below after any content or
design change and review `TESTING.md` and `REVIEW.md` before using an output.

## Requirements and setup

Python 3.12+ and uv. The included .python-version selects Python 3.13. Install uv
using its official instructions, or `python -m pip install uv` in a suitable Python
environment. First-time dependency installation needs internet access.

From this folder:

```sh
uv sync
uv run python -m unittest discover -s tests -v
uv run python scripts/cv.py build --variant motion
```

The three direct dependencies are pinned in pyproject.toml. The first `uv sync`
resolves transitive dependencies and creates uv.lock. Retain that file; subsequent
installs can use `uv sync --locked`. No fabricated or untested lockfile is included.

The scripts themselves do not call remote services. Dependencies and any missing
font/package assets must be installed or cached before attempting an offline build.
Codex's model connection is separate from local document rendering; this project
does not configure offline AI inference.

Optional independent PDF extraction uses Poppler (`pdftotext`). On macOS use
`brew install poppler`; on Debian/Ubuntu use `sudo apt-get install poppler-utils`.
On Windows, run those commands inside WSL or install a trusted Poppler distribution
and add its tools to PATH. Without Poppler, QA clearly records that check as skipped.

## Everyday commands

```sh
# Full source inventory; may be longer than the two-page submission target.
uv run python scripts/cv.py build --variant master

# Proposed motion-designer version.
uv run python scripts/cv.py build --variant motion

# Rebuild when content, variant, or style YAML changes.
uv run python scripts/cv.py watch --variant motion

# Generate the combined YAML only (no renderer invoked).
uv run python scripts/cv.py prepare --variant motion

# Recheck the previously rendered input/PDF pair.
uv run python scripts/cv.py check --variant motion
```

Open the PDF in a local viewer; inspect the QA PNGs for actual pagination. Watch
mode polls YAML files; after changing Python code, restart it. It does not serve
files on a network port or depend on browser automation.

## Where to edit

| File or folder | Purpose |
| --- | --- |
| source/ | Unchanged PDF, extracted text, recovered hyperlinks, source checksum |
| content/master.yaml | Complete editable inventory from the supplied PDF |
| variants/master.yaml | Full-content rendering |
| variants/motion.yaml | Proposed selected content, summary, headline and section order |
| design/blue.yaml | Fonts, blue accent, spacing, page geometry and experience-entry template |
| scripts/cv.py | Compose, build, watch, extract, validate and produce previews |
| tests/ | Source/composition/checker tests; not a RenderCV integration test |
| jobs/ | Local job descriptions for evidence-based tailoring |
| AGENTS.md | Project instructions Codex reads |
| .agents/skills/rebuild-cv/SKILL.md | Project-specific editing/build workflow |
| REVIEW.md | Unresolved source questions and user-approved corrections |

The renderer's built-in schema validates the final combined YAML during `build`.
The `prepare` command only checks our selection rules; it is not full RenderCV
schema validation. Only listed sections enter the combined submission payload.
Unselected content is absent, not hidden with colour, tiny text, or metadata.

The project-local `.agents/skills/rebuild-cv/SKILL.md` skill is the concise
workflow for Codex-assisted CV edits: it requires source-aware changes, local
tests and rendering, PNG/QA inspection, and explicit warnings about factual or
ATS limitations. It never authorizes publishing, submitting, or exposing the
private source files.

The source inventory remains complete. For application-specific changes, copy a
variant file to e.g. variants/art-director.yaml and edit its settings. Then build
with `--variant art-director`. Selections use zero-based indices into the master.
Do not duplicate or fabricate employment dates to make a new version.

The draft design keeps role, employer, location and dates in the same content
column via `design.templates.experience_entry`, without modifying RenderCV itself.
Start with these supported design controls rather than forking the upstream app.
For deeper Typst customisation, use the pinned RenderCV template-override guide and
adapt the build's template discovery paths explicitly; that is not preconfigured.

## Outputs after a successful local render

```text
out/motion/
  Artie_Hinz_CV.pdf      # Generated draft application document
  Artie_Hinz_CV.md       # RenderCV Markdown output
  Artie_Hinz_CV.typ      # Generated Typst; not the maintained source
  Artie_Hinz_CV.yaml     # Latest prepared renderer input
  rendered-input.yaml   # Snapshot corresponding to the rendered PDF
  build.json            # Renderer version, source hashes, draft status
  qa/
    page-1.png           # One preview per actual PDF page
    page-2.png
    extracted.txt
    extracted-layout.txt
    poppler.txt          # When Poppler is installed
    poppler-layout.txt
    report.json
```

These files are regenerated; do not edit them as the master. A failed renderer
run does not overwrite the last PDF. A rendered PDF with QA errors is retained in
out/ with its error report for inspection, and the command exits unsuccessfully.
Warnings require review even if the process exits successfully. There is no
automatic approval, upload, or application submission step.

## QA scope and limits

Checks cover extractable text, missing key fields, heading order, replacement
characters, small text, obvious non-painted/white/transparent text, page bounds,
font embedding, page count and file size. Poppler adds a second extraction view.

This is not full hidden-text or overlap detection. It does not establish correct
semantic parsing by a recruiter platform, skill validity, or a hiring probability.
It does not compare every word or hyperlink against the source. Inspect all pages,
read both text outputs, and manually verify links and factual changes. Page-count
limits are layout targets, not proof of an industry-wide rule.

## Working with Codex

Open this folder with a local Codex client, or start `codex` from this root. Git is
optional for these scripts; local version-control checkpoints are still useful.
Do not publish this project: it contains your private contact details and CV.

Suggested first task:

> Read AGENTS.md and REVIEW.md. Install the pinned environment, run the tests, and
> build the motion variant. Treat the source PDF as evidence, not as a record that
> every fact is current. Inspect every generated page and the QA report. Refine
> spacing to achieve a readable two-page draft without reducing body text below
> 10.5 pt. Keep role/employer/date relationships explicit. Report unresolved facts
> separately; do not invent missing information or submit the CV.

RenderCV also publishes an optional upstream agent skill. After reviewing it, it
can be installed for Codex using Node/npm:

```sh
npx skills add rendercv/rendercv-skill -a codex
```

This is optional and not a build dependency. Check its advice against pinned
RenderCV 2.8; upstream skills and documentation can move ahead of a pinned release.

## Primary documentation

- RenderCV repository: https://github.com/rendercv/rendercv
- RenderCV CLI: https://docs.rendercv.com/user_guide/cli_reference/
- Design schema: https://docs.rendercv.com/user_guide/yaml_input_structure/design/
- RenderCV agent skill: https://docs.rendercv.com/user_guide/how_to/use_the_ai_agent_skill/
- Codex project instructions: https://developers.openai.com/codex/agent-configuration/agents-md
- uv project workflow: https://docs.astral.sh/uv/guides/projects/

The upstream projects retain their own licences. No standalone font files,
third-party executables, installed dependencies, credentials, or generated CV PDF
are bundled. The original source PDF is included only as your private reference.
