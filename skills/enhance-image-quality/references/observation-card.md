# Observation card and request preparation

Read from step 2 of the [general guide](enhancement.md). Complete one card from the source you have actually inspected before writing the prompt. Use its shared observations for both strategies; select the permitted hair operation according to the user's decision. The complete English templates are in [color preservation](preserve-colors.md) and [hair harmonization](harmonize-hair.md).

## 1. Fill in the observed data

Save the card as card.json in the task's working folder. Write all values that enter the prompt in English. Replace the placeholders in braces with your own observations. Do not transfer hues, gradients or style from a different image.

```json
{
  "source_image": "{{absolute source path or path relative to card.json}}",
  "observations": {
    "edge_character": "{{visible edge colors, widths, sharpness and continuity}}",
    "interior_shading": "{{where shading is soft, flat or faceted; visible light direction}}",
    "eye_details": "{{visible iris hues and their placement, colored shapes, highlights and eyelid state}}",
    "face_tones": "{{visible skin base tone, illumination, local color and light-shadow transitions}}",
    "other_colors": "{{colors of clothing, accessories, objects and background; contrasting exceptions}}",
    "frame_and_identity": "{{expression, pose, proportions, distinctive motifs, occlusions, framing and source text}}",
    "local_improvement": "{{specific visible defect, location and desired improvement within the source style}}"
  },
  "hair": {
    "base_and_existing_colors": "{{dominant hair color, existing colored areas, shadows and light reflections}}",
    "preserve_details": "{{lock geometry, neighboring ribbons and ornaments, ambiguous stripes to preserve}}",
    "accent_plan": "NOT_REQUESTED"
  }
}
```

| Field | How to obtain precise data | What to avoid |
| --- | --- | --- |
| edge_character | Inspect outer contours and internal lines separately from fills; state their actual width and color | Calling the whole drawing soft because the light is soft; demanding uniformly sharp boundaries in intentionally blurred regions |
| interior_shading | Identify regions with soft transitions, flat fills and existing facets | Replacing observation with general words such as "pastel" or "glossy" |
| eye_details | In an enlarged crop, check colors and their placement, shapes and boundaries of internal patches, the dark central shape and distinct highlights; separately check eyelid state and differences between the two eyes | Only listing hues; replacing ambiguous patches with a familiar symbol; inventing complexity or the iris of a closed eye |
| face_tones | Separate skin tone, light color and local facial transitions | Giving all skin one uniform fill or adding absent hues for greater vividness |
| other_colors | List important color groups and small exceptions | Losing a small contrasting accent outside the dominant palette |
| frame_and_identity | Identify visible distinctive details, occlusions, pose and frame boundaries; preserve existing text | Completing cropped-out regions, changing the expression or treating the original signature as an artifact |
| local_improvement | State the defect and positive result: for example, continuity of a specific stair-stepped contour at its existing width | Inventing defects; automatically increasing saturation, gloss or sharpness across the whole image |
| hair | Distinguish dominant color, reflected light, strand coloring and neighboring materials | Mistaking a ribbon for a hair lock or intensifying an existing stripe without an instruction |

For invisible eyes or face, use the exact value NOT_VISIBLE in the corresponding field. If only a fragment is visible, describe that fragment. For an ambiguous detail, state the uncertainty and require its appearance to be preserved; do not fill the gap with a guess. If there is no obvious defect, state that honestly and limit refinement to observed existing lines without promising restoration.

If the visible pattern is small, inspect an enlarged crop of the same source before filling in eye_details. For each eye, check the shapes and adjacency of colored patches, their boundaries, the dark central region and highlights. State the number of elements only when clearly visible; leave ambiguous boundaries ambiguous. Enlargement adds no data. More precise text does not guarantee that the editor will preserve the pattern; verify the actual result against the source.

For consistent completion, this English structure can be used within a single field:

```text
Visibility and eyelids: {{observed state and occlusions}}. Colors and regions: {{visible hues and their relative placement}}. Internal forms and boundaries: {{visible shapes, adjacency and central dark form}}. Highlights: {{distinct visible light marks and their placement}}. Differences and uncertainty: {{perspective differences and unresolved boundaries to preserve}}.
```

For harmonization, fill hair.accent_plan with an actual plan in English: selected shade → visible source within the character → placement inside existing locks. Keep the dominant color predominant. For color preservation, NOT_REQUESTED is allowed; the accent plan is not transferred into its request.

## 2. Verify observations and assemble the prompt

Compare the completed card with the source. Check every statement about color, shape and style. Ensure that local refinement is compatible with the properties to preserve and that invisible regions have not been invented. This is the executor's visual check; a filled field does not replace it.

Use the builder from the active copy of the skill:

```bash
python /path/to/skill/scripts/prepare_request.py /path/to/card.json --strategy preserve-colors --out /path/to/prompt.txt
```

For the second strategy, select harmonize-hair. The builder takes the complete template from the selected Markdown file, transfers the card data, and checks required fields, Cyrillic characters, remaining placeholders and source-file existence. Do not call the editor until validation succeeds. Fix the error in the card or template rather than bypassing validation by manually shortening the request. Read the assembled prompt before sending it. If Python is unavailable, transfer the same fields into the template manually and explicitly note the lack of automatic validation.

Save the card, assembled prompt and receipt issued by the builder. For two strategies applied to the same frame, keep shared observations identical; differences are permitted only in the hair operation. common_observations_sha256 can verify that shared data matches. Text length and word count are not token usage.

## 3. Respect validation boundaries

The builder checks structure and data transfer. It does not establish whether the image description is true, measure quality or guarantee that the editor preserves details. After the call, return to the result check in the general guide.
