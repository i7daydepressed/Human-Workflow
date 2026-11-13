# Image Comparison

Code: `image-compare` · HTML revision: **1** · Rating: **not rated**.

To choose any two images and read documents independently, use the [HTML shell](../../resources/image-compare.html). For another task, return to the [catalog](../library.md).

## Populate

[build_comparison.py](../../scripts/build_comparison.py) populates the empty template. It accepts a source HTML file in CBK format (`cbk06-data`) or a custom JSON configuration with `--root`, preserving raster bytes and complete texts. Invocation, packaging, and requirements are in the [Python builder](../build-script.md) guide. Provenance paths are labels: files outside the supplied materials are not read through them.

## Interaction

Images can be selected freely in either panel. Linking copies zoom relative to fit and the normalized center; it can be disabled. Zoom, pan, fit, `1:1`, keyboard, wheel/pinch, and pointer gestures are available. Documents are selected separately by participant, type, and title.

“Reset view” resets both current images; “Reset comparison” restores the initial pair and view. Document selections survive resets. `1:1` refers to embedded pixels: when linked, it is exact for the chosen panel, while the other receives the same relative zoom.

## Configuration

- Root: `title`, lists `images`, `owners`, `documents`, and optional `regions`. Lists may be empty; identifiers are unique within each.
- Image: `id`, `label`, `src`—a Base64 PNG/JPEG/WEBP/GIF data URI or a relative file within `--root`; a resolved symbolic link must stay within the root. URLs and SVG are not accepted. Optional fields are `ownerId` of an existing participant and `strategy`.
- `sourcePath` is a provenance label. `width`/`height` are supplied together and describe the original according to the configuration; they do not confirm its availability. `previewWidth`/`previewHeight` are computed from the raster header; supplied copy dimensions are checked. `isPreview` cannot be disabled when original and copy dimensions differ.
- Participant: `id`, `label`. Document: `id`, `label`, an existing `ownerId`, `kind`, and exactly one of `text` or `file` (a relative UTF-8 file within the root). Additional fields are `sourcePath` and `strategy`. Main kinds: `prompt`, `log`, `notes`.
- `defaultLeft`, `defaultRight`, and `defaultOwner` refer to existing items; otherwise, the first available items are selected.
- Region: `id`, `label`, `box: [x0,y0,x1,y1]` with positive dimensions and coordinates from 0 to 1. Face/eye geometry in CBK import belongs only to that example and is not universal.

JSON is stored in `script#comparison-data`; the builder sets `snapshot` with timezone and safe escaping.

## Checks and limitations

The basis is a revision of the supplied `CBK06_Comparison.html`; personal images and documents are not included in the shell. Earlier checks of the source preset's populated CBK covered 7 images/12 texts, 49 pairs, interactions, documents, wide/narrow Chrome windows, and both packaging modes; screenshots were visually inspected. Gestures were checked programmatically; a physical trackpad and actual Safari were not tested.

Enlarging a preview does not restore detail: the source CBK embeds WEBP images 760 pixels wide. Fine details require supplied full-size data. Checking a header does not replace image decoding and loading in a browser.

This is a JavaScript snapshot viewer: it does not edit images, write decisions to the project, or update automatically. Check actual display and interactions of newly populated content separately; earlier checks do not mean it has been accepted.
