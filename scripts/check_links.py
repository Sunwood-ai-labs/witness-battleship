"""Check local Markdown/image links without network access."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import argparse

LINK = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)|(?:src|href)=[\"\x27]([^\"\x27]+)[\"\x27]')

def check_links(root):
    root = Path(root).resolve()
    checked, errors = 0, []
    for source in sorted(root.rglob('*.md')):
        if any(part in {'.git', '.agents', 'node_modules', '.venv'} for part in source.parts):
            continue
        for match in LINK.finditer(source.read_text(encoding='utf-8')):
            value = (match.group(1) or match.group(2)).split()[0].strip('<>')
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (source.parent / unquote(url.path)).resolve()
            checked += 1
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f'{source.relative_to(root)}: path escapes repository: {value}')
                continue
            if not target.exists():
                errors.append(f'{source.relative_to(root)}: missing target: {value}')
    return checked, errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    count, errors = check_links(args.root)
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print('PASS:', count, 'local Markdown/image links (external URLs and anchors not checked)')

if __name__ == '__main__':
    main()
