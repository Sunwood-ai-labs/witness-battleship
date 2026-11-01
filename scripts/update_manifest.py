"""Regenerate/check the manifest for version-controlled distribution files."""
from pathlib import Path
import argparse
import json
from distribution import sha256_file

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DIRS = {'cad', 'docs', 'geometry', 'images', 'scripts', 'tests', '.github', 'site'}
ALLOWED_ROOT = {'README.md', 'README.ja.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'AGENTS.md', '.gitignore', '.gitattributes'}

def is_generated_native(relative_path):
    return relative_path.as_posix() == 'cad/WITNESS_V62_PUBLIC.FCStd'

def build(root):
    rows = []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root)
        if any(part in {'.git', '__pycache__', '.venv'} for part in rel.parts) or p.suffix in {'.pyc', '.log'}:
            continue
        if is_generated_native(rel):
            continue
        if len(rel.parts) == 1 and rel.name not in ALLOWED_ROOT:
            continue
        if len(rel.parts) > 1 and rel.parts[0] not in ALLOWED_DIRS:
            continue
        rows.append({'path':rel.as_posix(), 'bytes':p.stat().st_size, 'sha256':sha256_file(p)})
    rows.sort(key=lambda row: row['path'])
    return {'version':'public-distribution-20261101-v4', 'files':rows}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    value = json.dumps(build(ROOT), indent=2, ensure_ascii=False) + '\n'
    path = ROOT / 'MANIFEST.json'
    if args.check:
        if not path.exists() or path.read_text(encoding='utf-8') != value:
            parser.exit(1, 'FAIL: MANIFEST.json is stale; run python scripts/update_manifest.py\n')
        print('PASS: manifest matches distribution files')
    else:
        path.write_text(value, encoding='utf-8')
        print('Updated MANIFEST.json')

if __name__ == '__main__':
    main()
