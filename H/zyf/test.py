#!/usr/bin/env python3
"""Compile sol.cpp and check ../data/*.in against matching .ans files.

Usage: python test.py [--timeout 1.0] [--io auto|file|stdio] [--compiler g++]
Only the Python standard library and a C++ compiler are required.
Each case runs in a fresh temporary directory; local zyf.in/out are untouched.
Exit codes: 0 = all passed, 1 = test failure, 2 = setup/compilation failure.
This is a local correctness/time check, not a memory-limit sandbox.
"""
import argparse
import os
from collections import Counter
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


def natural_key(path):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', path.name)]


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', type=Path, default=base / 'sol.cpp')
    parser.add_argument('--data', type=Path, default=base.parent / 'data')
    parser.add_argument('--compiler', default='g++')
    parser.add_argument('--timeout', type=float, default=1.0,
                        help='wall-clock seconds per case (default: 1.0)')
    parser.add_argument('--io', choices=['auto', 'file', 'stdio'], default='auto',
                        help='file uses zyf.in/out; auto detects zyf.out after running')
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    source, data = args.source.resolve(), args.data.resolve()
    if not source.is_file() or not data.is_dir():
        print(f'ERROR: missing source or data directory: {source}, {data}')
        return 2
    cases = sorted(data.glob('*.in'), key=natural_key)
    if not cases:
        print(f'ERROR: no .in files in {data}')
        return 2
    missing = [p.with_suffix('.ans') for p in cases if not p.with_suffix('.ans').is_file()]
    if missing:
        print('ERROR: missing answer files:\n' + '\n'.join(map(str, missing)))
        return 2

    counts = Counter()
    with tempfile.TemporaryDirectory(prefix='knifedge-test-', ignore_cleanup_errors=True) as temporary:
        root = Path(temporary)
        executable = root / 'sol.exe'
        command = [args.compiler, '-O2', '-std=c++14', str(source), '-o', str(executable)]
        if os.name == 'nt':
            # Route CRT assertions to stderr instead of an interactive dialog.
            helper = root / 'no_assert_dialog.cpp'
            helper.write_text('#include <stdlib.h>\n'
                              'struct Setup { Setup() { _set_error_mode(2); } };\n'
                              'static Setup setup;\n', encoding='utf-8')
            command.append(str(helper))
            import ctypes
            ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x0002 | 0x8000)
        print('Compile:', subprocess.list2cmdline(command), flush=True)
        try:
            compiled = subprocess.run(command, capture_output=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f'COMPILE ERROR: {exc}')
            return 2
        if compiled.stdout:
            print(compiled.stdout.decode(errors='replace'))
        if compiled.stderr:
            print(compiled.stderr.decode(errors='replace'))
        if compiled.returncode:
            print(f'COMPILE ERROR: exit code {compiled.returncode}')
            return 2
        print(f'Data: {data}\nCases: {len(cases)}; timeout: {args.timeout:g}s; IO: {args.io}')
        for index, input_path in enumerate(cases, 1):
            work = root / f'case-{index}'
            work.mkdir()
            if args.io != 'stdio':
                shutil.copyfile(input_path, work / 'zyf.in')
            expected = input_path.with_suffix('.ans').read_bytes().split()
            stdout_path, stderr_path = work / 'stdout.txt', work / 'stderr.txt'
            detail = ''
            started = time.perf_counter()
            try:
                with input_path.open('rb') as stdin, stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
                    result = subprocess.run([str(executable)], cwd=work, stdin=stdin,
                                            stdout=stdout, stderr=stderr, timeout=args.timeout)
                elapsed = time.perf_counter() - started
                if result.returncode:
                    status = 'RE'
                    detail = f'exit code {result.returncode}'
                    with stderr_path.open('rb') as stream:
                        error = stream.read(1000).decode(errors='replace').strip()
                    if error:
                        detail += '\n    ' + error.replace('\n', '\n    ')
                else:
                    file_output = work / 'zyf.out'
                    output = (file_output if args.io == 'file' or
                              (args.io == 'auto' and file_output.exists()) else stdout_path)
                    actual = output.read_bytes().split() if output.exists() else []
                    status = 'PASS' if actual == expected else 'WA'
                    if status == 'WA':
                        detail = (f'expected: {b" ".join(expected)[:200].decode(errors="replace")}\n'
                                  f'    actual:   {b" ".join(actual)[:200].decode(errors="replace") or "<empty>"}')
            except subprocess.TimeoutExpired:
                elapsed = time.perf_counter() - started
                status, detail = 'TLE', f'exceeded {args.timeout:g}s'
                with stderr_path.open('rb') as stream:
                    error = stream.read(2000).decode(errors='replace').strip()
                if 'assertion' in error.lower() or 'assert failed' in error.lower():
                    status = 'RE'
                    detail = error + '\n    (terminated after Windows assertion/abort wait)'
                elif error:
                    detail += '\n    stderr: ' + error
            except OSError as exc:
                elapsed = time.perf_counter() - started
                status, detail = 'ERROR', str(exc)
            counts[status] += 1
            print(f'[{index:2}/{len(cases)}] {input_path.name:12} {status:5} {elapsed:.3f}s', flush=True)
            if detail:
                print('    ' + detail, flush=True)
    print('\nSummary: ' + ', '.join(f'{key}={value}' for key, value in counts.items()))
    print('Note: local wall-clock timing; memory usage is not checked.')
    return 0 if counts['PASS'] == len(cases) else 1


if __name__ == '__main__':
    sys.exit(main())



