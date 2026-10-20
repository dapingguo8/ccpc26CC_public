"""Deterministic ACM-style generator for Carefree Melody.

Standalone (run from the problem directory):
    python3 gen.py --case 7 > data/7.in
    python3 gen.py --case 7 --seed 123 > another.in
    python3 gen.py --all --out-dir data  # regenerate 1..37 .in/.ans

Tuack calls gen(fin, args, cont); cont['case'] selects the data file.
Files 1 and 2 are exact copies of down/1 and down/2 (the samples).
Files 3..37 mix case lengths, k choices, and sequence patterns.
Every file respects T <= 10000 and sum(n) <= 200000.
"""

import argparse
from collections import Counter
from pathlib import Path
import random
import sys

MAX_SUM = 200000
MAX_T = 10000
MAX_VALUE = 1000000000

# Number of cases, minimum n, maximum n for the 35 non-sample files.
# File profiles range from 10,000 tiny cases to one maximum-sized case.
PROFILES = {
    3: (400, 2, 200),
    4: (10000, 2, 15),
    5: (10000, 2, 35),
    6: (2000, 2, 100),
    7: (1000, 100, 200),
    8: (1000, 150, 250),
    9: (250, 200, 900),
    10: (150, 500, 1700),
    11: (50, 2500, 5000),
    12: (20, 6000, 13000),
    13: (5, 20000, 60000),
    14: (8, 10000, 35000),
    15: (2, 80000, 120000),
    16: (3, 50000, 80000),
    17: (1, 200000, 200000),
    18: (1, 200000, 200000),
    19: (10, 15000, 25000),
    20: (500, 2, 500),
    21: (10000, 2, 20),
    22: (7000, 2, 45),
    23: (2500, 10, 120),
    24: (1200, 50, 220),
    25: (400, 200, 700),
    26: (200, 600, 1400),
    27: (100, 1000, 3000),
    28: (40, 3000, 7000),
    29: (16, 8000, 16000),
    30: (8, 18000, 35000),
    31: (4, 35000, 60000),
    32: (2, 90000, 110000),
    33: (1, 200000, 200000),
    34: (1, 200000, 200000),
    35: (1, 200000, 200000),
    36: (10000, 2, 2),
    37: (1, 200000, 200000),
}

# Focused full-size files, in addition to the mixtures in every multi-case file.
SPECIAL_K = {17: '2', 18: 'n', 33: '2', 34: 'n', 35: '3', 36: '2', 37: 'n-1'}
SPECIAL_STYLE = {17: 4, 18: 8, 33: 12, 34: 6, 35: 10, 37: 9}


def lengths(profile, rng):
    count, low, high = PROFILES[profile]
    remaining = MAX_SUM
    for index in range(count):
        left = count - index - 1
        ceiling = min(high, remaining - left * low)
        # Fix the n=2 / k=2 boundary early in every mixed profile.
        n = 2 if index == 0 and low == 2 else rng.randint(low, ceiling)
        remaining -= n
        yield n


