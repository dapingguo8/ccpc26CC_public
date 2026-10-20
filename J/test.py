#!/usr/bin/env python3
"""Standard-library-only verification of the 29-file Bitwise AND suite.

Run from the problem directory (executables must already be built):
    python3 test.py --std ./std/std --validator ./std/val \
        --reference ./std/bitwise --quick
    python3 test.py --std ./std/std --validator ./std/val \
        --reference ./std/bitwise --report outputs/test-report.json

The report parent must already exist. No input, answer, source, or executable
is generated or modified. Python executable paths are supported as well.
All process times are observed wall times, including startup, NOT judge limits.
The supplied validator must accept valid syntax (even unsatisfiable equations)
and reject malformed syntax or per-file aggregate overflow in the built-in corpus.
Each file must satisfy sum_n <= 500000 and sum_m <= 500000 independently.
--quick does not skip this
corpus or release gates: actual official desync evidence with unread edges and
a later test, a retained-OR state-leak failure on actual 12.in, and a T-cap
failure on actual 3.in or 29.in are required. Actual 29.in must reach both
aggregate budgets and T=500000, accepted by validator, std and reference.
T has no independent upper limit; n >= 1 derives T <= 500000 from sum_n.
"""

import argparse
from functools import lru_cache
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

MAX_N = 200000
MAX_M = 200000
MAX_K = 30
MAX_SUM_N = 500000
MAX_SUM_M = 500000
# Not a separate constraint: every testcase contributes at least one node.
DERIVED_MAX_T = MAX_SUM_N
# Process-startup reduction only; each batch still obeys both aggregate budgets.
BATCH_SIZE = 100
DETAIL_LIMIT = 100
# 500000 answers of at most 15 digits plus LF need 8000000 bytes (< 8 MiB).
MAX_OUTPUT_BYTES = 8 * 1024 * 1024
COUNT = 29
CASE_MUTATION_PROFILES = frozenset(range(1, 6))
STREAM_MUTATION_PROFILES = CASE_MUTATION_PROFILES | {12, 26, 28}
INTEGER = re.compile(rb'[+-]?[0-9]+\Z')
RANDOM_SEED = 0x46CC26


class CheckError(Exception):
    pass


class Results:
    def __init__(self, options):
        self.started = time.perf_counter()
        self.data = {
            'schema_version': 4,
            'status': 'running',
            'options': {'data_dir': str(options.data_dir.resolve()),
                        'std': options.std, 'validator': options.validator,
                        'reference': options.reference, 'quick': options.quick,
                        'process_timeout_seconds': options.timeout},
            'bounds': {'T': [1, None], 'derived_T': DERIVED_MAX_T, 'n': [1, MAX_N],
                       'm': [0, MAX_M], 'k': [1, MAX_K],
                       'sum_n': MAX_SUM_N, 'sum_m': MAX_SUM_M},
            'failures': [], 'failure_count': 0, 'files': [],
            'timing_note': 'Observed wall seconds including process startup; '
                           'no claim about judge speed, resource limits, or all wrong solutions.',
        }

    def fail(self, where, error, **details):
        self.data['failure_count'] += 1
        if len(self.data['failures']) < 100:
            self.data['failures'].append({'where': where, 'error': str(error), **details})

    def finish(self):
        self.data['runtime_seconds'] = time.perf_counter() - self.started
        self.data['status'] = 'fail' if self.data['failure_count'] else 'pass'


