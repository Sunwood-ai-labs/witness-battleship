"""Verify the public distribution without network access or mutation."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'MANIFEST.json').read_text())
for item in manifest['files']:
    p=root/item['path']
    assert p.is_file(),item['path']
    assert p.stat().st_size==item['bytes'],item['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],item['path']
print('PASS:',len(manifest['files']),'files')
