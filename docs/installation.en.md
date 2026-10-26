# Install from GitHub

Use one repository URL for Codex and Claude. The repository root is the plugin; `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` both point to it. Two skills share `locales/`, `shared/` and `docs/`. No archive build or conversion is required. [Русский](installation.ru.md).

## Codex CLI

Replace `REPOSITORY_URL` with the actual URL:

```bash
codex plugin marketplace add REPOSITORY_URL --json
codex plugin add workflow-tools-preview@workflow-tools --json
codex plugin list --marketplace workflow-tools --json
```

Inspect the installed/enabled state, then start a new session in your task directory. The old local `workflow-preview-i04` marketplace is a separate registration. Do not remove a working installation or private profile just to try this repository.

## Claude

In Claude Code:

```bash
claude plugin marketplace add REPOSITORY_URL
claude plugin install workflow-tools-preview@workflow-tools
```

In Claude's plugin interface, open Customize → Plugins → Add → Add marketplace, enter the GitHub URL and install Workflow Tools Preview. Use the plugin interface for the whole plugin. Begin a fresh conversation/session. If the account does not expose the relevant installation surface, report the client and actual message. A chat without installation tools cannot perform a local install merely by receiving a URL.

## Files and dependencies

Try an ordinary task after installation. Keep the full tree; tasks/profiles belong outside its installation/cache. Select an external profile explicitly when needed. Repeated initialization preserves existing profiles. Instruction, output and log languages are independent; layout and cover are independent choices. [Profile](profile.en.md).

Core helpers use Python's standard library; optional cover merge needs `lxml`. Word rendering and fonts depend on the host. [Word scope](word-preset.en.md). Local Linux/Python 3.12 checks and reported Mac/Python 3.14.5 evidence do not establish every client/version as supported.

The I04 base has scoped Codex CLI evidence. Direct installation of this repository and Claude execution have not yet been observed. [Client evidence](client-checks.en.md). No further manual test-package series is a prerequisite for trying a real task from GitHub.

Official references, checked 2026-10-26: [Codex commands](https://learn.chatgpt.com/docs/developer-commands), [Claude marketplaces](https://code.claude.com/docs/en/plugins/marketplace-reference), [Claude plugin interface](https://claude.com/docs/plugins/overview).
