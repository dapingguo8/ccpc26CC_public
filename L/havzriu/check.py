"""Compile and check Story after an edit: python havzriu/check.py.

Requires Python 3 and g++ (or --compiler PATH). No third-party Python packages.
Executables are built in a temporary directory and removed on exit.
"""

import argparse
import importlib.util
import io
import itertools
import os
from pathlib import Path
import random
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
PROBLEM = HERE.parent


def encode(text):
    # testlib readEoln uses native line endings in strict validation mode.
    return text.replace('\r\n', '\n').replace('\n', os.linesep).encode('ascii')


def payload(cases):
    return encode(str(len(cases)) + '\n' + '\n'.join(cases) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', default='g++')
    options = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='story-check-') as folder:
        binaries = {}
        for name in ('std', 'brute', 'validator'):
            exe = Path(folder) / (name + ('.exe' if os.name == 'nt' else ''))
            subprocess.run([options.compiler, '-std=c++14', '-O2', '-Wall', '-Wextra',
                            str(HERE / (name + '.cpp')), '-o', str(exe)], check=True)
            binaries[name] = exe

        def run(name, data, valid=True):
            result = subprocess.run([str(binaries[name])], input=data,
                                    capture_output=True, timeout=60)
            assert (result.returncode == 0) == valid, (name, result.returncode,
                                                       result.stderr[:2000])
            return result.stdout.split()

        def compare(cases, expected=None):
            data = payload(cases)
            run('validator', data)
            got = list(map(int, run('std', data)))
            slow = list(map(int, run('brute', data)))
            assert len(got) == len(slow) == len(cases)
            assert got == slow, next((s, a, b) for s, a, b in zip(cases, got, slow) if a != b)
            if expected is not None:
                assert got == expected, next((s, a, b) for s, a, b in zip(cases, got, expected) if a != b)

        # Independent oracle: bottom-up by length, enumerate every interval
        # and check palindrome by reversing it (not center expansion).
        oracle = {}
        cases = []
        for n in range(1, 15):
            for bits in itertools.product('01', repeat=n):
                s = ''.join(bits)
                best = n
                for l in range(n):
                    for r in range(l + 2, n + 1, 2):
                        part = s[l:r]
                        if part == part[::-1]:
                            best = min(best, oracle[s[:l] + '0' + s[r:]])
                oracle[s] = best
                cases.append(s)
        compare(cases, [oracle[s] for s in cases])
        print(f'PASS: {len(cases)} exhaustive strings (N=1..14), std/brute/independent oracle', flush=True)

        rng = random.Random(20261007)
        cases = []
        for i in range(300):
            n = rng.randint(15, 22)
            p = (0.15, 0.5, 0.85)[i % 3]
            cases.append(''.join('1' if rng.random() < p else '0' for _ in range(n)))
        compare(cases)
        print('PASS: 300 random strings (N=15..22)', flush=True)

        for part in ('down', 'pre', 'data'):
            for infile in sorted((PROBLEM / part).glob('*.in')):
                data = encode(infile.read_text(encoding='ascii'))
                run('validator', data)
                expected = infile.with_suffix('.ans').read_bytes().split()
                assert run('std', data) == expected, str(infile)
                # Use brute force only on data files containing small strings.
                if max(map(len, data.split()[1:])) <= 22:
                    assert run('brute', data) == expected, str(infile)
        print('PASS: all checked-in samples, pre-tests and data answers', flush=True)

        invalid = {
            'empty file': '', 'T zero': '0\n', 'T negative': '-1\n',
            'T too large': '100001\n', 'noninteger T': '1.0\n0\n',
            'empty A': '1\n\n', 'nonbinary A': '1\n012\n',
            'old N/A format': '1\n4\n0101\n',
            'old N=1 format': '1\n1\n0\n',
            'missing case': '2\n0\n', 'extra case': '1\n0\n1\n',
            'two strings on one line': '2\n0 1\n',
            'leading space': '1\n 0\n', 'trailing space': '1\n0 \n',
            'extra blank line': '1\n0\n\n', 'missing final EOL': '1\n0',
            'N too large': '1\n' + '0' * 1000001 + '\n',
            'sum N too large': '2\n' + '0' * 500001 + '\n' + '1' * 500000 + '\n',
        }
        for label, text in invalid.items():
            try:
                run('validator', encode(text), valid=False)
            except AssertionError as error:
                raise AssertionError(label) from error
        print(f'PASS: {len(invalid)} malformed/out-of-range inputs rejected', flush=True)

        boundaries = [
            (['0', '1'], [1, 1]),
            (['0' * 1000000], [1]),
            (['1' * 1000000], [1]),
            (['01' * 500000], [1000000]),
            (['1' * 999999, '0'], [2, 1]),
            (['0101010101'] * 100000, [10] * 100000),
        ]
        for cases, expected in boundaries:
            data = payload(cases)
            run('validator', data)
            begin = time.perf_counter()
            got = list(map(int, run('std', data)))
            elapsed = time.perf_counter() - begin
            assert got == expected
            print(f'PASS: boundary T={len(cases)}, sum N={sum(map(len, cases))}, std {elapsed:.3f}s', flush=True)

        spec = importlib.util.spec_from_file_location('story_generator', PROBLEM / 'gen.py')
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        for seed in range(3):
            out = io.StringIO()
            generator.write_input(out, 100, 20, 1500, random.Random(seed))
            tokens = out.getvalue().split()
            cases = tokens[1:]
            assert int(tokens[0]) == len(cases) == 100
            assert max(map(len, cases)) <= 20 and sum(map(len, cases)) == 1500
            compare(cases)
        random.seed(1)
        out = io.StringIO()
        generator.gen(out, {'t': 100000, 'n': 1000000, 'sum_n': 1000000}, {})
        data = encode(out.getvalue())
        run('validator', data)
        assert len(run('std', data)) == 100000
        print('PASS: generator, including the tuack interface at maximum T/sum N', flush=True)


if __name__ == '__main__':
    main()
