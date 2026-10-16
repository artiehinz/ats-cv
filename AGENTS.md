# Local resume template project

## Purpose

This is a local, privacy-conscious RenderCV template, not a hosted resume
builder or application bot. Keep work in this folder and do not publish,
submit, upload, or expose source resumes without explicit owner permission.

## Content rules

- Keep `content/master.yaml` as the complete editable inventory; use
  `variants/*.yaml` for focused versions.
- Replace placeholders only with owner-confirmed facts. Do not invent dates,
  employers, credentials, metrics, tools, proficiency, or work authorization.
- Keep local originals in `source/` or `old_cv/`; they are private input and
  ignored by Git. Do not edit or commit them.
- Before replacing tracked placeholder YAML with personal content, use a
  private repository or a separate ignored local project. Ignored
  inputs do not protect personalized `content/`, `variants/`, or `REVIEW.md`
  once those tracked files are changed. Inspect `git status` and the staged
  diff before sharing anything.
- Keep all rendered content visible: no hidden keywords, tiny text, or
  off-page content.

## Layout and validation

- Edit `design/blue.yaml` for typography and spacing. Preserve readable body
  text and inspect layout before calling a document ready.
- Run `uv run python -m unittest discover -s tests -v` and build the relevant
  profile after content or design changes.
- Inspect every QA PNG, report, and extraction output. Tests and QA do not
  verify facts, ATS interpretation, or submission readiness.
