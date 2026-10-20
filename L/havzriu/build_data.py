"""Build and verify the 10-point Story data set.

Run: python havzriu/build_data.py [--compiler g++]
All randomness is seeded. Requires Python 3, PyYAML and a C++14 compiler.
Inputs/answers are staged and verified before replacing data/1..10.in/ans.
"""

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
PROBLEM = HERE.parent
SEED = 20261007
DESCRIPTIONS = [
    'Exact copy of the public sample',
    'All binary strings of lengths 1..15',
    'All length-16 binary strings starting with 0',
    'All length-16 binary strings starting with 1',
    'Systematic block/endpoint/parity/zero-run corners and regressions',
    'Maximum N: alternating string, maximum possible answer',
    'Maximum N: all ones, maximum number of blocks',
    'Large structured cases: dominant blocks, thresholds, padding, palindromes',
    'Maximum T and sum N: 100000 cases with large/small transitions',
    'A 700000-character random string and 30 varied medium random cases',
]


def alternating(n, first='1'):
    return (('10' if first == '1' else '01') * ((n + 1) // 2))[:n]


def blocks(weights, gaps, leading=0, trailing=0):
    parts = ['0' * leading]
    for i, weight in enumerate(weights):
        parts.append('10' * (weight - 1) + '1')
        if i < len(weights) - 1:
            gap = gaps[i] if isinstance(gaps, list) else gaps
            assert gap == 0 or gap >= 2
            parts.append('0' * gap)
    parts.append('0' * trailing)
    return ''.join(parts)


def fit_blocks(weights, n=50000, leading=0, trailing=0):
    gaps = [2] * (len(weights) - 1)
    spare = n - len(blocks(weights, gaps, leading, trailing))
    assert spare >= 0 and gaps
    gaps[0] += spare
    return blocks(weights, gaps, leading, trailing)


def corner_cases():
    cases = set()
    for m in range(1, 6):
        for weights in itertools.product(range(1, 5), repeat=m):
            for leading, trailing in itertools.product((0, 1), repeat=2):
                for gaps in (0, 2, [0, 2, 3, 4][:m - 1]):
                    cases.add(blocks(weights, gaps, leading, trailing))
    special = [(1,), (2,), (8,), (21,), (1, 2), (2, 1), (2, 1, 1),
               (1, 3, 1), (3, 1, 1), (1, 1, 3), (2, 2), (1, 2, 1),
               (1, 2, 1, 1), (1, 4, 1), (1, 2, 1, 1, 1, 1)]
    for weights in special:
        for leading, trailing in itertools.product((0, 1, 2, 17), repeat=2):
            for gap in (0, 2, 3, 17):
                cases.add(blocks(weights, gap, leading, trailing))
    for n in range(1, 129):
        cases.update(('0' * n, '1' * n, alternating(n), alternating(n, '0')))
    cases.update(('11011001', '111', '1111', '1011', '1101', '01011',
                  '11010', '11011111', '10011', '01110', '101011'))
    result = sorted(cases)
    random.Random(SEED + 5).shuffle(result)
    return result


def random_bits(rng, n, probability=0.5):
    return ''.join('1' if rng.random() < probability else '0' for _ in range(n))


def make_case(index):
    rng = random.Random(SEED + index)
    if index == 1:
        tokens = (PROBLEM / 'down/1.in').read_text(encoding='ascii').split()
        assert int(tokens[0]) == len(tokens) - 1
        return tokens[1:]
    if index == 2:
        return [format(x, f'0{n}b') for n in range(1, 16) for x in range(1 << n)]
    if index in (3, 4):
        prefix = str(index - 3)
        return [prefix + format(x, '015b') for x in range(1 << 15)]
    if index == 5:
        return corner_cases()
    if index == 6:
        return [alternating(1000000)]
    if index == 7:
        return ['1' * 1000000]
    if index == 8:
        half = random_bits(rng, 25000)
        return [
            '0' * 50000, '1' * 50000,
            '1' * 49999 + '0', '0' + '1' * 49999,
            alternating(50000, '0'), alternating(50000),
            alternating(49999), alternating(50001, '0'),
            blocks([10000], 0, 15000, 15001),
            '0' * 25000 + '1' + '0' * 24999,
            fit_blocks([15000, 2500, 2500]),
            fit_blocks([2500, 15000, 2500]),
            fit_blocks([2500, 2500, 15000]),
            fit_blocks([15000, 2500, 2500], leading=1),
            fit_blocks([2500, 2500, 15000], trailing=1),
            fit_blocks([5000, 10000, 4999]),
            fit_blocks([5000, 10000, 5000]),
            fit_blocks([5000, 10000, 5001]),
            fit_blocks([99] * 201, leading=1, trailing=1),
            half + half[::-1],
        ]
    if index == 9:
        # Three large cases surrounded by tiny cases expose stale per-case state.
        lengths = [6] * 50012 + [5] * (99997 - 50012)
        rng.shuffle(lengths)
        for i in range(0, len(lengths) - 1, 2):
            total = lengths[i] + lengths[i + 1]
            lengths[i] = rng.randint(max(1, total - 11), min(11, total - 1))
            lengths[i + 1] = total - lengths[i]
        small = [random_bits(rng, n) for n in lengths]
        return ([alternating(150000)] + small[:49999] + ['1' * 150001]
                + small[49999:] + ['0' * 150002])
    if index == 10:
        cases = [random_bits(rng, 700000)]
        for i in range(30):
            mode = i % 10
            if mode < 7:
                cases.append(random_bits(rng, 10000,
                                         (0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999)[mode]))
            else:
                flip = (0.001, 0.1, 0.999)[mode - 7]
                bit = rng.randrange(2)
                chars = []
                for _ in range(10000):
                    if rng.random() < flip:
                        bit ^= 1
                    chars.append(str(bit))
                cases.append(''.join(chars))
        return cases
    raise ValueError(index)


def reference(s):
    # Independent segmentation implementation: regex instead of std's scan.
    weights = [part.count('1') for part in re.findall(r'1(?:01)*', s)]
    if not weights:
        return 1
    if len(weights) == 1:
        return 2 * weights[0] - 1 + (s[0] == '0') + (s[-1] == '0')
    total, largest = sum(weights), max(weights)
    k = max(total % 2, 2 * largest - total)
    if k == 0:
        return 1
    left = s[0] == '1' and (2 * largest < total or weights[0] == largest)
    right = s[-1] == '1' and (2 * largest < total or weights[-1] == largest)
    return 2 * k + (not (left or right))


# Exact interval DP, independent of the block formula. A substring reducible
# to zero follows Z -> 0 | 11 | ZZ | 1ZZ1, by the editorial's three local rules.
# The shortest partition into original single characters / Z's is the answer.
INTERVAL_ORACLE = r'''
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        string s; cin >> s;
        int n = (int)s.size();
        if (n > 256) return 2;
        vector<vector<unsigned char>> z(n, vector<unsigned char>(n));
        vector<vector<unsigned char>> pairz(n, vector<unsigned char>(n));
        for (int len = 1; len <= n; ++len) {
            for (int l = 0; l + len <= n; ++l) {
                int r = l + len - 1;
                for (int k = l; k < r; ++k) {
                    if (z[l][k] && z[k+1][r]) { pairz[l][r] = 1; break; }
                }
                z[l][r] = pairz[l][r]
                    || (len == 1 && s[l] == '0')
                    || (len == 2 && s[l] == '1' && s[r] == '1')
                    || (len >= 4 && s[l] == '1' && s[r] == '1' && pairz[l+1][r-1]);
            }
        }
        vector<int> dp(n+1, n+1); dp[0] = 0;
        for (int l = 0; l < n; ++l) {
            dp[l+1] = min(dp[l+1], dp[l]+1);
            for (int r = l; r < n; ++r)
                if (z[l][r]) dp[r+1] = min(dp[r+1], dp[l]+1);
        }
        cout << dp[n] << '\n';
    }
}
'''


def payload(cases):
    return (str(len(cases)) + '\n' + '\n'.join(cases) + '\n').replace('\n', os.linesep).encode('ascii')


def main():
    import yaml
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', default='g++')
    options = parser.parse_args()
    records = []
    with tempfile.TemporaryDirectory(prefix='story-data-') as directory:
        stage = Path(directory)
        (stage / 'interval.cpp').write_text(INTERVAL_ORACLE, encoding='ascii')
        binaries = {}
        for name in ('std', 'brute', 'validator', 'interval'):
            source = stage / 'interval.cpp' if name == 'interval' else HERE / (name + '.cpp')
            exe = stage / (name + ('.exe' if os.name == 'nt' else ''))
            subprocess.run([options.compiler, '-std=c++14', '-O2', '-Wall', '-Wextra',
                            str(source), '-o', str(exe)], check=True)
            binaries[name] = exe
        print('Compiled std, brute, validator, independent interval oracle', flush=True)

        def run(name, data):
            result = subprocess.run([str(binaries[name])], input=data,
                                    capture_output=True, timeout=180)
            assert result.returncode == 0, (name, result.returncode, result.stderr[:2000])
            return list(map(int, result.stdout.split()))

        for index in range(1, 11):
            cases = make_case(index)
            total = sum(map(len, cases))
            assert 1 <= len(cases) <= 100000 and total <= 1000000
            assert all(s and set(s) <= {'0', '1'} for s in cases)
            if index >= 6:
                assert total == 1000000
            data = (PROBLEM / 'down/1.in').read_bytes() if index == 1 else payload(cases)
            # Validate the actual file bytes; normalize only for native testlib EOL.
            native_data = data.replace(b'\r\n', b'\n').replace(b'\n', os.linesep.encode())
            run('validator', native_data)
            begin = time.perf_counter()
            got = run('std', data)
            elapsed = time.perf_counter() - begin
            expected = [reference(s) for s in cases]
            assert got == expected, (index, 'std/reference mismatch')
            verified = ['validator', 'std', 'independent formula']
            if index <= 4:
                print(f'Point {index}: checking exhaustive brute force...', flush=True)
                assert run('brute', data) == expected, (index, 'brute mismatch')
                verified.append('exponential brute')
            if index <= 5:
                assert run('interval', data) == expected, (index, 'interval DP mismatch')
                verified.append('exact interval DP')
            ans = ('\n'.join(map(str, expected)) + '\n').replace('\n', os.linesep).encode('ascii')
            if index == 1:
                sample_ans = (PROBLEM / 'down/1.ans').read_bytes()
                assert list(map(int, sample_ans.split())) == expected
                ans = sample_ans
            (stage / f'{index}.in').write_bytes(data)
            (stage / f'{index}.ans').write_bytes(ans)
            records.append({
                'point': index, 'description': DESCRIPTIONS[index - 1],
                'T': len(cases), 'min_N': min(map(len, cases)), 'max_N': max(map(len, cases)),
                'sum_N': total, 'input_bytes': len(data), 'answer_bytes': len(ans),
                'min_answer': min(expected), 'max_answer': max(expected),
                'std_seconds': round(elapsed, 4), 'verified_by': verified,
                'input_sha256': hashlib.sha256(data).hexdigest(),
                'answer_sha256': hashlib.sha256(ans).hexdigest(),
            })
            print(f'PASS point {index}: T={len(cases)}, Nmax={max(map(len,cases))}, '
                  f'sum N={total}, std={elapsed:.3f}s', flush=True)

        # Preserve all existing files outside the explicitly requested suite.
        for index in range(1, 11):
            for extension in ('in', 'ans'):
                shutil.copyfile(stage / f'{index}.{extension}', PROBLEM / 'data' / f'{index}.{extension}')

    config_path = PROBLEM / 'conf.yaml'
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    config['data'] = [{'cases': list(range(1, 11)), 'score': 100}]
    # Keep the existing hand-written formatting, changing only the data block.
    text = config_path.read_text(encoding='utf-8')
    updated, count = re.subn(r'^data:\n(?:[ \t-].*\n)*',
                             'data:\n- cases: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n  score: 100\n',
                             text, count=1, flags=re.MULTILINE)
    assert count == 1 and yaml.safe_load(updated) == config
    config_path.write_text(updated, encoding='utf-8')

    input_bytes = sum(r['input_bytes'] for r in records)
    answer_bytes = sum(r['answer_bytes'] for r in records)
    manifest = {'seed': SEED, 'points': records, 'input_bytes': input_bytes,
                'answer_bytes': answer_bytes, 'total_bytes': input_bytes + answer_bytes,
                'total_MB': (input_bytes + answer_bytes) / 1000000,
                'total_MiB': (input_bytes + answer_bytes) / 1048576}
    (HERE / 'data_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'points'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
