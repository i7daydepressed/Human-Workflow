# Extracting human-step from the plugin

The sibling `skills/scripts` directory is a required dependency for the skill's shared Python helpers. Copy that entire directory together with the skill, preserving names and relative locations:

```text
<destination>/
  skills/
    human-step/
    scripts/
```

Do not copy shared scripts back into the skill. `<shared-scripts>` in commands means the verified absolute path to that directory; the task's working directory may be elsewhere.

Preserve the skill's complete resources/ directory. Word commands require the resources of md-report or md-report-ru; shared word_cover.py locates its built-in samples in those standard sibling directories. Reporting, profiles and experience still require their referenced instructions. Shared scripts do not replace those instructions.

Read [SKILL.md](SKILL.md) and [scripts/README.md](../scripts/README.md). The scripts directory is not a separate skill. Local writes and checkpoints do not establish cloud synchronization.
