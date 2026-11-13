# Strategy: enhancement with hair color harmonization

Apply after color accents have been permitted in the [general guide](enhancement.md). Improve the quality of the same frame and change color within existing locks. Preserve the main hair color; preserve the colors of all other regions in the same way as in the strategy without hair color changes.

## 1. Prepare the hair change map

1. Perform the inspection in the [general guide](enhancement.md), fill in the [shared observation card](observation-card.md), and save card.json in the working folder. Fill in the shared observations for eyes, face, contours, and fills with the same level of detail as in color preservation.
2. Describe the main hair color, existing hues, shadows, and colored light reflections in hair.base_and_existing_colors. Separate hair from ribbons, trim, and ornaments; list exceptions to preserve and ambiguous bands in hair.preserve_details.
3. In hair.accent_plan, record the actual plan: the selected hue, its visible source in clothing, an accessory, or the eyes, and its placement within existing locks. The background and scene lighting alone do not establish a new palette. Do not import accent colors from a different image.
4. Preserve the dominance of the main color, the existing geometry, and the intensity of existing accents. If there is insufficient information to choose, ask for the specific missing reference before editing.
5. Assemble the request with the builder, read it, and compare it with the source. Form validation does not establish the visual accuracy of observations or the reliability of accent selection.

| What to determine for the hair | Where to record it |
| --- | --- |
| Dominant base, existing hues, and colored light reflections | hair.base_and_existing_colors |
| Accents to preserve, adjacent materials, and ambiguous bands | hair.preserve_details |
| New accent, visible source of the hue, and placement within a lock | hair.accent_plan |

```bash
python scripts/prepare_request.py /path/to/card.json --strategy harmonize-hair --out /path/to/harmonize-hair.txt
```

Run the command from the skill root or use the actual absolute path to scripts/prepare_request.py. Add --check-only to validate without writing. An actual accent plan is required; NOT_REQUESTED is not suitable for this strategy. The output file is not overwritten. The receipt contains hashes and text lengths, not token usage.

## 2. Full prompt template

The stated constraints and hue selection map express requirements whose fulfillment must be checked in the actual result.

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
Preserve the observed dominant hair color and its existing lighting. Add only the following restrained color accents within existing locks: {{hair_accent_plan}}
Keep the main hair color visually dominant. Follow the original shadows, highlights and lighting direction; preserve existing light reflections and stated exceptions without automatically intensifying them. Do not recolor neighboring ribbons, trim or ornaments, change lock geometry, or replace the main color with an accent. Leave ambiguous color bands unchanged.

SHARED PRESERVATION
Preserve the observed colors of the skin, eyes, clothing, ornaments, objects and background, including small contrasting exceptions. Retain the original lighting direction and color balance. Do not apply a new overall color filter or increase saturation across the whole image.
Preserve the original facial proportions, eye corners, eyelid opening, iris position, gaze, mouth shape, pose, hands and fingers. Preserve visible internal iris patterns, ornament shapes, spacing and occlusions. Do not replace an existing pattern with a similar new design or invent details of a hidden region.
Preserve the hair length, silhouette, fringe, parting and individual lock shapes; garment construction, accessories, objects, background geometry, camera angle, framing and aspect ratio. Keep cropped elements cropped. Do not add, remove or reposition elements.
Do not introduce a new rendering style, glossy finish, global sharpening, heavier outlines or additional texture merely to create an impression of greater detail.
Return one edited full version of this same frame, without captions, labels, a collage or a comparison sheet.
```

Take the number of results from the assignment; for a series, perform separate edits as described in the general guide.

## 3. Adapt the accents and verify

| Condition | Technique | Check after editing |
| --- | --- | --- |
| The main hair color is light | Preserve the light base; place accents inside selected existing strands | Check that the accent color has not become predominant in the hair |
| Accents already exist | Identify them as features to preserve; name the permitted addition separately | Check for automatic intensification of all bands and shadows |
| A colored band is adjacent to an ornament | Separate the hair material from the accessory; preserve an ambiguous band | Check that ribbons, trim, and adjacent strands have not been recolored |
| Background light differs from the costume palette | Take color references from the character; preserve the original colored light reflections | Check that background light has not turned into a new dominant hair color |
| Distinct contours coexist with soft light or complex eyes | Fill in separate fields for contours, fills, eye colors, and facial colors | Check edge readability, color transitions, pattern, and geometry independently of the hair |
| The result changes clothing, skin, or lock shapes | Treat this as a deviation rather than part of harmonization | Proceed to diagnosis and correction in the general guide |

After editing, return to [comparison, correction, and presentation of the result](enhancement.md). Compare the selected map with the actual placement of accents and check the other regions.

## 4. Apply the preservation checks

Judge accent selection from the current source and permitted change map. The dominant base, placement of accents and all other detail checks remain separate requirements. Successful hair harmonization does not establish preservation of eye patterns, facial geometry or the colors of other regions.
