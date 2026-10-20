#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立评测脚本（因为 tuack 这一版不直接支持交互题）。

它做三件事：

1. **校验数据合法性** —— 逐个检查 ``data/*.in`` 与 ``down/1.in`` 的格式、取值范围，
   并用一份独立实现重新计算每个询问的答案，与 ``.ans`` 比对。
2. **评测程序** —— 把 ``conf.yaml`` 中 ``users`` 登记的程序（C++ 自动编译，Python 直接运行）
   与交互器 ``data/chk/chk.cpp`` 对接跑完所有测试点，统计得分与耗时。
3. **输出 CSV** —— 结构与 tuack 的 ``result.csv`` 一致：
   第一列是程序名，随后是各测试点的得分，然后是 ``summary``，最后是各样例点的得分；
   每个程序占三行（user 行=得分，algo 行=耗时，第三行=评测信息）。

用法::

    python test.py                      # 校验数据 + 评测 conf.yaml 里登记的所有程序
    python test.py --validate           # 只校验数据，不跑程序
    python test.py --only std           # 只跑 名字里含 "std" 的 用户/算法
    python test.py -j 4                 # 用 4 个线程并行
    python test.py -o my_result.csv     # 指定输出文件
    python test.py --program std/std.cpp   # 追加评测某个未登记的程序

约定：交互器的 stdout 接选手 stdin，选手 stdout 接交互器 stdin，
交互器从 argv[1] 读输入文件，最后向 stderr 打印 ``ok`` / ``wa ...`` 并以退出码表示胜负。

计时：交互题里墙钟会带上交互器的管道开销，所以本脚本只测选手进程自己的
**user time**（Windows 用 GetProcessTimes，非 Windows 退回墙钟）。CSV 的
``algo`` 行即各测试点的 user time（秒）。
"""
from __future__ import print_function

import argparse
import math
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import yaml
except ImportError:                                        # pragma: no cover
    yaml = None

ROOT = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(ROOT, 'build')
ELF = '.exe' if os.name == 'nt' else ''
MAXV = 1 << 30
MAXQ = 1000
MAXK = 60


# --------------------------------------------------------------------------
# 计时：交互题里墙钟时间会把"交互器的管道开销"也计到选手头上，所以只测
# 选手进程自己的 user time。Windows 用 GetProcessTimes 精确读；
# 非 Windows 退回墙钟（评测机一般在 OJ 侧自行限时）。
# --------------------------------------------------------------------------
if os.name == 'nt':                                          # pragma: no cover
    import ctypes
    from ctypes import wintypes

    class _FILETIME(ctypes.Structure):
        _fields_ = [('lo', wintypes.DWORD), ('hi', wintypes.DWORD)]

    _kernel32 = ctypes.windll.kernel32

    def _ft2sec(ft):
        return ((ft.hi << 32) | ft.lo) / 1e7

    def _proc_cpu(handle):
        c = _FILETIME(); e = _FILETIME(); k = _FILETIME(); u = _FILETIME()
        if not _kernel32.GetProcessTimes(int(handle), ctypes.byref(c), ctypes.byref(e),
                                         ctypes.byref(k), ctypes.byref(u)):
            return None, None
        return _ft2sec(u), _ft2sec(k)

    def _proc_exited(handle):
        return _kernel32.WaitForSingleObject(int(handle), 0) == 0   # WAIT_OBJECT_0
else:
    def _proc_cpu(handle):                                       # pragma: no cover
        return None, None
    def _proc_exited(handle):                                    # pragma: no cover
        return False



# --------------------------------------------------------------------------
# 独立实现的参考解：a+g*delta 是否属于 S_r
# --------------------------------------------------------------------------
def _v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def reference_min_k(a, b, c, t):
    """独立算出的最小 k（不存在返回 -1）。与任何选手程序无关。"""
    if t < a or t > c:
        return -1
    d = math.gcd(b - a, c - a)
    u = _v2(d)
    g = d >> u
    p = (b - a) // d
    q = (c - a) // d
    if (t - a) % g != 0:
        return -1
    delta = (t - a) // g
    inv = pow(p, -1, q)
    for k in range(0, MAXK + 1):
        e = k - u
        if e >= 0:
            m = delta << e
        else:
            sh = -e
            if delta % (1 << sh) != 0:
                continue
            m = delta >> sh
        r0 = (m * inv) % q
        if m < r0 * p:
            continue
        if r0 + (m - r0 * p) // q <= (1 << k):
            return k
    return -1


# --------------------------------------------------------------------------
# 数据校验
# --------------------------------------------------------------------------
def check_case(infile, ansfile):
    """返回错误列表（空列表表示合法）。"""
    errs = []
    name = os.path.basename(infile)
    try:
        with open(infile, 'r') as f:
            lines = f.read().split('\n')
    except IOError as e:
        return [f'{name}: 无法读取 ({e})']

    def is_int(s):
        s = s.strip()
        return s.lstrip('-').isdigit() and s != ''

    body = [l for l in lines if l.strip() != '']
    if len(body) < 2:
        return [f'{name}: 行数不足，至少要有 "a b c" 和 "q" 两行']
    head = body[0].split()
    if len(head) != 3 or not all(is_int(x) for x in head):
        errs.append(f'{name}: 第 1 行必须是 3 个整数 a b c，实际为 {body[0]!r}')
        return errs
    a, b, c = (int(x) for x in head)
    if not (0 <= a < b < c <= MAXV):
        errs.append(f'{name}: 需满足 0 <= a < b < c <= 2^30，实际 a={a} b={b} c={c}')
    if not is_int(body[1]):
        errs.append(f'{name}: 第 2 行必须是整数 q，实际为 {body[1]!r}')
        return errs
    q = int(body[1])
    if not (1 <= q <= MAXQ):
        errs.append(f'{name}: 需满足 1 <= q <= {MAXQ}，实际 q={q}')
    tlines = body[2:]
    if len(tlines) != q:
        errs.append(f'{name}: q={q} 但后面有 {len(tlines)} 个 t')
    ts = []
    for i, line in enumerate(tlines):
        if len(line.split()) != 1 or not is_int(line):
            errs.append(f'{name}: 第 {i + 3} 行必须是 1 个整数 t，实际为 {line!r}')
            break
        t = int(line)
        if not (0 <= t <= MAXV):
            errs.append(f'{name}: 需满足 0 <= t <= 2^30，实际 t={t}')
            break
        ts.append(t)

    # --- 与 .ans 比对 ---
    if not os.path.exists(ansfile):
        errs.append(f'{name}: 缺少对应的 {os.path.basename(ansfile)}')
        return errs
    with open(ansfile, 'r') as f:
        alines = [l.strip() for l in f if l.strip() != '']
    if len(alines) != len(ts):
        errs.append(f'{name}: .ans 行数 {len(alines)} 与 q={len(ts)} 不一致')
    else:
        for i, (t, al) in enumerate(zip(ts, alines)):
            if not is_int(al):
                errs.append(f'{name}: .ans 第 {i + 1} 行不是整数：{al!r}')
                break
            got = int(al)
            if not (-1 <= got <= MAXK):
                errs.append(f'{name}: .ans 第 {i + 1} 行超出 [-1,{MAXK}]：{got}')
                break
            exp = reference_min_k(a, b, c, t)
            if got != exp:
                errs.append(f'{name}: 第 {i + 1} 个询问 t={t} 的答案错：.ans={got}，'
                            f'独立实现算出 {exp}')
                break
    return errs


def validate(case_list):
    """case_list: [(显示名, .in 路径, .ans 路径)]；返回错误列表。"""
    errs = []
    for name, infile, ansfile in case_list:
        errs += check_case(infile, ansfile)
    return errs


# --------------------------------------------------------------------------
# 程序编译 / 调用
# --------------------------------------------------------------------------
def compile_cpp(src, dst):
    """把 C++ 源码编译到 dst，失败抛异常。"""
    cmd = ['g++', '-O2', '-std=c++17', '-o', dst, src]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        raise RuntimeError(f'编译失败: {" ".join(cmd)}\n'
                           + p.stdout.decode('utf-8', 'replace'))
    return dst


def prepare_program(path):
    """把 conf.yaml 里的 path 变成可执行的命令列表。"""
    src = os.path.join(ROOT, path)
    if not os.path.exists(src):
        raise RuntimeError(f'找不到程序 {path}')
    stem = os.path.splitext(os.path.basename(path))[0]
    if path.endswith('.py'):
        return [sys.executable, src]
    exe = os.path.join(BIN, stem + ELF)
    if (not os.path.exists(exe)) or os.path.getmtime(exe) < os.path.getmtime(src):
        compile_cpp(src, exe)
    return [exe]


def run_case(interactor, prog_cmd, infile, time_limit):
    """跑一个测试点；返回 (是否通过, 用时秒, 报告)。

    交互器是 testlib 写的，按 testlib 的约定需要两个参数：
        <input-file> <output-file>
    其中 argv[2] 是交互过程日志文件（tout），交互器同时把它写一份作记录。
    选手与交互器之间仍然是：交互器 stdout -> 选手 stdin，选手 stdout -> 交互器 stdin。
    """
    errf = tempfile.TemporaryFile()
    fd, outlog = tempfile.mkstemp(prefix='dsh_interact_', suffix='.log')
    os.close(fd)
    chk = subprocess.Popen([interactor, infile, outlog], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=errf)
    try:
        prog = subprocess.Popen(prog_cmd, stdin=chk.stdout, stdout=chk.stdin,
                                stderr=subprocess.DEVNULL)
    except Exception as e:                                  # pragma: no cover
        chk.kill()
        errf.close()
        try:
            os.remove(outlog)
        except OSError:
            pass
        return False, 0.0, f'无法启动程序 ({e})'
    chk.stdout.close()
    chk.stdin.close()

    t0 = time.perf_counter()
    timed_out = False
    elapsed = 0.0
    if os.name == 'nt' and hasattr(prog, '_handle'):
        # 用 user time 计时；轮询，超限就杀（避免无限循环卡死）
        handle = int(prog._handle)
        last_u = 0.0
        while True:
            exited = _proc_exited(handle)
            u, s = _proc_cpu(handle)
            if u is not None:
                last_u = u
                if u > time_limit:
                    timed_out = True
                    elapsed = u
                    break
            if exited:
                elapsed = last_u
                break
            time.sleep(0.03)
        if timed_out:
            prog.kill()
        prog.wait()
    else:
        try:
            prog.wait(timeout=time_limit)
        except subprocess.TimeoutExpired:
            timed_out = True
            prog.kill()
            prog.wait()
        elapsed = time.perf_counter() - t0
    try:
        chk.wait(timeout=10)
    except subprocess.TimeoutExpired:
        chk.kill()
        chk.wait()
    errf.seek(0)
    report = errf.read().decode('utf-8', 'replace').strip().replace('\n', ' ')
    errf.close()
    try:
        os.remove(outlog)
    except OSError:
        pass

    if timed_out:
        return False, elapsed, f'TLE (user {elapsed:.2f}s > {time_limit}s)'
    if chk.returncode == 0:
        return True, elapsed, report or 'ok'
    return False, elapsed, report or f'WA (exit {chk.returncode})'


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def load_conf():
    path = os.path.join(ROOT, 'conf.yaml')
    if yaml is None:
        raise SystemExit('需要 PyYAML：pip install pyyaml')
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def collect_cases(conf):
    """返回 (测试点列表, 样例列表)，元素为 (名字, .in, .ans)。"""
    tests, samples = [], []
    for group in (conf.get('data') or []):
        for cs in group['cases']:
            tests.append((str(cs),
                          os.path.join(ROOT, 'data', f'{cs}.in'),
                          os.path.join(ROOT, 'data', f'{cs}.ans')))
    for group in (conf.get('samples') or []):
        for cs in group['cases']:
            samples.append((str(cs),
                            os.path.join(ROOT, 'down', f'{cs}.in'),
                            os.path.join(ROOT, 'down', f'{cs}.ans')))
    return tests, samples


def expect_ok(expr, score):
    """conf.yaml 里的 expected，例如 '== 100' / '< 100' / '>= 60'。"""
    if not expr:
        return True
    try:
        return bool(eval(f'round({score}, 8) {expr}'))
    except Exception:
        return True


def main():
    ap = argparse.ArgumentParser(description='交互题「平均」独立评测脚本')
    ap.add_argument('--validate', action='store_true', help='只校验数据')
    ap.add_argument('--only', default=None, help='只评测名字包含该子串的程序')
    ap.add_argument('-j', '--jobs', type=int, default=1, help='并行线程数')
    ap.add_argument('-o', '--out', default='result.csv', help='输出 CSV 文件名')
    ap.add_argument('--program', action='append', default=[],
                    help='额外评测的程序路径（可重复）')
    ap.add_argument('--data-dir', default=os.path.join(ROOT, 'data'))
    args = ap.parse_args()

    conf = load_conf()
    tests, samples = collect_cases(conf)
    tl = float(conf.get('time limit', 1.0))
    if not tests:
        raise SystemExit('conf.yaml 的 data 为空，先运行 python gen.py 生成数据')

    # ---------- 1. 校验数据 ----------
    print('[1/3] 校验数据 ...')
    errs = validate(tests + samples)
    if errs:
        print(f'  发现 {len(errs)} 个问题：')
        for e in errs[:40]:
            print('   -', e)
    else:
        print(f'  OK：{len(tests)} 个测试点 + {len(samples)} 个样例全部合法，'
              f'.ans 与独立实现一致')
    if args.validate:
        return 1 if errs else 0

    # ---------- 2. 准备交互器与程序 ----------
    print('[2/3] 编译交互器与程序 ...')
    interactor = os.path.join(BIN, 'chk' + ELF)
    os.makedirs(BIN, exist_ok=True)
    compile_cpp(os.path.join(ROOT, 'data', 'chk', 'chk.cpp'), interactor)
    print('  交互器 ->', os.path.relpath(interactor, ROOT))

    entries = []          # (user, algo, cmd, expected)
    for user, algos in (conf.get('users') or {}).items():
        for algo, info in algos.items():
            path = info if isinstance(info, str) else info.get('path')
            expected = '' if isinstance(info, str) else info.get('expected', '')
            if args.only and args.only not in user and args.only not in algo:
                continue
            try:
                cmd = prepare_program(path)
            except Exception as e:
                print(f'  [跳过] {user}/{algo}: {e}')
                continue
            print(f'  {user}/{algo} -> {" ".join(os.path.basename(x) for x in cmd)}')
            entries.append((user, algo, cmd, expected))
    for path in args.program:
        cmd = prepare_program(path)
        entries.append((os.path.basename(os.path.dirname(path)) or '.',
                        os.path.basename(path), cmd, ''))
    if not entries:
        raise SystemExit('没有可评测的程序')

    # ---------- 3. 评测 ----------
    all_cases = tests + samples
    n_test = len(tests)
    print(f'[3/3] 评测 {len(entries)} 个程序 x {len(all_cases)} 个数据点 '
          f'(time limit {tl}s, jobs={args.jobs}) ...')

    def evaluate(entry):
        user, algo, cmd, expected = entry
        res = []
        for name, inf, ansf in all_cases:
            if args.jobs > 1:
                res.append(run_case(interactor, cmd, inf, tl))
            else:
                res.append(run_case(interactor, cmd, inf, tl))
        return entry, res

    if args.jobs > 1:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(evaluate, entries))
    else:
        results = [evaluate(e) for e in entries]

    # ---------- 输出 CSV ----------
    out = os.path.join(ROOT, args.out)
    unit = 100.0 / n_test
    with open(out, 'w', encoding='utf-8') as f:
        f.write('%s,%s,summary,%s\n' % (
            conf.get('name', 'problem'),
            ','.join(n for n, _, _ in tests),
            ','.join(n for n, _, _ in samples)))
        summary = []
        for (user, algo, cmd, expected), res in results:
            scores = [unit if ok else 0.0 for ok, _, _ in res]
            times = [dt for _, dt, _ in res]
            reports = [rep for _, _, rep in res]
            tot = sum(scores[:n_test])
            tot_time = sum(times[i] for i in range(n_test) if scores[i] > 0)
            summary.append((user, algo, tot, expected))
            f.write('%s,%s,%.2f,%s\n' % (
                user, ','.join('%.2f' % s for s in scores), tot,
                ','.join('%.2f' % s for s in scores[n_test:])))
            f.write('%s,%s,%.3f,%s\n' % (
                algo, ','.join('%.3f' % t for t in times), tot_time,
                ','.join('%.3f' % t for t in times[n_test:])))
            f.write(',%s,,%s\n' % (
                ','.join(r.replace(',', ';').replace('\n', ' ') for r in reports),
                ','.join(r.replace(',', ';').replace('\n', ' ') for r in reports[n_test:])))
    print('CSV ->', os.path.relpath(out, ROOT))

    # ---------- 控制台汇总 ----------
    print('\n结果汇总（满分 100）：')
    bad = 0
    for user, algo, tot, expected in summary:
        mark = ''
        if expected and not expect_ok(expected, tot):
            mark = f'  <-- 未达到预期 ({expected})'
            bad += 1
        print(f'  {user + "/" + algo:36s} {tot:6.2f}  期望 {expected or "-":8s}{mark}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
