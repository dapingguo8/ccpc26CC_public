import random
from math import gcd

# ---------------------------------------------------------------------------
# Data generator for the interactive problem "average".
#
# Input file format (data/N.in):
#   a b c
#   q
#   t_1
#   ...
#   t_q
#
# The companion data/N.ans stores the correct minimal k (or -1) for each query;
# it is informational only, the interactor recomputes everything itself.
#
# Value range: 0 <= a < b < c <= 2^30, 0 <= t <= 2^30.
# With this range the answer satisfies k <= 60, hence every intermediate
# (coefficients <= 2^60, m = c_b*p + c_c*q <= 2^90) fits into a signed
# 128-bit integer.
#
# Every generator below produces (a, b, c, [t...]).  Run `python gen.py` to
# write data/1.in..data/N.in and the sample down/1.in.
# ---------------------------------------------------------------------------

MAXV = 1 << 30
MAXK = 60

def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def min_k(a, b, c, t):
    if t < a or t > c:
        return -1
    d = gcd(b - a, c - a)
    u = v2(d)
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
        sm = r0 + (m - r0 * p) // q
        if sm <= (1 << k):
            return k
    return -1

def make_abc(p, q, g, u, a=0):
    """Build a<b<c from normalized p<q, odd g, and u.  gcd(p,q)=1 required."""
    d = g * (1 << u)
    return a, a + p * d, a + q * d

def rand_coprime_pair(qmax):
    while True:
        q = random.randint(2, qmax)
        p = random.randint(1, q - 1)
        if gcd(p, q) == 1:
            return p, q

# ---------------------------------------------------------------------------
# 1) sample
# ---------------------------------------------------------------------------
def gen_sample():
    # small, human-checkable
    return (0, 1, 7, [0, 1, 7, 4, 2, 3, 8])

# ---------------------------------------------------------------------------
# 2) tiny exhaustive
# ---------------------------------------------------------------------------
def gen_tiny():
    cases = []
    for (a, b, c) in [(0, 1, 4), (0, 1, 7), (0, 2, 5), (0, 3, 8), (1, 3, 6)]:
        ts = list(range(0, c + 2)) + [c + 1, a, b, c]
        cases.append((a, b, c, ts))
    return cases

# ---------------------------------------------------------------------------
# 3) small random
# ---------------------------------------------------------------------------
def gen_small_random(rng, n=5):
    cases = []
    for _ in range(n):
        a = rng.randint(0, 10)
        b = rng.randint(a + 1, a + 1 + 40)
        c = rng.randint(b + 1, b + 1 + 40)
        ts = [rng.randint(0, c + 3) for _ in range(25)]
        ts += [a, b, c, c + 1, a - 1 if a > 0 else c + 1]
        cases.append((a, b, c, ts))
    return cases

