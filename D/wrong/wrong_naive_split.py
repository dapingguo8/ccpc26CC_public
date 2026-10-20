import sys
from math import gcd

# WRONG solution: computes the correct minimal k, but the construction uses a
# naive "peel a base value" split: (v,v), (a,2v-a), (b,2v-b), (c,2v-c).
# Whenever the only valid split has two interior children (e.g. {0,1,7}, t=3
# needs (2,4)), none of those candidates works and it outputs an invalid pair.

def read_ints():
    line = sys.stdin.readline()
    while line != '' and line.strip() == '':
        line = sys.stdin.readline()
    if line == '':
        return None
    return [int(x) for x in line.split()]

def main():
    a, b, c = read_ints()[:3]
    qn = read_ints()[0]
    d = gcd(b - a, c - a)
    tmp = d; u = 0
    while tmp % 2 == 0: tmp //= 2; u += 1
    g = tmp
    p = (b - a) // d
    q = (c - a) // d
    inv = pow(p, -1, q)
    q2u = q * (1 << u)

    def valid(delta, r):
        if delta < 0 or delta > q2u:
            return False
        e = r - u
        if e >= 0:
            m = delta << e
            r0 = (m * inv) % q
            if m < r0 * p:
                return False
            sm = r0 + (m - r0 * p) // q
            return sm <= (1 << r)
        else:
            sh = -e
            if delta % (1 << sh) != 0:
                return False
            m = delta >> sh
            r0 = (m * inv) % q
            if m < r0 * p:
                return False
            sm = r0 + (m - r0 * p) // q
            return sm <= (1 << r)

    def min_k(delta):
        for k in range(0, 130):
            if valid(delta, k):
                return k
        return -1

    for _ in range(qn):
        t = read_ints()[0]
        if t < a or t > c or (t - a) % g != 0:
            sys.stdout.write("-1\n"); sys.stdout.flush(); continue
        delta = (t - a) // g
        k = min_k(delta)
        if k == -1:
            sys.stdout.write("-1\n"); sys.stdout.flush(); continue
        if k == 0:
            sys.stdout.write("0\n"); sys.stdout.flush(); continue
        sys.stdout.write(str(k) + "\n"); sys.stdout.flush()
        cur = t
        for r in range(k, 0, -1):
            # naive candidates
            cands = [(cur, cur), (a, 2 * cur - a), (b, 2 * cur - b), (c, 2 * cur - c)]
            choice = None
            for x, y in cands:
                if y < a or y > c:
                    continue
                dx = (x - a) // g
                dy = (y - a) // g
                if valid(dx, r - 1) and valid(dy, r - 1):
                    choice = (x, y)
                    break
            if choice is None:
                choice = (cur, cur)  # will be rejected by the interactor
            sys.stdout.write("%d %d\n" % choice); sys.stdout.flush()
            if r == 1:               # 最后一轮：交互器不再回数
                break
            w = read_ints()[0]
            cur = w

if __name__ == "__main__":
    main()
