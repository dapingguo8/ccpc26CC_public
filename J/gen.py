"""Standalone, deterministic generator for the 29 official Bitwise AND files.

Input: positive T, then n m k and m triples x y z (one-based endpoints).
Bounds: 1 <= n <= 200000, 0 <= m <= 200000, 1 <= k <= 30;
sum_n,sum_m <= 500000 per file. T has no independent upper bound:
n >= 1 and sum_n <= MAX_SUM_N imply T <= MAX_SUM_N (500000).
There is no legacy c. Answers are minimum sums or -1.

    python3 gen.py --list
    python3 gen.py --case 7 --seed 123 --answers answer.txt > input.txt
    python3 gen.py --all --out-dir data
    python3 gen.py --custom --n 100 --m 300 --k 12 --tests 10 \
        --topology star --mask sparse --unsatisfiable --answers answer.txt

--all writes exactly 1..29.in/.ans into an EXISTING directory; optionally
use --start 21 --end 29 to regenerate only that inclusive range. Unexpected
files are never deleted. Samples 1 and 2 are read and checked from down at
runtime, never embedded or edited. --case1 through --case29 are aliases for
--case N. Custom topologies may repeat edges and include loops; in invalid
tests the topology describes padding around a reserved, certified
contradiction, not the entire graph. Only one test is materialized at a time,
including the 500000-test profile with pooled micro-loop specifications.
Tuack may call gen(fin, args, cont, seed=0, answers=None); args is unused
for official profiles, and cont['case'] selects the file.
"""

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import random
import re
import sys

MAX_N = 200000
MAX_M = 200000
MAX_K = 30
# Since every test has n >= 1, MAX_SUM_N is also the derived cap on T.
MAX_SUM_N = 500000
MAX_SUM_M = 500000
OFFICIAL_COUNT = 29
_LEGACY_COUNT = 80
WRITE_CHUNK = 8192
TOPOLOGIES = ('star', 'path', 'tree', 'cycle', 'disconnected', 'random',
              'loops', 'isolated', 'matching')
MASKS = ('zero', 'ones', 'high', 'sparse', 'dense', 'random',
         'alternating', 'blocks', 'stairs', 'distinct')
ORDERS = ('natural', 'shuffle', 'reverse', 'late')
GADGET_LIMITS = {
    'duplicate': (1, 2),
    'loop': (2, 2),
    'path': (4, 3),
    'triangle': (3, 3),
    'disjoint': (4, 3),
}


@dataclass(frozen=True)
class TestSpec:
    n: int
    m: int
    k: int
    topology: str = 'random'
    mask: str = 'random'
    satisfiable: bool = True
    gadget: str = 'auto'
    order: str = 'shuffle'
    relabel: bool = True
    mixed_loops: bool = False
    active: int = 0
    fixture: str = ''
    gadget_bit: int = field(default=-1, repr=False)

    def __post_init__(self):
        if self.fixture == 'late_or_growth':
            # This fixed fixture is contradictory even with default arguments.
            object.__setattr__(self, 'satisfiable', False)


@dataclass(frozen=True)
class Profile:
    description: str
    tests: tuple = ()
    sample: bool = False


@dataclass
class TestCase:
    n: int
    k: int
    edges: list
    satisfiable: bool
    result: int

    @property
    def m(self):
        return len(self.edges)


