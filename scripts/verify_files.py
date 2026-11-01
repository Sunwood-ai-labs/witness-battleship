"""Verify public distribution size and SHA-256, including under python -O."""
from pathlib import Path
import argparse
from distribution import ValidationError, verify_manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        count = verify_manifest(args.root)
    except ValidationError as exc:
        parser.exit(1, 'FAIL: ' + str(exc) + '\n')
    print('PASS:', count, 'files')

if __name__ == '__main__':
    main()
