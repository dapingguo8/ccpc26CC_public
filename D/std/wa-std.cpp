// Reference solution for the interactive problem "average".
//
// Range: 0 <= a < b < c <= 2^30, 0 <= t <= 2^30.  With this range the answer
// satisfies k <= 60, so
//   * coefficients c_a,c_b,c_c <= 2^60,
//   * m = c_b*p + c_c*q      <= 2^90,
// both of which fit into (unsigned) __int128.  The only products that could
// overflow are the modular multiplications modulo the power of two
// M = 2^(r-1-u) (up to 2^59), so they are done with a dedicated
// multiply-mod-2^s helper.
//
// Protocol: read `a b c` then `q` from stdin; for every query read `t`; print
// -1, 0, or `k` followed by k rounds of `x y`, reading back the chosen child.
#include <bits/stdc++.h>
using namespace std;

typedef __int128 i128;
typedef unsigned __int128 u128;

static const int MAX_K = 100;   // answer is provably <= 60
static const int PAD = 100;

static inline u128 lowmask(int s) {
    if (s <= 0) return 0;
    if (s >= 127) return ~(u128)0;
    return (((u128)1) << s) - 1;
}

// (a * b) mod 2^s.  Since the modulus is a power of two it is enough to keep the
// low s bits: unsigned 128-bit multiplication wraps modulo 2^128 by itself and
// 2^s divides 2^128.
static inline u128 mulmod2(u128 a, u128 b, int s) {
    return (a * b) & lowmask(s);
}

// inverse of an odd number modulo 2^s
static u128 invmod2(u128 a, int s) {
    if (s <= 0) return 0;
    u128 x = 1;
    int bits = 1;
    while (bits < s) {
        int nb = min(bits * 2, s);
        u128 ax = mulmod2(a, x, nb);
        u128 t = (2 - ax) & lowmask(nb);
        x = mulmod2(x, t, nb);
        bits = nb;
    }
    return x & lowmask(s);
}

static long long rd() {
    int ch;
    do { ch = getchar(); if (ch == EOF) exit(0); } while (ch != '-' && (ch < '0' || ch > '9'));
    bool neg = false;
    if (ch == '-') { neg = true; ch = getchar(); }
    long long x = 0;
    while (ch >= '0' && ch <= '9') { x = x * 10 + (ch - '0'); ch = getchar(); }
    return neg ? -x : x;
}

static void wr(u128 x) {
    if (x == 0) { putchar('0'); return; }
    char buf[48]; int n = 0;
    while (x > 0) { buf[n++] = (char)('0' + (int)(x % 10)); x /= 10; }
    while (n > 0) putchar(buf[--n]);
}

static u128 pow2mod(long long e, long long md) {
    u128 r = 1 % (u128)md, b = 2 % (u128)md;
    while (e > 0) {
        if (e & 1) r = r * b % (u128)md;
        b = b * b % (u128)md;
        e >>= 1;
    }
    return r;
}

struct Solver {
    long long a, b, c;
    long long d, u, g, p, q, inv;
    int vq, vp;
    u128 q2u;

    static long long modinv(long long x, long long m) {
        long long r0 = x, r1 = m;
        i128 s0 = 1, s1 = 0;
        while (r1) {
            long long qt = r0 / r1;
            long long t = r0 - qt * r1; r0 = r1; r1 = t;
            i128 s = s0 - (i128)qt * s1; s0 = s1; s1 = s;
        }
        long long res = (long long)(s0 % m);
        if (res < 0) res += m;
        return res;
    }

    void init(long long a_, long long b_, long long c_) {
        a = a_; b = b_; c = c_;
        long long ba = b - a, ca = c - a;
        d = __gcd(ba, ca);
        long long t = d; u = 0;
        while (t % 2 == 0) { t /= 2; u++; }
        g = t;
        p = ba / d; q = ca / d;
        inv = modinv(p, q);
        q2u = (u128)q << u;
        vq = 0; { long long x = q; while (x % 2 == 0) { x /= 2; vq++; } }
        vp = 0; { long long x = p; while (x % 2 == 0) { x /= 2; vp++; } }
    }

    // is a + g*delta reachable at depth r ?
    bool valid(i128 delta, int r) const {
        if (delta < 0) return false;
        if ((u128)delta > q2u) return false;
        int e = r - (int)u;
        if (e >= 0) {
            u128 twoE = (u128)1 << e;
            u128 dm = (u128)delta % (u128)q;
            u128 r0 = dm * pow2mod(e, q) % (u128)q;
            r0 = r0 * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            u128 need = (rp + twoE - 1) / twoE;      // ceil(rp / 2^e)
            if ((u128)delta < need) return false;
            u128 rqp = r0 * (u128)(q - p);
            u128 D = q2u - (u128)delta;
            u128 need2 = (rqp + twoE - 1) / twoE;    // ceil(rqp / 2^e)
            if (need2 > D) return false;
            return true;
        } else {
            int sh = -e;
            if ((long long)delta % (1LL << sh) != 0) return false;
            i128 m = (i128)delta >> sh;
            u128 r0 = (u128)m % (u128)q * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            if ((u128)m < rp) return false;
            u128 sm = r0 + ((u128)m - rp) / (u128)q;
            return sm <= ((u128)1 << r);
        }
    }

