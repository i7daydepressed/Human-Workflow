# Identity migration and rollback

[Русский](migration.ru.md). Target: `human-workflow` `0.0.7`, display Human-workflow-v0.0.7, Apache-2.0. Skills `human-step`/`md-word`, repository catalog `workflow-tools`, profile schema 1 and i02 Word preset IDs remain unchanged. This is a guide for a later explicitly authorized migration; no real installation, cache, profile or account is changed by preparing the candidate.

## Establish actual state

Record the current client/application and version, authentication mode when known, catalog registration, installed plugin name/version/path, enabled state and rollback package. Do not infer installed state from source HEAD. Hash only explicitly selected external profile/task/personal Word resources before changing registration; preserve these bytes and any newer work. Do not discover profiles or scan account history.

## Claude Code

The Claude marketplace contains the append-only rename `workflow-tools-preview` → `human-workflow`. Do not rewrite or remove existing rename history. [Official rename behavior](https://code.claude.com/docs/en/plugins/host-marketplace#rename-or-remove-a-plugin) documents settings-key handling, including managed settings that require an administrator update. Git/URL-backed catalogs may still need one explicit `claude plugin install human-workflow@workflow-tools` to populate the new cache.

With an available CLI, validate the candidate catalog/manifest using `claude plugin validate .` and record its actual output/version; otherwise mark validation not run. Validate a fresh context after the later authorized install. The map alone is not a migration result. CLI behavior does not establish Claude chat or account-synced behavior.

## Codex and other surfaces

No automatic rename equivalent has been verified. Use the supported plugin manager to inventory the old registration, keep a rollback artifact, prepare the new candidate, disable/remove the old active identity as appropriate, install the new identity and verify a fresh context. [Documented CLI management](https://learn.chatgpt.com/docs/developer-commands) includes `codex plugin list --json`, `codex plugin remove <plugin@marketplace> --json` and `codex plugin add human-workflow@workflow-tools --json`. Use the actual observed old identity; commands here are not an authorization to run them now.

Handle the separate legacy `workflow-preview-i04` catalog only if it actually exists. Do not rename/remove all catalogs, manually delete caches, or retain duplicate active coordinator copies as a migration strategy. Preserve unrelated extensions and registrations.

## Verify and roll back

Observe the new installed identity/version/body/resource paths in a fresh context and the absence of a duplicate active old coordinator. Recheck the selected external data hashes and inspect any intentional changes. Record selection/loading separately from arithmetic, helper or artifact success. Mark unavailable client, behavioral and migration checks not run.

Rollback restores the selected prior registration/package using supported management. It never overwrites newer task state, external profiles or personal Word resources. Keep an attributable record of actual actions and results. The old release's license remains historical; the Apache candidate does not rewrite it.
