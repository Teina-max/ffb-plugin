#!/usr/bin/env python3
"""FFB local persistence CLI. Structured inputs are read only from stdin."""
import argparse
import json
import sys

from ffb_local import paths, profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['profile-read', 'profile-save', 'save-draft', 'track-request',
                                            'copy-check', 'request-stats'])
    parser.add_argument('--root')
    parser.add_argument('--request-id')
    parser.add_argument('--source-ref')
    parser.add_argument('--month')
    args = parser.parse_args()
    if args.command != 'copy-check' and not args.root:
        parser.error('--root est requis pour ' + args.command)
    try:
        if args.command == 'copy-check':
            from ffb_local import overlap
            result = overlap.check(paths.decode_json(sys.stdin.read()))
        elif args.command == 'profile-read':
            result = profile.read(args.root)
        elif args.command == 'profile-save':
            result = profile.save(args.root, paths.decode_json(sys.stdin.read()))
        elif args.command == 'request-stats':
            from ffb_local import stats
            result = stats.compute(args.root, args.month)
        elif args.command == 'track-request':
            from ffb_local import tracking
            result = tracking.track(args.root, args.request_id, paths.decode_json(sys.stdin.read()))
        else:
            from ffb_local import records
            result = records.save(args.root, args.request_id, args.source_ref, paths.decode_json(sys.stdin.read()))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print('FFB : lecture ou enregistrement impossible : ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
