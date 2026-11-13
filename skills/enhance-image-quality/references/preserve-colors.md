# Strategy: enhancement while preserving hair colors

Apply after this strategy has been selected in the [general guide](enhancement.md). Improve the quality of the same frame; preserve the existing colors of the hair and all other regions. Do not switch strategies on your own based on an aesthetic preference.

## 1. Prepare a specific request

1. Perform the inspection in the [general guide](enhancement.md), fill in the [shared observation card](observation-card.md), and save it as card.json in the working folder. Take the characteristics from the source you have actually viewed; do not substitute the style of a different source.
2. Separate edge character from interior shading. Describe the visible eye colors and patterns, skin tones, and facial light-to-dark transitions. For eyes or a face that are not visible, use NOT_VISIBLE according to the form's rules.
3. In hair.base_and_existing_colors and hair.preserve_details, record the actual hues, colored light reflections, adjacent ribbons, trim, and ambiguous bands. Set hair.accent_plan to NOT_REQUESTED; an accent plan, if present for a separate comparison, will not enter this strategy's request.
4. Assemble the request with the builder; read the resulting file and compare its descriptions with the source before calling the editor. Form validation does not establish visual accuracy.

```bash
python scripts/prepare_request.py /path/to/card.json --strategy preserve-colors --out /path/to/preserve-colors.txt
```

Run the command from the skill root or use the actual absolute path to scripts/prepare_request.py. The output file is not overwritten; choose a new name for the next attempt. Add --check-only to validate without writing. The builder prints a receipt with hashes and text lengths; these lengths are not token usage.

## 2. Full prompt template

The stated constraints express requirements whose fulfillment must be checked in the actual result.

Fill in the card and every template field in English. Use the full template through the builder, which transfers the shared observations without omissions. The standalone template below remains available for reading and analysis.

```text
Edit the supplied image 1 as the sole source and edit target. Improve the quality of this existing frame while preserving its composition and observed rendering style.

SOURCE APPEARANCE
Edge character: {{edge_character}}
Interior shading and material transitions: {{interior_shading}}
Eye visibility, geometry, internal pattern and local colors: {{eye_details}}
Face visibility, skin tones and lighting transitions: {{face_tones}}
Other existing colors and contrasting exceptions: {{other_colors}}
Hair base, existing colors and light reflections: {{hair_base_and_existing_colors}}
Hair details, adjacent materials and ambiguous color bands to preserve: {{hair_preserve_details}}
Identity, expression, pose, scene, crop and source-specific invariants: {{frame_and_identity}}

LOCAL QUALITY TARGET
{{local_improvement}}
Refine the specified existing contours while preserving their position, width and original edge character. Make existing edges continuous and clearly distinguishable where they are distinct in the source. Keep interior shading soft only where it is soft in the source, and preserve existing flat areas and defined facets where those are present.
Preserve the observed local color structure and its placement in the visible eyes and face. Keep existing colored forms, light-to-dark transitions and highlights distinguishable. Do not flatten existing transitions into a uniform pastel fill or add new hues, highlights or ornament.

HAIR OPERATION
Strictly preserve the observed hair colors, their placement within the same locks, existing shadows, highlights and colored light reflections. Do not add new shades or colored strands, remove existing colors, or intensify existing accents. Preserve adjacent ribbons, trim and ornaments separately from the hair. Leave ambiguous color bands unchanged.

SHARED PRESERVATION
Preserve the observed colors of the skin, eyes, clothing, ornaments, objects and background, including small contrasting exceptions. Retain the original lighting direction and color balance. Do not apply a new overall color filter or increase saturation across the whole image.
Preserve the original facial proportions, eye corners, eyelid opening, iris position, gaze, mouth shape, pose, hands and fingers. Preserve visible internal iris patterns, ornament shapes, spacing and occlusions. Do not replace an existing pattern with a similar new design or invent details of a hidden region.
Preserve the hair length, silhouette, fringe, parting and individual lock shapes; garment construction, accessories, objects, background geometry, camera angle, framing and aspect ratio. Keep cropped elements cropped. Do not add, remove or reposition elements.
Do not introduce a new rendering style, glossy finish, global sharpening, heavier outlines or additional texture merely to create an impression of greater detail.
Return one edited full version of this same frame, without captions, labels, a collage or a comparison sheet.
```

Take the number of results from the assignment; for a series, perform separate edits as described in the general guide.

## 3. Adapt to the source and verify

| Source or result characteristic | Request technique | Check after editing |
| --- | --- | --- |
| Soft light with distinct contours | Describe edges and interior blending separately; preserve each observed characteristic | Contours remain readable, and soft transitions inside regions are preserved |
| White hair with colored lighting | Preserve the base color and the existing distribution of colored light reflections | Check for new colored strands or removal of an original hue |
| Several colors and a small contrasting accent | List the accent separately from the main palette | Check that its own color is preserved |
| Closed or partly closed eyes | State the actual eyelid condition; do not describe visible irises when the eyes are closed | Check that the eyes have not opened and the gaze and expression have not changed |
| Complex irises or ornament | Name the visible hues, their placement, shapes, gaps, and internal lines | Compare color structure, pattern, and geometry separately |
| New hues appear in the result | Treat this as a deviation from the selected strategy | Proceed to diagnosis and correction in the general guide |

After editing, return to [comparison, correction, and presentation of the result](enhancement.md). Also check regions outside the listed improvements.

## 4. Apply the preservation checks

Check clarity, softness, saturation, internal patterns and geometry separately. Cleaner contours do not prove that eye details or other small patterns were preserved. A quality improvement does not authorize new colored strands or any other recoloring in this strategy. Base color and detail descriptions on the current source.
