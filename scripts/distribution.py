"""Shared, network-free validation for the public CAD distribution."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re

class ValidationError(ValueError):
    """The distribution is incomplete, changed, or unsafe to restore."""

def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def safe_path(root, value, *, flat=False):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValidationError('Invalid relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ('', '.', '..') for part in value.split('/')):
        raise ValidationError('Path must stay inside the distribution')
    if flat and len(path.parts) != 1:
        raise ValidationError('Expected a plain filename')
    root = Path(root).resolve()
    candidate = root.joinpath(*path.parts)
    try:
        candidate.resolve().relative_to(root)
    except ValueError as exc:
        raise ValidationError('Path escapes the distribution') from exc
    if candidate.is_symlink():
        raise ValidationError('Symbolic-link outputs or inputs are not supported')
    return candidate

def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError('Cannot read valid JSON: ' + Path(path).name) from exc

def verify_record(path, record):
    size, digest = record.get('bytes'), record.get('sha256')
    if type(size) is not int or size < 0 or not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValidationError('Invalid size or SHA-256 metadata')
    if not Path(path).is_file():
        raise ValidationError('Missing file: ' + Path(path).name)
    if Path(path).stat().st_size != size or sha256_file(path) != digest:
        raise ValidationError('Size/SHA-256 mismatch: ' + Path(path).name)

def verify_manifest(root):
    root = Path(root)
    manifest = read_json(safe_path(root, 'MANIFEST.json', flat=True))
    if not isinstance(manifest, dict):
        raise ValidationError('Manifest must be an object')
    rows = manifest.get('files')
    if not isinstance(rows, list) or not rows:
        raise ValidationError('Manifest must contain files')
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValidationError('Invalid manifest record')
        path = safe_path(root, row.get('path'))
        if path in seen:
            raise ValidationError('Duplicate manifest path')
        seen.add(path)
        verify_record(path, row)
    return len(seen)
