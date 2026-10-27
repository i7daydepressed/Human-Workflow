# Word conversion using a sample

## Current input

For initial assembly, use agreed MD and the selected sample. After manual Word edits, obtain current DOCX and save its baseline SHA-256. Check project.md/log for changed captions, panel labels, image sizes, tables, fonts, cover. Apply the new edit to this DOCX. For MD content changes, compare old MD, new MD, and current Word; preserve manual edits and show exact conflicts.

The previous converter may not describe final Word: an earlier project preserved manual edits in later patch scripts. A DOCX hash differing from a historical snapshot signals a different revision, not necessarily corruption or unauthorized edits.

## Preparation

Obtain fresh MD, images, and selected DOCX. Read the documents skill and follow its runtime/render workflow. Explicitly select layout sample and current-work cover source; retaining a cover does not mean copying another lab's number/topic.

Run `python3 <package-root>/shared/scripts/inspect_word_sample.py sample.docx --out sample-inventory.json`. Inspect the sample and XML. Identify cover/section break, body, headings 1–3, caption, image, table/header/data row, equation, list, unnumbered section, TOC. Determine margins, spacing, indents, fonts, keepNext/keepLines, headers/footers, numbering. Bold alone does not identify a block role.

Do not reuse paragraph indices from a different lab/sample revision.

## XML blocks

Work on a sample-package copy, retaining styles, numbering, theme, headers/footers, sections, relationships. Preserve agreed cover blocks where possible and change only assigned details. Remove unrelated sample body text.

Check inherited Normal/theme effects; body edits must not move the approved cover. If necessary give cloned cover blocks a distinct style with original properties while preserving appearance. Do not redesign the cover or remove blank paragraphs without determining their role.

Deep-clone suitable `w:p`/`w:tbl` and replace contents while retaining required `pPr`/`rPr`. Avoid `.text = ...` when it destroys runs, links, or fields. Register new images/links with own relationships and unique drawing/bookmark IDs; no links to missing package parts.

Choose body style explicitly; remove accidentally inherited heading numPr/outlineLvl/keepNext. Nonprinting squares may indicate pagination/keep properties. Diagnose the actual cause rather than treating every square as a heading or changing the user's Word settings.

Clone table rows by role, preserving borders/fonts/alignment. Adapt cell counts/widths within margins. Repeat headers and avoid splitting short rows across pages.

## Headings and TOC

Map MD to real Heading 1/2/3 or local equivalents. Verify outlineLvl, common abstractNum/numId, level restarts, and `1 / 1.1 / 1.1.1`. Remove manually typed numbers only after correct automatic numbering is connected.

If level 3 incorrectly uses level-2 styling, preserve appearance while correcting semantic level/linkage. Do not create independent counters for patched sections.

Preserve live TOC, bookmarks, hyperlinks, PAGE/PAGEREF. A typed list is not an automatic TOC. Recalculate fields with an available editor. If reliable TOC updating is unavailable, fill a verified result cache while retaining the live instruction. Match cache to final-render page numbers using full section numbers/bookmarks; duplicate titles can occur.

Set fonts/sizes in TOC styles, not only current runs, so updates retain formatting. Add the first-level number's dot if the selected sample/profile requires it. If selected by the assignment/sample/profile, start conclusion/sources on a new page using explicit breaks/style properties and check for extra blank pages.

Recheck TOC pages after image/spacing/table changes. `updateFields=true` alone does not guarantee accurate cached page numbers.

## Verify

Preserve hyperlinks and use editable OMML equations where supported. Otherwise state the actual format; an equation image is not editable math. Scale figures proportionally, keep captions with figures, and check text readability.

Compare sections, figures, tables, equations against MD and check references to deleted material. Check cover, body, third-level headings, numbering, tables, links, final pages, placeholders, and sample leftovers.

Render under the documents skill and inspect every page. Open suspicious contact-sheet regions at readable scale. After a small repeat edit, inspect only changed pages if render comparison confirms others unchanged. Script counts do not establish visual review.

Keep QA renders internal. Deliver DOCX; add PDF/archives when requested. Preserve converter and chosen XML-block map without hardcoded transient scratch paths.

## Preservation checks

`docx_guard.py baseline.docx result.docx --cover-before N --tables --media` compares selected cover XML before body index N, table text only, and media bytes. Determine N from the actual sample. It does not compare renders or prove visual equivalence. Exclude intentional changes from invariants or check separately. For table-format repairs, check content preservation rather than requiring unchanged complete table XML.

## Tables and pagination

Preserve the selected table style; generic artifact defaults do not authorize decorative fill against a task choice. Check widths using actual bold headers and long values at the agreed font size. Excessive body keepNext/keepLines may create gaps; retain needed figure/caption links and diagnose nonprinting marks.


A universal MD → Word compositor is future work, not a feature of this version. Preserve project block maps, generators, and patch scripts as evidence; their presence does not guarantee automatic preservation of every future manual edit.
