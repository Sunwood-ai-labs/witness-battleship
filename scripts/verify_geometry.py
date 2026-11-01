"""Run with FreeCAD's Python environment. Read-only geometry verification."""
from pathlib import Path
import FreeCAD
import Part
def require(condition, message):
    if not condition:
        raise ValueError(message)

root=Path(__file__).resolve().parents[1]
def shape(p):
    s=Part.Shape();s.read(str(p));require(s.isValid() and len(s.Solids)==1, p.name)
    return s
r=root/'geometry/recipe'
base=shape(r/'V62_OriginalHull.brp')
a=shape(r/'V100_AlternativeHull.brp');b=shape(r/'V101_AlternativeHull.brp')
cut_a=base.cut(a);cut_b=base.cut(b)
require(cut_a.common(cut_b).Volume < .01, 'Removal regions overlap')
expected=base.cut(cut_a).cut(cut_b)
actual=shape(root/'geometry/v102/V102_TwoCutAlternativeHull.brp')
require(expected.cut(actual).Volume+actual.cut(expected).Volume < .01, 'Two-cut geometry mismatch')
parts=list((root/'geometry/v102').glob('*.brp'))
require(len(parts)==14, 'Expected exactly 14 parts')
for p in parts:shape(p)
print('PASS: 14 valid single-solid parts and exact two-cut recipe')
