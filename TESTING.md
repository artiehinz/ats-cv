# Test status

## Executed in the preparation environment

Environment: Python 3.13.5, PyYAML 6.0.3, PyMuPDF 1.26.7; Poppler available.

`python -m unittest discover -s tests -v`: **10 tests passed**.

These cover the original PDF checksum, section/entry inventory counts, nonmutating
variant composition, section selection/order, preservation of employment/date
records, invalid selection and section rejection, invisible-character rejection,
recovered hyperlink inventory, and a PDF-checker smoke test on the ORIGINAL PDF.

Both `prepare --variant master` and `prepare --variant motion` completed and
produced combined YAML inputs. They did not run RenderCV schema validation.

`build --variant motion` was attempted and exited with the expected explicit
missing-RenderCV error. No generated resume PDF is included.

## Not executed or established

- Installing/resolving the RenderCV environment and generating uv.lock.
- RenderCV 2.8 schema validation and PDF/Typst/Markdown generation.
- End-to-end build/watch behaviour with the renderer installed.
- Proposed design's actual page count, typography, wrapping, or visual quality.
- Full semantic parsing by any commercial ATS or recruiter system.
- Verification that source facts, work status, or portfolio links remain current.

Package installation was unavailable because the preparation runtime could not
reach external package hosts. A local Codex environment must perform the first
full build and inspect the output; dependency/schema/layout fixes may be needed.
The scripts use documented RenderCV CLI options and the v2.8 source schema, but
that is not a substitute for an executed integration test.
