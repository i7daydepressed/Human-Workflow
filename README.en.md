# Human Workflow

[Русский](README.md)

Human Workflow is a plugin for working with an AI agent on assignments, projects, and reports. It helps preserve requirements, explain what was actually done and checked, and continue work after a pause or a handoff to another executor.

For example, give the agent an assignment guide, source data, and a report sample. The workflow connects requirements, implementation, checks, and the document; available Word, spreadsheet, PDF, or coding skills perform format-specific operations. Results also depend on the inputs, host capabilities, and checks actually performed.

## Two skills

| Skill | When to use it |
| --- | --- |
| `md-word` | Complete and accompany an assignment or project, prepare a report from a guide and sample, resume work, and preserve state, evidence, and decisions |
| `human-step` | Prepare exact instructions for a person or agent, execute an assigned packet, review changes, and hand off results |

The skills can work together. Preparing instructions does not authorize execution. Accompaniment does not require a final report; general questions and isolated routine edits should not start the full process.

## What to provide

Provide the actual request, source materials, and required deliverables. A lab may have a guide, variant, and data; a project may have a task and current files. Missing facts must not be invented.

Your own Word template is **optional**. For your institution's formatting, supply a current DOCX sample and requirements. You may explicitly select the built-in neutral preset. Body formatting and cover are independent choices: your own cover, a cover from a full sample, or the neutral cover. The preset is not a universal institutional standard. No Word sample is needed for accompaniment without a Word report. [Layout and cover](docs/word-preset.en.md).

## Install

One repository for Codex and Claude: <https://github.com/i7daydepressed/Human-Workflow>.

Claude Code:

```bash
claude plugin marketplace add https://github.com/i7daydepressed/Human-Workflow
claude plugin install workflow-tools-preview@workflow-tools
```

Codex CLI:

```bash
codex plugin marketplace add https://github.com/i7daydepressed/Human-Workflow --json
codex plugin add workflow-tools-preview@workflow-tools --json
```

In Claude's plugin interface choose **Customize → Plugins → Add → Add marketplace**, enter the repository URL, and install Human Workflow. Availability depends on client/account settings. Use a fresh session after installation. A chat without installation tools cannot install a plugin merely by receiving a URL.

The technical identifiers `workflow-tools-preview` and `workflow-tools` remain for compatibility with existing installations. The display name is Human Workflow. Users do not need to build a separate archive. [Installation details](docs/installation.en.md).

## Start a task

Ask: “Use md-word to complete this assignment from the attached guide and prepare a report using the sample.” When checking installation, explicitly name `workflow-tools-preview:md-word` and ask for the instruction paths actually read. Seeing a name in the skill list does not establish that its workflow was loaded. Automatic selection is not guaranteed.

Other requests: “Accompany this task and preserve its state; no separate report is needed”; “Use human-step to prepare checkable steps for an executor; do not change anything yet.”

Instructions are available in English and Russian. English is the default; `instruction_language: ru` explicitly selects Russian instructions. Output and log languages are independent.

## State, logs, and private preferences

The agent saves significant actions, checks, decisions, and the next step in the selected workspace, following existing project rules. Otherwise it uses `agent-logs/<run-id>.md`. Logs stay out of the submitted report; exclude full conversations, secrets, and unnecessary personal data. A no-write request also applies to logs.

An optional private profile stores language choices, preferences, and user Word resources **outside the plugin installation/cache**. Select it explicitly. Product updates must not overwrite it; profile transfer excludes history and the machine-local workspace path. [Profile contract](docs/profile.en.md).

The plugin starts no background collection and does not automatically upload logs to its developer. It provides no cloud synchronization or permanent cross-chat memory: continuation depends on saved files and actual host access. The client's own processing is governed by its settings and terms.

## Host capabilities and checks

Preview `0.0.0-i06` includes resources inside each skill folder, generated from one canonical source set. This addresses file delivery; an actual new-version Claude run and Mac client update remain unverified. [Check scope](docs/client-checks.en.md).

Core helpers use Python's standard library; optional cover composition requires `lxml`. The plugin does not install Word, Excel, fonts, or a universal renderer. A saved file or successful calculation does not replace verification in the intended application and visual review.

## License and development support

The public license is [PolyForm Noncommercial 1.0.0](LICENSE), including its express organizational permissions. Commercial use outside those permissions needs a separate grant: **USD 10 once for one human user**, or **USD 50 once for up to five users**, covering the confirmed purchased major version. Devices, agents, runs, projects, and resulting reports are not separate billing units. [Details](docs/licensing.en.md), [commercial terms](COMMERCIAL-LICENSE.md).

Commercial licenses are intended as a way to support development. **Sales are not open:** licensor details, purchase contact, and payment method are not supplied. Downloading does not create a paid grant. This is a source-available project with a noncommercial public license.

For contributors: [canonical sources and generated resources](docs/skill-resources.en.md).
