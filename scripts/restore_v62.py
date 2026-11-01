"""Restore V62 after validating every layer; never overwrite an existing file."""
from pathlib import Path
import argparse
import io
import zipfile
from distribution import ValidationError, read_json, safe_path, sha256_file, verify_record
import hashlib

def restore(root):
    root = Path(root).resolve()
    cad_dir = safe_path(root, 'cad')
    parts_dir = safe_path(root, 'cad/v62_parts')
    meta = read_json(safe_path(parts_dir, 'PARTS.json', flat=True))
    if not isinstance(meta, dict):
        raise ValidationError('Invalid parts metadata')
    output = safe_path(cad_dir, meta.get('output_name'), flat=True)
    if output.exists() or output.is_symlink():
        raise ValidationError('Output already exists; not overwritten: ' + output.name)
    records = meta.get('parts')
    if not isinstance(records, list) or not records:
        raise ValidationError('No parts declared')
    chunks, seen = [], set()
    for record in records:
        if not isinstance(record, dict):
            raise ValidationError('Invalid part record')
        path = safe_path(parts_dir, record.get('name'), flat=True)
        if path in seen:
            raise ValidationError('Duplicate part name')
        seen.add(path)
        verify_record(path, record)
        chunks.append(path.read_bytes())
    archive = b''.join(chunks)
    if type(meta.get('archive_bytes')) is not int or len(archive) != meta['archive_bytes']:
        raise ValidationError('Archive size mismatch')
    if hashlib.sha256(archive).hexdigest() != meta.get('archive_sha256'):
        raise ValidationError('Archive SHA-256 mismatch')
    expected_size = meta.get('output_bytes')
    if type(expected_size) is not int or expected_size < 0:
        raise ValidationError('Invalid output size')
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            if z.namelist() != [output.name]:
                raise ValidationError('Archive must contain exactly the expected native file')
            info = z.infolist()[0]
            if info.file_size != expected_size or info.is_dir():
                raise ValidationError('Archive output size mismatch')
            data = z.read(info)
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise ValidationError('Invalid or corrupted ZIP archive') from exc
    if len(data) != expected_size or hashlib.sha256(data).hexdigest() != meta.get('output_sha256'):
        raise ValidationError('Native output size/SHA-256 mismatch')
    # Exclusive creation also protects against another process creating the output.
    try:
        with output.open('xb') as stream:
            stream.write(data)
    except FileExistsError as exc:
        raise ValidationError('Output already exists; not overwritten') from exc
    if sha256_file(output) != meta['output_sha256']:
        raise ValidationError('Written output verification failed')
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        output = restore(args.root)
    except (ValidationError, OSError) as exc:
        parser.exit(1, 'FAIL: ' + str(exc) + '\n')
    print('PASS: reconstructed', output.name, sha256_file(output))

if __name__ == '__main__':
    main()
