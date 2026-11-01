"""Small synthetic fixtures exercise failure paths without changing CAD assets."""
from pathlib import Path, PurePosixPath, PureWindowsPath
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from distribution import ValidationError, safe_path, verify_manifest
from restore_v62 import restore
from check_links import check_links
from update_manifest import is_generated_native, build as build_manifest


def digest(data):
    return hashlib.sha256(data).hexdigest()

class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.parts = self.root / 'cad/v62_parts'
        self.parts.mkdir(parents=True)
        self.native = b'synthetic CAD fixture, not a real model'
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('TEST.FCStd', self.native)
        archive = stream.getvalue()
        cut = len(archive)//2
        chunks = [archive[:cut], archive[cut:]]
        rows=[]
        for i, chunk in enumerate(chunks):
            name=f'archive.part{i:03}'
            (self.parts/name).write_bytes(chunk)
            rows.append({'name':name, 'bytes':len(chunk), 'sha256':digest(chunk)})
        self.meta={'parts':rows,'archive_bytes':len(archive),'archive_sha256':digest(archive),'output_name':'TEST.FCStd','output_bytes':len(self.native),'output_sha256':digest(self.native)}
        self.save_meta()

    def save_meta(self):
        (self.parts/'PARTS.json').write_text(json.dumps(self.meta))

    def test_restored_native_excluded_on_windows_and_posix(self):
        self.assertTrue(is_generated_native(PureWindowsPath(r'cad\WITNESS_V62_PUBLIC.FCStd')))
        self.assertTrue(is_generated_native(PurePosixPath('cad/WITNESS_V62_PUBLIC.FCStd')))
        self.assertFalse(is_generated_native(PureWindowsPath(r'cad\WITNESS_V102_PUBLIC.FCStd')))

    def test_manifest_order_is_canonical(self):
        (self.root/'README.md').write_text('readme')
        (self.root/'CHANGELOG.md').write_text('changes')
        paths=[item['path'] for item in build_manifest(self.root)['files']]
        self.assertEqual(paths, sorted(paths))

    def test_restore_success(self):
        self.assertEqual(restore(self.root).read_bytes(), self.native)

    def test_existing_output_is_preserved(self):
        output=self.root/'cad/TEST.FCStd';output.write_bytes(b'keep this')
        with self.assertRaises(ValidationError):restore(self.root)
        self.assertEqual(output.read_bytes(), b'keep this')

    def test_second_run_is_rejected(self):
        restore(self.root)
        with self.assertRaises(ValidationError):restore(self.root)

    def test_corrupt_part_rejected(self):
        p=self.parts/self.meta['parts'][0]['name'];p.write_bytes(b'x'*p.stat().st_size)
        with self.assertRaises(ValidationError):restore(self.root)
        self.assertFalse((self.root/'cad/TEST.FCStd').exists())

    def test_missing_part_rejected(self):
        (self.parts/self.meta['parts'][0]['name']).unlink()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_duplicate_part_rejected(self):
        self.meta['parts'].append(self.meta['parts'][0]);self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_invalid_part_paths_rejected(self):
        for value in ['../escape', '/tmp/escape', 'x/y', 'C:\\escape', '']:
            with self.subTest(value=value):
                self.meta['parts'][0]['name']=value;self.save_meta()
                with self.assertRaises(ValidationError):restore(self.root)

    def test_invalid_output_paths_rejected(self):
        for value in ['../escape', '/tmp/escape', 'x/y', 'C:\\escape', '']:
            with self.subTest(value=value):
                self.meta['output_name']=value;self.save_meta()
                with self.assertRaises(ValidationError):restore(self.root)

    def test_wrong_archive_hash_rejected(self):
        self.meta['archive_sha256']='0'*64;self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_wrong_native_hash_rejected(self):
        self.meta['output_sha256']='0'*64;self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_unexpected_zip_member_rejected(self):
        self.meta['output_name']='OTHER.FCStd';self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_optimized_python_still_rejects_corruption(self):
        p=self.parts/self.meta['parts'][0]['name'];p.write_bytes(b'x'*p.stat().st_size)
        result=subprocess.run([sys.executable,'-O',str(SCRIPTS/'restore_v62.py'),'--root',str(self.root)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('mismatch',result.stderr)
        self.assertFalse((self.root/'cad/TEST.FCStd').exists())

    def write_manifest(self, rows):
        (self.root/'MANIFEST.json').write_text(json.dumps({'files':rows}))

    def test_manifest_success(self):
        (self.root/'a.txt').write_bytes(b'a');self.write_manifest([{'path':'a.txt','bytes':1,'sha256':digest(b'a')}])
        self.assertEqual(verify_manifest(self.root),1)

    def test_manifest_corruption_and_optimized_mode(self):
        (self.root/'a.txt').write_bytes(b'b');self.write_manifest([{'path':'a.txt','bytes':1,'sha256':digest(b'a')}])
        with self.assertRaises(ValidationError):verify_manifest(self.root)
        result=subprocess.run([sys.executable,'-O',str(SCRIPTS/'verify_files.py'),'--root',str(self.root)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)

    def test_manifest_escape_rejected(self):
        self.write_manifest([{'path':'../a.txt','bytes':1,'sha256':digest(b'a')}])
        with self.assertRaises(ValidationError):verify_manifest(self.root)

    def test_manifest_duplicate_rejected(self):
        (self.root/'a.txt').write_bytes(b'a');row={'path':'a.txt','bytes':1,'sha256':digest(b'a')};self.write_manifest([row,row])
        with self.assertRaises(ValidationError):verify_manifest(self.root)

    def test_bad_metadata_shape_rejected(self):
        (self.root/'MANIFEST.json').write_text('[]')
        with self.assertRaises(ValidationError):verify_manifest(self.root)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            link=self.root/'outside'
            try:link.symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):self.skipTest('Symlinks not permitted on this platform')
            with self.assertRaises(ValidationError):safe_path(self.root,'outside/file.txt')

    def test_wrong_native_size_rejected(self):
        self.meta['output_bytes'] += 1;self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_wrong_archive_size_rejected(self):
        self.meta['archive_bytes'] += 1;self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_empty_parts_rejected(self):
        self.meta['parts']=[];self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_invalid_size_type_rejected(self):
        self.meta['parts'][0]['bytes']=True;self.save_meta()
        with self.assertRaises(ValidationError):restore(self.root)

    def test_cli_restore_success(self):
        result=subprocess.run([sys.executable,str(SCRIPTS/'restore_v62.py'),'--root',str(self.root)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.root/'cad/TEST.FCStd').read_bytes(),self.native)

    def test_link_escape_rejected(self):
        (self.root/'README.md').write_text('[outside](../outside.txt)')
        count,errors=check_links(self.root)
        self.assertEqual(count,1);self.assertIn('escapes',errors[0])

    def test_local_links_and_missing_image(self):
        (self.root/'README.md').write_text('[present](file.txt) ![missing](image.png) [web](https://example.com) [section](#x)')
        (self.root/'file.txt').write_text('ok')
        count,errors=check_links(self.root)
        self.assertEqual(count,2);self.assertEqual(len(errors),1);self.assertIn('image.png',errors[0])

if __name__=='__main__':unittest.main()
