# Owner review and migration notes

This is a starter, not an approved final CV. No employment or credential claim has
been independently verified. No new facts were obtained from portfolio websites.
Links were recovered directly from the original PDF's annotations.

## Confirm before submission

1. Is Studio Dialog still current? The source says Jun 2023 – Present.
2. What were the separate dates and relationships for New Cave Media, Blackbox,
   and Art. Lebedev Studio? Until confirmed, keep their 2017–2020 grouping intact.
3. Are Canadian work authorisation, relocation preferences, and international
   sponsorship requirements still current? The file does not establish status today.
4. What qualifications and completion dates belong to the two education entries?
   The source does not specify degrees, graduation dates, IELTS band, or test date.
5. Clarify individual awards versus project/team recognition versus work for an
   awards event. M1 Music Awards V currently describes live show visuals, not an
   explicitly stated award received by Artie.
6. Which pipeline contributions belong to which job? Do not assign them from inference.
7. Are project view counts and portfolio destinations still accurate? Check manually.
8. Confirm historical role spelling and portfolio project spelling as desired.
9. Decide whether to shorten work preferences and move confirmed Canadian work
    authorisation into the header or summary.

## Source mapping (original PDF)

Page 1: identity, contact details, summary, core skills, software, Studio Dialog,
freelance work, and Invite Agency.
Page 2: Sinners Studio; grouped 2017–2020 experience; six selected projects; five
AI/pipeline contributions; awards/recognition; work preferences; education/language.

## Migration versus proposed edits

content/master.yaml retains the source inventory and is now organized into ten
sections, including the owner-confirmed Languages section. Owner-confirmed wording
and tool updates are recorded below. Paragraph line wrapping and heading/role capitalisation were normalised. The
concatenated Studio Dialog role/employer heading was separated into distinct fields.
Dates are kept as the source's visible date strings; no missing months were supplied.
The unchanged original PDF remains the authority for exact wording and appearance.

variants/motion.yaml is a proposal: shorter summary, a new supported professional
headline, selected skills grouped into four lines, selected projects, experience
earlier, and a dedicated Languages section. The header uses the owner-confirmed
LinkedIn and GitHub labels; the full source inventory retains the network entries.
These are draft editing decisions, not user-approved corrections to the source.

The profile selection indices are zero-based. Update selections and tests when
reordering master entries. A new profile can override sections, but its claims still
need human source review; code cannot establish their truth.

## First local build checklist

- Run uv sync; keep uv.lock after successful resolution.
- Run all tests and build both master and motion.
- Inspect every PNG; two pages is a target, not a confirmed result in this starter.
- Confirm no clipped text, crowded header, isolated headings, or poor page breaks.
- Read extracted.txt and poppler.txt for section order and field relationships.
- Check phone, email, portfolio and project hyperlinks in the actual PDF.
- Review all source questions above before marking the PDF approved.

## User-confirmed changes

- Confirmed 2026-10-09: use 9+ years and state that Artie started as an intern in
  2017, without assigning an employer or separate internship dates.
- Confirmed 2026-10-09: add Russian and Ukrainian without proficiency levels;
  retain English at IELTS B2.
- Confirmed 2026-10-09: remove the US/EU visa-sponsorship sentence; update the
  Behance award to 3x 3D Motion and 3x After Effects Awards.
- Confirmed 2026-10-09: use Co-op Bubbles Campaign and its corrected portfolio
  URL; include RIMOWA in the motion selection; simplify the Projects section name.
- Confirmed 2026-10-09: remove the discontinued tools, add Higgsfield, and
  describe AI use as human-led.
