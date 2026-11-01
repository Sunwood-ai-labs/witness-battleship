# Getting started: open and edit

**English** | [日本語](../ja/guide/getting-started.md) · [Guide index](index.md)

[Back to README](../../README.md)

## 1. Choose your starting point

- **Whole-ship layout and appearance: V62.** A baseline snapshot with 35,761 objects; restore it from 16 compressed fragments first.
- **Two recessed hull bays: V102.** Open the included FCStd directly. It has one hull, 13 attached shapes, and one group—not a full ship assembly.
- **No installation: the eight README images.** Browse whole views, close-ups, and D4/D9 maps. Images do not guarantee integration status or dimensional accuracy.

Fresh opening of the public FCStd files was verified in FreeCAD 1.0R. Other versions are unverified.

## 2. Download and verify files

```sh
git clone https://github.com/Sunwood-ai-labs/witness-battleship.git
cd witness-battleship
uv run python scripts/verify_files.py
```

Use Python 3. Examples prefer `uv`; an existing installation can use `python` or `python3` instead of `uv run python`. If verification fails, investigate missing files or modifications before opening and editing.

## 3. Restore V62

```sh
uv run python scripts/restore_v62.py
```

Inputs are `cad/v62_parts/PARTS.json` and the 16 files ending in `.part001` through `.part016`. The output is `cad/WITNESS_V62_PUBLIC.FCStd`. Individual fragments cannot be opened in FreeCAD.

Restoration checks each fragment, the complete archive, and the output FCStd. Allow space for the restored file too. Memory use and execution time depend on the environment; no universal figures have been verified.

If the output already exists, the script stops to protect it. Do not delete a file without knowing whether it contains edits. Preserve it elsewhere if necessary, establish its origin, and only then retry.

## 4. Inspect in FreeCAD

1. Start FreeCAD and choose **File → Open** to select the FCStd.
2. Wait for loading, then fit the complete model into the view.
3. Select shapes in the model tree and inspect their properties and visibility.
4. V102's smaller part count makes it a useful entry point for examining the recessed hull, backs, and panels separately.

Compare separate documents rather than duplicating hulls in the same space. V100/V101 alternative hull BReps also contain complete hulls; they are not attachments to stack together.

## 5. Edit working copies

- Use **Save As** before editing and choose a separate working file.
- Keep distributed files unchanged to distinguish original issues from changes introduced by editing.
- Edit according to the shape type and retained properties. Complete sketch/feature history is not guaranteed.
- After changes, save, close, and freshly reopen the document to inspect display, parts, and geometry.
- Record version, changes, and display conditions for comparisons. Distinguish a comparison alternative from an adopted baseline.

Opening a `.brp` in FreeCAD is also useful for inspecting its shape. It does not recreate the FCStd's complete grouping, colors, or editing history.

## 6. If something goes wrong

See [README troubleshooting](../../README.md#troubleshooting), the [contribution guide (Japanese)](../../CONTRIBUTING.md) for reporting details, and [Verification](verification.md) for geometry-check instructions.
