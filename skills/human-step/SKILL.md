---
name: human-step
description: Prepare, execute, or review exact, readable step packets for a person or agent. Use for exact edits, a Markdown handoff, packet execution, continuation, diff review, and commit text. Do not trigger for a general explanation. Preparing steps does not authorize execution.
---

This is the primary English edition. Read the actual task and its explicit profile locator if supplied, then read the [English workflow](workflow.md). Use the bundled English instruction edition; the auxiliary Russian edition is the separate skill `human-step-ru`. Determine output and log language independently from the user/task/profile. Do not read both editions for ordinary execution.

Resolve instructions and helper commands from the directory containing this SKILL.md: workflow.md, references/, and scripts/. Resolve bundled data and templates from resources/. Run helpers by their absolute paths, regardless of the task's working directory. The skill folder contains its required resources; do not depend on the parent plugin tree or download missing instructions. If a required resource is unavailable, report its actual path and the affected operation; do not claim this workflow was executed from its description alone. Keep tasks, outputs and private profiles outside the installation. See the scoped [client checks](resources/docs/client-checks.en.md); reading files does not establish host installation.