    int minK(i128 delta) const {
        for (int k = 0; k <= MAX_K; k++) if (valid(delta, k)) return k;
        return -1;
    }

    // Fix cb'=x and solve cc' from x*p + y*q ≡ 0 (mod 2^s).
    // Needs 2^k | x*p  with k = min(vq,s); the solutions form one residue class
    // modulo 2^(s-k), so cb'+cc' runs over an AP of step 2^(s-k).
    bool tryCC(u128 cb1, u128 cb, u128 cc, u128 L, u128 U, int s, u128 &ccOut) const {
        if (cb1 > cb) return false;
        if (U < cb1) return false;
        int gqBits = min(vq, s);
        int sp = s - gqBits;
        u128 cb1p = cb1 * (u128)p;                 // <= 2^60
        if (gqBits > 0 && (cb1p & lowmask(gqBits)) != 0) return false;
        u128 A = (gqBits > 0) ? (cb1p >> gqBits) : cb1p;
        u128 lo = (L > cb1) ? (L - cb1) : 0;
        u128 hi = min(cc, U - cb1);
        if (lo > hi) return false;
        if (sp <= 0) { ccOut = lo; return true; }
        u128 Mp = (u128)1 << sp;
        u128 invm = invmod2((u128)(q >> vq), sp);  // q>>vq is odd
        u128 C = ((Mp - mulmod2(A & (Mp - 1), invm, sp)) & (Mp - 1));
        u128 t0 = (C >= lo) ? 0 : ((lo - C + Mp - 1) / Mp);
        u128 cc1 = C + t0 * Mp;
        if (cc1 <= hi) { ccOut = cc1; return true; }
        return false;
    }

    // Fix cc'=y and solve cb'.
    bool tryCB(u128 cc1, u128 cb, u128 cc, u128 L, u128 U, int s, u128 &cbOut) const {
        if (cc1 > cc) return false;
        if (U < cc1) return false;
        int gpBits = min(vp, s);
        int sp = s - gpBits;
        if (gpBits > 0) {
            u128 x = mulmod2(cc1, (u128)q, gpBits);   // (cc1*q) mod 2^gpBits
            if (x != 0) return false;
        }
        u128 lo = (L > cc1) ? (L - cc1) : 0;
        u128 hi = min(cb, U - cc1);
        if (lo > hi) return false;
        if (sp <= 0) { cbOut = lo; return true; }
        u128 Mp = (u128)1 << sp;
        u128 Xlow = mulmod2(cc1, (u128)q, s);         // (cc1*q) mod 2^s
        u128 Bm = Xlow >> gpBits;                     // (cc1*q/2^gpBits) mod 2^sp
        u128 invm = invmod2((u128)(p >> vp), sp);     // p>>vp is odd
        u128 C = ((Mp - mulmod2(Bm & (Mp - 1), invm, sp)) & (Mp - 1));
        u128 t0 = (C >= lo) ? 0 : ((lo - C + Mp - 1) / Mp);
        u128 cb1 = C + t0 * Mp;
        if (cb1 <= hi) { cbOut = cb1; return true; }
        return false;
    }

