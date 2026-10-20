import sys
from math import gcd

def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def read_ints():
    line = sys.stdin.readline()
    while line is not None and line != b'' and line.strip() == b'':
        line = sys.stdin.readline()
    if line is None or line == b'':
        return None
    return [int(x) for x in line.split()]

PAD = 64          # 结构化候选宽度
vp = 0            # v2(p)
vq = 0            # v2(q)

def split(ca, cb, cc, r, u, p, q):
    """Return child-1 coefficients (ca', cb', cc').

    解 x*p + y*q ≡ 0 (mod 2^s)，并满足 0<=x<=cb, 0<=y<=cc, L<=x+y<=U。
    固定 x 时 y 被同余式唯一确定到一个模 2^mbq 的剩余类，于是 x+y 落在一个
    步长为 2^mbq 的等差数列里；只要可行区间长度 >= 2^mbq 就必然命中——
    这正是“宽区间”候选 wlo..whi 的作用。固定 y 同理。
    """
    s = max(0, r - 1 - u)
    half = 1 << (r - 1)
    L = max(0, cb + cc - half)
    U = half

    if s == 0:
        target = U
        ca1 = min(ca, target); target -= ca1
        cb1 = min(cb, target); target -= cb1
        cc1 = min(cc, target)
        return (ca1, cb1, cc1)

    kq = min(vq, s); mbq = s - kq; Mq = 1 << mbq
    kp = min(vp, s); mbp = s - kp; Mp = 1 << mbp
    ivq = pow((q >> vq) % Mq, -1, Mq) if mbq else 0
    ivp = pow((p >> vp) % Mp, -1, Mp) if mbp else 0
    stepX = 1 << max(0, kq - vp)          # 合法 cb' 的步长
    stepY = 1 << max(0, kp - vq)

    def fixX(x):
        if x > cb or x > U:
            return None
        xp = x * p
        if xp & ((1 << kq) - 1):
            return None
        C = (-(xp >> kq) * ivq) % Mq if mbq else 0
        lo = max(0, L - x); hi = min(cc, U - x)
        if lo > hi:
            return None
        t = 0 if C >= lo else (lo - C + Mq - 1) // Mq
        v = C + t * Mq
        return v if v <= hi else None

    def fixY(y):
        if y > cc or y > U:
            return None
        yq = y * q
        if yq & ((1 << kp) - 1):
            return None
        C = (-((yq >> kp) % Mp) * ivp) % Mp if mbp else 0
        lo = max(0, L - y); hi = min(cb, U - y)
        if lo > hi:
            return None
        t = 0 if C >= lo else (lo - C + Mp - 1) // Mp
        v = C + t * Mp
        return v if v <= hi else None

    wloX = max(0, U - cc); whiX = min(cb, L)   # 此时 x+y 的可行区间恰为 [L,U]
    wloY = max(0, U - cb); whiY = min(cc, L)

    for dir in (0, 1):
        big = cc if dir else cb
        step = stepY if dir else stepX
        wlo = wloY if dir else wloX
        whi = whiY if dir else whiX

        def go(cand):
            if cand > big:
                return None
            other = fixY(cand) if dir else fixX(cand)
            if other is None:
                return None
            b1 = other if dir else cand
            c1 = cand if dir else other
            return (half - b1 - c1, b1, c1)

        lim = min(big, PAD)
        for i in range(lim + 1):
            res = go(i) or go(big - i)
            if res:
                return res
        res = go(big // 2) or go(big // 2 + 1)
        if res:
            return res
        if wlo <= whi:                       # 宽区间：区间长 >= 模数，必然成功
            x = wlo + (step - wlo % step) % step
            for _ in range(4):
                if x > whi:
                    break
                res = go(x)
                if res:
                    return res
                x += step
        for j in range(1, 64):               # 均布候选
            res = go(big // 64 * j)
            if res:
                return res
        if big <= 2000000:                   # 兜底全搜（正常不会用到）
            for i in range(big + 1):
                res = go(i)
                if res:
                    return res
    raise AssertionError("split failed: ca=%d cb=%d cc=%d r=%d" % (ca, cb, cc, r))

def min_k(delta, u, p, q):
    """Minimal k such that delta reachable at depth k. delta=(t-a)/g integer >=0."""
    if delta < 0:
        return -1
    inv = pow(p, -1, q)
    for k in range(0, 130):
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

def main():
    global vp, vq
    first = read_ints()
    a, b, c = first[0], first[1], first[2]
    qn = read_ints()[0]
    d = gcd(b - a, c - a)
    u = v2(d)
    g = d >> u
    p = (b - a) // d
    q = (c - a) // d
    inv = pow(p, -1, q)
    vp = v2(p)
    vq = v2(q)

    for _ in range(qn):
        t = read_ints()[0]
        if t < a or t > c or (t - a) % g != 0:
            sys.stdout.write("-1\n"); sys.stdout.flush()
            continue
        delta = (t - a) // g
        k = min_k(delta, u, p, q)
        if k == -1:
            sys.stdout.write("-1\n"); sys.stdout.flush()
            continue
        if k == 0:
            sys.stdout.write("0\n"); sys.stdout.flush()
            continue
        sys.stdout.write(str(k) + "\n"); sys.stdout.flush()

        # minimal-sum coefficients at depth k
        if k >= u:
            m = delta << (k - u)
        else:
            m = delta >> (u - k)
        cb = (m * inv) % q
        cc = (m - cb * p) // q
        ca = (1 << k) - cb - cc

        cur_val = t
        cur_r = k
        for step in range(k):
            ca1, cb1, cc1 = split(ca, cb, cc, cur_r, u, p, q)
            x = (ca1 * a + cb1 * b + cc1 * c) >> (cur_r - 1)
            y = 2 * cur_val - x
            sys.stdout.write("%d %d\n" % (x, y)); sys.stdout.flush()
            if step == k - 1:           # 最后一轮：交互器不再回数
                break
            w = read_ints()[0]
            if w == x:
                ca, cb, cc = ca1, cb1, cc1
                cur_val = x
            else:
                ca, cb, cc = ca - ca1, cb - cb1, cc - cc1
                cur_val = y
            cur_r -= 1

if __name__ == "__main__":
    main()
