"""Dependency-free structural checks for the published site (not browser QA)."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import re

CSS_URL = re.compile(r'url\(\s*[\"\']?([^\"\')]+)[\"\']?\s*\)', re.I)
EXTERNAL_SCHEMES = {'https', 'http', 'mailto', 'tel'}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.errors = []
        self.lang = ''
        self.title = ''
        self.in_title = False
        self.headings = []
        self.main_count = 0
        self.csp = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'html':
            self.lang = values.get('lang', '')
        if tag == 'title':
            self.in_title = True
        if tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.headings.append(tag)
        if tag == 'main':
            self.main_count += 1
        identifier = values.get('id')
        if identifier:
            if identifier in self.ids:
                self.errors.append('duplicate id: ' + identifier)
            self.ids.add(identifier)
        if tag == 'img' and 'alt' not in values:
            self.errors.append('image is missing alt attribute')
        for name, value in attrs:
            if name.lower().startswith('on'):
                self.errors.append('inline event handler: ' + name)
            if name in {'href', 'src', 'poster', 'data-image', 'data-original'} and value is not None:
                self.references.append((value, tag == 'a'))
            if name == 'srcset' and value:
                # This site uses file-based responsive assets, not data URLs.
                for item in value.split(','):
                    if item.strip():
                        self.references.append((item.strip().split()[0], False))
            if name == 'style' and value:
                self.references.extend((url.strip(), False) for url in CSS_URL.findall(value))
        if values.get('data-view'):
            for state in ('before', 'after'):
                self.references.append((f"assets/{values['data-view']}_{state}.webp", False))
        if tag == 'script' and not values.get('src') and values.get('type') not in {'application/ld+json', 'application/json'}:
            self.errors.append('executable inline script; use a local script file')
        if tag == 'meta' and values.get('http-equiv', '').lower() == 'content-security-policy':
            self.csp = values.get('content', '')
        if tag == 'a' and values.get('target') == '_blank':
            if not {'noopener', 'noreferrer'} & set(values.get('rel', '').split()):
                self.errors.append('new-window link needs rel=noopener or noreferrer')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def check_site(root):
    """Return (HTML page count, errors); external URLs are never fetched."""
    root = Path(root).resolve()
    errors, pages = [], {}
    if not root.is_dir():
        return 0, ['site directory is missing']
    for path in sorted(root.rglob('*.html')):
        try:
            path.resolve().relative_to(root)
            page = Page()
            page.feed(path.read_text(encoding='utf-8'))
            page.close()
        except (ValueError, OSError, UnicodeError) as exc:
            errors.append(f'{path.relative_to(root)}: cannot inspect page: {exc}')
            continue
        pages[path.resolve()] = page
        label = path.relative_to(root).as_posix()
        errors.extend(f'{label}: {error}' for error in page.errors)
        if not page.lang:
            errors.append(f'{label}: missing document language')
        if not page.title.strip():
            errors.append(f'{label}: missing page title')
        if page.headings.count('h1') != 1:
            errors.append(f'{label}: expected exactly one h1')
        if page.main_count != 1:
            errors.append(f'{label}: expected exactly one main landmark')
        # CSP is optional for this static site. If supplied, avoid a policy
        # that falsely promises isolation while permitting arbitrary scripts.
        if page.csp is not None:
            directives = {parts[0]: parts[1:] for item in page.csp.split(';') if (parts := item.split())}
            script = directives.get('script-src', directives.get('default-src', []))
            if not script or any(token in script for token in ["'unsafe-inline'", "'unsafe-eval'", '*']):
                errors.append(f'{label}: CSP does not restrict script execution')
    home = root / 'index.html'
    if home not in pages:
        errors.append('missing index.html')
    edges = {path: set() for path in pages}

    def check_reference(source, value, navigation=False):
        try:
            url = urlsplit(value)
        except ValueError:
            errors.append(f'{source.relative_to(root)}: malformed URL: {value}')
            return
        if url.scheme:
            if url.scheme.lower() not in EXTERNAL_SCHEMES:
                errors.append(f'{source.relative_to(root)}: unsupported URL scheme: {value}')
            return
        if url.netloc:
            return
        if url.path.startswith('/'):
            errors.append(f'{source.relative_to(root)}: root-relative URL breaks project Pages: {value}')
            return
        target = (source.parent / unquote(url.path)).resolve() if url.path else source
        try:
            target.relative_to(root)
        except ValueError:
            errors.append(f'{source.relative_to(root)}: path escapes site artifact: {value}')
            return
        if target.is_dir():
            target /= 'index.html'
        if not target.is_file():
            errors.append(f'{source.relative_to(root)}: missing local target: {value}')
            return
        if target.suffix.lower() == '.html' and target not in pages:
            errors.append(f'{source.relative_to(root)}: HTML target was not validated: {value}')
        if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'{source.relative_to(root)}: missing fragment: {value}')
        if navigation and source in edges and target in pages:
            edges[source].add(target)

    for source, page in pages.items():
        for value, navigation in page.references:
            check_reference(source, value, navigation)
    for source in sorted(root.rglob('*.css')):
        try:
            source.resolve().relative_to(root)
            css = source.read_text(encoding='utf-8')
        except (ValueError, OSError, UnicodeError):
            errors.append(f'{source.relative_to(root)}: cannot inspect stylesheet')
            continue
        for value in CSS_URL.findall(css):
            check_reference(source, value.strip())
    reached, pending = set(), [home]
    while pending:
        path = pending.pop()
        if path not in reached:
            reached.add(path)
            pending.extend(edges.get(path, ()))
    for path in pages.keys() - reached:
        errors.append(f'{path.relative_to(root)}: page is not reachable from index.html')
    english = root / 'en.html'
    if english in pages and home in pages:
        ja, en = pages[home], pages[english]
        if not ja.lang.startswith('ja') or not en.lang.startswith('en'):
            errors.append('locale pages must declare ja and en respectively')
        if ja.ids != en.ids or ja.headings != en.headings:
            errors.append('Japanese/English anchor or heading structure differs')
        if english not in edges[home] or home not in edges[english]:
            errors.append('locale pages need reciprocal language navigation')
    return len(pages), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1] / 'site')
    args = parser.parse_args()
    count, errors = check_site(args.root)
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print(f'PASS: {count} HTML pages; local assets, anchors, navigation and structural checks')


if __name__ == '__main__':
    main()
