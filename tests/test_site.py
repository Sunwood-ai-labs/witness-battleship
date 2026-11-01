"""Synthetic structural-site fixtures; no network or browser dependencies."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_site import check_site


def document(body='', lang='ja'):
    return f'<!doctype html><html lang="{lang}"><head><title>WITNESS</title></head><body><main id="main"><h1>WITNESS</h1>{body}</main></body></html>'


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('index.html', document())

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding='utf-8')

    def errors(self):
        return '\n'.join(check_site(self.root)[1])

    def test_valid_site_and_external_links(self):
        self.write('index.html', document('<a href="#main">Top</a><a href="https://example.com/no-check">External</a><img src="assets/x.svg" alt="Diagram"><link rel="stylesheet" href="assets/site.css">'))
        self.write('assets/x.svg', '<svg/>')
        self.write('assets/site.css', 'body { background: url(x.svg); }')
        self.assertEqual(check_site(self.root), (1, []))

    def test_missing_asset_and_fragment(self):
        self.write('index.html', document('<a href="#missing">Missing</a><img src="no.png" alt="Missing">'))
        self.assertIn('missing fragment', self.errors())
        self.assertIn('missing local target', self.errors())

    def test_escape_and_project_absolute_url(self):
        self.write('index.html', document('<a href="../outside">Outside</a><a href="/assets/x">Absolute</a>'))
        self.assertIn('escapes site artifact', self.errors())
        self.assertIn('root-relative URL', self.errors())

    def test_encoded_escape(self):
        self.write('index.html', document('<a href="%2e%2e/outside">Outside</a>'))
        self.assertIn('escapes site artifact', self.errors())

    def test_unsafe_scheme_and_handler(self):
        self.write('index.html', document('<a href="javascript:alert(1)" onclick="alert(1)">Bad</a>'))
        self.assertIn('unsupported URL scheme', self.errors())
        self.assertIn('inline event handler', self.errors())

    def test_document_basics(self):
        self.write('index.html', '<html><img src="x"><div id="x"></div><div id="x"></div></html>')
        for expected in ['missing document language', 'missing page title', 'one h1', 'one main', 'missing alt', 'duplicate id']:
            self.assertIn(expected, self.errors())

    def test_orphan_page(self):
        self.write('hidden.html', document())
        self.assertIn('not reachable', self.errors())

    def test_bilingual_parity(self):
        self.write('index.html', document('<a href="en.html">English</a>'))
        self.write('en.html', document('<a href="index.html">日本語</a>', 'en'))
        self.assertEqual(check_site(self.root), (2, []))
        self.write('en.html', document('<a href="index.html">日本語</a><h2 id="extra">Extra</h2>', 'en'))
        self.assertIn('structure differs', self.errors())

    def test_locale_switch_must_be_reciprocal(self):
        self.write('index.html', document('<a href="en.html">English</a>'))
        self.write('en.html', document('', 'en'))
        self.assertIn('reciprocal language navigation', self.errors())

    def test_css_missing_target(self):
        self.write('style.css', 'body {background: url("missing.png")}')
        self.assertIn('missing local target', self.errors())

    def test_srcset_assets(self):
        self.write('index.html', document('<img srcset="small.webp 1x, large.webp 2x" alt="View">'))
        self.write('small.webp', 'fixture')
        self.assertIn('large.webp', self.errors())

    def test_interactive_asset_references(self):
        self.write('index.html', document('<button data-view="bay0" data-image="assets/detail.webp">View</button>'))
        errors = self.errors()
        for filename in ['bay0_before.webp', 'bay0_after.webp', 'detail.webp']:
            self.assertIn(filename, errors)

    def test_script_and_optional_csp(self):
        self.write('index.html', document('<script>alert(1)</script><meta http-equiv="Content-Security-Policy" content="script-src *">'))
        self.assertIn('executable inline script', self.errors())
        self.assertIn('CSP does not restrict', self.errors())

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            asset = Path(outside) / 'x.svg'
            asset.write_text('<svg/>')
            try:
                (self.root / 'x.svg').symlink_to(asset)
            except (OSError, NotImplementedError):
                self.skipTest('symlinks unavailable')
            self.write('index.html', document('<img src="x.svg" alt="Diagram">'))
            self.assertIn('escapes site artifact', self.errors())

    def test_missing_site(self):
        count, errors = check_site(self.root / 'missing')
        self.assertEqual(count, 0)
        self.assertTrue(errors)


if __name__ == '__main__':
    unittest.main()
