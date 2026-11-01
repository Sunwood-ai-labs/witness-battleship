"""Reconstruct V62 locally, validate every part and never overwrite an output."""
from pathlib import Path
import hashlib,io,json,zipfile
root=Path(__file__).resolve().parents[1]
parts=root/'cad/v62_parts';meta=json.loads((parts/'PARTS.json').read_text());chunks=[]
output=root/'cad'/meta['output_name']
if output.exists():raise SystemExit('Output already exists; not overwritten: '+output.name)
for item in meta['parts']:
    assert Path(item['name']).name==item['name']
    data=(parts/item['name']).read_bytes()
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],item['name']
    chunks.append(data)
archive=b''.join(chunks)
assert len(archive)==meta['archive_bytes'] and hashlib.sha256(archive).hexdigest()==meta['archive_sha256']
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    assert z.namelist()==[meta['output_name']]
    assert z.testzip() is None
    data=z.read(meta['output_name'])
assert len(data)==meta['output_bytes'] and hashlib.sha256(data).hexdigest()==meta['output_sha256']
with output.open('xb') as f:f.write(data)
print('PASS: reconstructed',output.name,hashlib.sha256(data).hexdigest())
