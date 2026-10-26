# Workflow Tools — preview

Two workflows in one plugin: **human-step** prepares, executes and reviews exact step packets; **md-word** accompanies tasks, preserves state and prepares reports when requested. Both use paired English/Russian instructions, one shared runtime, an external private profile and a neutral Word preset. [Русский](README.ru.md).

## Install from GitHub

Give an agent this repository's GitHub URL and ask: “Install Workflow Tools from this repository using its README for my client.” An agent with terminal access can use the commands below. Replace `REPOSITORY_URL` with the actual GitHub URL.

Claude Code:

```bash
claude plugin marketplace add REPOSITORY_URL
claude plugin install workflow-tools-preview@workflow-tools
```

Codex CLI:

```bash
codex plugin marketplace add REPOSITORY_URL --json
codex plugin add workflow-tools-preview@workflow-tools --json
```

In Claude's plugin interface, use **Customize → Plugins → Add → Add marketplace**, enter the repository URL and install Workflow Tools Preview. Availability depends on account/client settings. Start a new conversation/session after installation. [Installation details](docs/installation.en.md).

No ZIP build is needed. Both marketplace catalogs point to this repository root with the same two skills and shared resources. Keep the full plugin tree. Store tasks and private profiles outside the installation/cache; see the [profile contract](docs/profile.en.md).

## Use

Ask for an exact handoff packet, execution of an approved packet, or task accompaniment with preserved state. Accompaniment does not require a final report. Ordinary questions and isolated code edits should not start the full workflow. English instructions are the default; an explicit task/profile setting can select Russian. Output and log languages are independent.

The [Word preset](docs/word-preset.en.md) provides cleaned example formatting. Users can select their own samples and preferences. Rendering, fonts and optional dependencies depend on the host; installation does not provide them. Core helpers use Python's standard library; the optional bounded cover merge needs `lxml`.

## Licensing and prices

The public license is [PolyForm Noncommercial 1.0.0](LICENSE), including its express organizational permissions. Commercial uses outside those permissions need a separate commercial grant: **USD 10 once for one human user**, or **USD 50 once for up to five users**, covering the confirmed purchased major version. Devices, agents, runs, projects and resulting reports are not separate billing units. See [licensing details](docs/licensing.en.md) and [prepared commercial terms](COMMERCIAL-LICENSE.md).

**Commercial sales are not open:** the public licensor identity, purchase contact and payment method have not been supplied. Downloading this preview does not create a purchase or a paid grant. The prepared terms require final sales documents and legal review before payments. This is a source-available project with a noncommercial public license.

## Status

The base was exercised on Mac with Codex CLI 0.162.1. [Client evidence](docs/client-checks.en.md) records the actual scope. The direct GitHub layout is prepared; installation from the future GitHub URL and actual Claude behavior have not yet been observed. The technical identity `workflow-tools-preview` / `0.0.0-i05` is retained for preview use. The owner selected the licensing model below. Public upload, permanent identity and opening commercial sales remain separate steps.

Personal originals, private profiles and personal logs are excluded. Anonymized historical examples are reference material, not live user history. Development tests and optional archive builders remain in `tests/` and `tools/`; users do not need them to install from GitHub. [Release status](packaging/release-status.json).
