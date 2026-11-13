# Adding an HTML Preset

Read this when asked to include or update a reusable shell in the author-maintained package. If only saving a finished result is needed, use the [collection rules](library-additions.md).

## Select a solution

Compare the example against the catalog by the user's action. A **case** applies an existing solution. A **candidate** offers a useful difference in interaction, delivery, or reuse. **Included** means that a preset has been extracted from the candidate and added at the author's request. A score above 1 does not replace a useful difference or the author's decision.

Authors and users can propose examples in the same way. Record provenance, version, differences, feedback, and checks in the candidate's record; take the location, index, and record outline from the [collection rules](library-additions.md). Incorporate a closely related new capability into an existing preset when that preserves its purpose, rather than creating a duplicate. Do not ask again for permission already given for a specific inclusion.

## Prepare the package

1. Separate the common shell from case data. Keep neutral HTML and a clear empty state in `resources/<code>.html`; private materials stay outside the package.
2. For repeated population, add or adapt `scripts/build_<code>.py`. Reuse a compatible existing builder if it already solves the task. Requirements and invocation are described separately: [Python builder](build-script.md).
3. Create the required `references/templates/<code>.md`. Briefly describe the purpose, HTML, code/revision, population and data, builder/command, essential interactions, provenance, actual checks, and limitations. It must be possible to build a result without reading the entire shell. A standalone HTML file without replaceable data does not require a builder; state this explicitly in the guide.
4. Add a **when useful → Markdown guide** row to the catalog, rather than a direct HTML link. If a new transferable technique emerges, add a ready-to-use recommendation without the project's history; do not expand the core for a single case.

## Verify and record

Run population with suitable materials; check data fidelity, required dependencies, and essential interactions in the delivered page. Also check expected builder failures for invalid input and overwriting; details belong in its guide. Check package links and SKILL.md metadata.

If `skill-creator/scripts/quick_validate.py` is available in the environment, run it with the package path: `python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/html-preview-helper-en`. This is a command pattern; replace paths with those found in the current environment. If the validator is unavailable, state the limitation without claiming it passed. It does not replace checking the page itself.

When HTML behavior or the data format changes, increase the revision in the guide; editing only the guide's text does not change the HTML revision. Record inclusion and the preset link in the candidate's record and index, preserving previous reviews. A case's rating does not automatically transfer to the shell; user acceptance of a new revision remains a separate fact.
