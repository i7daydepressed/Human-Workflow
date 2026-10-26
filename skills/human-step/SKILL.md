---
name: human-step
description: Prepare, execute, or review exact, readable step packets for a person or agent. Use for exact edits, a Markdown handoff, packet execution, continuation, diff review, and commit text. Do not trigger for a general explanation. Preparing steps does not authorize execution.
---

Read the actual task and its explicit profile locator if supplied. Use an explicit instruction-edition setting (`instruction_language: en` or `ru`) from the task, then an explicitly selected profile. A requested output/log language does not select instruction language. With no explicit instruction-edition choice, use `en` even when the request is written in Russian. Read exactly one body: [English](../../locales/en/human-step/workflow.md) or [Russian](../../locales/ru/human-step/workflow.md). Determine output and log language independently from the user/task/profile. Do not read both editions for ordinary execution.

Use the complete portable preview tree. This entry lives under skills/ and uses shared resources at the plugin root. See the scoped [client checks](../../docs/client-checks.en.md): the I04 base has Codex CLI evidence; this I05 candidate has not been installed on that client. Keep the complete package tree; do not claim installation from file reads.
