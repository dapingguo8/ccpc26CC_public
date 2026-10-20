import sys
from math import gcd

# Brute force reference for the interactive problem "average".
# Only intended for SMALL a, b, c (<= ~20) because it enumerates S_k as sets.
# It computes S_k by the literal definition (averages of pairs), answers each
# query with the minimal k, and produces a valid descent by brute-force search.

MAX_K = 16

def read_ints():
    line = sys.stdin.readline()
    while line != '' and line.strip() == '':
        line = sys.stdin.readline()
    if line == '':
        return None
    return [int(x) for x in line.split()]

def main():
    first = read_ints()
    if first is None:
        return
    a, b, c = first[:3]
    qn = read_ints()[0]

    # Brute force is only meaningful for small values.
    if c - a > 60:
        sys.stderr.write("bf: value range too large, brute force not applicable\n")
        sys.exit(1)

    S = [set([a, b, c])]
    while len(S) <= MAX_K:
        prev = S[-1]
        cur = set(prev)
        lst = list(prev)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                s = lst[i] + lst[j]
                if s % 2 == 0:
                    cur.add(s // 2)
        S.append(cur)
        if cur == prev and len(S) >= 3:
            break

    for _ in range(qn):
        r = read_ints()
        if r is None:
            return
        t = r[0]
        k = -1
        for kk in range(len(S)):
            if t in S[kk]:
                k = kk
                break
        if k == -1:
            sys.stdout.write("-1\n"); sys.stdout.flush()
            continue
        if k == 0:
            sys.stdout.write("0\n"); sys.stdout.flush()
            continue
        sys.stdout.write(str(k) + "\n"); sys.stdout.flush()
        cur = t
        for r in range(k, 0, -1):
            prev = S[r - 1]
            found = None
            for x in prev:
                y = 2 * cur - x
                if y in prev:
                    found = (x, y)
                    break
            if found is None:
                # shouldn't happen for a correct S; fall back to (cur, cur)
                found = (cur, cur)
            sys.stdout.write("%d %d\n" % found); sys.stdout.flush()
            r = read_ints()
            if r is None:
                return
            w = r[0]
            cur = w

if __name__ == "__main__":
    main()
