# Human-workflow-v0.0.7

[Русский](README.md)

Human Workflow is a plugin for working with an AI agent on assignments, projects, and reports. It helps preserve requirements, explain what was actually done and checked, and continue work after a pause or a handoff to another executor.

For example, give the agent an assignment guide, source data, and a report sample. The workflow connects requirements, implementation, checks, and the document; available Word, spreadsheet, PDF, or coding skills perform format-specific operations. Results also depend on the inputs, host capabilities, and checks actually performed.

## How it works

Attach an assignment, source materials or an existing project and ask: “Let's begin working on the task.” To select the process explicitly, name Human Workflow and md-word. The sequence below applies after the agent has selected and loaded the relevant skill.

This is the full workflow. The assignment determines which stages are needed: complete the core and prepare a report, obtain only step-by-step instructions, or accompany work without a final report.

**1. Read the assignment and identify the submission**

The agent examines the guide, variant, inputs, sample, current files and user decisions. It identifies the main work—the core—and the mandatory deliverables: a program, SQL script, table, JSON, report, additional answers or demonstration. The assignment determines the need for a report, theory and intermediate materials.

**2. Establish a clear technical specification**

The agent uses an existing technical specification (TS) or prepares a working specification from the original request and agreed clarifications. It records the goal, mandatory core requirements, inputs, environment and constraints, deliverables, formats, completion criteria and materials needed for explanation.

A few points in a working note can suffice for a small task; a large task may need a separate specification. The agent presents the working basis and resolves substantive ambiguities. Execution follows the selected TS revision; requirement changes are recorded separately from actual implementation facts.

**3. Execute the core against the specification**

The agent identifies the part it can perform with its available knowledge, tools and access, briefly states that scope and proceeds with the assigned work. When the core is feasible here—for example, a calculation, table, JSON, SQL or small program—the current agent performs and checks it using available means.

Results and required intermediate materials are retained during execution. A prepared file, a completed calculation and a run in the target environment establish different facts: written SQL is not evidence that the queries were executed in a database.

**3.1 Continue a large core through steps or another executor**

Large work can be divided into successive stages and continued with the current agent. When some actions cannot be performed directly, the agent identifies that part and prepares human-readable steps. The user can perform them personally, pass them to another agent, or continue with the current agent while receiving successive instructions.

Each step identifies the object and starting state, exact action, purpose, expected result, check and materials to return. The current agent receives actual results, reconciles them with the TS, records completed work and prepares the next stage. A bounded assignment for another executor includes relevant requirements, inputs and boundaries; the entire previous conversation is not required.

**4. Preserve the work history and current state**

Throughout the work, the agent keeps a readable log of actual actions: inputs received, changes made, results and checks obtained, and decisions taken. Concise current state separately records what is complete, blocked or remaining, and the next action.

Information returned by the user or another executor retains its source. Significant results and a continuation point are saved before costly or interruptible stages; actual saving and cloud synchronization are tracked separately.

**5. Reconcile results with the specification**

Results are compared with requirements regardless of who performed the core. Significant requirements remain traceable through: requirement → completed step → artifact and version → check and its limits.

The agent inspects accessible materials and records discrepancies, missing evidence and remaining work. Suitable earlier evidence retains its validity within its original version and scope.

**6. Prepare the human-readable Markdown report**

When a report is required, the agent writes a connected explanation: purpose → inputs → method and relevant theory → actions → results → checks → conclusion. The text follows actual work and assignment requirements; necessary illustrations, examples and sources serve those requirements.

The log supports reconstruction of the work history; the report explains the solution to its reader. Markdown becomes the content basis for the final document. Accompaniment without a report retains the necessary explanation and state.

**7. Approve the content**

For a newly authored report proceeding to Word, the agent presents the current Markdown revision or an accessible link and records pending approval. The user can refine the content or approve conversion of that revision. Independent authorized work can continue.

Approval covers specific content and is reused when it already covers the selected revision. Material changes require approval of the affected content; formatting-only changes do not automatically restart the process. An explicit direct-conversion request or waiver is recorded with its source where the assignment permits it.

**8. Assemble the final document**

