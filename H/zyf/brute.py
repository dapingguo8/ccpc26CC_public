#!/usr/bin/env python3
"""Exact small-n brute force using a Markov chain and rational elimination.

Usage:
  python brute.py input.in
  python brute.py < input.in
  python brute.py --samples

No potential-function formula is used. All integer partitions of n are
states; transition probabilities are computed by enumerating ordered pairs
of distinct categories. Default size limit: n <= 12.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import sys
import time

MOD = 998244353


def partitions(total, minimum=1):
    if total == 0:
        yield ()
    else:
        for first in range(minimum, total + 1):
            for rest in partitions(total - first, first):
                yield (first,) + rest


def transitions(state):
    denominator = sum(x * y for i, x in enumerate(state)
                      for j, y in enumerate(state) if i != j)
    result = defaultdict(F)
    for i, x in enumerate(state):
        for j, y in enumerate(state):
            if i == j:
                continue
            next_state = list(state)
            next_state[i] -= 1
            next_state[j] += 1
            key = tuple(sorted(value for value in next_state if value))
            result[key] += F(x * y, denominator)
    assert sum(result.values(), F(0)) == 1
    return result


def solve(matrix, rhs):
    """Exact Gaussian elimination with pivoting; inputs are not modified."""
    size = len(rhs)
    rows = [list(row) + [F(value)] for row, value in zip(matrix, rhs)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        if pivot is None:
            raise ValueError('singular Markov-chain system')
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for i in range(column + 1, size):
            if not rows[i][column]:
                continue
            factor = rows[i][column] / rows[column][column]
            rows[i][column] = F(0)
            for j in range(column + 1, size + 1):
                rows[i][j] -= factor * rows[column][j]
    answer = [F(0)] * size
    for i in range(size - 1, -1, -1):
        answer[i] = (rows[i][size] - sum(
            (rows[i][j] * answer[j] for j in range(i + 1, size)), F(0)
        )) / rows[i][i]
    return answer


def brute(n, counts):
    initial = tuple(sorted(x for x in counts if x))
    if initial == (n,):
        return F(0), F(0), F(0), 0
    states = [state for state in partitions(n) if len(state) > 1]
    index = {state: i for i, state in enumerate(states)}
    size = len(states)
    matrix = [[F(int(i == j)) for j in range(size)] for i in range(size)]
    for i, state in enumerate(states):
        for target, probability in transitions(state).items():
            if len(target) > 1:
                matrix[i][index[target]] -= probability
    # E = 1 + Q E; H = 1 + 2 Q E + Q H = 2 E - 1 + Q H.
    expectation = solve(matrix, [F(1)] * size)
    second_moment = solve(matrix, [2 * value - 1 for value in expectation])
    i = index[initial]
    variance = second_moment[i] - expectation[i] ** 2
    assert variance >= 0
    return expectation[i], second_moment[i], variance, size


def evaluate(text, max_n):
    values = list(map(int, text.split()))
    if len(values) < 2:
        raise ValueError('expected n, k and k category sizes')
    n, k = values[:2]
    counts = values[2:]
    if n < 1 or k < 1 or len(counts) != k or any(x < 0 for x in counts) or sum(counts) != n:
        raise ValueError('invalid input: require n >= 1, k >= 1, k nonnegative sizes summing to n')
    if n > max_n:
        raise ValueError(f'n={n} exceeds brute-force limit {max_n}; use --max-n to override')
    started = time.perf_counter()
    mean, second, variance, size = brute(n, counts)
    modular = variance.numerator * pow(variance.denominator, -1, MOD) % MOD
    detail = (f'n={n}, transient states={size}, E[tau]={mean}, '
              f'E[tau^2]={second}, Var[tau]={variance}, '
              f'time={time.perf_counter()-started:.3f}s')
    return modular, detail


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input', nargs='?', type=Path)
    parser.add_argument('--samples', action='store_true', help='check ../down/*.in against *.ans')
    parser.add_argument('--max-n', type=int, default=12)
    args = parser.parse_args()
    if args.samples and args.input:
        parser.error('use an input file or --samples, not both')
    try:
        if args.samples:
            directory = Path(__file__).resolve().parent.parent / 'down'
            inputs = sorted(directory.glob('*.in'))
            if not inputs:
                raise ValueError(f'no sample files found in {directory}')
            failed = 0
            for path in inputs:
                answer, detail = evaluate(path.read_text(encoding='utf-8'), args.max_n)
                expected = int(path.with_suffix('.ans').read_text(encoding='utf-8').strip())
                ok = answer == expected
                failed += not ok
                print(f'{path.name}: {"PASS" if ok else "FAIL"}, got={answer}, expected={expected}')
                print('  ' + detail)
            print(f'Summary: {len(inputs)-failed}/{len(inputs)} passed')
            return int(bool(failed))
        text = args.input.read_text(encoding='utf-8') if args.input else sys.stdin.read()
        answer, detail = evaluate(text, args.max_n)
        print(answer)
        print(detail, file=sys.stderr)
        return 0
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
