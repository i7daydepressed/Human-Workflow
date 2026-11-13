# General image enhancement

Read this guide before calling the editor. Apply one shared procedure and one of two strategies; do not turn detail correction into a third strategy. Obtain the working request from the selected strategy's prepared template, adapting it to the observed features of the frame.

## 1. Clarify the hair palette and select a strategy

Check the current assignment and applicable user decisions in this conversation. Use a choice already made without asking again. Naming a character palette or making a general request to "improve the quality" does not authorize hair changes and does not replace the selection.

If no choice has been made, always ask and wait for an answer before editing:

> Must the hair palette be strictly preserved, or may restrained accents from the character's palette be added while keeping the dominant color?

Offer two answers: "Strictly preserve" and "Accents are allowed". While waiting for the answer, inspect available source images if useful; do not call the editor. Do not treat silence as a choice. Do not ask again for every frame in a series if the decision applies to the whole series; check its applicability when the task changes.

| What the user has already specified or answered | Action | What is permitted for the hair |
| --- | --- | --- |
| Strictly preserve colors; enhance without recoloring | Read [color preservation](preserve-colors.md) | Existing palette, with no new hues or strands |
| Restrained accents are allowed; harmonize hair colors with the character | Read [hair harmonization](harmonize-hair.md) | Accents within existing locks while preserving the dominant color |
| Only general enhancement; the hair answer is absent or ambiguous | Ask the question above and wait for an answer | Not yet determined |
| Replace the dominant hair color, recolor clothing or change the design | Clarify the separate scope of the color task | These changes fall outside the two enhancement strategies |

Preserve the colors of all other regions in both strategies. If the user has asked you to choose hair shades independently, choose them within the permitted accents; do not ask again about an already resolved decision. If requirements conflict, clarify the specific conflict.

## 2. Inspect the source and complete the observation card

Select a specific frame and actually inspect it. For an assigned series, process each source separately. Do not replace an inaccessible source with memory or a similar picture. Assign a role to additional images: a detail, color or quality reference; do not merge scenes automatically.

Read and complete the [observation card](observation-card.md). Describe contours and interior fills separately, along with the visible color structure of the eyes and face, other colors, properties to preserve and local refinement. Soft light does not imply soft contours; a clear contour does not require hard skin shading. Do not add unseen hair, body parts, objects or details. Use the card as prepared data for both templates rather than composing a new general description for each run.

## 3. Process with the selected strategy

After selection, read [color preservation](preserve-colors.md) or [hair harmonization](harmonize-hair.md). Assemble the complete request from the card using scripts/prepare_request.py as described in the observation card. Before calling the editor, check that all visible regions have been transferred and no placeholders or contradictions remain. Shared data must match across both strategies for the same frame; do not mix color operations or replace observations with a short general style description.

Supply the actual source through an available image-editing tool, following its current requirements. Supply additional images only with explicit roles. Do not invent a seed, model, technical mask, upscaling factor or guarantees that the tool does not provide. Prompt text alone does not technically lock regions that are supposed to remain unchanged.

## 4. Compare the result with the source

| Check | What to compare | Where to go if there is a problem |
| --- | --- | --- |
| Quality | Readability of existing lines and facets; whether they have been replaced with a new similar pattern | Specify the defect in step 5 |
| Contours and fills | Edge continuity at the original width; separately, the softness/flatness of interior shading | Correct the local deviation while retaining the card's separate requirements |
| Eye and face color detail | Readability of existing hues, internal colored shapes, highlights and local transitions without new coloring or flattening | Compare the card with the source and correct the specific loss in step 5 |
| Colors | According to the selected strategy; inspect hair, eyes, skin, clothing and contrasting exceptions separately | Return to the selected strategy's check table |
| Geometry | Face, silhouette and objects; for eyes, corners, width, height, eyelids and iris position | Specify the changed geometry in step 5 |
| Fine patterns | Shapes, placement, spacing and internal lines in crops at the same scale | Step 5; inspect the original details before describing a correction |
| Rendering style | Softness, contours, shadows, highlights, saturation and texture | Specify the observed property to preserve in step 5 |
| File | Actual dimensions, proportions, viewpoint and framing | Record the deviation; do not treat a larger image as proof of improvement |

On the next attempt, compare with the source and the accepted working version saved separately. Distinguish user feedback, observation and measurement; do not turn subjective percentages into tolerances. Do not treat a clean appearance as proof of accurate restoration.

If lines are cleaner but a recognizable pattern, shape or local color has changed, record the two outcomes separately: improved clarity and a preservation deviation. A vivid eye with a new similar pattern does not pass the original-pattern check. A complete card and successful receipt do not replace this check.

## 5. Fix a specific deviation

First name the difference from the source, then choose a technique. Do not run another general enhancement merely because the result "could be better".

| Observation | Prepared technique | Next check |
| --- | --- | --- |
| Pattern elements have disappeared | List the missing shapes, internal lines and spacing; give the source the role of pattern reference | The pattern itself, its placement and the region's geometry |
| The pattern is clearer, but the eye has widened | Request restoration of the original shape separately from the internal pattern | Corners, width, height, eyelids and iris |
| Unrelated colors have appeared or accents have intensified | Identify the changed region and the required source colors according to the selected strategy | Hair and all other color groups |
| Correction has changed other regions | Remove repeated general refinement; retain the accepted version and request only the observed correction | The full frame outside the correction |

Use the targeted-correction template after filling in the observed features:

Complete the template fields in English.

```text
Image 1 is the working version to edit; image 2 is the original frame and the reference for the original pattern and geometry.
In [area], correct only [specific difference from the source].
Restore the [shapes, internal lines, spacing or colors] visible in the source. Do not add a similar new pattern.
Preserve the original shape of the area, the positions of its elements, perspective and occlusions. For eyes, separately preserve the corners, width, height, eyelids and iris position.
Preserve the chosen hair color operation and all other properties of image 1. Do not perform another overall enhancement, smoothing pass or color filter.
Return the full edited frame with the same proportions, without a collage or captions.
```

When supplying an enlarged source crop, add: "Image 3 is a detail reference from the source, not a framing reference". Such a crop adds no source information. Check the result using step 4; a textual region restriction does not guarantee technical isolation.

If the technique is unclear or did not help, inspect the specific source region and compare the correction with the accepted version. Keep pattern, geometry and color requirements separate. Enlarging a crop adds no source information; if both the crop and the text change, do not attribute an improvement to either change without evidence. Do not continue identical attempts without a new specific reason; keep the accepted version and explicitly record the remaining deviation.

## 6. Present the result

Show results separately with stable labels, noting improvements and material deviations. For comparison, use the source and result at the same scale. If display fails, use a supported presentation method; do not regenerate merely to display the result.

Take the storage destination from the assignment. Keep the source, selected strategy, actual request, result, checks performed and available feedback with the task materials so the result remains traceable.

For requested measurements, use actual dimensions, verifiable features and available call records. Take token usage and internal durations only from telemetry explicitly linked to the run; if unavailable, mark them unknown. Keep editor-call waiting time separate from preparation time, text length separate from tokens, and visual observation separate from measurement.
