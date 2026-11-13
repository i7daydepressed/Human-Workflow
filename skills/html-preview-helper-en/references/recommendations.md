# Recommendations for HTML Views

First identify the question the user finds difficult to resolve. Choose an action that gives them observable evidence for an answer. Add controls for that question, rather than for interactivity itself.

## Choose an interaction

| What makes understanding difficult | What action to provide | What the user can check |
| --- | --- | --- |
| Differences are not visible | Compare alternatives | Where and what changed |
| The result's origin is unclear | Select an element and trace the steps | Which data and actions produced the result |
| The consequences of a decision are hard to assess | Change a parameter | What depends on its value |
| An important detail cannot be distinguished | Zoom in or select a region | What is visible in the relevant area |
| The basis of a conclusion is unclear | Open the source and context | Which materials support the claim |

Techniques can be combined; the tables do not limit the scope of HTML or require a separate template for every task.

## Techniques by task

| When and why | What to show and how |
| --- | --- |
| **Review an interface before implementation:** explore how it will be used | Show the main flow and significant states; make actions relevant to the decision work, such as selecting an item, related settings, and filters. Check a long list and scrolling when they exist and affect usability. The selection, description, and settings should remain understandable. |
| **Explain an operation, including computer vision:** understand how the result was obtained | Choose the starting point according to the user's request and background; connect notation to visible data. Let the user trace a specific element through an action to the result: for example, a selected pixel → neighbors and coefficients → a new value. Compare the input, intermediate data, and outcome; connect a parameter to a specific visible change. When comparing images, keep the same region and scale. |
| **Compare versions or images:** find significant differences and choose an option | Label the versions and allow the desired pair to be selected. For fine details, add zoom, pan, linked views, and reset. Preserve proportions; account for alignment when overlaying images. Select documents independently of images. If names could steer the assessment, they may be temporarily hidden behind neutral labels, with the mapping revealed afterward. |
| **Explore several files:** navigate materials and move between them | Provide a tree or list, access to the chosen file, understandable names, and search where useful. Separate the full source text from explanations; preserve access to the exact data. A simple page with links may suffice for a few short texts—a larger shell is justified by the volume, the way the materials are explored, and the opportunity for reuse. |
| **Explore parameters or alternatives:** independently check the consequences of a decision | Allow meaningful values to be changed and immediately show the result, constraints, or conflict. Preserve the initial state and provide reset; add saved alternatives for comparison when sequential changes are insufficient. Specify clear units and allowed ranges. |

## Important distinctions

- In explanations, explicitly distinguish actual computation, switching between prepared results, and a simulated demonstration. Do not promise recalculation for arbitrary parameters when only saved examples are available.
- In comparisons, represent the available detail honestly: enlarging a reduced preview does not restore original detail. Spatial alignment of panels does not prove that their content or object geometry matches.
- After agreement, preserve the specific version and significant decisions. During implementation, compare states and behavior against it; accepting a mockup does not confirm that the application is ready, and a new revision requires separate consideration of the changed parts.
- In file views and exploration of alternatives, state what is a snapshot and what is saved. Showing something or changing it in page memory must not look like writing to the source project.
