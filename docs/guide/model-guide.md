# Model guide

**English** | [日本語](../ja/guide/model-guide.md) · [Guide index](index.md)

[Back to README](../../README.md)

## V62: the whole-ship baseline

V62 is a whole-ship baseline snapshot containing 35,761 objects. It is not a latest ship incorporating every later local alternative. Restore the public derivative FCStd from 16 compressed fragments.

The D4/D9 images include display composites reflecting later local versions. Do not infer that every later result visible in them has been integrated into public V62.

## V102: one hull and 13 attached shapes

`geometry/v102/` contains the following 14 BReps. The FCStd adds one group to these 14 parts.

| Filename | Count | Role |
| --- | ---: | --- |
| `V102_TwoCutAlternativeHull.brp` | 1 | Hull after applying two removal regions |
| `V102_FromV100_RecessBack.brp` | 1 | Recess back derived from V100 |
| `V102_FromV100_RecessedWarmPane0.brp`–`5.brp` | 6 | Warm panels derived from V100 |
| `V102_FromV101_RecessBack.brp` | 1 | Recess back derived from V101 |
| `V102_FromV101_RecessedWarmPane0.brp`–`4.brp` | 5 | Warm panels derived from V101 |
| **Total** | **14** | One hull + two backs + 11 panels |

BRep single-solid validity and the cutting recipe are checked. Those checks alone do not establish whole-ship structural safety or design compatibility between components.

## Cutting recipe

Contents of `geometry/recipe/`:

| File | Meaning |
| --- | --- |
| `V62_OriginalHull.brp` | Base hull |
| `V100_AlternativeHull.brp` | Alternative hull with the first bay's 650 mm recess |
| `V101_AlternativeHull.brp` | Alternative hull with the adjacent bay's 500 mm recess |
| `REMOVAL_V100.brp` | Removal region corresponding to V100 |
| `REMOVAL_V101.brp` | Removal region corresponding to V101 |

V100 and V101 each contain an entire hull. Overlaying or adding them together does not produce V102.

```text
Removal A = base hull - V100 alternative hull
Removal B = base hull - V101 alternative hull
V102 hull = base hull - Removal A - Removal B
```

The verification script calculates removal regions from the alternative hulls, checks their non-overlap, and compares the result with the distributed V102 hull using a volume tolerance. See [Verification](verification.md).

## Reading the relationship between images and CAD

- `WHOLE_BEFORE.png` / `WHOLE_AFTER.png`: local styling in a whole-ship view, not evidence of V102's standalone component inventory.
- `BAY0_BEFORE.png` / `BAY0_AFTER.png`: close-up of a bay with five warm panels.
- `BAY1_BEFORE.png` / `BAY1_AFTER.png`: close-up of a bay with six warm panels.
- `D4_FLOOR_MAP.png`: display composite showing mess, galley, common room, medical and life-support areas. Its annotations reference V62 + V65/66/67/68 + V79.
- `D9_FLOOR_MAP.png`: upper-bridge display composite. Its annotations reference confirmed V75 geometry.

D4/D9 hide ceilings and objects above the cutting plane. In D9, label 1 identifies the interior; other dark areas include separate roof structures. Use the images to understand layout, not as substitutes for integrated CAD.

## Comparison, adoption, and completion are different

Two of 14 bays have been verified as comparisons, with zero bays adopted into the baseline. The remaining 12 are incomplete. “2/14” measures comparison scope, not whole-ship completion or reconstruction accuracy.
