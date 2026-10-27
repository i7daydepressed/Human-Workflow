# Figures and code excerpts

## Presentation

Use the app's style and approved figures. Choose code representation and theme from the task/profile. For rendered excerpts, use readable monospace, a filename header and actual line numbers. Match card backgrounds, borders, accents, and geometry. Check readability at final Word width.

Render exact diagrams, matrices, and calculations programmatically/SVG. Do not use generative images for exact code, numbers, or pixel diagrams. Use imagegen under its skill for genuinely illustrative raster material.

Preserve generators for future edits and record source/method in figure-index.md. Inspect every new/changed illustration; a successful generator run does not replace viewing it.

## Algorithm explanation

Separate before/after effects from calculation explanations. Show every pass of compound operations, e.g. “Step 1 …”, “Step 2 …” in the report language; an overall `→` is acceptable. Draw independent branches separately: two subtraction operands may derive from one input rather than from each other.

For a pixel-operation diagram, if the task selects this example legend:

- Blue border: anchor.
- Red: current-pass changes.
- Purple: previous-pass changed positions only when comparison requires them.
- Match cell/grid sizes and panel spacing.

Explain every border. Do not carry purple automatically into difference operations. Verify arithmetic, pixel count/color, kernel reflection, anchor, and grid alignment. Put `−`, `=`, and arrows between the correct operands.

## Code and roadmap

Capture real source from a pinned commit or accurately render its text with highlighting. Call rendered text a code excerpt, not an IDE screenshot. Do not modify code for appearance. Mark omissions; mark visual wrapping or select another excerpt for long lines.

Cite method, file, and lines of the pinned commit. When delegating to a library, explain your call and its separate role. Check primary sources before precise internal-algorithm claims; your call alone does not establish the library's implementation.

At a key section's start, show object/class data flow. Reuse the same map with explained blocks expanded when useful, keeping position/names stable. Use field/method/role subcards inside a window/ViewModel when prose is ambiguous. Do not repeat maps to inflate figure count.

## Surrounding text

Explain what is shown before the figure. After its caption, interpret the concrete result and, when useful, application. Use concrete, example-specific terms for visible regions instead of ambiguous abstractions. Avoid starting every conclusion with “таким образом”.

Do not place independent figures back-to-back or jump directly from a figure to a new section. Panels sharing one caption/legend may be adjacent. Text between figures must explain substance, not merely announce the next image.

Place panels together in MD with no separate intermediate caption, then one shared `Рисунок N – ...` in Russian reports, or `Figure N – ...` in English reports. Count the group as one figure, not each PNG. Record multiple files under one figure-index caption. If the user removes а/б labels, update references to actual positions such as upper/lower; do not restore removed labels from old MD.

Omit final caption periods when required by the selected profile/guide. For landscape pages check orientation, section boundaries, margins, numbering, and return to portrait. Before shrinking table fonts against the sample, consider widths, wrapping, and orientation.

## Consistency and evidence

Choose a code representation before making a set: text, rendered excerpts, or another agreed form. Apply it consistently. Mark visual wraps and verify recombination reproduces the source. Image generators must not overwrite fresh MD with stale embedded text.

A retained historical case records positive user feedback on image selection/style; its causal effect on the numerical rating is unknown. See the adapted case examples, not private artifacts.

Retain execution screenshots as received evidence. Calculation tables/cards explain but do not replace a requested execution frame. Record visible/cropped portions, version, and source. Never retouch numbers/messages to imply success.