def choose_k(n, index, profile, rng):
    special = SPECIAL_K.get(profile)
    if special is not None:
        return {'2': 2, '3': 3, 'n': n, 'n-1': n - 1}[special]
    choices = (
        2, n, max(2, n - 1), min(n, 3),
        max(2, n // 2), max(2, int(n ** 0.5)),
        rng.randint(2, n), rng.randint(2, n),
    )
    return choices[(index + profile) % len(choices)]


def make_sequence(n, k, style, rng):
    phase = rng.randrange(k)
    other = (phase + rng.randint(1, k - 1)) % k
    period = max(1, n // 7)
    values = []
    for index in range(n):
        expected = (phase + index) % k + 1
        alternative = (other + index) % k + 1
        if style == 0:  # Already a perfect repeater.
            value = expected
        elif style == 1:  # One changed value still in [1, k].
            value = alternative if index == n // 2 else expected
        elif style == 2:  # One changed value outside [1, k].
            value = MAX_VALUE if index == n // 2 else expected
        elif style == 3:  # Everything must be changed.
            value = rng.randint(k + 1, MAX_VALUE)
        elif style == 4:  # Frequent changes of the best phase.
            value = alternative if (index // period) % 2 else expected
        elif style == 5:  # Mostly correct, with in-range errors.
            value = alternative if rng.randrange(4) == 0 else expected
        elif style == 6:  # No planted repeater.
            value = rng.randint(1, k)
        elif style == 7:  # Uniform over the full value range.
            value = rng.randint(1, MAX_VALUE)
        elif style == 8:  # Mix of two phases and invalid values.
            roll = rng.randrange(10)
            value = expected if roll < 5 else alternative if roll < 8 else k + 1
        elif style == 9:  # Two phases with near-equal support.
            value = expected if index < n // 2 else alternative
        elif style == 10:  # All values equal (including k=2).
            value = phase + 1
        elif style == 11:  # Boundary values and local corruption.
            value = (1, k, k + 1, MAX_VALUE, expected)[index % 5]
        elif style == 12:  # Only one value can be preserved.
            value = expected if index == n // 2 else k + 1
        elif style == 13:  # Competing phases alternate at each position.
            value = expected if index % 2 == 0 else alternative
        elif style == 14:  # Sparse valid entries, mostly large distractors.
            value = expected if index % 17 == 0 else MAX_VALUE
        else:  # Almost all entries follow the wrong phase.
            value = expected if index % 19 == 0 else alternative
        values.append(value)
    return values


def answer(n, k, values):
    frequencies = Counter((value - index) % k for index, value in enumerate(values, 1) if value <= k)
    return n - max(frequencies.values(), default=0)


def gen(fin, args, cont, seed=0, answers=None):
    """Generate one ACM input file; optional answers receives its outputs."""
    profile = int(cont['case'])
    if profile in (1, 2):
        # The first two numbered data files are precisely the distributed samples.
        sample_dir = Path(__file__).resolve().parent / 'down'
        fin.write((sample_dir / f'{profile}.in').read_text(encoding='ascii'))
        if answers is not None:
            answers.write((sample_dir / f'{profile}.ans').read_text(encoding='ascii'))
        return
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile}; choose 1..37")
    rng = random.Random(20261004 + profile * 1000003 + seed)
    count, _, _ = PROFILES[profile]
    assert 1 <= count <= MAX_T
    fin.write(f"{count}\n")
    total = 0
    for index, n in enumerate(lengths(profile, rng)):
        k = choose_k(n, index, profile, rng)
        style = SPECIAL_STYLE.get(profile, (index + profile) % 16)
        values = make_sequence(n, k, style, rng)
        fin.write(f"{n} {k}\n")
        fin.write(' '.join(map(str, values)) + '\n')
        if answers is not None:
            answers.write(f"{answer(n, k, values)}\n")
        total += n
    assert total <= MAX_SUM


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--case', type=int, choices=range(1, 38))
    group.add_argument('--all', action='store_true')
    parser.add_argument('--seed', type=int, default=0, help='reproducible variation')
    parser.add_argument('--out-dir', type=Path, help='directory for all inputs and answers')
    options = parser.parse_args()
    if options.all:
        if options.out_dir is None or not options.out_dir.is_dir():
            parser.error('--all requires an existing --out-dir directory')
        for profile in range(1, 38):
            with (options.out_dir / f'{profile}.in').open('w', encoding='ascii', newline='\n') as fin:
                with (options.out_dir / f'{profile}.ans').open('w', encoding='ascii', newline='\n') as ans:
                    gen(fin, {}, {'case': profile}, options.seed, ans)
    else:
        if options.out_dir is not None:
            parser.error('--out-dir can only be used with --all')
        gen(sys.stdout, {}, {'case': options.case}, options.seed)


if __name__ == '__main__':
    main()
