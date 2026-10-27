# Canonical sources and skill-local resources

[Русский](skill-resources.ru.md).

Edit the canonical `locales/`, `shared/`, and `docs/` sources. Run `python3 tools/sync_skill_resources.py` from the repository root to regenerate `skills/<name>/resources/`. Commit the generated files with the source change when publication is authorized: direct GitHub installation must already contain the required bytes. Users need no build step.

Each entry links only to its own resource folder. Referenced instruction trees, templates, scripts, schemas, and Word assets stay available when a host copies one skill without the parent plugin. Resolve helper commands against that resource root, not the task's current directory. `resource-manifest.json` records source paths and hashes. `packaging/skill-resources.json` records the shared provenance for contributors.

There is one maintained source set and multiple generated physical copies for distribution. This replaces the earlier requirement of exactly one physical runtime file in the package. Do not edit the copies manually or add private profiles, task files, logs, or secrets to them. The synchronizer reports unmanaged files instead of deleting them. `--check` verifies freshness without writing; plugin builders reject stale copies.

Check isolated skills locally, including relative links, Python imports from a different working directory, external profile preservation, and rejection of outputs inside installation. These checks do not emulate every host or prove a Claude web installation. Preserve the separate scope recorded in [client checks](client-checks.en.md).
