# Project, cloud, and checkpoints

For accompaniment without a report, keep current requirements/specification, core state, log, and needed evidence. Create illustration/Word folders and report.md only when useful. Use actual project names; the table lists possible materials, not mandatory empty files.

## Structure

| Path | Purpose |
| --- | --- |
| `project.md` or equivalent | Requirements/specification, deliverables, core/report state, versions, checks, decisions, next step |
| Actual specification/map path | Required outcome, limits, criteria, explanation evidence; separate from execution facts |
| `agent-logs/<run-id>.md` | Individual executor log; applicable AGENTS.md takes precedence |
| `report.md` | Selected working text; reconcile local and remote versions and the recorded content authority on resumption |
| `sources/` | Guide, assignment, source materials |
| `assets/cards/` | Educational illustrations, diagrams, cards |
| `assets/code/` | Actual source-code excerpts |
| `assets/screenshots/` | User-provided or actual application-run screenshots |
| `assets/figure-index.md` | Files, caption, section, provenance, commit/calculation, legend |
| `checkpoints/<timestamp>-<label>/` | Selected MD, assets, project.md, logs, output, converters, manifest; exclude recursive checkpoints |
| `word-examples/` | DOCX samples and catalog.md with status/scope |
| `output/` | Final DOCX and explicitly requested formats |

Do not restructure an existing project to match names. Record actual mappings in project.md and create remote folders as needed.

For a report, record selected MD filename (short/full included), current DOCX ID, `content_authority`, `layout_authority`, and `md_docx_diverged`. Record manual Word changes and converter/patch-script links. Edit current Word rather than rerunning an old MD conversion.

Keep current status concise; move history to logs. Historical “not accepted” must not look current after confirmed acceptance. The shared example-rating registry does not replace project status.

## Synchronization/delivery

Use the connected tool for the user's chosen service; read the Google Drive skill before Drive operations. Ground links, IDs, and MIME types in tool results. Do not change location/sharing without assignment.

Update working MD under its existing ID and keep relative illustration names. `assets/code/example.png` works in a downloaded tree/MD editor/converter; uploading MD/images to Drive alone does not prove inline web preview support. Do not promise unverified rendering; link the image itself when needed.

Refresh a file before writing if the user may have edited it. Merge non-overlapping changes and show exact semantic conflicts. Use conditional/version-guarded writes where supported; otherwise do not claim atomic protection, and check the version immediately before writing.

Keep snapshots separate from the working ID. Inspect every operation result; top-level batch success does not prove each file succeeded. A local copy is not a synchronized copy.

When ZIP distribution is requested, package necessary files with portable relative paths, exclude caches/development clutter, and check the archive locally once. Provide it for user unpacking. Do not upload/reread individual Drive files solely for the same delivery. Do not claim the user installed it. Actual remote edits still require save checks.

## Checkpoints

“Save current as a checkpoint; retain previous” means snapshot text and figures together. Otherwise replacing an image under the same name changes the old report's visible content.

Use UTC in technical names and the user's timezone in communication. Add a unique suffix on collisions. Store MD/file hashes, time, label, and source path in the manifest; do not embed the manifest's own hash in itself.

Separate `user-final` and `teacher-accepted`. A final “not yet accepted by the teacher” uses the former. The script requires separate acceptance evidence; never generate it on the user's behalf. For large external sources, store pinned URL/commit and identify included bytes versus link-only materials.

Restore only on request after saving current unfinished work as a draft. Restore text with its illustrations and retain other snapshots.

After a significant core or draft result and before costly or interruptible conversion/rendering, save proportionate state and an attributable event while tools are available. Include actual checks/results, selected MD/DOCX authorities, approval state, unresolved issues and next action; verify the write. If the agreed remote destination is unavailable, record pending synchronization and any permitted local copy. Do not initialize all report folders or save before every trivial operation.

## Resume

Read current state and requirements for the next stage, plus selected MD if a report exists. Do not reread all code on every “next.” Preserve exact paths/commits; inspect relevant source before new claims. Do not restore a user-deleted section from an old snapshot.

Compare the relevant selected local/remote versions and recorded content/layout authority before overwriting. Merge non-overlapping changes; show concrete semantic conflicts. Neither remote location nor modification time alone establishes authority. Preserve manual DOCX changes, selected layout/cover and known MD/DOCX divergence, including pending or revision-bound approved content.

The standard `checks/` folder is included in snapshots. Explicitly include necessary evidence elsewhere; do not claim arbitrary paths were included automatically. MD audit does not decode images.

## Local commands

`report_workspace.py init <project> --mode accompany` creates minimal state/log folders; final-report necessity remains unknown until reading the assignment. `--mode report` (default) creates report materials without automatically copying a Word sample or selecting a cover. Repeated init is not a state editor.

`checkpoint <project> --mode accompany` requires no MD. For reports select `--report <filename>`. Include nonstandard specifications, packets, or evidence with repeatable `--include <relative-path>`; paths must exist inside the project and outside checkpoints. Preserve actual names.

Check `included_paths` and manifest hashes. External links do not include their bytes. An accompaniment snapshot is not a finished report, and local checkpointing is not cloud synchronization.
