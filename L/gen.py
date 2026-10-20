"""Generate Story inputs: T followed by T nonempty binary strings.

Standalone: python gen.py --seed 1 --t 100 --n 20 --sum-n 2000
Also supports tuack's gen(fin, args, cont) interface.
Rebuild the verified official suite: python havzriu/build_data.py
"""

import argparse
import random
import sys


def make_cases(t, n, sum_n, rng):
    if not (1 <= t <= 100000 and 1 <= n <= 1000000
            and t <= sum_n <= 1000000):
        raise ValueError('require 1 <= T <= 100000, 1 <= N <= 1000000, '
                         'T <= sum_N <= 1000000')
    remaining = min(sum_n, t * n)
    for i in range(t):
        left = t - i
        lo = max(1, remaining - (left - 1) * n)
        hi = min(n, remaining - left + 1, max(lo, 2 * (remaining // left)))
        length = rng.randint(lo, hi)
        mode = i % 8
        if mode == 0:
            s = '0' * length
        elif mode == 1:
            s = '1' * length
        elif mode in (2, 3):
            s = (('01' if mode == 2 else '10') * ((length + 1) // 2))[:length]
        elif mode == 4:
            half = ''.join(rng.choice('01') for _ in range(length // 2))
            s = half + ('0' if length % 2 else '') + half[::-1]
        elif mode == 5:
            chars = list(('01' * ((length + 1) // 2))[:length])
            if length > 1:
                pos = rng.randrange(1, length)
                chars[pos] = chars[pos - 1]
            s = ''.join(chars)
        else:
            s = ''.join(rng.choice('01') for _ in range(length))
        remaining -= length
        yield s


def write_input(fin, t, n, sum_n, rng):
    cases = list(make_cases(t, n, sum_n, rng))
    fin.write(str(len(cases)) + '\n')
    fin.write('\n'.join(cases) + '\n')


def gen(fin, args, cont):
    # Keep the official data-point order when invoked by tuack.
    if cont.get('folder') == 'data':
        import importlib.util
        from pathlib import Path
        case = int(cont['case'])
        source = Path(__file__).resolve().parent / 'havzriu' / 'build_data.py'
        spec = importlib.util.spec_from_file_location('story_suite', source)
        suite = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(suite)
        cases = suite.make_case(case)
        fin.write(str(len(cases)) + '\n' + '\n'.join(cases) + '\n')
        return
    # Standalone/random stress tests retain the parameterized generator.
    write_input(fin, args['t'], args['n'], args['sum_n'], random)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--t', type=int, default=100)
    parser.add_argument('--n', type=int, default=20)
    parser.add_argument('--sum-n', type=int, default=2000)
    options = parser.parse_args()
    write_input(sys.stdout, options.t, options.n, options.sum_n,
                random.Random(options.seed))