The agent uses available capabilities to prepare DOCX, PDF or another required format. Body layout and cover are selected independently; an explicit no-separate-cover choice is supported. The agent preserves the agreed sample, selected current revision and manual user changes.

Content, structure and visual layout are checked within the available tools. Conversion, rendering and target-editor capabilities depend on the host; unavailable checks remain explicit limitations.

**9. Save and deliver the result**

The agent saves mandatory files, checks the save results and provides accessible deliverables with a concise account of completed work and remaining limitations. Content approval, file delivery, submission and teacher/customer acceptance are tracked separately.

After completion, the agent requests brief feedback once, reusing answers already supplied. An absent rating remains unknown and does not delay delivery.

**10. Resume after a pause or executor change**

A continuation record retains the current TS, selected versions and content/layout authorities, completed actions, check results, approval state, open questions and next action. The current agent, a fresh chat, another agent or the user can continue from those materials.

Continuation takes actual current files and divergence into account while preserving completed work. Access to saved materials depends on the selected destination and host capabilities.

In version 0.0.7, the explicit Markdown approval transition is defined for Word; the same transition for direct PDF assembly is not yet separately specified in the instructions.

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
claude plugin install human-workflow@workflow-tools
```

Codex CLI:

```bash
codex plugin marketplace add https://github.com/i7daydepressed/Human-Workflow --json
codex plugin add human-workflow@workflow-tools --json
```

In Claude's plugin interface choose **Customize → Plugins → Add → Add marketplace**, enter the repository URL, and install Human Workflow. Availability depends on client/account settings. Use a fresh session after installation. A chat without installation tools cannot install a plugin merely by receiving a URL.

The technical plugin name is `human-workflow`, version `0.0.7`, displayed as Human-workflow-v0.0.7. The repository marketplace remains `workflow-tools`; both skill names are unchanged. Existing `workflow-tools-preview` installations need a controlled [migration](docs/migration.en.md). This local candidate has not been published or installed by this change. [Installation details](docs/installation.en.md).

## Start a task

Ask: “Use md-word to complete this assignment from the attached guide and prepare a report using the sample.” When checking installation, explicitly name `human-workflow:md-word` and ask for the instruction paths actually read. Seeing a name in the skill list does not establish that its workflow was loaded. Automatic selection is not guaranteed.

Other requests: “Accompany this task and preserve its state; no separate report is needed”; “Use human-step to prepare checkable steps for an executor; do not change anything yet.”

Instructions are available in English and Russian. English is the default; `instruction_language: ru` explicitly selects Russian instructions. Output and log languages are independent.

## State, logs, and private preferences

The agent saves significant actions, checks, decisions, and the next step in the selected workspace, following existing project rules. Otherwise it uses `agent-logs/<run-id>.md`. Logs stay out of the submitted report; exclude full conversations, secrets, and unnecessary personal data. A no-write request also applies to logs.

An optional private profile stores language choices, preferences, and user Word resources **outside the plugin installation/cache**. Select it explicitly. Product updates must not overwrite it; profile transfer excludes history and the machine-local workspace path. [Profile contract](docs/profile.en.md).

The plugin starts no background collection and does not automatically upload logs to its developer. It provides no cloud synchronization or permanent cross-chat memory: continuation depends on saved files and actual host access. The client's own processing is governed by its settings and terms.

## Host capabilities and checks

Candidate `0.0.7` retains generated resources inside each skill folder and adds revision-bound Markdown approval, early persistence, installation-write guards, and containing-package diagnostics. Actual client loading, behavior, and identity migration remain unverified. [Check scope](docs/client-checks.en.md).

Core helpers use Python's standard library; optional cover composition requires `lxml`. The plugin does not install Word, Excel, fonts, or a universal renderer. A saved file or successful calculation does not replace verification in the intended application and visual review.

## License

Publisher-controlled material in candidate `0.0.7` is provided under [Apache License 2.0](LICENSE), to the extent the publisher may license it. Commercial use is permitted on those terms without a separate paid license or seat limit. Preserve applicable third-party licenses/notices; the license does not cover user profiles, personal originals, or task outputs merely because the plugin handles them. Earlier releases retain their historical licensing. [Scope and obligations](docs/licensing.en.md).

For contributors: [canonical sources and generated resources](docs/skill-resources.en.md).
