---
name: enhance-image-quality
description: Enhance an existing character image while preserving its frame, design and rendering style. Use for requests such as "improve the quality", "make it clearer", "clean up artifacts", and enhancement with color accents in the hair. Follow the general enhancement guide and choose one of two hair strategies. If the user has not already made the choice, always clarify whether the hair palette must be strictly preserved and wait for an answer before editing.
license: Apache-2.0
---

# Character image enhancement

## Workflow

1. Before the first edit, read the [general enhancement guide](references/enhancement.md). Complete its strategy-selection step: if no choice has already been made, always ask the user about preserving the hair palette and wait for an answer. A request to "improve the quality" does not select a strategy by itself.
2. Complete the [observation card](references/observation-card.md) from the source, then follow the guide's table to the selected strategy: color preservation or hair harmonization. Read it in full; assemble the complete prompt from the card and template, and check it before calling the editor. The shared observations and enhancement instructions are the same in both strategies; only the permitted hair color operation differs. If the user requests both strategies, run them independently from the same source.
3. Return to the general guide for comparison with the source, targeted correction if needed, and presentation of the result. Apply the documented techniques to the observed features of the current frame.

Edit the actual source frame. Preserve the face, expression, pose, geometry, clothing design, scene, framing and rendering style. A new outfit, pose, hairstyle shape, replacement of the dominant hair color or a new character requires a separate task. Take the number of results and storage destination from the assignment.

Write prompt templates and completed editor requests in English, including replacement fields and additional insertions. In this English edition, keep instructions, explanations and reference tables in English as well.

## Material index

Follow the workflow above; use the direct links below to return to the relevant step.

| Material | Role in the workflow |
| --- | --- |
| [General enhancement](references/enhancement.md) | Required shared procedure: question, selection, inspection, processing, checks, correction and presentation |
| [Observation card](references/observation-card.md) | Required observations, transfer into the prompt and check before calling the editor |
| [Request builder](scripts/prepare_request.py) | Schema validation and deterministic transfer of observations into the selected full template |
| [Color preservation](references/preserve-colors.md) | The first of two strategies; read after selection in the general guide |
| [Hair harmonization](references/harmonize-hair.md) | The second strategy; read after hair color accents have been authorized |

Structural validation checks the request, not image quality. Compare each result with its actual source and distinguish visible observations, measurements and user feedback.
