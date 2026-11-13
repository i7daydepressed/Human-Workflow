# File Viewer

Code: `file-viewer` · HTML revision: **1** · Rating: **not rated**.

To explore several texts and images, use the [HTML shell](../../resources/file-viewer.html): a tree, closable tabs, line numbers, search in the open file, copying, simple Markdown reading, and a theme switch. For another task, return to the [catalog](../library.md).

## Populate

The template is empty. [build_viewer.py](../../scripts/build_viewer.py) inserts selected real files into its copy; the shell and sources remain unchanged. Invocation and requirements are in the [Python builder](../build-script.md) guide.

Pass `--root`, a new `--output`, and relative paths of explicitly selected files. UTF-8 and PNG/JPEG/WEBP/GIF are accepted; resolved symbolic links must remain within the root. Files are embedded in full, without changing their bytes. For large materials, assess suitable packaging: the ready-made helper does not create a separate assets folder.

The build records a time with timezone, paths, size, and SHA-256. The snapshot does not update when sources change.

## Data when adapting

JSON is stored in `script#ed-data`: `title`, `snapshot`, `groups`, `files`, and `initial`. A group contains `id`/`label`. A file contains `id` with the full relative path, `group`, `path`, `type`, `bytes`, `sha256`, and `purpose`. Text requires `type: "text"` and `content`; a raster requires `type: "image"` and `preview` with a data URI. The builder generates these fields and safe escaping automatically.

## Behavior and limitations

- Viewing does not edit sources or execute code/skills. The full open file's text is copied; system clipboard availability depends on the environment.
- Search is limited to the current text. Tabs, theme, and search reset on reload.
- Markdown supports simple headings, lists, tables, code, and links. Complex formatting is simplified; exact content is available in “Source” mode. Internal links open embedded files, heading fragments are not processed. External addresses are shown only, without navigation.
- Rasters preserve proportions; dimensions appear after loading. Comparison and general-purpose zoom are not included.
- JavaScript is required; there are no external libraries or persistent storage. Check loading, interactions, and the clipboard in the chosen viewing environment.

The basis is the supplied `Character_Skills_Explorer.html`; the other project's data was removed. Earlier checks of the source preset covered build fidelity, wide/narrow Chrome windows, and the empty template; the wide screenshot was visually inspected. Clipboard behavior was checked with a mock; the real clipboard and other embedded clients were not confirmed. These checks do not replace checking new populated content.