    // split the node (ca,cb,cc) at depth r into child 1 (ca1,cb1,cc1)
    void split(u128 ca, u128 cb, u128 cc, int r,
               u128 &ca1o, u128 &cb1o, u128 &cc1o) const {
        int s = max(0, r - 1 - (int)u);
        u128 half = (u128)1 << (r - 1);
        u128 L = (cb + cc > half) ? (cb + cc - half) : 0;
        u128 U = half;
        if (s == 0) {
            u128 target = U;
            u128 ca1 = min(ca, target); target -= ca1;
            u128 cb1 = min(cb, target); target -= cb1;
            u128 cc1 = min(cc, target);
            ca1o = ca1; cb1o = cb1; cc1o = cc1;
            return;
        }
        int kq = min(vq, s), kp = min(vp, s);
        u128 stepX = (u128)1 << max(0, kq - vp);   // legal cb' step
        u128 stepY = (u128)1 << max(0, kp - vq);   // legal cc' step
        // "wide" ranges: there the feasible interval for cb'+cc' is exactly
        // [L,U], whose length is 2^(r-1)-L >= 2^(s-k).  An AP with that step
        // must then hit it, so these candidates are provably sufficient.
        u128 wloX = (U > cc) ? (U - cc) : 0, whiX = min(cb, L);
        u128 wloY = (U > cb) ? (U - cb) : 0, whiY = min(cc, L);

        for (int dir = 0; dir < 2; dir++) {
            u128 big = dir ? cc : cb, step = dir ? stepY : stepX;
            u128 wlo = dir ? wloY : wloX, whi = dir ? whiY : whiX;
            for (u128 i = 0; i <= min(big, (u128)PAD); i++) {
                for (int e = 0; e < 2; e++) {
                    u128 cand = e ? big - i : i, other;
                    bool ok = dir ? tryCB(cand, cb, cc, L, U, s, other)
                                  : tryCC(cand, cb, cc, L, U, s, other);
                    if (!ok) continue;
                    if (dir) { cc1o = cand; cb1o = other; }
                    else { cb1o = cand; cc1o = other; }
                    ca1o = half - cb1o - cc1o; return;
                }
            }
            for (u128 cand : {big / 2, big / 2 + 1}) {
                u128 other;
                bool ok = dir ? tryCB(cand, cb, cc, L, U, s, other)
                              : tryCC(cand, cb, cc, L, U, s, other);
                if (!ok) continue;
                if (dir) { cc1o = cand; cb1o = other; }
                else { cb1o = cand; cc1o = other; }
                ca1o = half - cb1o - cc1o; return;
            }
            if (wlo <= whi) {
                u128 x = wlo + (step - wlo % step) % step;
                for (int t = 0; t < 4 && x <= whi; t++, x += step) {
                    u128 other;
                    bool ok = dir ? tryCB(x, cb, cc, L, U, s, other)
                                  : tryCC(x, cb, cc, L, U, s, other);
                    if (!ok) continue;
                    if (dir) { cc1o = x; cb1o = other; }
                    else { cb1o = x; cc1o = other; }
                    ca1o = half - cb1o - cc1o; return;
                }
            }
            for (int j = 1; j < 64; j++) {          // spread candidates
                u128 cand = big / 64 * j, other;
                bool ok = dir ? tryCB(cand, cb, cc, L, U, s, other)
                              : tryCC(cand, cb, cc, L, U, s, other);
                if (!ok) continue;
                if (dir) { cc1o = cand; cb1o = other; }
                else { cb1o = cand; cc1o = other; }
                ca1o = half - cb1o - cc1o; return;
            }
            if (big <= 2000000) {                   // exhaustive fallback
                for (u128 cand = 0; cand <= big; cand++) {
                    u128 other;
                    bool ok = dir ? tryCB(cand, cb, cc, L, U, s, other)
                                  : tryCC(cand, cb, cc, L, U, s, other);
                    if (!ok) continue;
                    if (dir) { cc1o = cand; cb1o = other; }
                    else { cb1o = cand; cc1o = other; }
                    ca1o = half - cb1o - cc1o; return;
                }
            }
        }
        fprintf(stderr, "split failed (ca=%llu cb=%llu cc=%llu r=%d)\n",
                (unsigned long long)ca, (unsigned long long)cb, (unsigned long long)cc, r);
        exit(1);
    }
};

int main() {
    long long a = rd(), b = rd(), c = rd(), qn = rd();
    Solver S;
    S.init(a, b, c);

    for (long long qi = 0; qi < qn; qi++) {
        long long t = rd();
        i128 delta = -1;
        int k = -1;
        if (t >= a && t <= c && (t - a) % S.g == 0) {
            delta = (i128)((t - a) / S.g);
            k = S.minK(delta);
        }
        if (k < 0) { printf("-1\n"); fflush(stdout); continue; }
        if (k == 0) { printf("0\n"); fflush(stdout); continue; }

        printf("%d\n", k); fflush(stdout);

        u128 m;
        {
            int e = k - (int)S.u;
            if (e >= 0) m = ((u128)delta) << e;
            else m = ((u128)delta) >> (-e);
        }
        u128 cb = (m % (u128)S.q) * (u128)S.inv % (u128)S.q;
        u128 cc = (m - cb * (u128)S.p) / (u128)S.q;
        u128 ca = (((u128)1) << k) - cb - cc;

        u128 curv = (u128)t;
        int r = k;
        for (int step = 0; step < k; step++) {
            u128 ca1, cb1, cc1;
            S.split(ca, cb, cc, r, ca1, cb1, cc1);
            u128 num = ca1 * (u128)a + cb1 * (u128)b + cc1 * (u128)c;
            u128 x = num >> (r - 1);
            u128 y = 2 * curv - x;
            wr(x); putchar(' '); wr(y); putchar('\n'); fflush(stdout);
            if(step == k - 1) break;    // 最后一轮：交互器不再回数
            long long w = rd();
            if ((u128)w == x) { ca = ca1; cb = cb1; cc = cc1; curv = x; }
            else { ca -= ca1; cb -= cb1; cc -= cc1; curv = y; }
            r--;
        }
    }
    return 0;
}
