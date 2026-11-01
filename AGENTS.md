# Repository maintenance

- Preserve the V62 whole-model baseline and V102 comparison as distinct artifacts.
- Keep the verified local scope (2/14 bays, zero baseline adoptions) separate from whole-ship completeness.
- Do not overwrite source CAD or restored outputs; publish explicit new versions for geometry changes.
- Keep private paths, account identifiers, credentials, service receipts and personal communications out of public artifacts.
- Inspect actual images before changing their captions. Do not describe renders as newly regenerated without evidence.
- Run `python -m unittest discover -s tests -v`, `python scripts/check_links.py`, `python scripts/update_manifest.py --check` and `python scripts/verify_files.py` before publishing.
- After intentional file edits, regenerate `MANIFEST.json` with `python scripts/update_manifest.py` and re-run checks.
- Run FreeCAD geometry checks when a compatible installation is available; distinguish unavailable checks from passes.
- Never grant a new license, enable paid services or alter repository security settings as routine maintenance.

- Run `python scripts/check_site.py` for website changes; preserve Japanese/English structural parity.
- Website source is `site/`; verify below the project base path and distinguish skipped Pages deployment from success.
- The locally installed repository-polish skill is under `.agents/skills/repository-polish`; do not include local skill copies in the public CAD manifest.