# ---------------------------------------------------------------------------
# 4) general random, values up to 2^30
# ---------------------------------------------------------------------------
def gen_random(rng, n=10):
    cases = []
    for _ in range(n):
        a = rng.randint(0, MAXV // 4)
        b = rng.randint(a + 1, a + 1 + MAXV // 2)
        c = rng.randint(b + 1, min(MAXV, b + 1 + MAXV // 2))
        ts = []
        for _ in range(20):
            lo = max(0, a - 10)
            hi = min(MAXV, c + 10)
            ts.append(rng.randint(lo, hi))
        ts += [a, b, c, c + 1]
        cases.append((a, b, c, ts))
    return cases

# ---------------------------------------------------------------------------
# 5) large u: d = gcd(b-a,c-a) has a big power of two -> kills "ignore u"
# ---------------------------------------------------------------------------
def gen_large_u(rng, n=4):
    cases = []
    for _ in range(n):
        u = rng.randint(10, 25)
        p, q = 1, 3
        a = rng.randint(0, 1000)
        _, b, c = make_abc(p, q, 1, u, a)
        if c > MAXV:
            continue
        ts = []
        # values a + k that are reachable but whose (t-a) is not divisible by 2^u
        for k in range(1, 30):
            ts.append(a + k)
        ts += [a, b, c]
        # some random in range
        for _ in range(10):
            ts.append(rng.randint(a, min(MAXV, c)))
        cases.append((a, b, c, ts))
    return cases

# ---------------------------------------------------------------------------
# 6) large odd g: d has a big odd part -> kills "ignore g"
# ---------------------------------------------------------------------------
def gen_large_g(rng, n=4):
    cases = []
    odds = [3, 5, 7, 9, 15, 21, 27, 33, 101, 65537]
    for i in range(n):
        g = odds[rng.randint(0, len(odds) - 1)]
        u = rng.randint(0, 10)
        p = 1
        q = 2
        a = rng.randint(0, 100)
        _, b, c = make_abc(p, q, g, u, a)
        if c > MAXV:
            continue
        ts = []
        # t with (t-a) not divisible by g -> answer -1
        for off in range(1, min(g, 40)):
            if off % g != 0:
                ts.append(a + off)
        ts += [a, b, c]
        for _ in range(10):
            ts.append(rng.randint(a, min(MAXV, c)))
        cases.append((a, b, c, ts))
    return cases

MAXQ = 1000

def pad_queries(ts, rng, lo, hi, extra=(), total=MAXQ):
    """把询问表补到 total 条（去重、保序）：先放 extra 与已有内容，再补随机 t。"""
    seen = set()
    out = []
    for t in list(ts) + list(extra):
        t = max(lo, min(hi, int(t)))
        if t not in seen:
            seen.add(t); out.append(t)
    guard = 0
    while len(out) < total and guard < total * 50:
        guard += 1
        t = rng.randint(lo, hi)
        if t not in seen:
            seen.add(t); out.append(t)
    return out[:total]

def pad_reach(rng, ts, a, g, dmax, c, total=MAXQ, bias=0.7, extra=(), small_hi=None):
    """补到 total 条，其中约 bias 比例取"形式上可能可达"的 t = a + g*delta
    （delta ∈ [0, dmax]），其余在 [0, 2^30] 里随机（c 很小时一半随机也限制在
    [0, small_hi]，免得整组都是 -1），用来同时覆盖 -1 与各种 k。"""
    seen = set()
    out = []
    for t in list(ts) + list(extra):
        t = max(0, min(MAXV, int(t)))
        if t not in seen:
            seen.add(t); out.append(t)
    guard = 0
    while len(out) < total and guard < total * 200:
        guard += 1
        if rng.random() < bias and dmax > 0:
            t = a + g * rng.randint(0, dmax)
            if t > c or t > MAXV:
                continue
        else:
            hi = MAXV
            if small_hi is not None and rng.random() < 0.5:
                hi = small_hi
            t = rng.randint(0, hi)
        if t not in seen:
            seen.add(t); out.append(t)
    return pad_queries(out, rng, 0, MAXV, (), total)

# ---------------------------------------------------------------------------
# 7) extreme depth: minimal k reaches the theoretical maximum 60
# ---------------------------------------------------------------------------
def gen_extreme_k(rng, n=3):
    """Deep trees (minimal k close to the bound 60).

    The pairs (p, q) are chosen so that the two structurally different cases
    occur: q odd (gcd(q, 2^s) = 1) and q even with a small 2-adic valuation.
    These are exactly the cases where a naive "try cb' = 0 / cb / cb/2" split
    search fails, so they stress the split routine of the reference solution.
    每组补满 1000 次询问（$t$ 密集取在 $q$ 附近，最小 $k$ 都在 50~60）。
    """
    cases = []
    for (p, q) in [(2, (1 << 30) - 1), (1, (1 << 30) - 108), (3, (1 << 30) - 100)]:
        a = 0
        b = a + p  # d = 1
        c = a + q
        ts = [q - 1, q - 2, q - 3, q - 4, q - 2**15, q // 2, 1, p, q, 0]
        for e in range(1, 8):
            ts.append(q - (1 << e))
        ts += [q - 3, q - 5, q - 7]
        extra = [q - 1 - i for i in range(1, 400)] + [q - 2**15 - i for i in range(300)]
        ts = pad_queries(ts, rng, 0, q, extra)
        cases.append((a, b, c, ts))
    return cases[:n]


# ---------------------------------------------------------------------------
# 8) kill a split search based on ad-hoc candidates.
#
#    At the node these queries reach, the feasible interval for cb'+cc' is
#    extremely short (ca = 26, 26, 28, 32) while the congruence modulus is
#    about 2^22..2^28.  A construction (like the one in std.cpp/std1.cpp/std.py)
#    that only tries candidates such as 0, cb, cb/2, a "wide region" or a few
#    spread points will never land in the interval and therefore fails, while
#    the lemma-based constructions (std-lemma*.cpp) succeed.
#    The failure happens at the root split, so it does not depend on the
#    interactor's random choice of child.
# ---------------------------------------------------------------------------
def gen_kill_patchwork(rng, n=4):
    raw = [
        (0, 3, 4194281, 2097139, 22),        # p=3、q=2^22-7，根节点 ca=26
        (0, 3, 16777193, 8388592, 23),       # p=3、q=2^24-9，根节点 ca=26
        (0, 5, 67108841, 33554403, 24),      # p=5、q=2^26-23，根节点 ca=28
        (0, 9, 268435433, 134217433, 23),    # p=9、q=2^28-23，根节点 ca=32
    ]
    cases = []
    for (a, b, c, t, k) in raw[:n]:
        extra = [t] + [t + i for i in range(-200, 200)] + [a + (c - a) * i // 1000 for i in range(200)]
        ts = pad_queries([t, a, b, c, 0, a + 1, c - 1], rng, 0, MAXV, extra)
        cases.append((a, b, c, ts))
    return cases


# ---------------------------------------------------------------------------
# 8) exact-feasibility boundary: with a small p,q the whole valid delta range
#    [0, q*2^u] is enumerated, so the boundary between "representable" and
#    "not representable" (Frobenius) and the boundary of "sum <= 2^k" are both
#    hit exhaustively.
# ---------------------------------------------------------------------------
def gen_frobenius_boundary(rng, n=4):
    cases = []
    for _ in range(n):
        p, q = rand_coprime_pair(30)
        u = rng.randint(0, 2)
        g = 1
        a = rng.randint(0, 10)
        aa, b, c = make_abc(p, q, g, u, a)
        if c > MAXV:
            continue
        D = q * (2 ** u)          # valid delta runs over 0..D
        if D <= 300:
            ts = [a + g * d for d in range(0, D + 1)]     # exhaustive
        else:
            cand = {0, 1, 2, 3, p, q, D, D - 1, D - 2, D // 2}
            thr = (p - 1) * (q - 1)
            for d in range(thr - 3, thr + 4):
                if 0 <= d <= D:
                    cand.add(d)
            ts = sorted(a + g * d for d in cand)
        ts += [a, b, c]
        cases.append((a, b, c, ts))
    return cases

# ---------------------------------------------------------------------------
# 9) adversarial construction: the unique split has two interior children
#    -> kills the naive "peel a base value" construction
# ---------------------------------------------------------------------------
def gen_adversarial_split(rng, n=5):
    cases = []
    fixed = [(0, 1, 7, [3, 4]), (0, 6, 7, [4, 3, 5]), (0, 1, 4, [2]),
             (0, 2, 8, [5, 3, 6]), (0, 3, 5, [2, 4])]
    for (a, b, c, extra) in fixed[:n]:
        ts = list(range(0, c + 1)) + extra
        cases.append((a, b, c, ts))
    return cases

# ---------------------------------------------------------------------------
# 10) deep-tree split stress: q near 2^30, p small, delta 取在 q/2 附近。
#     这些询问的根节点上，c_b'+c_c' 的可行区间同样极窄（ca = 39, 363, 300），
#     同余模数约 2^31 —— 候选集拼凑式的分裂（只试 0/cb/cb/2/均布点）在这里
#     依旧全部落空（见 README 第七节）。核心询问是实测会踩中缺陷的 t，其余
#     询问用 c 附近与随机值补满 1000 条。
# ---------------------------------------------------------------------------
def gen_deep_split(rng, n=3):
    raw = [
        (0, 11, 1073741802, [536870900]),     # q=2^30-22、p=11，根节点 ca=39
        (0, 13, 1073741716, [536870845]),     # q=2^30-108、p=13，根节点 ca=363
        (0, 7, 1073741531, [536868977]),      # q=2^30-293、p=7，根节点 ca=300
    ]
    cases = []
    for (a, b, c, ts) in raw[:n]:
        ts = list(ts) + [c - 1, c - 2, a + 1]
        extra = [c - 1 - i for i in range(400)] + [a + (c - a) * i // 700 for i in range(300)]
        cases.append((a, b, c, pad_queries(ts, rng, 0, c, extra)))
    return cases

# ---------------------------------------------------------------------------
# 11) 把"一维穷举"拉满：让分裂搜索退化到最坏情况
#
#    这类询问针对的是"直接解同余方程"式做法里的兜底枚举（先扫 1e5 个候选 T，
#    扫不到就从头把整个区间 [L,U] 逐点枚举一遍）。构造依据：
#
#      取深度 k，令 U = 2^(k-1)、s = k-1，归一化参数满足 q ≡ -c (mod 2^s)，
#      即 q = 2^(k-1) - c，并要求 c + p ≡ 0 (mod 10)（且 c,p 同为奇数）。
#
#    于是 (x,y) = (c*t, p*t) 恒为同余方程的解：
#        c*t*p + p*t*q = p*t*(c+q) ≡ 0 (mod 2^s),
#    可行的 T = x+y 恰好是 (c+p) 的倍数（(c+p) 又是 10 的倍数）。而"候选 T"
#    那一步的步长是 dT*stepj（k=22 时 = 2*10 = 20，k=23 时 = 40，k=24 时 = 82，
#    k=25 时 = 166），采样点恒为 T ≡ dT*lo_j (mod dT*stepj)，两个格点集因
#    gcd(c+p, dT*stepj) ∤ dT*lo_j 而永不相交 —— 1e5 次采样全部落空、1e5 次
#    调用白烧，之后才逐点扫到第一个合法 T。每次询问因此固定消耗约 1e5 次枚举
#    （实测 F2 = 104857 次、F3 少量），单点 3s 以上（见 README 第十节）。
#
#    表中每项 (p, q, [(t0, step, cnt), ...])，即询问 t = t0 + step*i。
#    k = 22 的 6 组用同一族 (q = 2^21 - c)，另外 3 组把深度抬到 23 / 24 / 25。
# ---------------------------------------------------------------------------
def gen_kill_enum(rng, n=9):
    raw = [
        # ---- k = 22：U = 2^21，dT*stepj = 20，c+p ∈ {10,30,50,60} ----
        (1, 2097143, [(209716, 1, 1000)]),          # c = 9,  c+p = 10
        (3, 2097145, [(209719, 3, 1000)]),          # c = 7,  c+p = 10
        (3, 2097125, [(209716, 1, 1000)]),          # c = 27, c+p = 30
        (5, 2097107, [(209716, 1, 1000)]),          # c = 45, c+p = 50
        (1, 2097123, [(69922, 1, 1000)]),           # c = 29, c+p = 30
        (1, 2097093, [(69912, 1, 802), (34961, 1, 198)]),   # c = 59, c+p = 60
        # ---- k = 23 / 24 / 25：U = 2^22 / 2^23 / 2^24 ----
        (1, 4194295, [(419431, 1, 1000)]),          # c = 9,   c+p = 10
        (1, 8388527, [(102301, 1, 1000)]),          # c = 81,  c+p = 82
        (1, 16777051, [(202137, 1, 531), (303204, 1, 469)]),  # c = 165, c+p = 166
    ]
    cases = []
    for (p, q, spec) in raw[:n]:
        ts = []
        for (t0, step, cnt) in spec:
            ts += [t0 + step * i for i in range(cnt)]
        assert len(ts) <= MAXQ
        cases.append((0, p, q, ts))
    return cases

# ---------------------------------------------------------------------------
# 12) 满 1000 次询问的"综合"数据（强度适中）
#
#     与 gen_kill_enum 不同：这里不追求把某种做法卡到超时，而是把各种参数形态
#     的询问都填满 1000 条，用来区分「忽略 u / 忽略 g / 漏掉和约束 c_b+c_c<=2^k /
#     只按 Frobenius 阈值判可达 / 朴素贴边分裂 / 深树里没写对」等错误做法，
#     同时给正确解一个覆盖面足够大的压力测试（每组都是 1000 次询问）。
#
#     每组：(a,b,c) 由 make_abc(p,q,g,u,a0) 造出，d = g*2^u；
#     询问混合三类 —— 边界值（a,b,c,0,c+1,c-1,...）、"形式上可达"的
#     t = a + g*delta、以及全值域随机 t（多数为 -1）。
# ---------------------------------------------------------------------------
def gen_full_mixed(rng, n=10):
    specs = [
        # (p, q, g, u, a0, 说明, 模式)
        (1, 3, 1, 0, 0,             "最小 p,q：小范围边界 + 随机", "small"),
        (1, 2, 1, 6, 0,             "u=6：大量 t-a 不被 2^u 整除的不可达询问", "u"),
        (2, 3, 3, 8, 5,             "u=8 且 g=3：两个因子都非平凡", "u"),
        (1, 2, 65537, 4, 7,         "g=65537 且 u=4：大奇数因子 + 2 的幂", "g"),
        (7, (1 << 24) + 1, 9, 2, 3, "u=2、g=9、q 奇、c≈6.0e8", "u"),
        (3, 4, 1, 0, 0,             "q 偶：gcd(q,2^s)>1 的分支", "reach"),
        (2, 5, 1, 1, 3,             "p 偶：v_2(p)>0 的分支", "reach"),
        (1, 1 << 20, 1, 0, 0,       "中等深度 k≈40", "reach"),
        (1, (1 << 30) - 1, 1, 0, 0, "q=2^30-1：最小 k 顶到 60", "deep"),
        (3, (1 << 30) - 101, 1, 0, 0, "极深树变体（q 奇、p=3）", "deep"),
    ]
    cases = []
    for (p, q, g, u, a0, _desc, mode) in specs:
        if mode == "skip" or gcd(p, q) != 1 or p >= q:
            continue
        a, b, c = make_abc(p, q, g, u, a0)
        if c > MAXV:
            continue
        d = g * (1 << u)
        dmax = q * (1 << u)
        # 通用边界值
        edge = [0, 1, a, a + 1, a + 2, b - 1 if b > a + 1 else a + 1, b, b + 1,
                c - 1, c, c + 1, MAXV, a - 1 if a > 0 else 0,
                (a + b) // 2, (b + c) // 2, (a + c) // 2, a + g, a + g - 1,
                a + d, a + d - 1, a + d + 1]
        if mode == "small" and c <= 80:
            edge += list(range(0, c + 2))
        if mode == "deep":
            edge += [c - i for i in range(1, 400)]
        if mode in ("u", "g"):
            edge += [a + g * i for i in range(0, 40)]            # 可达形式
            edge += [a + g * i + 1 for i in range(0, 40)]        # 大概率不可达
            edge += [a + d * i for i in range(0, 30)]
        ts = pad_reach(rng, edge, a, g, dmax, c, bias=0.75 if mode != "g" else 0.5,
                       small_hi=(c + 4) if c <= (1 << 20) else None)
        cases.append((a, b, c, ts))
    return cases[:n]

# ---------------------------------------------------------------------------
# 13) 满 1000 询问的"深树"数据：逼着正确解跑满 O(k^2) = O(log^2 V)
#
#     与 gen_kill_enum（data/47~55）不同，这里不做"格点对齐"去卡枚举式做法，
#     而是把 t 密集取在 δ≈q*2^u 附近（答案 k 稳定在 49~60、接近理论上界 60），
#     于是每次询问都要走 ~60 层、每层都做分裂——正确解（引理构造）是 O(k^2)，
#     常数稍大或每层重复快速幂/重建序列的实现会在这里被放大约 60^2 倍。
#     覆盖 q 奇/偶、p 奇/偶、u>0 等不同参数形态（g>1 已在 gen_full_mixed 里覆盖）。
# ---------------------------------------------------------------------------
def gen_full_deep(rng, n=5):
    specs = [
        (1, (1 << 30) - 1001, 1, 0, 0),              # q 奇、p=1
        ((1 << 15) + 1, (1 << 30) - 3, 1, 0, 0),     # q 奇、p 大（≈2^15）
        (1, (1 << 30) - 2, 1, 0, 0),                 # q 偶（v_2(q)=1）
        (2, (1 << 30) - 3, 1, 0, 0),                 # p 偶（v_2(p)=1）、q 奇
        (1, (1 << 29) - 1, 1, 1, 0),                 # u=1、d=2 → c=2^30-2
    ]
    cases = []
    for (p, q, g, u, a0) in specs:
        if p >= q or gcd(p, q) != 1:
            continue
        a, b, c = make_abc(p, q, g, u, a0)
        if c > MAXV:
            continue
        dmax = q * (1 << u)                 # δ 的上限 = q*2^u
        ts = []
        seen = set()
        # 前 300 个紧贴 δ = dmax，k 落在 59~60
        for j in range(0, 300):
            d = dmax - j
            if d < 0:
                break
            t = a + g * d
            if t <= c and t not in seen:
                seen.add(t); ts.append(t)
        # 其余在 δ ∈ [dmax-2200, dmax] 随机（k ≈ 49~60）
        guard = 0
        while len(ts) < MAXQ and guard < MAXQ * 100:
            guard += 1
            d = dmax - rng.randint(0, 2200)
            if d < 0:
                continue
            t = a + g * d
            if t <= c and t not in seen:
                seen.add(t); ts.append(t)
        ts = pad_queries(ts, rng, 0, MAXV, (), MAXQ)
        cases.append((a, b, c, ts))
    return cases[:n]

# ---------------------------------------------------------------------------
# 14) 满 1000 询问的"随机深树"数据：较大的 k，但 t 完全随机、看不出规律
# ---------------------------------------------------------------------------
def gen_deep_random(rng, n=5):
    """和 gen_full_deep 一样是深树（k 较大），但 t 不用连续/等差序列，
    而是在 δ 靠近 q*2^u 的一带里随机采样，让数据"看不出规律"。

    对 u=0、g=1 的情形，答案约 k ≈ 60 - log2(2*(dmax-delta))。取
    W = 2^13，从 [0, W] 随机挑 1000 个互异的 j，t = a + g*(dmax - j)，
    于是大多数询问 k ∈ [41, 59]，同时 t 是散布的、无显式规律。
    """
    W = 1 << 13
    specs = [
        (1, (1 << 30) - 7, 1, 0, 0),      # q 奇、p=1
        (3, (1 << 30) - 5, 1, 0, 0),      # q 奇、p=3
        (1, (1 << 30) - 4, 1, 0, 0),      # q 偶、v_2(q)=2
        (4, (1 << 30) - 5, 1, 0, 0),      # p 偶、v_2(p)=2
        (1, (1 << 29) - 3, 1, 1, 0),      # u=1、d=2 → c=2^30-6
    ]
    cases = []
    for (p, q, g, u, a0) in specs:
        if p >= q or gcd(p, q) != 1:
            continue
        a, b, c = make_abc(p, q, g, u, a0)
        if c > MAXV:
            continue
        dmax = q * (1 << u)
        js = rng.sample(range(0, W + 1), MAXQ)          # 随机且互异，无连续/等差规律
        ts = [a + g * (dmax - j) for j in js if dmax - j >= 0]
        ts = pad_queries(ts, rng, 0, MAXV, (), MAXQ)
        cases.append((a, b, c, ts))
    return cases[:n]

def write_case(path_in, path_ans, a, b, c, ts):
    with open(path_in, "w") as f:
        f.write("%d %d %d\n" % (a, b, c))
        f.write("%d\n" % len(ts))
        for t in ts:
            f.write("%d\n" % t)
    with open(path_ans, "w") as f:
        for t in ts:
            f.write("%d\n" % min_k(a, b, c, t))

def main():
    rng = random.Random(20240517)

    all_cases = []
    def add(cases):
        for cse in cases:
            all_cases.append(cse)

    add([gen_sample()])
    add(gen_tiny())
    add(gen_small_random(rng))
    add(gen_random(rng))
    add(gen_large_u(rng))
    add(gen_large_g(rng))
    add(gen_extreme_k(rng))
    add(gen_deep_split(rng))
    add(gen_kill_patchwork(rng))
    add(gen_frobenius_boundary(rng))
    add(gen_adversarial_split(rng, n=4))
    add(gen_kill_enum(rng))
    add(gen_full_mixed(rng, n=10))
    add(gen_full_deep(rng, n=5))
    add(gen_deep_random(rng, n=5))

    # write sample
    a, b, c, ts = all_cases[0]
    write_case("down/1.in", "down/1.ans", a, b, c, ts)

    # write data cases
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    for i, (a, b, c, ts) in enumerate(all_cases[1:], start=1):
        write_case("data/%d.in" % i, "data/%d.ans" % i, a, b, c, ts)

    print("generated %d data cases + 1 sample" % (len(all_cases) - 1))

if __name__ == "__main__":
    main()
