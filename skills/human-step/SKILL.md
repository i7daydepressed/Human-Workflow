---
name: human-step
description: Prepare, execute, or review exact, readable step packets for a person or agent. Use for exact edits, a Markdown handoff, packet execution, continuation, diff review, and commit text. Do not trigger for a general explanation. Preparing steps does not authorize execution.
---

Shared Python helpers are in the required sibling [scripts](../scripts/README.md) directory. Keep that whole directory when extracting the skill; see [README.md](README.md). `<shared-scripts>` in commands means its verified absolute path.

This is the primary English edition. Read the actual task and its explicit profile locator if supplied, then read the [English workflow](workflow.md). Use the bundled English instruction edition; the auxiliary Russian edition is the separate skill `human-step-ru`. Determine output and log language independently from the user/task/profile. Do not read both editions for ordinary execution.

Resolve instructions from the directory containing this SKILL.md: workflow.md and references/. Resolve data and templates from resources/. Reports and shared helpers use [md-report](../md-report/SKILL.md), installed together with human-step; helper scripts live in md-report/scripts/ and run by absolute paths. Keep tasks, outputs and private profiles outside the installation. If a required resource is unavailable, report its actual path and the affected operation; reading instructions does not establish execution or host installation. See the scoped [client checks](resources/docs/client-checks.en.md).
