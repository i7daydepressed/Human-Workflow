# Install from one GitHub repository

[Русский](installation.ru.md). Repository: <https://github.com/i7daydepressed/Human-Workflow>.

The repository root is the plugin. `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` both point to it. Keep the technical identity `workflow-tools-preview@workflow-tools`; its display name is Human Workflow.

## Codex CLI

```bash
codex plugin marketplace add https://github.com/i7daydepressed/Human-Workflow --json
codex plugin add workflow-tools-preview@workflow-tools --json
codex plugin list --marketplace workflow-tools --json
```

## Claude

```bash
claude plugin marketplace add https://github.com/i7daydepressed/Human-Workflow
claude plugin install workflow-tools-preview@workflow-tools
```

In the plugin interface use Customize → Plugins → Add → Add marketplace and the repository URL. Availability depends on the client/account. Use a fresh session after installation. Preserve an existing working installation and external profile; the old `workflow-preview-i04` marketplace is a separate registration.

I06 includes all runtime resources inside each skill's `resources/` folder. A skill must not require sibling folders outside its copied directory. Contributors generate these files from canonical sources before publishing; users need no ZIP build. Read [resource layout](skill-resources.en.md).

For an installation check, explicitly request md-word or human-step and ask for the paths of instructions actually read. A name in the list proves neither reading nor execution. If a path is missing, retain the actual error and host information; do not silently reconstruct the workflow from descriptions or network sources. Automatic selection is a separate behavioral check.

Tasks, logs, outputs, and explicitly selected profiles belong outside installation/cache. Use absolute helper paths rooted at the selected skill's resource folder. Profile initialization does not select Word layout or cover. Instruction, output, and log languages are independent. [Profile](profile.en.md), [Word scope](word-preset.en.md).

Python's standard library supports core helpers; optional cover composition needs `lxml`. Rendering and fonts depend on the host. Existing I04 client evidence and current limitations are in [client checks](client-checks.en.md). Local isolation tests do not establish a real Claude run or Mac upgrade.