def load_generator():
    path = Path(__file__).resolve().with_name('gen.py')
    spec = importlib.util.spec_from_file_location('_bitand_generator_for_tests', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def brute_per_bit(n, k, edges):
    """Cache only tiny equations, never large graphs or per-case metadata."""
    if n <= 9 and len(edges) <= 32:
        return _tiny_brute_per_bit(n, k, tuple(edges))
    raise CheckError('independent enumeration requires n<=9 and m<=32')


@lru_cache(maxsize=8192)
def _tiny_brute_per_bit(n, k, edges):
    """Independent oracle: enumerate all Boolean assignments, minimizing each bit.

    No incident OR, propagation, or minimum-candidate construction is used.
    For n=1 enumerate its two Boolean choices analytically: no equations allow
    zero; otherwise every loop must prescribe the same value at every bit.
    """
    if n == 1:
        if not edges:
            return 0
        value = edges[0][2]
        return value if all(z == value for _, _, z in edges) else -1
    total = 0
    for bit in range(k):
        equations = [(x - 1, y - 1, (z >> bit) & 1) for x, y, z in edges]
        minimum = None
        for assignment in range(1 << n):
            if all(((assignment >> x) & (assignment >> y) & 1) == z
                   for x, y, z in equations):
                ones = bin(assignment).count('1')
                if minimum is None or ones < minimum:
                    minimum = ones
        if minimum is None:
            return -1
        total += minimum << bit
    return total


class TokenStream:
    """Bounded-memory ASCII token scanner, also hashing exact source bytes."""
    def __init__(self, stream):
        self.stream = stream
        self.sha = hashlib.sha256()
        self.bytes = 0
        self.sum_n = 0
        self.sum_m = 0
        self.tokens = self._tokens()

    def _tokens(self):
        pending = b''
        while True:
            block = self.stream.read(65536)
            if not block:
                if pending:
                    yield pending
                return
            self.sha.update(block)
            self.bytes += len(block)
            parts = (pending + block).split()
            if block[-1] in b' \t\r\n\v\f':
                pending = b''
            elif parts:
                pending = parts.pop()
            else:
                pending = b''
            if len(pending) > 32 or any(len(part) > 32 for part in parts):
                raise CheckError('integer token exceeds 32 bytes')
            yield from parts

    def integer(self):
        token = next(self.tokens, None)
        if token is None or not INTEGER.fullmatch(token):
            raise CheckError('missing or non-integer ASCII token')
        return int(token)

    def end(self):
        if next(self.tokens, None) is not None:
            raise CheckError('extra tokens (legacy c is not supported)')


def check_count(count):
    if not 1 <= count <= DERIVED_MAX_T:
        raise CheckError('T must be positive and compatible with sum_n <= %d; '
                         'n >= 1 implies T <= %d' % (MAX_SUM_N, DERIVED_MAX_T))


def dimensions(n, m, k):
    if not (1 <= n <= MAX_N and 0 <= m <= MAX_M and 1 <= k <= MAX_K):
        raise CheckError('dimensions out of bounds: n=%s m=%s k=%s' % (n, m, k))


def read_case(tokens):
    n, m, k = tokens.integer(), tokens.integer(), tokens.integer()
    dimensions(n, m, k)
    tokens.sum_n += n
    tokens.sum_m += m
    if tokens.sum_n > MAX_SUM_N:
        raise CheckError('sum_n exceeds %d (%d)' % (MAX_SUM_N, tokens.sum_n))
    if tokens.sum_m > MAX_SUM_M:
        raise CheckError('sum_m exceeds %d (%d)' % (MAX_SUM_M, tokens.sum_m))
    edges = []
    for index in range(m):
        x, y, z = tokens.integer(), tokens.integer(), tokens.integer()
        if not (1 <= x <= n and 1 <= y <= n and 0 <= z < (1 << k)):
            raise CheckError('edge %d out of bounds: %s' % (index + 1, (x, y, z)))
        edges.append((x, y, z))
    return n, k, edges


def output_integers(raw):
    if len(raw) > MAX_OUTPUT_BYTES:
        raise CheckError('answer output exceeds %d bytes' % MAX_OUTPUT_BYTES)
    words = raw.split()
    if any(not INTEGER.fullmatch(word) for word in words):
        raise CheckError('answer contains a non-integer token')
    return [int(word) for word in words]


def command_for(value):
    path = Path(value).expanduser()
    if path.is_file():
        path = path.resolve()
    else:
        found = shutil.which(value)
        if not found:
            raise CheckError('executable not found: ' + value)
        path = Path(found).resolve()
    return [sys.executable, str(path)] if path.suffix.lower() == '.py' else [str(path)]


def run_process(command, timeout, input_path=None, payload=None):
    started = time.perf_counter()
    info = {'command': command}
    try:
        if input_path is None:
            process = subprocess.run(command, input=payload, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, timeout=timeout)
        else:
            with input_path.open('rb') as source:
                process = subprocess.run(command, stdin=source, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, timeout=timeout)
        info.update(returncode=process.returncode,
                    stderr=process.stderr[:2000].decode('utf-8', 'replace'))
        raw = process.stdout  # Keep full output for comparison, including profile 29.
        info['stdout_bytes'] = len(raw)
        if process.returncode:
            info['error'] = 'process exited with code %d' % process.returncode
    except subprocess.TimeoutExpired:
        info['error'] = 'process timeout (harness limit, not a judge measurement)'
        raw = b''
    except OSError as exc:
        info['error'] = str(exc)
        raw = b''
    info['runtime_seconds'] = time.perf_counter() - started
    return info, raw


def check_program(report, where, name, command, timeout, expected,
                  input_path=None, payload=None):
    info, raw = run_process(command, timeout, input_path, payload)
    if 'error' in info:
        if name == 'validator':
            info['accepted'] = False
        report.fail(where + '/' + name, info['error'], process=info)
        return info
    if name == 'validator':
        info['accepted'] = True
        return info
    try:
        actual = output_integers(raw)
        info['answers'] = actual
        if expected is not None and actual != expected:
            first = next((i + 1 for i, (want, got) in enumerate(zip(expected, actual))
                          if want != got), min(len(expected), len(actual)) + 1)
            raise CheckError('answers differ at test %d: expected %d answers %s, got %d %s' %
                             (first, len(expected), expected[:DETAIL_LIMIT],
                              len(actual), actual[:DETAIL_LIMIT]))
    except CheckError as exc:
        report.fail(where + '/' + name, exc)
        info['error'] = str(exc)
    return info


def encode_cases(cases):
    lines = [str(len(cases))]
    for n, k, edges, _ in cases:
        lines.append('%d %d %d' % (n, len(edges), k))
        lines.extend('%d %d %d' % edge for edge in edges)
    return ('\n'.join(lines) + '\n').encode('ascii')


def case_summary(n, k, edges):
    summary = {'n': n, 'm': len(edges), 'k': k}
    if len(edges) <= 24:
        summary['edges'] = edges
    return summary


MODEL_DESCRIPTIONS = {
    'no_second_verification': 'OR both endpoints, return sum without checking equations.',
    'online_verification': 'Check only the current equation after OR; never revisit earlier zero bits.',
    'reject_or_growth': 'Reject any change to an already nonzero incident value.',
    'max_instead_or': 'Use numeric max at each endpoint, then verify.',
    'overwrite_instead_or': 'Assign the most recently read z at each endpoint, then verify.',
    'only_left': 'OR only the first endpoint, then verify.',
    'skip_loops': 'Discard self-loops in both construction and verification.',
    'skip_zero': 'Discard zero equations in both construction and verification.',
    'overwrite_duplicate': 'Keep only the last equation for each unordered endpoint pair.',
    'component_or': 'Give every vertex in a connected component the OR of its edge masks.',
    'sum_edges': 'Check feasibility correctly but report sum of edge labels.',
    'int32_sum': 'Check feasibility correctly but wrap the sum to signed 32 bits.',
    'uint32_sum': 'Check feasibility correctly but wrap the sum to unsigned 32 bits.',
    'highbit_truncate': 'Drop bit 29 during construction, then verify original equations.',
    'unconditional_valid': 'Always assign all k bits to every vertex and report that sum, unchecked.',
    'reject_m0': 'Reject empty graphs instead of returning zero.',
    'connected_heuristic': 'Reject a feasible graph unless all n vertices are connected.',
    'degree_heuristic': 'Reject a feasible graph when some vertex has degree above two.',
    'omit_last_vertex': 'Verify correctly but omit vertex n from the answer sum.',
    'xor_instead_or': 'XOR incident masks rather than OR, then verify.',
    'double_count_loops': 'Verify correctly but count each loop-incident vertex twice in the sum.',
    'k_off_by_one': 'Use only bits 0 through k-2 during construction, then verify.',
    'early_exit_desync': 'On online contradiction, print -1 and parse next header without consuming remaining edges.',
    'state_leak': 'Retain per-vertex OR values across test cases; read every edge and perform final checking.',
    'cap_T_at_10': 'Process only the first ten tests, silently ignoring all later tests.',
}


def forced_values(n, edges):
    values = [0] * (n + 1)
    for x, y, z in edges:
        values[x] |= z
        values[y] |= z
    return values


def verified_sum(values, edges):
    if any(values[x] & values[y] != z for x, y, z in edges):
        return -1
    return sum(values)


def mutant_value(name, n, k, edges, base, correct):
    if name == 'no_second_verification':
        return sum(base)
    if name == 'unconditional_valid':
        return n * ((1 << k) - 1)
    if name == 'reject_m0':
        return -1 if not edges else correct
    if name in ('sum_edges', 'int32_sum', 'uint32_sum', 'omit_last_vertex',
                'double_count_loops', 'degree_heuristic', 'connected_heuristic'):
        if correct == -1:
            return -1
        if name == 'sum_edges':
            return sum(z for _, _, z in edges)
        if name == 'int32_sum':
            return ((correct + (1 << 31)) % (1 << 32)) - (1 << 31)
        if name == 'uint32_sum':
            return correct % (1 << 32)
        if name == 'omit_last_vertex':
            return correct - base[n]
        if name == 'double_count_loops':
            return correct + sum(base[x] for x in {x for x, y, _ in edges if x == y})
        if name == 'degree_heuristic':
            degrees = [0] * (n + 1)
            for x, y, _ in edges:
                degrees[x] += 1
                degrees[y] += 1
            return -1 if max(degrees) > 2 else correct
    if name in ('component_or', 'connected_heuristic'):
        parent = list(range(n + 1))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for x, y, _ in edges:
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
        roots = [find(x) for x in range(n + 1)]
        if name == 'connected_heuristic':
            return correct if len(set(roots[1:])) == 1 else -1
        masks = [0] * (n + 1)
        for x, _, z in edges:
            masks[roots[x]] |= z
        return verified_sum([0] + [masks[roots[x]] for x in range(1, n + 1)], edges)
    if name == 'overwrite_duplicate':
        last = {}
        for x, y, z in edges:
            last[min(x, y), max(x, y)] = z
        reduced = [(x, y, z) for (x, y), z in last.items()]
        return verified_sum(forced_values(n, reduced), reduced)
    values = [0] * (n + 1)
    for x, y, z in edges:
        if name == 'skip_loops' and x == y or name == 'skip_zero' and z == 0:
            continue
        if name == 'reject_or_growth' and any(values[v] and values[v] | z != values[v]
                                            for v in (x, y)):
            return -1
        if name == 'max_instead_or':
            values[x], values[y] = max(values[x], z), max(values[y], z)
        elif name == 'overwrite_instead_or':
            values[x] = values[y] = z
        elif name == 'xor_instead_or':
            values[x] ^= z
            if x != y:
                values[y] ^= z
        else:
            mask = z & ((1 << 29) - 1) if name == 'highbit_truncate' else (
                z & ((1 << (k - 1)) - 1) if name == 'k_off_by_one' else z)
            values[x] |= mask
            if name != 'only_left':
                values[y] |= mask
        if name == 'online_verification' and values[x] & values[y] != z:
            return -1
    if name == 'online_verification':
        return sum(values)
    checked = (edge for edge in edges if not (
        name == 'skip_loops' and edge[0] == edge[1] or name == 'skip_zero' and edge[2] == 0))
    return verified_sum(values, checked)


def simulate_desync(tokens, early_exits=None):
    """Virtual stdin process; consumes exactly what the faulty parser consumes."""
    outputs = []
    early_exits = [] if early_exits is None else early_exits
    synchronized = True
    try:
        count = tokens.integer()
        check_count(count)
        for test_index in range(count):
            n, m, k = tokens.integer(), tokens.integer(), tokens.integer()
            dimensions(n, m, k)
            values = [0] * (n + 1)
            for edge_index in range(m):
                x, y, z = tokens.integer(), tokens.integer(), tokens.integer()
                if not (1 <= x <= n and 1 <= y <= n and 0 <= z < (1 << k)):
                    return 'out-of-bounds input after desynchronization'
                values[x] |= z
                values[y] |= z
                if values[x] & values[y] != z:
                    outputs.append(-1)
                    unread = m - edge_index - 1
                    early_exits.append({'test': test_index + 1, 'edge': edge_index + 1,
                                        'unread_edges': unread, 'total_tests': count,
                                        'has_later_testcase': test_index + 1 < count,
                                        'synchronized_before_exit': synchronized})
                    if unread:
                        synchronized = False
                    break  # Deliberately WRONG: unread edges become the next header.
            else:
                outputs.append(sum(values))
        tokens.end()
        return outputs
    except CheckError as exc:
        return 'parse failure: ' + str(exc)


def simulate_state_leak(tokens):
    """Consume a whole input with a persistent vertex array and final checking."""
    count = tokens.integer()
    check_count(count)
    values = [0]
    outputs = []
    for _ in range(count):
        n, k, edges = read_case(tokens)
        if len(values) <= n:
            values.extend([0] * (n + 1 - len(values)))
        for x, y, z in edges:
            values[x] |= z
            values[y] |= z
        # Deliberately WRONG: values[1:n+1] are never cleared between tests.
        if any(values[x] & values[y] != z for x, y, z in edges):
            outputs.append(-1)
        else:
            outputs.append(sum(itertools.islice(values, 1, n + 1)))
        del edges
    tokens.end()
    return outputs


def simulate_cap_T_at_10(tokens, gen):
    """Faulty stream process: read at most ten complete tests, ignore the rest."""
    count = tokens.integer()
    check_count(count)
    outputs = []
    for _ in range(min(count, 10)):
        n, k, edges = read_case(tokens)
        outputs.append(gen.answer(n, k, edges))
    return outputs


class Mutations:
    def __init__(self):
        self.models = {name: {'description': description, 'evaluations': {},
                              'kills': {}, 'first_failure': None, 'runtime_seconds': 0.0}
                       for name, description in MODEL_DESCRIPTIONS.items()}
        self.matrix = {}
        self.true_official_desync_witnesses = []
        self.actual_12_state_leak_failure = None
        self.cap_T_official_failure = None

    def record(self, name, source, expected, actual, details, seconds):
        row = self.models[name]
        row['runtime_seconds'] += seconds
        row['evaluations'][source] = row['evaluations'].get(source, 0) + 1
        if actual == expected:
            return
        row['kills'][source] = row['kills'].get(source, 0) + 1
        failure = {'source': source, 'expected': expected, 'actual': actual, **details}
        for field in ('expected', 'actual'):
            answers = failure[field]
            if isinstance(answers, list) and len(answers) > DETAIL_LIMIT:
                failure[field] = answers[:DETAIL_LIMIT]
                failure[field + '_count'] = len(answers)
                failure[field + '_truncated_answer_count'] = len(answers) - DETAIL_LIMIT
        if row['first_failure'] is None:
            row['first_failure'] = failure
        if source.endswith('.in'):
            column = self.matrix.setdefault(source, {})
            column.setdefault(name, failure)

    def case(self, source, index, n, k, edges, expected):
        base = forced_values(n, edges)
        correct = verified_sum(base, edges)
        if correct != expected:
            raise CheckError('mutation control disagrees with checked answer')
        for name in self.models:
            if name in ('early_exit_desync', 'state_leak', 'cap_T_at_10'):
                continue
            started = time.perf_counter()
            actual = mutant_value(name, n, k, edges, base, correct)
            self.record(name, source, expected, actual,
                        {'test': index, **case_summary(n, k, edges)},
                        time.perf_counter() - started)

    def stream(self, source, tokens, expected, official=False):
        started = time.perf_counter()
        early_exits = []
        actual = simulate_desync(tokens, early_exits)
        self.record('early_exit_desync', source, expected, actual,
                    {'scope': 'entire stdin file/batch', 'early_exits': early_exits},
                    time.perf_counter() - started)
        if official and actual != expected:
            for event in early_exits:
                if (event['synchronized_before_exit'] and event['unread_edges'] > 0
                        and event['has_later_testcase'] and event['total_tests'] == len(expected)
                        and expected[event['test'] - 1] == -1):
                    self.true_official_desync_witnesses.append(
                        {'source': source, **event, 'expected': expected, 'actual': actual})

    def state_stream(self, source, tokens, expected, official=False):
        started = time.perf_counter()
        actual = simulate_state_leak(tokens)
        first = next((i + 1 for i, (want, got) in enumerate(zip(expected, actual))
                      if want != got), None)
        details = {'scope': 'entire stdin file/batch', 'first_differing_test': first}
        self.record('state_leak', source, expected, actual, details,
                    time.perf_counter() - started)
        if official and source == '12.in' and actual != expected:
            self.actual_12_state_leak_failure = {
                'source': source, 'expected': expected, 'actual': actual, **details}

    def cap_stream(self, source, tokens, expected, gen):
        started = time.perf_counter()
        actual = simulate_cap_T_at_10(tokens, gen)
        details = {'scope': 'first ten tests of entire stdin',
                   'expected_answer_count': len(expected), 'actual_answer_count': len(actual)}
        self.record('cap_T_at_10', source, expected, actual, details,
                    time.perf_counter() - started)
        if source in ('3.in', '29.in') and len(expected) > 10 and actual == expected[:10]:
            self.cap_T_official_failure = {'source': source, **details}

    def finish(self, report):
        survivors = [name for name, row in self.models.items() if not row['kills']]
        official_untested = [name for name, row in self.models.items()
                             if not any(source.endswith('.in') for source in row['evaluations'])]
        official_survivors = [name for name in self.models if name not in official_untested
                              and not any(name in column for column in self.matrix.values())]
        for name, row in self.models.items():
            files = sorted((file for file, column in self.matrix.items() if name in column),
                           key=lambda file: int(file.split('.')[0]))
            row['killing_files'] = files
            row['first_official_failure'] = self.matrix[files[0]][name] if files else None
        report.data['mutations'] = {
            'model_count': len(self.models), 'models': self.models,
            'file_kill_matrix': self.matrix, 'survivors': survivors,
            'official_survivors': official_survivors, 'official_untested': official_untested,
            'has_true_official_desync_witness': bool(self.true_official_desync_witnesses),
            'true_official_desync_witnesses': self.true_official_desync_witnesses,
            'selection': 'Per-case models: actual profiles 1..5 only (non-micro cases). '
                         'Desync and state-leak streams: actual profiles 1..5,12,26,28. '
                         'T-cap streams: actual 3.in and 29.in. All cases still checked '
                         'against generator, answers, bounds and independent tiny oracle. '
                         'Also exhaustive tiny cases, randomized cases, and exact gadgets.',
            'claim': 'Only these explicitly defined wrong models are tested; '
                     'this is not proof that all wrong solutions are killed.',
        }
        has_witness = bool(self.true_official_desync_witnesses)
        state_killed_12 = self.actual_12_state_leak_failure is not None
        report.data['release_gates'] = {
            'has_true_official_desync_witness': has_witness,
            'desync_requirement': 'Actual official stream, synchronized before the exit, '
                                  'unread_edges > 0, a later testcase, and incorrect process result.',
            'desync_witnesses': self.true_official_desync_witnesses,
            'state_leak_killed_by_actual_12': state_killed_12,
            'state_leak_actual_12_failure': self.actual_12_state_leak_failure,
            'cap_T_at_10_killed_by_actual_3_or_29': self.cap_T_official_failure is not None,
            'cap_T_at_10_official_failure': self.cap_T_official_failure,
            'official_29_T500000': report.data.get('official_29_T500000', False),
        }
        if not has_witness:
            report.fail('release/has_true_official_desync_witness',
                        'no actual official early exit with unread edges and a later testcase')
        if not state_killed_12:
            report.fail('release/state_leak', 'state-leak model was not killed by actual 12.in')
        if self.cap_T_official_failure is None:
            report.fail('release/cap_T_at_10', 'T-cap model was not killed by actual 3.in or 29.in')
        if not report.data.get('official_29_T500000', False):
            report.fail('release/official_29_T500000',
                        'actual 29.in must have T=sum_n=sum_m=500000 and be accepted by '
                        'validator, std and reference with 500000 correct answers each')
        if survivors:
            report.fail('mutations', 'meaningful model survived every checked case', models=survivors)
        if official_survivors:
            report.fail('mutations/official', 'intended-covered model survived selected official data',
                        models=official_survivors)
        if official_untested:
            report.fail('mutations/official', 'models could not be evaluated on actual official data',
                        models=official_untested)


class MemoryTokens:
    def __init__(self, payload):
        self.tokens = iter(payload.split())
        self.sum_n = 0
        self.sum_m = 0

    def integer(self):
        token = next(self.tokens, None)
        if token is None or not INTEGER.fullmatch(token):
            raise CheckError('missing or non-integer token')
        return int(token)

    def end(self):
        if next(self.tokens, None) is not None:
            raise CheckError('unread input after early exit')


def exhaustive_cases():
    for n in (1, 2, 3):
        alphabet = [(x, y, z) for x in range(1, n + 1)
                    for y in range(1, n + 1) for z in (0, 1)]
        for m in range(4):
            for edges in itertools.product(alphabet, repeat=m):
                yield n, 1, list(edges), None


def randomized_cases(gen):
    rng = random.Random(RANDOM_SEED)
    for index in range(2000):
        n, k, m = rng.randint(1, 6), rng.randint(1, 4), rng.randint(0, 18)
        mode = index % 4
        if mode < 2:
            edges = [(rng.randint(1, n), rng.randint(1, n), rng.randrange(1 << k))
                     for _ in range(m)]
            yield n, k, edges, None
        elif mode == 2:
            witness = [rng.randrange(1 << k) for _ in range(n)]
            edges = []
            for _ in range(m):
                x, y = rng.randint(1, n), rng.randint(1, n)
                edges.append((x, y, witness[x - 1] & witness[y - 1]))
            yield n, k, edges, None
        else:
            valid = bool(rng.getrandbits(1))
            if not valid:
                m = max(m, 2)
            feasible = [g for g, (low_n, low_m) in gen.GADGET_LIMITS.items()
                        if low_n <= n and low_m <= m]
            spec = gen.TestSpec(n, m, k, topology=rng.choice(gen.TOPOLOGIES),
                                mask=rng.choice(gen.MASKS), satisfiable=valid,
                                gadget='auto' if valid else rng.choice(feasible),
                                order=rng.choice(gen.ORDERS), mixed_loops=True)
            case = gen.make_case(spec, 'harness-random/%d/%d' % (RANDOM_SEED, index))
            yield n, k, case.edges, case.result


def targeted_cases():
    full = (1 << 30) - 1
    gadgets = [
        ('empty', 3, 30, []),
        ('positive_pair', 2, 1, [(1, 2, 1)]),
        ('positive_loop', 1, 1, [(1, 1, 1)]),
        ('conflicting_loop', 1, 1, [(1, 1, 1), (1, 1, 0)]),
        ('reverse_duplicate', 2, 1, [(1, 2, 1), (2, 1, 0)]),
        ('disjoint_bits_star', 3, 2, [(1, 2, 1), (1, 3, 2)]),
        ('late_or_growth', 4, 1, [(2, 3, 0), (1, 2, 1), (3, 4, 1)]),
        ('triangle', 3, 1, [(1, 2, 1), (2, 3, 1), (1, 3, 0)]),
        ('component_not_constant', 3, 1, [(1, 2, 1), (2, 3, 0)]),
        ('degree_three_valid', 4, 1, [(1, 2, 1), (1, 3, 1), (1, 4, 1)]),
        ('disconnected_valid', 4, 1, [(1, 2, 1), (3, 4, 1)]),
        ('repeated_positive', 2, 1, [(1, 2, 1), (1, 2, 1)]),
        ('bit29', 2, 30, [(1, 2, 1 << 29)]),
        ('signed_and_unsigned_overflow', 5, 30, [(i, i, full) for i in range(1, 6)]),
        ('early_failure_unread_padding', 2, 1,
         [(1, 2, 1), (2, 1, 0), (1, 1, 0), (2, 2, 0)]),
        ('after_early_failure', 1, 1, []),
        ('state_leak_force_high_vertex', 6, 4, [(6, 6, 8)]),
        ('state_leak_shrink_empty', 1, 1, []),
        ('state_leak_grow_empty', 6, 1, []),
    ]
    return gadgets


def check_small(source, cases, gen, commands, options, report, mutations):
    started = time.perf_counter()
    stats = {'cases': 0, 'valid': 0, 'invalid': 0, 'batches': 0,
             'cases_by_n': {}, 'n_min': None, 'n_max': None, 'k_min': None, 'k_max': None,
             'process_runtime_seconds': {name: 0.0 for name in commands if name != 'validator'}}
    if source == 'randomized':
        stats['seed'] = RANDOM_SEED
    batch = []

    def flush():
        check_count(len(batch))
        if (sum(case[0] for case in batch) > MAX_SUM_N
                or sum(len(case[2]) for case in batch) > MAX_SUM_M):
            raise CheckError('small batch exceeds aggregate budgets')
        payload = encode_cases(batch)
        expected = [case[3] for case in batch]
        where = '%s/batch%d' % (source, stats['batches'] + 1)
        for name, command in commands.items():
            if name == 'validator':
                continue
            info = check_program(report, where, name, command, options.timeout,
                                 expected, payload=payload)
            stats['process_runtime_seconds'][name] += info['runtime_seconds']
            if 'error' in info:
                failed = report.data.setdefault('failed_small_batches', [])
                if len(failed) < 100:
                    failed.append({'where': where, 'program': name, 'cases': batch.copy()})
        mutations.stream(source, MemoryTokens(payload), expected)
        mutations.state_stream(source, MemoryTokens(payload), expected)
        mutations.cap_stream(source, MemoryTokens(payload), expected, gen)
        stats['batches'] += 1
        batch.clear()

    for n, k, edges, claimed in cases:
        stats['cases'] += 1
        stats['cases_by_n'][str(n)] = stats['cases_by_n'].get(str(n), 0) + 1
        for field, value in (('n', n), ('k', k)):
            stats[field + '_min'] = value if stats[field + '_min'] is None else min(stats[field + '_min'], value)
            stats[field + '_max'] = value if stats[field + '_max'] is None else max(stats[field + '_max'], value)
        expected = brute_per_bit(n, k, edges)
        actual = gen.answer(n, k, edges)
        if actual != expected or claimed is not None and claimed != expected:
            report.fail(source, 'generator disagrees with independent per-bit oracle',
                        test=stats['cases'], expected=expected, actual=actual,
                        claimed=claimed, **case_summary(n, k, edges))
        stats['valid' if expected != -1 else 'invalid'] += 1
        mutations.case(source, stats['cases'], n, k, edges, expected)
        batch.append((n, k, edges, expected))
        if len(batch) == BATCH_SIZE:
            flush()
    if batch:
        flush()
    stats['runtime_seconds'] = time.perf_counter() - started
    stats['oracle'] = ('All 2**n Boolean assignments independently per bit; minimum ones weighted '
                       'by 2**bit. n=1 uses analytic enumeration of its two choices; tiny keys cached.')
    report.data[source] = stats
    print('%s: %d cases, %d batches, %.3fs' %
          (source, stats['cases'], stats['batches'], stats['runtime_seconds']), flush=True)


class CompareSink:
    """Text writer comparing regenerated chunks directly with the existing file."""
    def __init__(self, source):
        self.source = source
        self.sha = hashlib.sha256()
        self.bytes = 0
        self.first_mismatch = None

    def write(self, text):
        raw = text.encode('ascii')
        actual = self.source.read(len(raw))
        if actual != raw and self.first_mismatch is None:
            common = min(len(raw), len(actual))
            offset = next((i for i in range(common) if raw[i] != actual[i]), common)
            self.first_mismatch = self.bytes + offset
        self.sha.update(raw)
        self.bytes += len(raw)
        return len(text)

    def finish(self):
        if self.source.read(1) and self.first_mismatch is None:
            self.first_mismatch = self.bytes
        return {'generated_sha256': self.sha.hexdigest(), 'generated_bytes': self.bytes,
                'match': self.first_mismatch is None, 'first_mismatch_byte': self.first_mismatch}


def check_determinism(profile, input_path, answer_path, gen):
    started = time.perf_counter()
    with input_path.open('rb') as source, answer_path.open('rb') as answer:
        input_sink, answer_sink = CompareSink(source), CompareSink(answer)
        gen.gen(input_sink, {}, {'case': profile}, seed=0, answers=answer_sink)
        info = {'seed': 0, 'input': input_sink.finish(), 'answer': answer_sink.finish()}
    info['runtime_seconds'] = time.perf_counter() - started
    return info


def inspect_official(profile, path, expected, gen, report, mutations):
    started = time.perf_counter()
    tests = []
    valid = independent = mutation_cases = 0
    n_min, n_max, k_min, k_max = MAX_N, 0, MAX_K, 0
    metadata = gen.PROFILES[profile]
    specs = None if metadata.sample else metadata.tests
    with path.open('rb') as source:
        tokens = TokenStream(source)
        count = tokens.integer()
        check_count(count)
        if count != len(expected):
            raise CheckError('answer count differs from T')
        if specs is not None and count != len(specs):
            raise CheckError('T differs from official profile')
        for index in range(count):
            n, k, edges = read_case(tokens)
            if specs is not None and (n, len(edges), k) != (
                    specs[index].n, specs[index].m, specs[index].k):
                raise CheckError('test %d dimensions differ from official profile' % (index + 1))
            answer = expected[index]
            if not (answer == -1 or 0 <= answer <= n * ((1 << k) - 1)):
                raise CheckError('answer outside possible range')
            computed = gen.answer(n, k, edges)
            if answer != computed:
                report.fail(path.name, 'official answer disagrees with generator',
                            test=index + 1, expected=answer, actual=computed)
            if specs is not None and (computed != -1) != specs[index].satisfiable:
                report.fail(path.name, 'satisfiability differs from official profile', test=index + 1)
            independently_checked = n <= 9 and len(edges) <= 32
            if independently_checked:
                oracle = brute_per_bit(n, k, edges)
                if oracle != answer or oracle != computed:
                    report.fail(path.name, 'official tiny case disagrees with independent oracle',
                                test=index + 1, expected=oracle, answer=answer, generator=computed)
            selected_for_case_mutations = profile in CASE_MUTATION_PROFILES
            if selected_for_case_mutations:
                mutations.case(path.name, index + 1, n, k, edges, computed)
            valid += computed != -1
            independent += independently_checked
            mutation_cases += selected_for_case_mutations
            n_min, n_max = min(n_min, n), max(n_max, n)
            k_min, k_max = min(k_min, k), max(k_max, k)
            # Never allocate 500000 testcase dictionaries for the micro profile.
            if len(tests) < DETAIL_LIMIT:
                tests.append({'test': index + 1, 'n': n, 'm': len(edges), 'k': k,
                              'answer': answer, 'valid': computed != -1,
                              'independent_oracle': independently_checked,
                              'per_case_mutations': selected_for_case_mutations})
            del edges
        tokens.end()
        digest, byte_count = tokens.sha.hexdigest(), tokens.bytes
        sum_n, sum_m = tokens.sum_n, tokens.sum_m
    if profile in STREAM_MUTATION_PROFILES:
        with path.open('rb') as source:
            mutations.stream(path.name, TokenStream(source), expected, official=True)
        with path.open('rb') as source:
            mutations.state_stream(path.name, TokenStream(source), expected, official=True)
    if profile in (3, 29):
        with path.open('rb') as source:
            mutations.cap_stream(path.name, TokenStream(source), expected, gen)
    return {'tests': count, 'testcases': tests,
            'testcases_truncated': count > len(tests),
            'truncated_testcase_count': count - len(tests),
            'testcase_detail_note': 'First 100 only; all tests parsed and checked.',
            'sum_n': sum_n, 'sum_m': sum_m, 'n_min': n_min, 'n_max': n_max,
            'k_min': k_min, 'k_max': k_max, 'valid': valid, 'invalid': count - valid,
            'independent_oracle_cases': independent, 'per_case_mutation_cases': mutation_cases,
            'input_bytes': byte_count, 'input_sha256': digest,
            'inspection_runtime_seconds': time.perf_counter() - started}


def check_T_stress_release(row, expected):
    """Evaluate before report-only answer truncation; require the real reference."""
    processes = row['processes']
    if (row.get('tests') != DERIVED_MAX_T or row.get('sum_n') != MAX_SUM_N
            or row.get('sum_m') != MAX_SUM_M or expected is None
            or len(expected) != DERIVED_MAX_T
            or not processes.get('validator', {}).get('accepted')):
        return False
    return all('error' not in processes.get(name, {})
               and processes.get(name, {}).get('returncode') == 0
               and processes.get(name, {}).get('answers') == expected
               for name in ('std', 'reference'))


def trim_process_answers(info):
    answers = info.get('answers')
    if answers is not None:
        info['answer_count'] = len(answers)
        info['answers_truncated'] = len(answers) > DETAIL_LIMIT
        info['truncated_answer_count'] = max(0, len(answers) - DETAIL_LIMIT)
        if info['answers_truncated']:
            info['answers'] = answers[:DETAIL_LIMIT]


def check_official(gen, commands, options, report, mutations):
    started = time.perf_counter()
    for profile in range(1, COUNT + 1):
        file_started = time.perf_counter()
        input_path = options.data_dir / ('%d.in' % profile)
        answer_path = options.data_dir / ('%d.ans' % profile)
        row = {'file': input_path.name, 'profile': profile, 'processes': {}}
        report.data['files'].append(row)
        failures_before = report.data['failure_count']
        if not input_path.is_file():
            report.fail(input_path.name, 'missing official input')
            row['status'] = 'missing'
            row['runtime_seconds'] = time.perf_counter() - file_started
            continue
        expected = None
        try:
            with answer_path.open('rb') as source:
                raw = source.read(MAX_OUTPUT_BYTES + 1)
            expected = output_integers(raw)
            row['answer_sha256'] = hashlib.sha256(raw).hexdigest()
        except (OSError, CheckError) as exc:
            report.fail(answer_path.name, exc)
        for name, command in commands.items():
            row['processes'][name] = check_program(
                report, input_path.name, name, command, options.timeout, expected,
                input_path=input_path)
        std_answers = row['processes']['std'].get('answers')
        if expected is None and std_answers is not None:
            expected = std_answers
        reference_answers = row['processes'].get('reference', {}).get('answers')
        if std_answers is not None and reference_answers is not None and std_answers != reference_answers:
            report.fail(input_path.name + '/reference', 'standard and reference disagree',
                        std=std_answers[:DETAIL_LIMIT], reference=reference_answers[:DETAIL_LIMIT],
                        std_answer_count=len(std_answers), reference_answer_count=len(reference_answers))
        try:
            if expected is not None:
                row.update(inspect_official(profile, input_path, expected, gen, report, mutations))
        except (OSError, ValueError, CheckError, AssertionError) as exc:
            report.fail(input_path.name + '/parse', exc)
        if profile == 29:
            report.data['official_29_T500000'] = (
                report.data['failure_count'] == failures_before
                and check_T_stress_release(row, expected))
        # Keep full lists until parsing, mutations, release checks and process
        # comparisons finish; only the stored report gets truncated.
        for info in row['processes'].values():
            trim_process_answers(info)
        if options.quick and profile > 18:
            row['determinism'] = {'status': 'skipped', 'reason': '--quick; profile > 18'}
        else:
            try:
                row['determinism'] = check_determinism(profile, input_path, answer_path, gen)
                if not all(row['determinism'][kind]['match'] for kind in ('input', 'answer')):
                    report.fail(input_path.name + '/determinism',
                                'default-seed regeneration differs from existing bytes',
                                comparison=row['determinism'])
            except (OSError, ValueError, AssertionError) as exc:
                report.fail(input_path.name + '/determinism', exc)
        row['runtime_seconds'] = time.perf_counter() - file_started
        row['status'] = 'pass' if report.data['failure_count'] == failures_before else 'fail'
        print('%2d.in: %s T=%s n=%s m=%s %.3fs' % (
            profile, row['status'], row.get('tests', '?'), row.get('sum_n', '?'),
            row.get('sum_m', '?'), row['runtime_seconds']), flush=True)
    parsed = [row for row in report.data['files'] if 'tests' in row]
    report.data['official'] = {
        'expected_files': COUNT, 'parsed_files': len(parsed),
        'tests': sum(row['tests'] for row in parsed),
        'sum_n': sum(row['sum_n'] for row in parsed),
        'sum_m': sum(row['sum_m'] for row in parsed),
        'input_bytes': sum(row['input_bytes'] for row in parsed),
        'valid': sum(row['valid'] for row in parsed),
        'invalid': sum(row['invalid'] for row in parsed),
        'runtime_seconds': time.perf_counter() - started,
    }


def validator_corpora():
    """Accept unsatisfiable equations; reject syntax, per-test, or per-file bound violations."""
    valid_cases = [
        (1, 1, [], 0),
        (2, 1, [(1, 2, 1)], 2),
        (3, 2, [(1, 2, 1), (1, 3, 2)], 6),
        (1, 30, [(1, 1, (1 << 30) - 1)], (1 << 30) - 1),
        (3, 1, [(1, 1, 0), (1, 1, 0), (2, 3, 0)], 0),
    ]
    unsat_cases = [
        (1, 1, [(1, 1, 1), (1, 1, 0)], -1),
        (3, 1, [(1, 2, 1), (2, 3, 1), (1, 3, 0)], -1),
        (2, 2, [(1, 2, 1), (2, 1, 2)], -1),
    ]
    positive = [
        ('valid_equations', encode_cases(valid_cases)),
        ('unsatisfiable_equations', encode_cases(unsat_cases)),
        ('ten_mixed_tests', encode_cases((valid_cases[:2] + unsat_cases[:3]) * 2)),
        ('maximum_n_empty', b'2\n200000 0 30\n200000 0 1\n'),
        ('T_eleven_valid', b'11\n' + b'1 0 1\n' * 11),
        ('T500000_empty', b'500000\n' + b'1 0 30\n' * DERIVED_MAX_T),
    ]
    malformed = [
        ('empty_input', b''), ('T_zero', b'0\n'), ('T_eleven_truncated', b'11\n'),
        ('T_negative', b'-1\n'),
        ('T_above_aggregate_possible', b'500001\n' + b'1 0 1\n' * 500001),
        ('T_uint64_overflow', b'18446744073709551616\n'),
        ('n_zero', b'1\n0 0 1\n'), ('n_too_large', b'1\n200001 0 1\n'),
        ('m_negative', b'1\n1 -1 1\n'), ('m_too_large', b'1\n1 200001 1\n'),
        ('k_zero', b'1\n1 0 0\n'), ('k_thirty_one', b'1\n1 0 31\n'),
        ('x_zero', b'1\n2 1 1\n0 1 0\n'), ('x_n_plus_one', b'1\n2 1 1\n3 1 0\n'),
        ('y_zero', b'1\n2 1 1\n1 0 0\n'), ('y_n_plus_one', b'1\n2 1 1\n1 3 0\n'),
        ('z_limit_low_bit', b'1\n1 1 1\n1 1 2\n'),
        ('z_limit_bit_thirty', b'1\n1 1 30\n1 1 1073741824\n'),
        ('z_negative', b'1\n1 1 1\n1 1 -1\n'),
        ('uint64_overflow', b'1\n1 1 30\n1 1 18446744073709551616\n'),
        ('truncated_header', b'1\n1 0\n'),
        ('truncated_edge', b'1\n1 1 1\n1 1\n'),
        ('truncated_later_test', b'2\n1 0 1\n'),
        ('trailing_token', b'1\n1 0 1\n9\n'),
        ('non_decimal_token', b'1\n1_0 0 1\n'),
        ('legacy_c_zero_then_T', b'0 1\n1 0 1\n'),
        ('legacy_c_one_then_T', b'1 1\n1 0 1\n'),
    ]
    huge = b'9' * 1000
    malformed.extend([
        ('huge_decimal_T', huge + b'\n'),
        ('huge_decimal_n', b'1\n' + huge + b' 0 1\n'),
        ('huge_decimal_m', b'1\n1 ' + huge + b' 1\n'),
        ('huge_decimal_k', b'1\n1 0 ' + huge + b'\n'),
        ('huge_decimal_x', b'1\n1 1 1\n' + huge + b' 1 0\n'),
        ('huge_decimal_y', b'1\n1 1 1\n1 ' + huge + b' 0\n'),
        ('huge_decimal_z', b'1\n1 1 1\n1 1 ' + huge + b'\n'),
    ])
    aggregate_cases = [
        (positive, 'aggregate_exact_sum_n', [(200000, 0), (200000, 0), (100000, 0)]),
        (positive, 'aggregate_exact_sum_m', [(1, 200000), (1, 200000), (1, 100000)]),
        (positive, 'aggregate_exact_both',
         [(200000, 200000), (200000, 200000), (100000, 100000)]),
        (positive, 'aggregate_exact_both_T10',
         [(200000, 200000), (200000, 200000), (99993, 100000)] + [(1, 0)] * 7),
        (malformed, 'aggregate_sum_n_500001', [(200000, 0), (200000, 0), (100001, 0)]),
        (malformed, 'aggregate_sum_m_500001', [(1, 200000), (1, 200000), (1, 100001)]),
        (malformed, 'aggregate_sum_n_late_plus_one',
         [(200000, 0), (200000, 0), (100000, 0), (1, 1)]),
        (malformed, 'aggregate_sum_m_late_plus_one',
         [(1, 200000), (1, 200000), (1, 100000), (1, 1)]),
        (malformed, 'aggregate_sum_n_T10_plus_one',
         [(200000, 0), (200000, 0), (99993, 0)] + [(1, 0)] * 6 + [(2, 1)]),
        (malformed, 'aggregate_sum_m_T10_plus_one',
         [(1, 200000), (1, 200000), (1, 100000)] + [(1, 0)] * 6 + [(1, 1)]),
    ]
    for corpus, label, specs in aggregate_cases:
        payload = str(len(specs)).encode('ascii') + b'\n' + b''.join(
            ('%d %d 1\n' % (n, m)).encode('ascii') + b'1 1 0\n' * m for n, m in specs)
        corpus.append((label, payload))
    return positive, malformed


def check_validator_corpus(command, options, report):
    started = time.perf_counter()
    positive, malformed = validator_corpora()
    stats = {'positive': [], 'malformed': [], 'accepted_positive': 0,
             'rejected_malformed': 0, 'command': command,
             'contract': 'Exit 0 on valid syntax within independent aggregate budgets, '
                         'including unsatisfiable equations; normal nonzero exit on syntax '
                         'or bound violations. Aggregate diagnostics must identify sum_n or sum_m. '
                         'T has no independent upper bound; T above 500000 must identify '
                         'T and the implied sum_n budget. Timeout/crash is a failure.'}
    report.data['validator_corpus'] = stats
    before = report.data['failure_count']
    for category, corpus in (('positive', positive), ('malformed', malformed)):
        for label, payload in corpus:
            info, _ = run_process(command, options.timeout, payload=payload)
            row = {'name': label, 'input_bytes': len(payload),
                   'input_sha256': hashlib.sha256(payload).hexdigest(), 'process': info}
            stats[category].append(row)
            code = info.get('returncode')
            passed = code == 0 if category == 'positive' else code is not None and 0 < code < 256
            axis = next((axis for axis in ('sum_n', 'sum_m')
                         if label.startswith('aggregate_' + axis + '_')), None)
            if category == 'malformed' and axis is not None:
                row['expected_aggregate_axis'] = axis
                diagnostic = info.get('stderr', '')
                passed = (passed and axis in diagnostic and '500000' in diagnostic
                          and ('sum_m' if axis == 'sum_n' else 'sum_n') not in diagnostic)
            if category == 'malformed' and label in (
                    'T_above_aggregate_possible', 'T_uint64_overflow', 'huge_decimal_T'):
                diagnostic = info.get('stderr', '')
                row['expected_derived_axis'] = 'T implies sum_n'
                passed = (passed and 'T' in diagnostic and 'sum_n' in diagnostic
                          and '500000' in diagnostic)
            row['passed'] = passed
            if passed:
                stats['accepted_positive' if category == 'positive' else 'rejected_malformed'] += 1
                if category == 'malformed':
                    info['expected_rejection'] = info.pop('error', 'normal nonzero exit')
            else:
                expectation = 'accept valid syntax within bounds' if category == 'positive' else (
                    'reject bound violation with a %s diagnostic' % axis if axis is not None
                    else 'reject malformed syntax')
                report.fail('validator_corpus/' + label, 'validator did not ' + expectation,
                            process=info)
    stats['runtime_seconds'] = time.perf_counter() - started
    stats['status'] = 'pass' if report.data['failure_count'] == before else 'fail'
    print('Validator corpus: %d/%d accepted, %d/%d rejected, %.3fs (%s)' % (
        stats['accepted_positive'], len(positive), stats['rejected_malformed'], len(malformed),
        stats['runtime_seconds'], stats['status']), flush=True)


def parser_self_checks():
    import io
    valid = b'2\n1 0 1\n2 2 30\n1 2 0\n2 2 536870912\n'
    positive, malformed = validator_corpora()

    def parse(raw):
        tokens = TokenStream(io.BytesIO(raw))
        count = tokens.integer()
        check_count(count)
        for _ in range(count):
            read_case(tokens)
        tokens.end()
        if tokens.sha.hexdigest() != hashlib.sha256(raw).hexdigest():
            raise CheckError('stream hash mismatch')

    parse(valid)
    boundary = b'1\n1 1 30\n' + b' ' * 65517 + b'1 1 536870912\n'
    parse(boundary)
    for _, payload in positive:
        parse(payload)
    sink = CompareSink(io.BytesIO(b'1\n2\n'))
    sink.write('1\n')
    sink.write('2\n')
    if not sink.finish()['match']:
        raise CheckError('comparison sink rejected identical chunks')
    for expected, actual, offset in ((b'abc', b'axc', 1), (b'ab', b'abc', 2),
                                     (b'abcd', b'abc', 3)):
        sink = CompareSink(io.BytesIO(expected))
        sink.write(actual.decode('ascii'))
        if sink.finish()['first_mismatch_byte'] != offset:
            raise CheckError('comparison sink failed a mismatch/length self-check')
    aggregate_rejections = 0
    for label, raw in malformed:
        axis = next((axis for axis in ('sum_n', 'sum_m')
                     if label.startswith('aggregate_' + axis + '_')), None)
        try:
            parse(raw)
        except CheckError as exc:
            if axis is not None:
                if not str(exc).startswith(axis + ' exceeds '):
                    raise CheckError('%s rejected for the wrong reason: %s' % (label, exc))
                aggregate_rejections += 1
        else:
            raise CheckError('parser accepted invalid input %s (%d bytes)' % (label, len(raw)))
        if axis is not None and label.endswith('plus_one'):
            # The last header already exceeds the budget, even with its edge omitted.
            try:
                parse(raw[:-len(b'1 1 0\n')])
            except CheckError as exc:
                if not str(exc).startswith(axis + ' exceeds '):
                    raise CheckError('%s did not reject before edges: %s' % (label, exc))
            else:
                raise CheckError('%s aggregate overflow was not rejected before edges' % label)
    for scanner in (TokenStream, MemoryTokens):
        for axis, totals in (('sum_n', (500000, 0)), ('sum_m', (0, 500000))):
            raw = b'1 1 1\n'
            tokens = scanner(io.BytesIO(raw)) if scanner is TokenStream else scanner(raw)
            tokens.sum_n, tokens.sum_m = totals
            try:
                read_case(tokens)
            except CheckError as exc:
                if not str(exc).startswith(axis + ' exceeds '):
                    raise CheckError('%s failed independent %s budget check' % (scanner.__name__, axis))
            else:
                raise CheckError('%s accepted %s overflow' % (scanner.__name__, axis))
    return {'valid_examples': 2 + len(positive), 'rejected_examples': len(malformed),
            'aggregate_rejections': aggregate_rejections, 'before_edges_examples': 8,
            'comparison_sink_examples': 4}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent / 'data')
    parser.add_argument('--std', required=True, metavar='PATH')
    parser.add_argument('--validator', required=True, metavar='PATH',
                        help='stdin validator; accept valid/unsat syntax within bounds; reject syntax/aggregate corpus')
    parser.add_argument('--reference', metavar='PATH')
    parser.add_argument('--quick', action='store_true',
                        help='skip default-seed regeneration of profiles 19..%d only' % COUNT)
    parser.add_argument('--report', type=Path, metavar='PATH', help='JSON report; existing parent required')
    parser.add_argument('--timeout', type=float, default=120.0,
                        help='per-process safety timeout in seconds, not a judge limit (default 120)')
    options = parser.parse_args(argv)
    if not options.timeout > 0 or options.timeout == float('inf'):
        parser.error('--timeout must be positive and finite')
    if options.report is not None:
        target = options.report
        protected_dirs = [Path(__file__).resolve().parent / 'down', options.data_dir.resolve()]
        if (not target.parent.is_dir() or target.is_symlink() or target.suffix.lower() != '.json'
                or any(folder == target.resolve() or folder in target.resolve().parents
                       for folder in protected_dirs)):
            parser.error('--report must be a .json path with an existing parent, outside data/down, '
                         'and must not be a symlink')
    report = Results(options)
    mutations = Mutations()
    try:
        gen = load_generator()
        commands = {name: command_for(value) for name, value in (
            ('std', options.std), ('validator', options.validator), ('reference', options.reference))
                    if value is not None}
        if options.report and any(options.report.resolve() == Path(command[-1]).resolve()
                                  for command in commands.values()):
            parser.error('--report must not overwrite an executable')
        report.data['parser_self_checks'] = parser_self_checks()
        check_validator_corpus(commands['validator'], options, report)
        check_small('exhaustive', exhaustive_cases(), gen, commands, options, report, mutations)
        check_small('randomized', randomized_cases(gen), gen, commands, options, report, mutations)
        gadgets = targeted_cases()
        report.data['targeted_gadget_names'] = [g[0] for g in gadgets]
        check_small('targeted', ((n, k, edges, None) for _, n, k, edges in gadgets),
                    gen, commands, options, report, mutations)
        check_official(gen, commands, options, report, mutations)
        mutations.finish(report)
    except (CheckError, OSError, ValueError, AssertionError, ImportError) as exc:
        report.fail('harness', exc)
    except KeyboardInterrupt:
        report.fail('harness', 'interrupted by caller')
    report.finish()
    if options.report is not None:
        try:
            with options.report.open('w', encoding='utf-8', newline='\n') as target:
                json.dump(report.data, target, indent=2, ensure_ascii=True)
                target.write('\n')
        except OSError as exc:
            report.fail('report', exc)
            report.finish()
    matrix = report.data.get('mutations', {})
    if matrix:
        killed = sum(bool(row['killing_files']) for row in matrix['models'].values())
        print('Mutations: %d/%d killed by selected official files (not all possible wrong solutions).' %
              (killed, matrix['model_count']))
        for name, row in matrix['models'].items():
            files = row['killing_files']
            outcome = (files[0] + ' (%d killing files)' % len(files)) if files else (
                'NOT EVALUATED on official data' if name in matrix['official_untested']
                else 'SURVIVED official selection')
            print('  %s: %s' % (name, outcome))
    gates = report.data.get('release_gates')
    if gates:
        print('Release gates: true official desync=%s; state leak killed by actual 12=%s; '
              'T-cap killed by actual 3/29=%s; actual 29 T500000=%s' % (
                  gates['has_true_official_desync_witness'], gates['state_leak_killed_by_actual_12'],
                  gates['cap_T_at_10_killed_by_actual_3_or_29'], gates['official_29_T500000']))
    print('%s: %d failure(s), %.3fs total%s' % (
        report.data['status'].upper(), report.data['failure_count'], report.data['runtime_seconds'],
        '; JSON ' + str(options.report) if options.report else ''))
    for failure in report.data['failures'][:8]:
        print('  %s: %s' % (failure['where'], failure['error']))
    return 1 if report.data['failure_count'] else 0


if __name__ == '__main__':
    sys.exit(main())
