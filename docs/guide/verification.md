# Public-set verification

**English** | [日本語](../ja/guide/verification.md) · [Guide index](index.md)

[Back to README](../../README.md)

## Checks during public preparation

This records local checks on 2026-11-01. Consult commit history for published changes and GitHub Actions for CI results. Local checks do not imply success for an unexecuted CI run.

| Item | Evidence |
| --- | --- |
| Public derivative V62 FCStd | Only private XML metadata replaced; the other 107,342 ZIP members match the originals by SHA-256 |
| Fresh V62 opening | Opened in FreeCAD 1.0R; 35,761 objects confirmed |
| V102 FCStd | 59 ZIP members match the original; freshly opened in FreeCAD 1.0R with 15 objects: 14 parts plus one group |
| V102 BReps | All 14 are valid single solids; removal-region non-overlap and cumulative-recipe volume difference checked |
| PNGs | Text and other metadata removed from public copies; all RGBA pixels match before and after removal |
| Public files | Sizes, SHA-256, fragmented distribution, and restored output checked |
| Scripts | 27 Python unit tests passed locally at this preparation stage |

The public tree and FCStd members were pattern-scanned for private keys, common token formats, private identifiers, and private working paths. This is not proof that every unknown form of secret is absent.

## Recheck with standard Python

Run from the repository root. These standard-library checks do not require FreeCAD. Examples prefer `uv`; existing Python 3 installations can use `python` or `python3` instead of `uv run python`.

```sh
uv run python scripts/verify_files.py
uv run python scripts/check_links.py
uv run python -m unittest discover -s tests -v
uv run python scripts/update_manifest.py --check
```

- `verify_files.py`: compare distributed sizes and SHA-256 hashes.
- `check_links.py`: check local Markdown file/image targets; external URLs and page anchors are excluded.
- `unittest`: check behavior for missing/corrupted data, invalid inputs, overwrite refusal, and related cases.
- `update_manifest.py --check`: compare the manifest with current files. Normal use does not require rewriting the manifest.

Intentional edits can also cause hash mismatches. Keep verification of distributed files separate from verification of your edits. Do not update the manifest just to make a mismatch disappear.

## Verification during V62 restoration

```sh
uv run python scripts/restore_v62.py
```

The archive is distributed in 16 fragments to meet transfer limits. Restoration verifies each fragment, the combined archive, and the output FCStd by SHA-256. Existing outputs are not overwritten. See [Getting started](getting-started.md).

## Verify geometry in FreeCAD

If ordinary Python cannot `import FreeCAD`, use FreeCAD's Python console. Replace the placeholder below with the absolute path to your checkout's `scripts/verify_geometry.py`:

```python
import runpy
runpy.run_path("/path/to/witness-battleship/scripts/verify_geometry.py", run_name="__main__")
```

On Windows, a path such as `C:/.../scripts/verify_geometry.py` can be used. These examples are placeholders, not actual checkout locations.

The script reads BReps without saving or modifying models. It checks:

1. The base and V100/V101 alternative hulls are valid single solids.
2. The two removal regions calculated from their differences do not overlap.
3. Subtracting both regions produces a hull within the volume tolerance of public V102.
4. All 14 parts in `geometry/v102/` are valid single solids.

Both the overlap volume and the sum of the two directional difference volumes must be `< 0.01` in FreeCAD's shape-volume units. This is not mathematical identity or a manufacturing tolerance guarantee. Distributed removal-region BReps are recipe material; the script recomputes removal regions from alternative hulls.

The success message is `PASS: 14 valid single-solid parts and exact two-cut recipe`. Here, `exact` refers to the numerical checks described above.

## Outside the verified scope

- Compatibility beyond FreeCAD 1.0R or operation on all operating systems/hardware.
- Whole-ship operation, strength, watertightness, manufacturing suitability, or safety certification.
- Rendering identity at every viewpoint and visibility state.
- A finished whole-ship model integrating every later local result.
- Complete recovery of all historical versions, generation sources, and editing history.

Existing V101/V102 source backups were previously restored into fresh folders and checked for native/payload/local-image redraw consistency. New checks of the public derivatives are limited to the scope above; they must not be generalized into whole-ship revalidation.
