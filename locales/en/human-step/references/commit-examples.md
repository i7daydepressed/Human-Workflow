# Illustrative message structure

These are paraphrased, neutralized mechanism examples derived from earlier message patterns, not verbatim historical quotes or statements about the current diff. Use the actual repository's language/format and verified names. Known limitations belong in the message when material; commit/push needs its own authorization.

```text
- EditorModel.MoveStep() moves the selected object in Steps and recalculates the result
- TransformService.Process() applies the supplied steps in queue order and returns the resulting bytes
- the two histogram views receive the same comparison data after adding, moving and removing a step

Known limitation:
- the legacy settings path remains; removing it is a separate task
```

Prefer these concrete mechanisms to “refactor UI” or “improve architecture”. Do not copy method names or assert builds/GUI checks unless established in the current source and run.
