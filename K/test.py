#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""纸带染色 独立评测 / 验题脚本。

它做三件事：

1. **校验数据格式** —— 对 ``data/*.in`` 与 ``down/*.in`` 逐个运行 ``rsy/std/val.cpp``
   （testlib 格式，编译到 ``build/val``），检查 $n,m,q,o_i,x_i,l_j,r_j$ 的取值范围与行数。
2. **独立重算答案** —— 用一份与 ``std.cpp`` 无关的 Python 实现（单调栈 + 双指针 +
   树状数组）重新计算每个询问的答案，与 ``.ans`` 逐行比对。
3. **评测程序** —— 把 ``conf.yaml`` 中 ``users`` 登记的程序（C++ 自动编译，Python 直接
   运行）在全部数据点上跑一遍，统计得分与耗时，与 ``expected`` 比对。

用法::

    python test.py                 # 格式校验 + 独立重算 + 评测全部程序
    python test.py --validate      # 只做前两步，不跑程序
    python test.py --no-ref        # 跳过独立重算（大数据上较快）
    python test.py --only std      # 只评测用户名/代码名里含 "std" 的程序
    python test.py -j 4            # 用 4 个线程并行评测
    python test.py --tl 2.0        # 覆盖 conf.yaml 的时限（本机较慢时用）
    python test.py -o result.csv   # 指定输出 CSV

注意：评测时只限制时间，不限制内存（Windows 下不易实现）；``rsy/bf/bf.cpp`` 已经自带
内存安全阀，遇到 $n$ 过大的数据点会主动放弃并判错。
"""
from __future__ import print_function

import argparse
import array
import os
import subprocess
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor

try:
    import yaml
except ImportError:                                        # pragma: no cover
    yaml = None

ROOT = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(ROOT, 'build')
ELF = '.exe' if os.name == 'nt' else ''
MAXN = 1000000000
MAXMQ = 500000


# --------------------------------------------------------------------------
# 独立实现的参考解（与 std.cpp 无关，只是同一套推导的另一种语言实现）
# --------------------------------------------------------------------------
def reference_solve(n, m, q, op, x, ql, qr):
    """返回每个询问的答案列表，复杂度 O((m + q) log m)。"""
    INF = m + 1

    # nxt[i]：前缀操作为 i 之后第一个 x >= x_i 的前缀操作，后缀操作同理取 <=
    nxt = array.array('i', [INF]) * (m + 2)
    stk = []
    for i in range(1, m + 1):
        if op[i] == 0:
            while stk and x[stk[-1]] <= x[i]:
                nxt[stk.pop()] = i
            stk.append(i)
    del stk[:]
    for i in range(1, m + 1):
        if op[i] == 1:
            while stk and x[stk[-1]] >= x[i]:
                nxt[stk.pop()] = i
            stk.append(i)

    # full[r]：使操作 full[r]..r 能覆盖整条纸带的最大下标，不存在为 0
    full = array.array('i', [0]) * (m + 2)
    dqmax, dqmin = deque(), deque()
    lo = 1
    for r in range(1, m + 1):
        if op[r] == 0:
            while dqmax and x[dqmax[-1]] <= x[r]:
                dqmax.pop()
            dqmax.append(r)
        else:
            while dqmin and x[dqmin[-1]] >= x[r]:
                dqmin.pop()
            dqmin.append(r)
        while lo < r:
            P = 0
            if dqmax:
                P = x[dqmax[0]]
                if dqmax[0] == lo:
                    P = x[dqmax[1]] if len(dqmax) >= 2 else 0
            S = n + 1
            if dqmin:
                S = x[dqmin[0]]
                if dqmin[0] == lo:
                    S = x[dqmin[1]] if len(dqmin) >= 2 else n + 1
            if P >= S - 1:
                if dqmax and dqmax[0] == lo:
                    dqmax.popleft()
                if dqmin and dqmin[0] == lo:
                    dqmin.popleft()
                lo += 1
            else:
                break
        P = x[dqmax[0]] if dqmax else 0
        S = x[dqmin[0]] if dqmin else n + 1
        full[r] = lo if P >= S - 1 else 0

    # 询问按 r 分桶
    head = array.array('i', [-1]) * (m + 2)
    qnext = array.array('i', [-1]) * q
    qleft = array.array('i', [0]) * q
    for j in range(q):
        r = qr[j]
        qleft[j] = ql[j]
        qnext[j] = head[r]
        head[r] = j

    # 激活位置按 nxt[i] 分桶
    bhead = array.array('i', [-1]) * (m + 2)
    bnext = array.array('i', [-1]) * (m + 1)
    for i in range(1, m + 1):
        t = nxt[i] if nxt[i] <= m else m + 1
        bnext[i] = bhead[t]
        bhead[t] = i

    bit = array.array('i', [0]) * (m + 2)
    ans = array.array('i', [0]) * q
    for R in range(m, 0, -1):
        t = m + 1 if R == m else R + 1
        i = bhead[t]
        while i != -1:
            j = i
            while j <= m:
                bit[j] += 1
                j += j & (-j)
            i = bnext[i]
        i = head[R]
        while i != -1:
            A = qleft[i] if qleft[i] > full[R] else full[R]
            s = 0
            j = R
            while j > 0:
                s += bit[j]
                j -= j & (-j)
            j = A - 1
            while j > 0:
                s -= bit[j]
                j -= j & (-j)
            ans[i] = s
            i = qnext[i]
    return ans


def load_case(infile):
    """读入数据文件，返回 (n, m, q, op, x, ql, qr)。"""
    with open(infile, 'r') as f:
        tokens = f.read().split()
    n, m, q = int(tokens[0]), int(tokens[1]), int(tokens[2])
    op = array.array('i', [0]) * (m + 1)
    x = array.array('i', [0]) * (m + 1)
    pos = 3
    for i in range(1, m + 1):
        op[i] = int(tokens[pos])
        x[i] = int(tokens[pos + 1])
        pos += 2
    ql = array.array('i', [0]) * q
    qr = array.array('i', [0]) * q
    for j in range(q):
        ql[j] = int(tokens[pos])
        qr[j] = int(tokens[pos + 1])
        pos += 2
    return n, m, q, op, x, ql, qr


# --------------------------------------------------------------------------
# 编译 / 运行
# --------------------------------------------------------------------------
def compile_cpp(src, dst, std='c++17', extra_flags=()):
    """编译 src 到 dst；两者都可以是绝对路径。

    注意：题目目录里有非 ASCII 字符（``长春``），MinGW 的 ld 无法写这种路径的输出文件，
    因此这里统一用「相对 ROOT 的路径 + cwd=ROOT」来调用 g++。
    """
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    rel_src = os.path.relpath(src, ROOT).replace('\\', '/')
    rel_dst = os.path.relpath(dst, ROOT).replace('\\', '/')
    cmd = ['g++', '-O2', '-std=' + std, '-Wall', '-o', rel_dst, rel_src]
    cmd.extend(extra_flags)
    p = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        raise RuntimeError('编译失败: %s\n%s' % (' '.join(cmd),
                                                p.stdout.decode('utf-8', 'replace')))
    return rel_dst


def prepare_program(path):
    src = os.path.join(ROOT, path)
    if not os.path.exists(src):
        raise RuntimeError('找不到程序 %s' % path)
    stem = os.path.splitext(os.path.basename(path))[0]
    if path.endswith('.py'):
        return [sys.executable, os.path.relpath(src, ROOT)]
    exe = os.path.join(BIN, stem + ELF)
    if (not os.path.exists(exe)) or os.path.getmtime(exe) < os.path.getmtime(src):
        compile_cpp(src, exe)
    return [os.path.relpath(exe, ROOT).replace('\\', '/')]


def run_case(cmd, infile, ansfile, time_limit):
    """返回 (是否通过, 用时秒, 报告)。cmd 为相对 ROOT 的命令。"""
    with open(infile, 'rb') as fin:
        t0 = time.perf_counter()
        try:
            p = subprocess.run(cmd, cwd=ROOT, stdin=fin, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=time_limit)
        except subprocess.TimeoutExpired:
            return False, time.perf_counter() - t0, 'TLE (>%.2fs)' % time_limit
        elapsed = time.perf_counter() - t0
    with open(ansfile, 'rb') as f:
        expected = f.read().split()
    got = p.stdout.split()
    if got == expected:
        return True, elapsed, 'ok'
    if p.returncode != 0:
        err = p.stderr.decode('utf-8', 'replace').strip().split('\n')[-1]
        return False, elapsed, 'RE (exit %d) %s' % (p.returncode, err[:80])
    if len(got) != len(expected):
        return False, elapsed, 'WA (输出 %d 行，应为 %d 行)' % (len(got), len(expected))
    for k, (a, b) in enumerate(zip(got, expected)):
        if a != b:
            return False, elapsed, 'WA (第 %d 行 %s != %s)' % (k + 1, a.decode(), b.decode())
    return False, elapsed, 'WA'


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def load_conf():
    if yaml is None:
        raise SystemExit('需要 PyYAML：pip install pyyaml')
    with open(os.path.join(ROOT, 'conf.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def collect_cases(conf):
    tests, samples = [], []
    for group in (conf.get('data') or []):
        for cs in group['cases']:
            tests.append((str(cs),
                          os.path.join(ROOT, 'data', '%s.in' % cs),
                          os.path.join(ROOT, 'data', '%s.ans' % cs)))
    for group in (conf.get('samples') or []):
        for cs in group['cases']:
            samples.append((str(cs),
                            os.path.join(ROOT, 'down', '%s.in' % cs),
                            os.path.join(ROOT, 'down', '%s.ans' % cs)))
    return tests, samples


def validate(case_list, do_ref):
    """格式校验 + 独立重算答案，返回错误列表。"""
    errs = []
    # 数据统一为 LF 行尾；Windows 上需 -DFOR_LINUX 让 testlib 严格模式按 LF 判定
    val = compile_cpp(os.path.join(ROOT, 'rsy', 'std', 'val.cpp'), os.path.join(BIN, 'val' + ELF),
                      extra_flags=['-DFOR_LINUX'])
    for name, infile, ansfile in case_list:
        with open(infile, 'rb') as fin:
            p = subprocess.run([val], cwd=ROOT, stdin=fin,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            errs.append('数据 %s.in 不合法：%s' % (name,
                        p.stderr.decode('utf-8', 'replace').strip()))
            continue
        n, m, q, op, x, ql, qr = load_case(infile)
        if not (1 <= n <= MAXN):
            errs.append('%s: 需满足 1 <= n <= 1e9，实际 n=%d' % (name, n))
        if not (1 <= m <= MAXMQ and 1 <= q <= MAXMQ):
            errs.append('%s: 需满足 1 <= m, q <= 5e5，实际 m=%d, q=%d' % (name, m, q))
        with open(ansfile, 'r') as f:
            alines = f.read().split()
        if len(alines) != q:
            errs.append('%s: .ans 有 %d 行，应为 q=%d 行' % (name, len(alines), q))
            continue
        if not do_ref:
            continue
        got = reference_solve(n, m, q, op, x, ql, qr)
        for j in range(q):
            a = int(alines[j])
            if a != got[j]:
                errs.append('%s: 第 %d 个询问 [%d,%d] 答案错，.ans=%d，独立实现=%d'
                            % (name, j + 1, ql[j], qr[j], a, got[j]))
                break
            if not (1 <= a <= qr[j] - ql[j] + 1):
                errs.append('%s: 第 %d 个询问答案 %d 超出 [1, r-l+1]' % (name, j + 1, a))
                break
    return errs


def main():
    ap = argparse.ArgumentParser(description='纸带染色 独立评测脚本')
    ap.add_argument('--validate', action='store_true', help='只校验数据与答案，不跑程序')
    ap.add_argument('--no-ref', action='store_true', help='跳过独立重算答案')
    ap.add_argument('--only', default=None, help='只评测名字含该子串的程序')
    ap.add_argument('-j', '--jobs', type=int, default=1, help='并行线程数')
    ap.add_argument('--tl', type=float, default=None, help='覆盖时限（秒）')
    ap.add_argument('-o', '--out', default='result.csv', help='输出 CSV 文件名')
    args = ap.parse_args()

    conf = load_conf()
    tests, samples = collect_cases(conf)
    tl = args.tl if args.tl is not None else float(conf.get('time limit', 1.0))
    if not tests:
        raise SystemExit('conf.yaml 的 data 为空，先运行 python -m tuack.dmk 生成数据')

    # ---------- 1. 校验数据 ----------
    print('[1/3] 校验数据%s ...' % ('' if not args.no_ref else '（跳过独立重算）'))
    errs = validate(tests + samples, not args.no_ref)
    if errs:
        print('  发现 %d 个问题：' % len(errs))
        for e in errs[:40]:
            print('   -', e)
    else:
        print('  OK：%d 个测试点 + %d 个样例全部合法%s'
              % (len(tests), len(samples), '（.ans 与独立实现一致）' if not args.no_ref else ''))
    if args.validate:
        return 1 if errs else 0

    # ---------- 2. 编译程序 ----------
    print('[2/3] 编译程序 ...')
    entries = []
    for user, algos in (conf.get('users') or {}).items():
        for algo, info in algos.items():
            path = info if isinstance(info, str) else info.get('path')
            expected = '' if isinstance(info, str) else info.get('expected', '')
            if args.only and args.only not in user and args.only not in algo:
                continue
            try:
                cmd = prepare_program(path)
            except Exception as e:
                print('  [跳过] %s/%s: %s' % (user, algo, e))
                continue
            print('  %s/%s -> %s' % (user, algo, os.path.basename(cmd[-1])))
            entries.append((user, algo, cmd, expected))
    if not entries:
        raise SystemExit('没有可评测的程序')

    # ---------- 3. 评测 ----------
    all_cases = tests + samples
    n_test = len(tests)
    print('[3/3] 评测 %d 个程序 x %d 个数据点 (time limit %.2fs, jobs=%d) ...'
          % (len(entries), len(all_cases), tl, args.jobs))

    def evaluate(entry):
        user, algo, cmd, expected = entry
        return entry, [run_case(cmd, inf, ansf, tl) for _, inf, ansf in all_cases]

    if args.jobs > 1:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(evaluate, entries))
    else:
        results = [evaluate(e) for e in entries]

    # ---------- 输出 CSV ----------
    out = os.path.join(ROOT, args.out)
    unit = 100.0 / n_test
    summary = []
    with open(out, 'w', encoding='utf-8') as f:
        f.write('%s,%s,summary,%s\n' % (
            conf.get('name', 'problem'),
            ','.join(n for n, _, _ in tests),
            ','.join(n for n, _, _ in samples)))
        for (user, algo, cmd, expected), res in results:
            scores = [unit if ok else 0.0 for ok, _, _ in res]
            times = [dt for _, dt, _ in res]
            reports = [rep for _, _, rep in res]
            tot = sum(scores[:n_test])
            summary.append((user, algo, tot, expected))
            f.write('%s,%s,%.2f,%s\n' % (
                user, ','.join('%.2f' % s for s in scores), tot,
                ','.join('%.2f' % s for s in scores[n_test:])))
            f.write('%s,%s,%.3f,%s\n' % (
                algo, ','.join('%.3f' % t for t in times),
                sum(times[i] for i in range(n_test) if scores[i] > 0),
                ','.join('%.3f' % t for t in times[n_test:])))
            f.write(',%s,,%s\n' % (
                ','.join(r.replace(',', ';').replace('\n', ' ') for r in reports),
                ','.join(r.replace(',', ';').replace('\n', ' ') for r in reports[n_test:])))
    print('CSV ->', os.path.relpath(out, ROOT))

    # ---------- 汇总 ----------
    print('\n结果汇总（满分 100）：')
    bad = 0
    for user, algo, tot, expected in summary:
        mark = ''
        if expected and not eval('round(%r, 8) %s' % (tot, expected)):
            mark = '  <-- 未达到预期 (%s)' % expected
            bad += 1
        print('  %-30s %6.2f  期望 %-8s%s' % (user + '/' + algo, tot, expected or '-', mark))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())