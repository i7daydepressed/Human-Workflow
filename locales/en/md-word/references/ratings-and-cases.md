# Ratings, provenance and case formats

Keep separate acceptance, user rating, teacher rating and quality observations. Record value/precision, display, rater, scope, original scale, date/report date and evidence. Distinguish direct teacher evidence from a teacher number reported by the user. Draft approval is not submission; historical acceptance does not certify cleaned derivatives or mutable current files. Unknown is null, not zero.

Preserve the actual scale and clarification history. A recorded relative-preference scale may have baseline 1 with higher preferred and no specified bounds; that is not a percentage, probability or universal academic rubric. Do not normalize values above 1, average different opinions/scales or invent causes/conversion coefficients. Select examples by requirements/data/evidence/layout before scores. A pre-release case does not test a later skill's effectiveness.

The [adapted historical cases](../examples/index.md) and [structured alternative](../../../../shared/examples/historical-candidates.json) are review drafts, not a new approved runtime catalog. They use accurate paraphrases, with identifiers/quotes/links and some dates withheld. Withheld known dates differ from dates unknown in the source. Their canonical private originals remain unchanged. Synthetic parser fixtures are independent test data, not migrated submissions. Do not fabricate an original quote to make an adapted summary pass a legacy validator.

For an explicitly selected private working catalog, `case_catalog.py` still supports schema 1/2 unchanged. Use schema 2 for clarified attribution/scales; decimal values are strings and display must agree. Schema 2 retains actual quote/source, scope, rater, date or reported_date; teacher source is `teacher_reported_by_user` with source_ref. A scale_id may be null when unknown; enforce only explicit bounds. Acceptance needs actual user-confirmed evidence. Keep the current catalog under its existing identity after freshness checks; ordinary task completion does not rewrite installed snapshots.

The helper accepts these exact English headers (or their Russian equivalents) within the case header:

```text
Current user report rating: **VALUE**
Teacher rating reported by the user: **VALUE**
```

Use `python3 <package-root>/shared/scripts/case_catalog.py validate <private-catalog>/ratings.json`, then `index <private-catalog>/ratings.json --language en --out <private-catalog>/index.md`. Replace placeholders with selected paths. An index uses only observed case URLs; local case_file remains relative. Validation establishes consistency, not real acceptance/quality. If the catalog is inaccessible, save an explicitly unsynchronized task record, not a competing canonical registry.
