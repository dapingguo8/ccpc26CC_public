#!/usr/bin/env python3
"""Check data formatting without modifying any files.

Default: ../data/*.in and ../data/*.ans, relative to this script.
Rules: UTF-8; LF only; no leading/trailing ASCII spaces; no consecutive
ASCII spaces; no invisible characters (except ASCII space and LF).
Only the final empty segment after an optional trailing LF is allowed:
'1\\n' is valid, '1\\n\\n' is invalid. An empty file is invalid.
Exit codes: 0 = valid, 1 = format violations, 2 = setup/read error.
"""
import argparse
from pathlib import Path
import re
import sys
import unicodedata


def natural_key(path):
    return [int(x) if x.isdigit() else x.lower()
            for x in re.split(r'(\d+)', path.name)]


def check_bytes(raw, limit=20):
    """Return (total violation count, first `limit` diagnostic messages)."""
    messages = []
    count = 0

    def report(line, column, message):
        nonlocal count
        count += 1
        if len(messages) < limit:
            messages.append(f'line {line}, column {column}: {message}')

    try:
        text = raw.decode('utf-8')  # Deliberately retain a BOM for detection.
    except UnicodeDecodeError as exc:
        prefix = raw[:exc.start]
        report(prefix.count(b'\n') + 1,
               len(prefix.rsplit(b'\n', 1)[-1]) + 1,
               f'invalid UTF-8 at byte offset {exc.start}')
        return count, messages
    if not text:
        report(1, 1, 'empty file')
        return count, messages

    lines = text.split('\n')  # Do not normalize CRLF or other separators.
    for index, line in enumerate(lines):
        number = index + 1
        if not line:
            if index != len(lines) - 1:
                report(number, 1, 'empty line before end of file')
            continue
        if line.startswith(' '):
            report(number, 1, 'leading space')
        if line.endswith(' '):
            report(number, len(line), 'trailing space')
        for match in re.finditer(r' {2,}', line):
            report(number, match.start() + 1,
                   f'consecutive spaces (run length {len(match.group())})')
        for column, char in enumerate(line, 1):
            if char == ' ':
                continue
            category = unicodedata.category(char)
            if char == '\r':
                report(number, column, 'CR (U+000D): only LF (\\n) line endings are allowed')
            elif (not char.isprintable() or category.startswith(('C', 'Z'))
                  or category in ('Mn', 'Me') or char == '\u2800'):
                name = unicodedata.name(char, 'unnamed/control character')
                report(number, column, f'invisible/disallowed character U+{ord(char):04X} ({name})')
    return count, messages


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('paths', nargs='*', type=Path,
                        help='files or directories; default: ../data')
    parser.add_argument('--ext', nargs='+', default=['.in', '.ans'],
                        help='directory file extensions, e.g. --ext .in')
    parser.add_argument('--max-errors', type=int, default=20,
                        help='maximum diagnostics printed per file (default: 20)')
    args = parser.parse_args()
    if args.max_errors < 1:
        parser.error('--max-errors must be positive')
    paths = args.paths or [Path(__file__).resolve().parent.parent / 'data']
    extensions = {'.' + ext.lstrip('.') for ext in args.ext}
    files = set()
    for path in paths:
        if path.is_file():
            files.add(path.resolve())
        elif path.is_dir():
            files.update(p.resolve() for p in path.iterdir()
                         if p.is_file() and p.suffix in extensions)
        else:
            print(f'ERROR: path does not exist: {path}')
            return 2
    if not files:
        print('ERROR: no matching files')
        return 2
    failed = errors = read_errors = 0
    for path in sorted(files, key=lambda p: (str(p.parent), natural_key(p))):
        try:
            total, details = check_bytes(path.read_bytes(), args.max_errors)
        except OSError as exc:
            read_errors += 1
            print(f'ERROR {path}: {exc}')
            continue
        errors += total
        if total:
            failed += 1
            print(f'FAIL {path} ({total} violation(s))')
            for detail in details:
                print('  ' + detail)
            if total > len(details):
                print(f'  ... {total - len(details)} further violation(s) omitted')
        else:
            print(f'PASS {path.name}')
    print(f'\nFiles={len(files)}, PASS={len(files)-failed-read_errors}, '
          f'FAIL={failed}, READ_ERROR={read_errors}, violations={errors}')
    return 2 if read_errors else (1 if failed else 0)


if __name__ == '__main__':
    sys.exit(main())
