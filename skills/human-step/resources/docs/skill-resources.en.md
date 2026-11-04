# Resources and report-skill dependency

human-step owns step packets, their execution and acceptance. Its references live in references/; forms and data live in resources/.

Reports and shared helpers belong to [md-report](../../../md-report/SKILL.md), installed together with human-step. human-step has no scripts directory. Run helpers by their absolute paths in md-report/scripts/. Follow the report skill for report preparation, the [profile contract](../../../md-report/resources/docs/profile.en.md) for profiles, and the [Word guide](../../../md-report/resources/docs/word-preset.en.md) for document formatting.

The local resource-manifest.json lists paths relative to resources/. Paths starting with ../ refer to root-level instructions. source preserves provenance; generated=false identifies manual adaptation. Helpers are inventoried by md-report.

Edit the current skills directly in skills/. The old root locales/, shared/, generator and builders describe the former layout and do not support the current four editions. Do not regenerate over these skills until that tooling has been adapted separately.

Keep tasks, outputs, journals and private profiles outside the installation. Verify skill availability and actual operation results; file presence does not establish host loading or execution. See the scoped [client checks](client-checks.en.md).
