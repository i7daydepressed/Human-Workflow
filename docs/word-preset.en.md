# Word preset and independent cover — I02

[Русская редакция](word-preset.ru.md). The neutral [layout](../shared/assets/word/base.docx) and [cover](../shared/assets/word/cover.docx) are derived from preserved formatted blocks of a supplied sample. This is a formatting demonstration, not a submitted report or an institution-wide standard. Its Russian demonstration text does not select the report language. English and Russian workflow instructions share these same binary assets and [format catalog](../shared/assets/word/catalog.json).

The layout retains A4 geometry, measured margins, Times New Roman declarations, justified body paragraphs, three real heading levels, one shared multilevel heading list, live TOC/PAGEREF and PAGE fields, a plain grid table, and image/caption blocks. Heading 3 is corrected to the actual third level. Neutral charts and a matrix replace all source images. A slightly oversized image was fitted to the text width; header repetition, table spacing and heading tabs were made explicit. No historical acceptance or rating transfers to this derivative.

Choose layout and cover separately before Word work. `unselected` remains a missing choice. The built-in IDs are `base-layout-i02` and `base-cover-i02`; record the choice in task state and use a private profile only when explicitly selected. Neither workspace initialization nor a product update selects these resources or changes a user's profile. Accompaniment without a report needs no Word files.

For the neutral cover, request the assignment's actual fields. Department, programme, chair, teacher, group and work number can be omitted when irrelevant; a student-record number is not required. Replace the placeholders and remove unused rows while preserving their surrounding layout. Also offer the user's cover, including a cover already present in a full sample. The helper below merges covers; it does not fill placeholders or convert Markdown.

Run these commands from the source directory, replacing the example paths. Outputs must be new files outside the source/installation:

```bash
python3 shared/scripts/word_cover.py --layout <task-layout.docx> --cover-source builtin --out <new-result.docx>
python3 shared/scripts/word_cover.py --layout <task-layout.docx> --cover-source uploaded --cover <standalone-cover.docx> --out <new-result.docx>
python3 shared/scripts/word_cover.py --layout <task-layout.docx> --cover-source from_sample --cover <full-sample.docx> --out <new-result.docx>
python3 shared/scripts/docx_package.py <new-result.docx>
```

If `--layout` is omitted, the helper uses the neutral base. A layout needs an explicit first cover section. `uploaded` accepts a standalone single-section cover; `from_sample` takes the first explicit section of a sample, or its only section. A section is not necessarily one page: check the selected cover's actual extent. A full sample without a cover-section boundary is not automatically separable.

Cover merge is optional Word mode and requires `lxml`; the other helpers and package audit use the Python standard library. The helper copies selected cover paragraphs/tables, simple embedded pictures, section geometry, headers/footers, referenced styles and numbering. It remaps part/relationship/style/list/drawing identities, isolates cover defaults from body styles, and blocks new cover headers/footers from inheriting into the body. The section-break paragraph's trailing spacing follows the layout boundary to preserve the first body paragraph's placement. It refuses existing results, product-directory outputs and symlink destinations. It never writes to the profile or either input.

This bounded helper rejects embedded objects, textboxes/VML, tracked/review content and notes, embedded fonts, picture bullets, cross-reference fields in the cover, non-picture drawing data, linked pictures and header/footer bookmarks. Some checks conservatively inspect the sample's font/numbering definitions too. Unsupported documents require an explicit document-specific patch. Cover theme fonts resolve to the theme's Latin family. Theme colours use stored explicit RGB when available; tint/shade without stored RGB is rejected. Full theme/script fidelity is not promised. Existing task data, hyperlinks and metadata are not anonymized by cover merge; use a separate privacy review before public sharing.

After editing, refresh fields in the target editor, save a new version, render and inspect every final page. Verify TOC pages against physical headings, page-number continuity, table borders/widths, image geometry, captions and all cover fields. The supplied neutral layout was reviewed as 9 pages and the cover as 1 page on the recorded Linux/LibreOffice renderer. All ten cached TOC rows matched. Three merge modes were exercised with a synthetic custom cover; body pages and the custom cover were compared as rendered pixels. These observations apply to the recorded fixtures, not arbitrary covers.

The DOCX declares Times New Roman. The inspected PDF actually used Liberation Serif; Windows/Microsoft Word has not been tested. A LibreOffice reopen/save remained a 9-page document with live fields and neutral content, but moved several blocks slightly. It is a QA copy, not the distributed binary. Re-render after changing editor, fonts, fields, cover length or report content. `docx_package.py --public-preset` checks package structure/reachable parts and selected prohibited parts; it does not certify anonymity or visual layout. `docx_guard.py --require-toc` checks TOC presence; `--tables` checks table text only.
