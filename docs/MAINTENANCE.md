# Repository polish and publishing

## Maintenance skill

This public presentation was prepared using [repository-polish](https://github.com/Sunwood-ai-labs/repository-polish-skill) at commit `89e98c167fb3d9475763311b562e15bfc62e8970`, reviewed before use and installed with the official Codex skill-installer into the working checkout's `.agents/skills/repository-polish` directory. The local skill copy is excluded from the CAD distribution. Installing a skill is separate from verifying the resulting repository.

The selected scope is full repository polish: English/Japanese documentation, a bespoke static GitHub Pages experience, reproducible validation, and retained model/version distinctions. PowerShell was unavailable in the maintenance environment, so the skill's inventory and staged-payload checks were performed with equivalent Git and Python checks. No new model license is granted.

## Website architecture

`site/` is the complete static publishing payload. It has no build-time package dependency or external analytics. This deliberately uses HTML/CSS/JavaScript rather than a documentation framework: the landing experience is centered on real CAD imagery and interactive comparisons; detailed, versioned guides remain in the repository. Paths must work below `/witness-battleship/`, not only at a domain root.

The distribution manifest covers site source and assets as well as CAD files. Run the existing tests, Markdown link checks, website checks and manifest verification before publication. A successful site check does not establish native CAD validity or whole-ship completion.

## Deployment boundary

`.github/workflows/deploy-pages.yml` validates the distribution first. It publishes only when the repository's existing Pages configuration has `build_type: workflow`. If Pages is not enabled, validation succeeds but deployment is explicitly skipped with a job-summary explanation; this is **not** a successful website publication. Once enabled, the next main push or manual workflow dispatch performs deployment.

The workflow uses GitHub's short-lived built-in token and OIDC only, with read-only permissions for validation and Pages deployment permissions isolated to the deploy job. It does not create credentials, change repository visibility, or enable paid services. Action versions are pinned to reviewed commit hashes.

## Required signoff

- Normal and optimized-Python distribution tests.
- Manifest and Markdown/website local links.
- English/Japanese structure and factual parity.
- Actual desktop and mobile preview, keyboard controls, and reduced-motion behavior.
- Public commit readback and CI outcome, distinguished from any skipped deployment.
- Actual live Pages URL and assets before claiming deployment success.
- Versioned archive plus restore/hash verification before claiming backup success.

Keep the original V62 whole-model baseline, V102 local comparison, 2/14 prototype bays and zero baseline adoptions distinct throughout all presentation changes.