def _build_profiles():
    s = TestSpec
    profiles = {
        1: Profile('Exact down/1 sample, loaded at runtime', sample=True),
        2: Profile('Exact down/2 sample, loaded at runtime', sample=True),
        3: Profile('n=1, m=0/1, zero/one/bit 29 self-loops', (
            s(1, 0, 1, mask='zero'), s(1, 1, 1, 'loops', 'zero'),
            s(1, 1, 1, 'loops', 'ones'), s(1, 1, 30, 'loops', 'high'))),
        4: Profile('All zero, duplicate self-loops and disconnected vertices', (
            s(3, 8, 1, fixture='zero_duplicates'),
            s(64, 192, 30, 'loops', 'zero'),
            s(200, 500, 7, 'disconnected', 'zero', mixed_loops=True))),
        5: Profile('Bit 29 on pairs, cycles and random edges', (
            s(2, 1, 30, 'star', 'high'), s(17, 17, 30, 'cycle', 'high'),
            s(101, 303, 30, 'random', 'high', mixed_loops=True))),
        6: Profile('Empty graph, isolated n endpoint, sparse incident vertices', (
            s(9, 0, 30, mask='high', relabel=False),
            s(101, 1, 30, fixture='last_endpoint', relabel=False),
            s(1000, 3, 4, fixture='isolated_endpoint', relabel=False))),
        7: Profile('Bitwise OR is not numeric max: disjoint incident bits', (
            s(3, 2, 2, fixture='or_star'), s(4, 3, 3, fixture='or_star'),
            s(5, 4, 4, fixture='or_star'))),
        8: Profile('64-bit answer: 50000 fully forced 30-bit values', (
            s(50000, 50000, 30, 'loops', 'ones'),)),
        9: Profile('Hidden witness sum differs from the minimum; mixed masks', (
            s(6, 0, 30, mask='ones'), s(8, 3, 30, 'star', 'high'),
            s(17, 17, 6, 'cycle', 'alternating'),
            s(30, 45, 10, 'disconnected', 'random', mixed_loops=True))),
        10: Profile('k=1/30, dense labels, staircase bits and sparse matching', (
            s(2, 1, 1, 'star', 'ones'), s(16, 48, 30, 'tree', 'dense'),
            s(127, 254, 30, 'path', 'stairs', mixed_loops=True),
            s(129, 129, 5, 'matching', 'sparse'))),
    }
    gadget_names = tuple(GADGET_LIMITS)
    for p in range(11, 19):
        tests = []
        for i in range(10):
            k = 1 + (p + i) % 5
            if i % 2 == 0:
                tests.append(s(1 + (3 * p + 5 * i) % 9,
                               0 if i == 0 else (p + 7 * i) % 25, k,
                               TOPOLOGIES[(p + i) % len(TOPOLOGIES)],
                               MASKS[(p + i) % len(MASKS)], mixed_loops=True))
            else:
                gadget = gadget_names[((p + i) // 2) % len(gadget_names)]
                low_n, low_m = GADGET_LIMITS[gadget]
                tests.append(s(low_n + (p + i) % 3,
                               low_m + (3 * p + i) % 12, k,
                               TOPOLOGIES[(p + i) % len(TOPOLOGIES)],
                               MASKS[(p + 2 * i) % len(MASKS)], False, gadget,
                               ORDERS[(p + i) % len(ORDERS)]))
        if p == 11:
            tests[1] = s(1, 2, 1, 'loops', 'zero', False, 'duplicate')
        profiles[p] = Profile(
            'Ten tiny independent low-k tests, five valid and five certified invalid',
            tuple(tests))
    valid_topologies = ('star', 'path', 'tree', 'cycle', 'disconnected',
                        'random', 'matching', 'loops')
    for p, topology in enumerate(valid_topologies, 19):
        tests = []
        for i, mask in enumerate(('sparse', 'dense', 'alternating', 'random')):
            n = 1200 + (p - 19) * 700 + i * 137
            if i == 0:
                m = n // 2 if topology == 'matching' else n if topology in (
                    'cycle', 'loops') else n - 1
            else:
                m = 2 * n + 31 * i
            tests.append(s(n, m, 1 if i == 0 and p % 2 else 30 - i,
                           topology, mask, mixed_loops=i >= 2))
        profiles[p] = Profile(
            f'Valid {topology}: sparse/dense/mixed masks and optional loops', tuple(tests))
    invalid_gadgets = ('duplicate', 'loop', 'triangle', 'disjoint',
                       'path', 'duplicate', 'triangle', 'disjoint')
    for p, gadget in enumerate(invalid_gadgets, 27):
        n = 4000 + (p - 27) * 1100
        secondary = 211 + (p - 27) * 97
        tiny = 73 + (p - 27) * 31
        order = 'late' if p in (31, 34) else ORDERS[(p - 27) % 3]
        tests = (
            s(n, 3 * n + 17 + (p - 27) * 71, 30 - p % 3,
              valid_topologies[(p - 27) % 8], 'dense', False, gadget, order),
            s(secondary, 3 * secondary, 1 + p % 12,
              valid_topologies[(p - 26) % 8], 'sparse', mixed_loops=True),
            s(tiny, 4 * tiny, 1 + p % 5, 'random', 'alternating', False,
              gadget_names[(p + 1) % 5], 'reverse' if p % 2 else 'late'),
        )
        profiles[p] = Profile(
            f'Certified {gadget} contradictions, {order} order, valid secondary test', tests)
    profiles.update({
        35: Profile('Maximum n: huge valid dense star', (
            s(MAX_N, MAX_N - 1, 30, 'star', 'dense'),)),
        36: Profile('Maximum n: valid long path, staircase bit propagation trap', (
            s(MAX_N, MAX_N - 1, 30, 'path', 'stairs'),)),
        37: Profile('Maximum n/m: all fully forced loops, 64-bit answer', (
            s(MAX_N, MAX_M, 30, 'loops', 'ones'),)),
        38: Profile('Maximum n/m: random dense graph with last-edge triangle contradiction', (
            s(MAX_N, MAX_M, 30, 'random', 'dense', False, 'triangle', 'late'),)),
        39: Profile('Maximum n/m: high-bit edges on eight vertices, mostly isolated', (
            s(MAX_N, MAX_M, 30, 'isolated', 'high', active=8, mixed_loops=True),)),
        40: Profile('Maximum n/m: high-bit star plus late disjoint-forcing contradiction', (
            s(MAX_N, MAX_M, 30, 'star', 'high', False, 'disjoint', 'late'),)),
    })
    top41 = ('star', 'path', 'tree', 'cycle', 'loops', 'random',
             'disconnected', 'isolated', 'matching', 'random')
    masks41 = ('dense', 'high', 'random', 'sparse', 'ones', 'alternating',
               'dense', 'high', 'sparse', 'distinct')
    profiles[41] = Profile('Ten n=m=50000 tests, alternating valid/invalid and k', tuple(
        s(50000, 50000, (30, 1, 29, 2, 28, 3, 27, 4, 26, 5)[i],
          top41[i], masks41[i], i % 2 == 0, 'auto' if i % 2 == 0 else gadget_names[i // 2],
          'shuffle' if i % 2 == 0 else 'reverse' if i == 3 else 'late',
          mixed_loops=i in (5, 6, 9), active=12 if i == 7 else 0)
        for i in range(10)))
    top42 = ('loops', 'path', 'star', 'random', 'isolated', 'random',
             'tree', 'cycle', 'disconnected', 'random')
    masks42 = ('high', 'high', 'distinct', 'dense', 'sparse', 'random',
               'alternating', 'dense', 'zero', 'dense')
    profiles[42] = Profile('Ten n=m=50000 tests: high bits, dense labels, zero and isolation', tuple(
        s(50000, 50000, (30, 1, 30, 2, 30, 3, 30, 4, 30, 5)[i],
          top42[i], masks42[i], i % 3 != 1,
          'auto' if i % 3 != 1 else ('duplicate', 'loop', 'triangle')[i // 3],
          'late' if i % 3 == 1 else 'shuffle', mixed_loops=i in (3, 5, 9),
          active=6 if i == 4 else 0)
        for i in range(10)))
    sizes = ((1, 0), (200000, 200000), (2, 2), (100000, 0), (99999, 99999),
             (4, 3), (31, 90), (99835, 99656), (1, 100000), (127, 250))
    palettes = (
        (1, 30, 2, 29, 17, 1, 5, 30, 3, 12),
        (30, 1, 30, 2, 30, 3, 29, 4, 30, 5),
        (2, 29, 1, 30, 5, 30, 1, 29, 2, 30),
        (29, 2, 30, 1, 30, 5, 30, 1, 29, 2),
    )
    for p in range(43, 43 + len(palettes)):
        tests = []
        for i, (n, m) in enumerate(sizes):
            invalid = i in (1, 2, 5, 8) or i == 7 and p % 2 == 0 or i == 9 and p == 43 + len(palettes) - 1
            gadget = {1: 'triangle', 2: 'duplicate', 5: 'path',
                      7: 'disjoint', 8: 'duplicate', 9: 'loop'}.get(i, 'auto')
            tests.append(s(n, m, palettes[p - 43][i],
                           valid_topologies[(p + i) % 8],
                           MASKS[(p + 3 * i) % len(MASKS)], not invalid,
                           gadget if invalid else 'auto',
                           'natural' if i == 1 else 'late' if i == 7 else
                           'reverse' if i in (2, 5, 6, 9) else 'shuffle',
                           mixed_loops=i in (4, 6, 9)))
        profiles[p] = Profile(
            'Ten alternating sizes/k: empty, early failure with unread padding, '
            'later tests, late gadgets and reversed endpoints', tuple(tests))
    large_sizes = ((200000, 200000), (200000, 200000), (100000, 100000))
    valid_variants = (
        ('high', ('star', 'path', 'loops'), (30, 29, 30), 'natural'),
        ('zero', ('random', 'disconnected', 'loops'), (30, 1, 29), 'shuffle'),
        ('ones', ('loops', 'matching', 'cycle'), (30, 29, 30), 'reverse'),
        ('alternating', ('path', 'matching', 'star'), (30, 29, 28), 'natural'),
        ('random', ('random', 'tree', 'cycle'), (30, 29, 30), 'shuffle'),
        ('sparse', ('matching', 'disconnected', 'isolated'), (30, 29, 27), 'reverse'),
        ('dense', ('tree', 'random', 'star'), (30, 29, 28), 'shuffle'),
        ('blocks', ('path', 'cycle', 'disconnected'), (30, 29, 30), 'natural'),
        ('stairs', ('path', 'tree', 'cycle'), (30, 29, 28), 'reverse'),
        ('distinct', ('random', 'star', 'matching'), (30, 29, 30), 'shuffle'),
    )
    for p, (mask, topologies, ks, order) in enumerate(valid_variants, 47):
        tests = tuple(s(n, m, ks[i], topologies[i], mask, order=order,
                        mixed_loops=p in (51, 53, 56) and i == 1,
                        active=8 if topologies[i] == 'isolated' else 0)
                      for i, (n, m) in enumerate(large_sizes))
        profiles[p] = Profile(
            f'Three large valid {mask} tests: {"/".join(topologies)}, '
            f'k={"/".join(map(str, ks))}, {order} order', tests)
    invalid_variants = (
        ('duplicate', 'star', 'dense', 'late'),
        ('loop', 'loops', 'high', 'reverse'),
        ('path', 'path', 'stairs', 'natural'),
        ('triangle', 'random', 'random', 'shuffle'),
        ('disjoint', 'disconnected', 'alternating', 'late'),
        ('duplicate', 'matching', 'sparse', 'reverse'),
        ('loop', 'tree', 'distinct', 'natural'),
        ('path', 'cycle', 'blocks', 'late'),
        ('triangle', 'isolated', 'high', 'reverse'),
        ('disjoint', 'random', 'dense', 'shuffle'),
    )
    for p, (gadget, topology, mask, order) in enumerate(invalid_variants, 57):
        tests = (
            s(200000, 200000, 30, topology, mask, False, gadget, order,
              active=8 if topology == 'isolated' else 0, gadget_bit=29),
            s(200000, 200000, 29, valid_topologies[(p - 57) % 8],
              MASKS[(p - 55) % len(MASKS)], mixed_loops=p % 2 == 0),
            s(100000, 100000, 30, topology, mask, False, gadget,
              'late' if order != 'late' else 'reverse',
              active=8 if topology == 'isolated' else 0, gadget_bit=29),
        )
        profiles[p] = Profile(
            f'Three large tests: two bit-29 {gadget} contradictions on {topology} '
            f'({order}/{tests[2].order}), one valid secondary', tests)
    ten_variants = (
        ('loops', 'ones', ()),
        ('matching', 'alternating', ()),
        ('path', 'stairs', (1, 3, 5, 7, 9)),
        ('tree', 'dense', (0, 2, 4, 6, 8)),
        ('cycle', 'blocks', (2, 5, 8)),
        ('disconnected', 'sparse', (1, 4, 7)),
        ('random', 'distinct', (0, 3, 6, 9)),
        ('isolated', 'high', (1, 3, 5, 7, 9)),
    )
    ten_ks = (1, 30, 2, 29, 3, 28, 4, 27, 5, 26)
    for p, (topology, mask, invalid_indices) in enumerate(ten_variants, 67):
        tests = []
        for i, k in enumerate(ten_ks):
            n = 49999 if p == 68 and i % 2 == 0 else 50001 if p == 68 else 50000
            invalid = i in invalid_indices
            tests.append(s(n, 50000, k, topology, mask, not invalid,
                           gadget_names[i // 2 % 5] if invalid else 'auto',
                           ORDERS[(p + i) % len(ORDERS)],
                           mixed_loops=p in (70, 72, 73) and i % 3 == 0,
                           active=8 if topology == 'isolated' else 0,
                           gadget_bit=k - 1 if invalid else -1))
        profiles[p] = Profile(
            f'Ten large {topology}/{mask} tests, alternating k=1/30/2/29/.../5/26, '
            f'{len(invalid_indices)} highest-bit contradictions'
            + ('; odd n=49999/50001 fixed matchings' if p == 68 else ''), tuple(tests))
    profiles.update({
        75: Profile('Full-mask forcing before n-max empty graph; dense path and repeated high loop', (
            s(200000, 200000, 30, 'loops', 'ones', order='natural', relabel=False),
            s(200000, 0, 1, mask='zero', relabel=False),
            s(99999, 200000, 29, 'path', 'dense', order='reverse'),
            s(1, 100000, 30, 'loops', 'high'))),
        76: Profile('n=1/m-max repeated valid and conflicting loops, then n-max zero loops', (
            s(1, 200000, 30, 'loops', 'ones', order='natural'),
            s(1, 200000, 30, 'loops', 'high', False, 'duplicate', 'late', gadget_bit=29),
            s(200000, 100000, 1, 'loops', 'zero'))),
        77: Profile('n=2/m-max reversed valid pairs and conflicting duplicates, then dense matching', (
            s(2, 200000, 30, 'matching', 'high', order='reverse', relabel=False),
            s(2, 200000, 29, 'matching', 'dense', False, 'duplicate', 'reverse',
              relabel=False, gadget_bit=28),
            s(200000, 100000, 30, 'matching', 'dense', order='reverse'))),
        78: Profile('Three mostly-isolated active-eight tests: valid high/dense, late bit-29 triangle', (
            s(200000, 200000, 30, 'isolated', 'high', active=8, mixed_loops=True),
            s(200000, 200000, 30, 'isolated', 'dense', active=8, order='reverse'),
            s(100000, 100000, 30, 'isolated', 'high', False, 'triangle', 'late',
              active=5, gadget_bit=29))),
        79: Profile('Early triangle failure leaves 199997 edges unread; forcing, empty, reversed follow-ups', (
            s(200000, 200000, 30, 'random', 'dense', False, 'triangle', 'natural',
              relabel=False, gadget_bit=29),
            s(100000, 100000, 30, 'loops', 'ones', order='natural'),
            s(99999, 0, 1, mask='zero', relabel=False),
            s(100000, 100000, 29, 'path', 'stairs', order='reverse'),
            s(1, 100000, 30, 'loops', 'high'))),
        80: Profile('Three 64-bit sums: every vertex fully forced to full 30/29/30-bit masks', (
            s(200000, 200000, 30, 'loops', 'ones', order='natural', relabel=False),
            s(200000, 200000, 29, 'loops', 'ones', order='reverse'),
            s(100000, 100000, 30, 'loops', 'ones', order='shuffle'))),
    })
    assert set(profiles) == set(range(1, _LEGACY_COUNT + 1))
    for profile in profiles.values():
        if not profile.sample:
            validate_budget(profile.tests)
            for spec in profile.tests:
                validate_spec(spec)
    return profiles


def validate_spec(spec):
    if not 1 <= spec.n <= MAX_N:
        raise ValueError(f'n must be in 1..{MAX_N}')
    if not 0 <= spec.m <= MAX_M:
        raise ValueError(f'm must be in 0..{MAX_M}')
    if not 1 <= spec.k <= MAX_K:
        raise ValueError(f'k must be in 1..{MAX_K}')
    if spec.topology not in TOPOLOGIES or spec.mask not in MASKS or spec.order not in ORDERS:
        raise ValueError('unknown topology, mask or ordering')
    if spec.active and not 1 <= spec.active <= spec.n:
        raise ValueError('active vertex count must be in 1..n')
    if spec.gadget != 'auto' and spec.gadget not in GADGET_LIMITS:
        raise ValueError('unknown contradiction gadget')
    if spec.satisfiable and spec.gadget != 'auto':
        raise ValueError('a contradiction gadget requires --unsatisfiable')
    if spec.gadget_bit != -1 and (spec.satisfiable or not 0 <= spec.gadget_bit < spec.k):
        raise ValueError('gadget_bit requires an invalid test and a bit in 0..k-1')
    if spec.fixture == 'micro_loop' and (
            spec.n != 1 or spec.m not in (0, 1, 2) or spec.order != 'natural' or spec.relabel):
        raise ValueError('micro_loop requires n=1, m=0/1/2, natural order and no relabeling')
    if not spec.satisfiable:
        if spec.m < 2:
            raise ValueError('unsatisfiable tests require m >= 2 (including n=1)')
        if spec.gadget != 'auto':
            low_n, low_m = GADGET_LIMITS[spec.gadget]
            if spec.n < low_n or spec.m < low_m:
                raise ValueError(f'{spec.gadget} requires n >= {low_n}, m >= {low_m}')


def _validate_count(count):
    """MAX_SUM_N bounds T only because each test contributes at least one node."""
    if not isinstance(count, int) or not 1 <= count <= MAX_SUM_N:
        raise ValueError(f'T must be positive and compatible with aggregate sum_n <= '
                         f'{MAX_SUM_N}; n >= 1 implies T <= MAX_SUM_N '
                         f'({MAX_SUM_N}), not an independent T limit')


def validate_budget(tests, sum_n=None, sum_m=None):
    """Check either TestSpec/TestCase iterables or integer count/node/edge totals."""
    if sum_n is None and sum_m is None:
        count = sum_n = sum_m = 0
        for test in tests:
            count += 1
            sum_n += test.n
            sum_m += test.m
            validate_budget(count, sum_n, sum_m)
    else:
        count = tests
    _validate_count(count)
    if not isinstance(sum_n, int) or not count <= sum_n <= MAX_SUM_N:
        raise ValueError(f'aggregate sum_n must be in T..{MAX_SUM_N}')
    if not isinstance(sum_m, int) or not 0 <= sum_m <= MAX_SUM_M:
        raise ValueError(f'aggregate sum_m must be in 0..{MAX_SUM_M}')
    return count, sum_n, sum_m


def _compress_profiles(legacy):
    """Select the 29 official points; private legacy builders remain reusable."""
    parents = {
        3: (*range(3, 8), 9, 10, *range(11, 19)),
        4: tuple(range(19, 27)),
        5: tuple(range(27, 35)),
        6: (8,), 7: (35, 36), 8: (37, 40), 9: (38, 39),
        **{point: (point + 31,) for point in range(10, 21)},
        26: (75,), 28: (79,),
    }
    profiles = {1: legacy[1], 2: legacy[2]}
    for point, old_points in parents.items():
        tests = tuple(spec for old in old_points for spec in legacy[old].tests)
        # Check the complete old 19..26 bundle before considering any scaling:
        # T=32, sum_n=123376, sum_m=216335; both budgets fit unchanged.
        validate_budget(tests)
        profiles[point] = Profile('Combined legacy ' + '/'.join(map(str, old_points)), tests)
    profiles[3] = Profile('Small adversarial cases, including late OR growth',
                          profiles[3].tests + (TestSpec(
                              4, 3, 1, fixture='late_or_growth',
                              relabel=False, order='natural'),))
    profiles[6] = Profile('64-bit forcing and maximum-dimension boundary cases',
                          profiles[6].tests + (
                              TestSpec(MAX_N, 0, 1, mask='zero', relabel=False),
                              TestSpec(1, MAX_M, 30, 'loops', 'ones',
                                       relabel=False, order='natural'),
                              TestSpec(1, MAX_M, 1, 'loops', 'zero', False,
                                       'duplicate', 'late', relabel=False, gadget_bit=0)))
    for point, old_points in {
            21: (52, 53, 54), 22: (55, 56, 57), 23: (58, 59, 60),
            24: (61, 62, 63), 25: (64, 65, 66), 27: (76, 77, 78)}.items():
        profiles[point] = Profile(
            'Selected legacy ' + '/'.join(f'{old}[{i}]' for i, old in enumerate(old_points)),
            tuple(legacy[old].tests[i] for i, old in enumerate(old_points)))
    # Index periods: k=6, m=3, m=2 validity=6, m=1 mask=9; lcm=18.
    # Store only 18 specifications and a tuple of references, never 500000 specs.
    cycle = tuple(TestSpec(
        1, (2, 0, 1)[i % 3], (30, 1, 29, 2, 15, 3)[i % 6],
        'loops', ('sparse', 'ones', 'high')[(i // 3) % 3] if i % 3 == 2 else 'sparse',
        satisfiable=i % 3 != 0 or (i // 3) % 2 == 1,
        order='natural', relabel=False, fixture='micro_loop') for i in range(18))
    repeats, remainder = divmod(MAX_SUM_N, len(cycle))
    profiles[29] = Profile(
        '500000 n=1 tests; m=2/0/1, changing k, conflicting/duplicate loops and resets',
        cycle * repeats + cycle[:remainder])
    profiles = dict(sorted(profiles.items()))
    assert set(profiles) == set(range(1, OFFICIAL_COUNT + 1))
    for profile in profiles.values():
        if not profile.sample:
            validate_budget(profile.tests)
            for spec in set(profile.tests):
                validate_spec(spec)
    assert validate_budget(profiles[29].tests) == (MAX_SUM_N, MAX_SUM_N, MAX_SUM_M)
    return profiles


PROFILES = _compress_profiles(_build_profiles())


def answer(n, k, edges):
    """Validate bounds and compute the minimum candidate, never a witness sum."""
    if not 1 <= n <= MAX_N or not 1 <= k <= MAX_K or len(edges) > MAX_M:
        raise ValueError('test dimensions are out of bounds')
    limit = 1 << k
    candidate = [0] * (n + 1)
    for x, y, z in edges:
        if not 1 <= x <= n or not 1 <= y <= n or not 0 <= z < limit:
            raise ValueError('edge endpoint or mask is out of bounds')
        candidate[x] |= z
        candidate[y] |= z
    for x, y, z in edges:
        if candidate[x] & candidate[y] != z:
            return -1
    return sum(candidate)


def _witness(count, k, style, rng):
    full = (1 << k) - 1
    high = 1 << (k - 1)
    values = []
    even_bits = 0x55555555 & full
    for i in range(count):
        if style == 'zero':
            value = 0
        elif style == 'ones':
            value = full
        elif style == 'high':
            value = high
        elif style in ('sparse', 'dense'):
            sparse = 0
            for bit in rng.sample(range(k), rng.randint(1, min(3, k))):
                sparse |= 1 << bit
            value = sparse if style == 'sparse' else full ^ sparse
        elif style == 'random':
            value = rng.getrandbits(k)
        elif style == 'alternating':
            value = full if i % 7 == 0 else even_bits if i % 2 else full ^ even_bits
        elif style == 'blocks':
            if i % 127 == 0:
                block = rng.getrandbits(k)
            value = block
        elif style == 'stairs':
            value = (1 << (1 + i % k)) - 1
        else:  # Distinct, bit-dense labels for large k.
            value = ((i + 1) * 2654435761) & full
        values.append(value)
    return values


def _padding(count, vertices, k, topology, mask, mixed_loops, rng, forced=None):
    """Derive every padding equation from a hidden witness, not its sum."""
    if count == 0:
        return []
    size = len(vertices)
    assert size > 0
    witness = forced if forced is not None else _witness(size, k, mask, rng)
    parents = [0] + [rng.randrange(i) for i in range(1, size)] if topology == 'tree' else None
    edges = []
    width = min(31, max(2, size // 5))
    for i in range(count):
        if size == 1 or topology == 'loops':
            x = y = i % size
        elif mixed_loops and i % 13 == 0:
            x = y = i % size
        elif topology == 'star':
            x, y = 0, 1 + i % (size - 1)
        elif topology == 'path':
            x = i % (size - 1)
            y = x + 1
        elif topology == 'tree':
            y = 1 + i % (size - 1)
            x = parents[y]
        elif topology == 'cycle':
            x, y = i % size, (i + 1) % size
        elif topology == 'matching':
            # Reuse a fixed matching. Modulo size would change pairing parity
            # for odd sizes and accidentally turn repeated pairs into a path.
            x = 2 * (i % (size // 2))
            y = x + 1
        elif topology == 'disconnected':
            x = i % size
            base = x // width * width
            y = rng.randrange(base, min(base + width, size))
        else:  # Random, or random edges restricted to the active isolated set.
            x, y = rng.randrange(size), rng.randrange(size)
        edges.append((vertices[x], vertices[y], witness[x] & witness[y]))
    return edges


def _gadget(name, n, k, rng):
    bit = 1 << rng.randrange(k)
    if name == 'duplicate':
        y = 1 if n == 1 else 2
        return y, [(1, y, bit), (1, y, 0)], [bit] * y
    if name == 'loop':
        return 2, [(1, 2, bit), (1, 1, 0)], [bit, bit]
    if name == 'triangle':
        return 3, [(1, 2, bit), (2, 3, bit), (1, 3, 0)], [bit] * 3
    if name == 'path':
        return 4, [(1, 2, bit), (3, 4, bit), (2, 3, 0)], [bit] * 4
    return 4, [(1, 2, bit), (3, 4, bit), (1, 3, 0)], [bit] * 4


def _fixture(spec):
    if spec.fixture == 'zero_duplicates':
        return [(1, 1, 0), (1, 1, 0), (2, 2, 0), (2, 2, 0),
                (1, 2, 0), (2, 1, 0), (3, 3, 0), (3, 3, 0)]
    if spec.fixture == 'last_endpoint':
        return [(1, spec.n, 1 << 29)]
    if spec.fixture == 'isolated_endpoint':
        return [(1, 2, 1), (2, 3, 2), (spec.n, spec.n, 4)]
    if spec.fixture == 'or_star':
        return [(1, i + 2, 1 << i) for i in range(spec.n - 1)]
    if spec.fixture == 'late_or_growth':
        return [(2, 3, 0), (1, 2, 1), (3, 4, 1)]
    raise ValueError(f'unknown fixture {spec.fixture}')


def _make_micro_case(spec, seed=0):
    """Direct n=1 loop oracle; no RNG, witness array, relabeling or edge shuffle."""
    offset = seed if isinstance(seed, int) else sum(map(ord, str(seed)))
    bit = 1 << ((offset + spec.k // 2) % spec.k)
    if spec.m == 0:
        edges, result = [], 0
    elif spec.m == 1:
        value = (1 << spec.k) - 1 if spec.mask == 'ones' else (
            1 << (spec.k - 1) if spec.mask == 'high' else bit)
        edges, result = [(1, 1, value)], value
    else:
        edges = [(1, 1, bit), (1, 1, bit if spec.satisfiable else 0)]
        result = bit if spec.satisfiable else -1
    return TestCase(1, spec.k, edges, spec.satisfiable, result)


def make_case(spec, seed=0):
    """Exported harness API: materialize and certify one TestSpec."""
    validate_spec(spec)
    if spec.fixture == 'micro_loop':
        case = _make_micro_case(spec, seed)
        assert answer(case.n, case.k, case.edges) == case.result
        assert (case.result != -1) == spec.satisfiable
        return case
    rng = random.Random(seed)
    if spec.fixture:
        edges = _fixture(spec)
    elif spec.satisfiable:
        active = spec.active or (min(spec.n, 8) if spec.topology == 'isolated' else spec.n)
        edges = _padding(spec.m, range(1, active + 1), spec.k, spec.topology,
                         spec.mask, spec.mixed_loops, rng)
    else:
        name = spec.gadget
        if name == 'auto':
            feasible = [g for g, (n, m) in GADGET_LIMITS.items() if spec.n >= n and spec.m >= m]
            name = rng.choice(feasible)
        reserved, gadget, forced = _gadget(name, spec.n, spec.k, rng)
        if spec.gadget_bit != -1:
            bit = 1 << spec.gadget_bit
            gadget = [(x, y, bit if z else 0) for x, y, z in gadget]
            forced = [bit] * reserved
        if reserved < spec.n:
            available = spec.n - reserved
            active = min(available, spec.active or (8 if spec.topology == 'isolated' else available))
            vertices = range(reserved + 1, reserved + active + 1)
            padding = _padding(spec.m - len(gadget), vertices, spec.k,
                               spec.topology, spec.mask, spec.mixed_loops, rng)
        else:
            # No disconnected vertex is available. These endpoints are explicitly
            # forced by the positive gadget edges, so padding agrees with them.
            padding = _padding(spec.m - len(gadget), range(1, reserved + 1), spec.k,
                               spec.topology, spec.mask, spec.mixed_loops, rng, forced)
        if spec.order == 'late':
            rng.shuffle(padding)
            edges = gadget[:-1] + padding + gadget[-1:]
        else:
            edges = gadget + padding
    if spec.relabel:
        labels = list(range(1, spec.n + 1))
        rng.shuffle(labels)
        edges = [(labels[x - 1], labels[y - 1], z) for x, y, z in edges]
    if spec.order == 'shuffle':
        rng.shuffle(edges)
        edges = [(y, x, z) if rng.getrandbits(1) else (x, y, z) for x, y, z in edges]
    elif spec.order == 'reverse':
        edges = [(y, x, z) for x, y, z in reversed(edges)]
    assert len(edges) == spec.m, (spec, len(edges))
    result = answer(spec.n, spec.k, edges)
    assert (result != -1) == spec.satisfiable, (spec, result)
    return TestCase(spec.n, spec.k, edges, spec.satisfiable, result)


def parse_input(text):
    """Parse/check ACM input for samples and external test harnesses."""
    tokens = iter(text.split())

    def integer():
        try:
            return int(next(tokens))
        except (StopIteration, ValueError) as exc:
            raise ValueError('missing or non-integer input token') from exc

    count = integer()
    _validate_count(count)
    tests = []
    sum_n = sum_m = 0
    for index in range(count):
        n, m, k = integer(), integer(), integer()
        if not 1 <= n <= MAX_N or not 0 <= m <= MAX_M or not 1 <= k <= MAX_K:
            raise ValueError('input dimensions are out of bounds')
        sum_n += n
        sum_m += m
        validate_budget(index + 1, sum_n, sum_m)
        edges = [(integer(), integer(), integer()) for _ in range(m)]
        result = answer(n, k, edges)
        tests.append(TestCase(n, k, edges, result != -1, result))
    if next(tokens, None) is not None:
        raise ValueError('extra input tokens; no legacy c is supported')
    return tests


def _load_sample(profile):
    directory = Path(__file__).resolve().parent / 'down'
    texts = []
    for extension in ('in', 'ans'):
        path = directory / f'{profile}.{extension}'
        text = path.read_bytes().decode('ascii')
        if '\r' in text or not text.endswith('\n'):
            raise ValueError(f'{path} must be ASCII with LF and a final newline')
        texts.append(text)
    tests = parse_input(texts[0])
    if [int(token) for token in texts[1].split()] != [test.result for test in tests]:
        raise ValueError(f'down/{profile}.ans disagrees with the minimum-candidate oracle')
    return texts[0], texts[1], tests


def iter_profile(profile, seed=0):
    """Yield independent TestCase objects; official dimensions never depend on seed."""
    if profile not in PROFILES:
        raise ValueError(f'profile must be in 1..{OFFICIAL_COUNT}')
    metadata = PROFILES[profile]
    if metadata.sample:
        yield from _load_sample(profile)[2]
        return
    micro_seed = seed if isinstance(seed, int) else sum(map(ord, str(seed)))
    for index, spec in enumerate(metadata.tests):
        if spec.fixture == 'micro_loop':
            yield _make_micro_case(spec, micro_seed + index % 18)
        else:
            yield make_case(spec, f'bitand-v29/{profile}/{seed}/{index}')


def profile_sizes(profile):
    """Exact test/node/edge counts without generating non-sample edges."""
    metadata = PROFILES[profile]
    tests = _load_sample(profile)[2] if metadata.sample else metadata.tests
    count, sum_n, sum_m = validate_budget(tests)
    if metadata.sample:
        max_n = max(test.n for test in tests)
        max_m = max(test.m for test in tests)
        valid = sum(test.satisfiable for test in tests)
    else:
        frequencies = {}
        for spec in tests:
            key = id(spec)
            frequencies[key] = frequencies.get(key, 0) + 1
        unique = {id(spec): spec for spec in tests}
        for spec in unique.values():
            validate_spec(spec)
        max_n = max(spec.n for spec in unique.values())
        max_m = max(spec.m for spec in unique.values())
        valid = sum(frequencies[key] for key, spec in unique.items() if spec.satisfiable)
    return {
        'tests': count, 'sum_n': sum_n, 'sum_m': sum_m,
        'max_n': max_n, 'max_m': max_m, 'valid': valid, 'invalid': count - valid,
    }


def _write_cases(fin, count, tests, answers):
    _validate_count(count)
    fin.write(f'{count}\n')
    seen = sum_n = sum_m = 0
    for test in tests:
        seen += 1
        sum_n += test.n
        sum_m += test.m
        validate_budget(seen, sum_n, sum_m)
        assert seen <= count
        assert (test.result != -1) == test.satisfiable
        fin.write(f'{test.n} {test.m} {test.k}\n')
        lines = []
        for x, y, z in test.edges:
            lines.append(f'{x} {y} {z}\n')
            if len(lines) == WRITE_CHUNK:
                fin.write(''.join(lines))
                lines.clear()
        if lines:
            fin.write(''.join(lines))
        if answers is not None:
            answers.write(f'{test.result}\n')
        del test
    assert seen == count


def gen(fin, args, cont, seed=0, answers=None):
    """Tuack-compatible official-file callback; no Tuack import or config edits."""
    profile = int(cont['case'])
    if profile not in PROFILES:
        raise ValueError(f'profile must be in 1..{OFFICIAL_COUNT}')
    profile_sizes(profile)
    if PROFILES[profile].sample:
        # Tuack opens an input destination before calling us. Public samples are
        # manual in conf.yaml; also fail clearly if another caller targets down.
        destination = getattr(fin, 'name', None)
        sample_source = Path(__file__).resolve().parent / 'down' / f'{profile}.in'
        if isinstance(destination, (str, bytes)) and Path(destination).resolve() == sample_source:
            raise ValueError('public sample inputs are manual; do not regenerate down in place')
        input_text, answer_text, _ = _load_sample(profile)
        fin.write(input_text)
        if answers is not None:
            answers.write(answer_text)
        return
    _write_cases(fin, len(PROFILES[profile].tests), iter_profile(profile, seed), answers)


def gen_custom(fin, spec, tests=1, seed=0, answers=None):
    """Write positive T independently seeded custom tests within aggregate budgets."""
    validate_spec(spec)
    _validate_count(tests)
    validate_budget(tests, tests * spec.n, tests * spec.m)
    cases = (make_case(spec, f'bitand-custom-v1/{seed}/{i}') for i in range(tests))
    _write_cases(fin, tests, cases, answers)


def _list_profiles():
    totals = {'tests': 0, 'sum_n': 0, 'sum_m': 0}
    missing = []
    for profile, metadata in PROFILES.items():
        try:
            sizes = profile_sizes(profile)
        except (OSError, ValueError) as exc:
            if not metadata.sample:
                raise
            missing.append(profile)
            print(f'{profile:2}: runtime sample unavailable ({exc}) | {metadata.description}')
            continue
        print(f"{profile:2}: T={sizes['tests']:2} n={sizes['sum_n']:7} m={sizes['sum_m']:7} "
              f"valid/invalid={sizes['valid']}/{sizes['invalid']} | {metadata.description}")
        for name in totals:
            totals[name] += sizes[name]
    suffix = f'; excludes missing runtime samples {missing}' if missing else ''
    print(f"TOTAL: tests={totals['tests']}, sum_n={totals['sum_n']}, "
          f"sum_m={totals['sum_m']}{suffix}")


def _generate_all(directory, seed, start=1, end=OFFICIAL_COUNT):
    if not 1 <= start <= end <= OFFICIAL_COUNT:
        raise ValueError(f'--all range must satisfy 1 <= start <= end <= {OFFICIAL_COUNT}')
    if not directory.is_dir():
        raise ValueError('--all requires an existing destination directory')
    # Preflight ALL profiles and samples before opening any destination; never delete.
    for profile in range(1, OFFICIAL_COUNT + 1):
        profile_sizes(profile)
    expected = {f'{i}.{extension}' for i in range(1, OFFICIAL_COUNT + 1)
                for extension in ('in', 'ans')}
    selected = {f'{i}.{extension}' for i in range(start, end + 1)
                for extension in ('in', 'ans')}
    entries = list(directory.iterdir())
    numbered = {entry.name for entry in entries if re.fullmatch(r'[0-9]+\.(in|ans)', entry.name)}
    unexpected = sorted(numbered - expected)
    if unexpected:
        print('Warning: unexpected numbered files are left untouched: ' + ', '.join(unexpected),
              file=sys.stderr)
    existing = sorted(numbered & selected)
    if existing:
        print(f'Warning: --all will overwrite {len(existing)} existing official files.', file=sys.stderr)
    sources = {Path(__file__).resolve(), *(Path(__file__).resolve().parent / 'down' / name
                                        for name in ('1.in', '1.ans', '2.in', '2.ans'))}
    for name in selected:
        target = directory / name
        if target.is_symlink() or target.is_dir() or target.resolve() in sources:
            raise ValueError(f'refusing to overwrite a symlink, directory or sample source: {target}')
    for profile in range(start, end + 1):
        with (directory / f'{profile}.in').open('w', encoding='ascii', newline='\n', buffering=1 << 20) as fin:
            with (directory / f'{profile}.ans').open('w', encoding='ascii', newline='\n', buffering=1 << 20) as ans:
                gen(fin, {}, {'case': profile}, seed, ans)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--case', type=int, choices=range(1, OFFICIAL_COUNT + 1), metavar='N',
                      help=f'official profile in 1..{OFFICIAL_COUNT}')
    for number in range(1, OFFICIAL_COUNT + 1):
        mode.add_argument(f'--case{number}', dest='case', action='store_const', const=number,
                          help=argparse.SUPPRESS)
    mode.add_argument('--all', action='store_true')
    mode.add_argument('--list', action='store_true')
    mode.add_argument('--custom', action='store_true')
    parser.add_argument('--seed', type=int, default=0, help='deterministic variation; samples stay exact')
    parser.add_argument('--out-dir', type=Path, help='existing destination directory, only for --all')
    parser.add_argument('--start', type=int, help='first official profile, only for --all (default 1)')
    parser.add_argument('--end', type=int,
                        help=f'last official profile, only for --all (default {OFFICIAL_COUNT})')
    parser.add_argument('--answers', type=Path, help='optional answer file for --case or --custom')
    parser.add_argument('--n', type=int)
    parser.add_argument('--m', type=int)
    parser.add_argument('--k', type=int)
    parser.add_argument('--tests', type=int,
                        help='positive custom T; no independent cap, aggregate n/m budgets apply')
    parser.add_argument('--topology', choices=TOPOLOGIES)
    parser.add_argument('--mask', choices=MASKS)
    status = parser.add_mutually_exclusive_group()
    status.add_argument('--satisfiable', dest='satisfiable', action='store_const', const=True, default=None)
    status.add_argument('--unsatisfiable', dest='satisfiable', action='store_const', const=False)
    parser.add_argument('--gadget', choices=('auto', *GADGET_LIMITS), help='custom certified contradiction')
    parser.add_argument('--order', choices=ORDERS, help='custom edge ordering (default shuffle)')
    options = parser.parse_args(argv)
    custom_fields = ('n', 'm', 'k', 'tests', 'topology', 'mask', 'satisfiable', 'gadget', 'order')
    if not options.custom and any(getattr(options, field) is not None for field in custom_fields):
        parser.error('dimension, topology, mask, status, gadget and order options require --custom')
    if not options.all and (options.start is not None or options.end is not None):
        parser.error('--start and --end can only be used with --all')
    start = options.start if options.start is not None else 1
    end = options.end if options.end is not None else OFFICIAL_COUNT
    if options.all:
        if not 1 <= start <= end <= OFFICIAL_COUNT:
            parser.error(f'--all range must satisfy 1 <= start <= end <= {OFFICIAL_COUNT}')
        if options.out_dir is None or not options.out_dir.is_dir():
            parser.error('--all requires an existing --out-dir directory')
        if options.answers is not None:
            parser.error('--all writes numbered answers; do not use --answers')
    elif options.out_dir is not None:
        parser.error('--out-dir can only be used with --all')
    if options.list and options.answers is not None:
        parser.error('--answers is only for --case or --custom')
    if options.answers is not None:
        if not options.answers.parent.is_dir():
            parser.error('--answers requires an existing parent directory')
        protected = {Path(__file__).resolve(), *(Path(__file__).resolve().parent / 'down' / name
                                                for name in ('1.in', '1.ans', '2.in', '2.ans'))}
        if options.answers.is_symlink() or options.answers.resolve() in protected:
            parser.error('--answers must not overwrite a source or sample file or follow a symlink')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='ascii', newline='\n')
    try:
        if options.list:
            _list_profiles()
        elif options.all:
            _generate_all(options.out_dir, options.seed, start, end)
        else:
            if options.custom:
                if any(getattr(options, name) is None for name in ('n', 'm', 'k')):
                    parser.error('--custom requires --n, --m and --k')
                spec = TestSpec(options.n, options.m, options.k,
                                options.topology or 'random', options.mask or 'random',
                                options.satisfiable if options.satisfiable is not None else True,
                                options.gadget or 'auto', options.order or 'shuffle')
                validate_spec(spec)
                tests = options.tests if options.tests is not None else 1
                _validate_count(tests)
                validate_budget(tests, tests * spec.n, tests * spec.m)

                def emit(fin, ans):
                    gen_custom(fin, spec, tests, options.seed, ans)
            else:
                profile_sizes(options.case)

                def emit(fin, ans):
                    gen(fin, {}, {'case': options.case}, options.seed, ans)
            if options.answers is None:
                emit(sys.stdout, None)
            else:
                with options.answers.open('w', encoding='ascii', newline='\n', buffering=1 << 20) as ans:
                    emit(sys.stdout, ans)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
