# Saving Examples and Feedback

Read this when asked to save a specific HTML result, version, or review. Including a reusable shell in the package follows a separate procedure: [adding a preset](preset-additions.md).

## Location and duplicates

Use the chosen permanent collection outside the installed skill. If none exists, create `html-preview-library` in the project's permanent working folder; clarify an unknown location. Save when requested or covered by an existing agreement; saving does not mean publishing.

The `library.md` index contains a table: **task → record → preset/revision → status → rating**. In the example's subfolder, keep the HTML, its dependencies, and a Markdown record with the same base name. The index one level above links to the record, which links to the HTML; internal links are relative.

Compare against the existing collection and catalog. Do not copy an exact duplicate of the HTML **and all assets** again; add a new review to the existing record if one was provided. Compare SHA-256 when needed: an HTML hash does not capture separate assets. Different data in the same shell usually means a new case, not a new preset.

Save a finished result without rebuilding it, checking that the copy matches. A record may link to an existing permanent file if the absence of a separate snapshot is explicit. When creating a result from a preset, the build method is described separately: [Python builder](build-script.md). Give a new version separate HTML and a record linking to its predecessor; preserve older artifacts and reviews.

## Record

Fill in this outline with confirmed information; state what is unknown. Replace example names with actual links. Project-specific materials stay in the personal collection and are not copied into the author-maintained preset.

```md
# Example title

- Task: which user action the HTML helps with.
- Result: [name.html](name.html), version, date, required assets.
- Provenance: materials, result author, reason for saving; state what is unknown.
- Preset: guide, code, and revision, or “custom, not yet included”.
- Closest alternative and useful difference: what was reused and added; note when there is no difference.
- Status: case / candidate / included; for candidacy and inclusion, give the basis and the author's decision.

## Feedback

Not rated. For a review: date, reviewer, version and subject of the rating, number on the scale, and comment. Without a number, preserve the written feedback.

## Checks and limitations

Who checked what, where, the result, and unverified capabilities. Add hashes and a link to a separate report when needed.
```

Use the catalog's rating scale. Do not infer a number from praise, average different reviews automatically, or transfer a case's rating to the reusable preset. A new version does not inherit a rating or acceptance. After changing a status or review, update the record and index together.

Before finishing, read the saved entries back and check links and the complete HTML/assets package. Do not copy detailed logs into the record. Report the saved location, actual checks, and limitations.
