# Client evidence — I06

Updated 2026-10-27. The I06 source tree (`0.0.0-i06`) is published on GitHub at commit `a8d124f77f77cb14ffcfca6abc0e839baee8fbd6`; its verified I05 base is commit `23a57e765494ab2480461e62843ed6c4c8716d37`. License terms and prices have been selected; commercial sales remain closed. Publication does not establish host installation or a Mac client upgrade; these checks remain unverified for I06.

I06 adds generated skill-local resources, clearer md-word selection metadata and cooperation with available format skills, paired human-facing documentation, and profile/output protection for isolated resource paths. Canonical Word files and profile schema are preserved.

Two distinct Claude observations were supplied by the owner: one executor reported missing parent-tree resources after opening the entry files; another saw the skill descriptions but completed a task with format skills without reading md-word. Their exact host/install path and complete selection trace are unavailable. The second executor's later explanation is a self-report, not independent evidence that description wording caused the omission. Successful files from a run that did not use the plugin do not validate it. No exact model ID, subscription eligibility, or guaranteed automatic selection is inferred.

Local regression checks cover isolated folder links, helpers, resource provenance/freshness, and preservation of a synthetic external profile. These are file/runtime checks, not real Claude account execution or an actual client upgrade. Claude Code validation and a fresh I06 run in the intended Claude surface remain separate checks. See [resource layout](skill-resources.en.md).

Local I06 validation: 92 tests passed (baseline: 85). An additional synthetic run by a separate agent with explicitly assigned, isolated md-word read bundled instructions and saved a checked result, continuation state, and log without a final Word report. The returned files were inspected by the main agent. This does not test automatic selection or an actual Claude host.

## Historical evidence retained with its original scope

The following I05-era record describes its historical state. Its statements about pending publication/licensing are not the current release summary above.

### Historical I05 review record

Recorded 2026-10-26. This package is `0.0.0-i05`; the client exercised its `0.0.0-i04` base. I05 changes review/status documentation, temporary package version and matching builder/test constants. Runtime scripts, schemas, Word files, entry descriptions, language routing and task contracts are unchanged. No install or update of I05 on the Mac is claimed.

| Check on I04 | Evidence and scope |
| --- | --- |
| Local marketplace registration, install and enabled state | Owner supplied JSON from Codex CLI 0.162.1 |
| Explicit human-step and md-word | Executor responses identify installed-cache resources; returned task files were inspected |
| Default EN instructions with RU result/log; explicit RU | Executor resource lists and actual Russian outputs |
| Implicit human-step and md-word | Ordinary requests selected the expected installed entries according to executor reports |
| Concept explanation and ordinary code edit | Responses reported no skill reads or unwanted reporting process; edited code was not returned |
| Shared templates, workspace helper and neutral Word resource | Reported helper success, returned state/log and exact neutral DOCX bytes |
| Profile init, repeat init, export and import | Six recorded helper commands exited 0; twelve reported checks; returned profiles, manifests, selected DOCX and exclusions independently inspected |
| Explicit profile in a fresh context | RU instructions selected from profile; four reported SHA-256 values match the earlier returned baseline; PREPARE did not execute the requested edit according to the executor |

The profile scenario reports macOS 26.5.2 arm64 and Python 3.14.5. The build environment is Linux/Python 3.12. These are observations, not a minimum Python version or a cross-platform guarantee. The integrator did not control the Mac directly; reported commands/read traces remain attributed to the executor. Artifact inspection independently establishes file contents and consistency, not every historical filesystem action.

One early state check was completed in a follow-up. Two searches used incorrect resource paths and recovered. One log omitted attribution metadata; a later log included edition/version and unknown model fields after an explicit request. These observations do not justify a new architecture or a claim that future agent compliance is guaranteed. Detailed personal paths, transcripts and profiles remain private.

## Remaining scope

I05 installation/update on Mac, a separate picker inventory, other client surfaces, Windows and Microsoft Word remain untested. A staged helper/profile preservation test is not a real CLI upgrade. Existing I04 installation can continue to be used; repeated manual trigger tests are not required merely to review this candidate. Check an actual update when changing the installed package.

The neutral Word files retain earlier rendered/visual evidence by identical hashes. That renderer used Liberation Serif in place of the declared font; Microsoft Word layout is not established. The owner's visual opinion was positive, but the viewing app was not supplied. No public publication or external push occurred. Product name, public author, license and release version remain review decisions.
