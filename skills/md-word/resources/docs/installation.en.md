# Installation and client surfaces

[Русский](installation.ru.md). Repository: <https://github.com/i7daydepressed/Human-Workflow>.

The candidate is `human-workflow` `0.0.7`, displayed as Human-workflow-v0.0.7. Both repository catalogs point to the plugin root `./` and retain `workflow-tools`. These source changes do not publish the candidate: confirm the actual distributed revision before installation. Existing installations need the [migration guide](migration.en.md), not blind duplicate installation.

## Documented distribution versus observed support

| Surface | Documented route/capabilities | Candidate evidence |
| --- | --- | --- |
| Claude chat custom skills | Free and paid plans with code execution enabled; upload a ZIP containing a skill folder. Organization policy can restrict it. | Dedicated upload ZIPs are not built or host-validated by this candidate; a whole-repository ZIP is not that format. |
| Claude chat plugins | Paid-plan route; bundled skills/commands work in chat. Hooks and subagents do not run there. | No new account installation or execution observed. |
| Claude Cowork / Code | Hook/subagent-capable surfaces, subject to their actual runtime and permissions. This plugin requires neither hooks nor subagents. | No inference from chat or source-only tests. |
| Codex CLI / Desktop | Root portable `plugin.json`, `skills/`, and OpenAI presentation under `extensions.com.openai`; no extra compatibility overlay is needed here. | Record the actual application/CLI version, installation form and observed bytes. Historical CLI evidence does not establish Desktop execution. |

Sources checked 2026-10-27: [Claude skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [Claude plugins](https://support.claude.com/en/articles/13837440-use-plugins-in-claude), [OpenAI packaging](https://developers.openai.com/plugins/build/plugins). These are documentation facts, not account entitlement or an installation result.

## Future authorized repository installation

Codex CLI:

```bash
codex plugin marketplace add https://github.com/i7daydepressed/Human-Workflow --json
codex plugin add human-workflow@workflow-tools --json
codex plugin list --marketplace workflow-tools --json
```

Claude Code:

```bash
claude plugin marketplace add https://github.com/i7daydepressed/Human-Workflow
claude plugin install human-workflow@workflow-tools
```

Use the supported client interface when CLI tools are unavailable. These commands describe a later authorized installation after the candidate is distributed; they were not executed during source implementation. The isolated archive's `workflow-preview-i04` catalog is a separate legacy registration. [CLI management reference](https://learn.chatgpt.com/docs/developer-commands).

## Verify actual use

Start a fresh context. Separate available metadata, actual selection, loading of entry/body/resources, execution, checks, verified saves, and delivery. For an explicit check, name `human-workflow:md-word` or `human-workflow:human-step` and record paths actually read. A visible name or polished output alone proves neither loading nor coordinated execution. An automatic-selection test uses an ordinary prompt in another fresh context; explicit success is not its result. Missing traces are unassessed. A quota interruption is not evidence of missing entitlement or instruction compliance.

Each skill has generated `resources/`; resolve helpers by absolute paths from that resource root. Keep tasks, outputs, logs and explicitly selected profiles outside installation/cache. Instruction/output/log languages are independent. [Resources](skill-resources.en.md), [profile](profile.en.md), [Word scope](word-preset.en.md), [check scope](client-checks.en.md), [Apache-2.0](licensing.en.md).

Core helpers use Python's standard library; optional cover composition needs `lxml`. Fonts and suitable rendering remain host capabilities. Documentation compatibility and local tests do not certify installation or visual Word acceptance.
