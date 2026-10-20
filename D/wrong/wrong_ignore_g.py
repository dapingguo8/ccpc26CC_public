import sys
from math import gcd

# WRONG solution: ignores the odd part g of d = gcd(b-a, c-a).
# It extracts u = v2(d) correctly but pretends g = 1, so it never answers -1
# for t whose (t-a) is not divisible by g.

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
    # BUG: g forced to 1
    g = 1
    p = (b - a) // d
    q = (c - a) // d
    inv = pow(p, -1, q)

    def min_k(delta):
        for k in range(0, 130):
            e = k - u
            if e >= 0: m = delta << e
            else:
                sh = -e
                if delta % (1 << sh) != 0: continue
                m = delta >> sh
            r0 = (m * inv) % q
            if m < r0 * p: continue
            if r0 + (m - r0 * p) // q <= (1 << k):
                return k
        return -1

    for _ in range(qn):
        t = read_ints()[0]
        if t < a or t > c:  # BUG: no divisibility by g
            sys.stdout.write("-1\n"); sys.stdout.flush(); continue
        delta = (t - a)  # BUG: not divided by g
        k = min_k(delta)
        if k == -1:
            sys.stdout.write("-1\n"); sys.stdout.flush(); continue
        if k == 0:
            sys.stdout.write("0\n"); sys.stdout.flush(); continue
        sys.stdout.write(str(k) + "\n"); sys.stdout.flush()
        for step in range(k):
            sys.stdout.write("%d %d\n" % (a, c)); sys.stdout.flush()
            if step == k - 1:          # 最后一轮：交互器不再回数
                break
            read_ints()

if __name__ == "__main__":
    main()
