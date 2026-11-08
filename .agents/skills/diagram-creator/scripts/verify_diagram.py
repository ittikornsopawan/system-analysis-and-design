#!/usr/bin/env python3
"""Check editable source/PNG parity and native cell integrity, not visual quality."""
import argparse
import sys
import zlib
from drawio_core import verify_artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='Native .drawio source')
    parser.add_argument('png', help='Editable .drawio.png exported from source')
    parser.add_argument('--require-nested', action='store_true', help='Require a vertex parent containing a child vertex on every page')
    parser.add_argument('--roundtrip', help='PNG re-exported with identical renderer/version/scale/fonts; compare pixel stream')
    parser.add_argument('--max-bytes', type=int, help='Optional delivery size constraint')
    args = parser.parse_args()
    try:
        result = verify_artifact(args.source, args.png, args.require_nested, args.roundtrip, args.max_bytes)
    except (ValueError, OSError, SyntaxError, zlib.error) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    print('PASS editable model/PNG integrity:', result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
