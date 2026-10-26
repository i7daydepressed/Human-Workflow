# Workflow Tools Preview — I05

Local review package: two workflows, English/Russian instructions, one shared runtime, external private profiles and a neutral Word preset. The technical name/version are temporary; public branding and author are undecided. This I05 package is not published or client-installed; its I04 base has scoped client evidence in docs/client-checks.en.md.

After extraction, keep root `plugin.json`, `skills/`, `locales/`, `shared/` and `docs/` together. The complete plugin uses shared resources outside each individual skill folder. Read `docs/installation.en.md` (or `.ru.md`) for the isolated marketplace route, client check prompts and requirements. Entry descriptions support explicit use and intended implicit matching; I04 discovery has client evidence; I05 installation/update remains untested.

The default instruction edition is English, even for Russian result requests. A task's explicit `instruction_language: ru`, or the selected private profile, chooses Russian. Output/log languages are separate. Do not load both editions for an ordinary run.

From this plugin root, the local helpers can be called with absolute paths from another working directory:

```bash
python3 shared/scripts/report_workspace.py init /absolute/path/to/task --mode accompany --language ru
python3 shared/scripts/profile.py init /absolute/path/to/private-profile --instruction-language en --output-language ru --log-language ru
```

Keep profiles and task folders outside the package/cache. Installation/update does not overwrite them. Core helpers need Python; cover merging additionally needs `lxml`. No renderer, font, cloud adapter or universal MD→Word converter is installed. See `docs/word-preset.en.md` for the measured Word scope.

Historical experience is retained in both narrative and JSON form by the owner's representation choice. It remains reference material, not a live private acceptance catalog or evidence for a new submission. Source originals, private identifiers/quotes/links and owner profile are excluded. `PACKAGE-MANIFEST.json` records source paths and hashes. It does not attest host installation or publication.

Licensing: PolyForm Noncommercial 1.0.0 or a separately purchased commercial license. Approved one-time prices: USD 10 for one person; USD 50 for up to five people, for the confirmed purchased major version. Commercial sales are not open; seller/contact/payment details and legal review remain outstanding. See LICENSE, COMMERCIAL-LICENSE.md and docs/licensing.en.md.
