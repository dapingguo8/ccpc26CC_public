// std-solve.cpp —— 直接解同余方程版标程（不使用引理构造）
//
// 目标：在深度 r 的节点上找 (x,y) 使
//     (1) x*p + y*q ≡ 0 (mod 2^s),  s = r-1-u
//     (2) 0 <= x <= cb, 0 <= y <= cc
//     (3) L <= x+y <= U,  L = max(0, cb+cc-2^(r-1)), U = 2^(r-1)
//   x+y = 2^(r-1) - ca'，所以 (3) 等价于 ca' ∈ [0,ca]。
//
// 求解顺序（前面几条都是 O(1) 且可证明正确，最后才是穷举）：
//   A. L == 0            -> (0,0)
//   B. U <= cc           -> (0,U)   因为 0*p + U*q = 2^(r-1)*q ≡ 0 (mod 2^s)
//   C. U <= cb           -> (U,0)   同理
//   D. 固定 x 的“宽区间”：x ∈ [max(0,U-cc), min(cb,L)]，此时 x+y 的可行区间长度
//      恰为 U-L；固定 x 后 x+y 落在步长 M2 = 2^(s-min(v2(q),s)) 的等差数列里，
//      只要 U-L >= M2 就必然命中 -> O(1)。
//   E. 固定 y 同理（步长 M1 = 2^(s-min(v2(p),s))，区间长 U-L）。
//   F. 穷举 min(U-L, cb, cc)+1 个候选（一定正确）。
//   G. 兜底：结构化候选 + 均布候选（覆盖 F 太慢时的极端参数带）。
//
// ！注意：F2/F3 这两步是"一维枚举"，它正确但没有多项式时间保证，最坏情况
//   可以被对手精确对齐格点：取深度 k、q = 2^(k-1) - c、c+p ≡ 0 (mod 10) 时，
//   合法解 T = x+y 恒为 (c+p) 的倍数，而 F2 的采样格点恒为
//   T ≡ dT*lo_j (mod dT*stepj)，两个格点集永不相交 —— 于是每次询问白烧 1e5 次
//   枚举。k=22~25 都能这样对齐（见 README 第十节）。本仓库的 data/47~55 就是
//   这样构造的，本程序在 2s 限制下单点要 3.2~3.3s，九组合计约 29s。
//   因此正式的满分标程是 std/std-lemma.cpp（配对引理，O(k) 确定性分组）。
#include <bits/stdc++.h>
using namespace std;
typedef __int128 i128;
typedef unsigned __int128 u128;

static const int MAX_K = 100;
static const u128 CAP = 4000000;      // 穷举上限

static inline u128 lowmask(int s) {
    if (s <= 0) return 0;
    if (s >= 127) return ~(u128)0;
    return (((u128)1) << s) - 1;
}
static inline u128 mulmod2(u128 a, u128 b, int s) { return (a * b) & lowmask(s); }
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
static u128 pow2mod(long long e, long long md) {
    u128 r = 1 % (u128)md, b = 2 % (u128)md;
    while (e > 0) {
        if (e & 1) r = r * b % (u128)md;
        b = b * b % (u128)md;
        e >>= 1;
    }
    return r;
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

struct Solver {
    long long a, b, c, d, u, g, p, q, inv;
    int vp, vq;
    u128 q2u;

    static long long modinv(long long x, long long m) {
        long long r0 = x, r1 = m;
        i128 s0 = 1, s1 = 0;
        while (r1) {
            long long qt = r0 / r1, t = r0 - qt * r1; r0 = r1; r1 = t;
            i128 s = s0 - (i128)qt * s1; s0 = s1; s1 = s;
        }
        long long res = (long long)(s0 % m);
        return res < 0 ? res + m : res;
    }
    void init(long long a_, long long b_, long long c_) {
        a = a_; b = b_; c = c_;
        long long ba = b - a, ca = c - a;
        d = std::gcd(ba, ca);
        long long t = d; u = 0;
        while (t % 2 == 0) { t /= 2; u++; }
        g = t; p = ba / d; q = ca / d;
        inv = modinv(p, q); q2u = (u128)q << u;
        vq = 0; { long long x = q; while (x % 2 == 0) { x /= 2; vq++; } }
        vp = 0; { long long x = p; while (x % 2 == 0) { x /= 2; vp++; } }
    }
    bool valid(i128 delta, int r) const {
        if (delta < 0 || (u128)delta > q2u) return false;
        int e = r - (int)u;
        if (e >= 0) {
            u128 twoE = (u128)1 << e;
            u128 r0 = (u128)delta % (u128)q * pow2mod(e, q) % (u128)q;
            r0 = r0 * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            if ((u128)delta < (rp + twoE - 1) / twoE) return false;
            u128 rqp = r0 * (u128)(q - p);
            return (rqp + twoE - 1) / twoE <= q2u - (u128)delta;
        } else {
            int sh = -e;
            if ((long long)delta % (1LL << sh) != 0) return false;
            i128 m = (i128)delta >> sh;
            u128 r0 = (u128)m % (u128)q * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            if ((u128)m < rp) return false;
            return r0 + ((u128)m - rp) / (u128)q <= ((u128)1 << r);
        }
    }
    int minK(i128 delta) const {
        for (int k = 0; k <= MAX_K; k++) if (valid(delta, k)) return k;
        return -1;
    }

    // 固定 x 求 y（y 落在一个步长 M2 的等差数列里，取区间内的代表元）
    bool fixX(u128 x, u128 cb, u128 cc, u128 L, u128 U, int s, int mbq, u128 ivq, u128 &out) const {
        if (x > cb || x > U) return false;
        int k = s - mbq;
        u128 xp = x * (u128)p;
        if (xp & lowmask(k)) return false;
        u128 M = (u128)1 << mbq;
        u128 C = mbq ? (M - mulmod2((xp >> k) & (M - 1), ivq, mbq)) & (M - 1) : 0;
        u128 lo = L > x ? L - x : 0, hi = min(cc, U - x);
        if (lo > hi) return false;
        u128 t = C >= lo ? 0 : (lo - C + M - 1) / M, v = C + t * M;
        if (v > hi) return false;
        out = v; return true;
    }
    bool fixY(u128 y, u128 cb, u128 cc, u128 L, u128 U, int s, int mbp, u128 ivp, u128 &out) const {
        if (y > cc || y > U) return false;
        int k = s - mbp;
        if (mulmod2(y, (u128)q, k)) return false;
        u128 M = (u128)1 << mbp;
        u128 B = (mulmod2(y, (u128)q, s) >> k) & (M - 1);
        u128 C = mbp ? (M - mulmod2(B, ivp, mbp)) & (M - 1) : 0;
        u128 lo = L > y ? L - y : 0, hi = min(cb, U - y);
        if (lo > hi) return false;
        u128 t = C >= lo ? 0 : (lo - C + M - 1) / M, v = C + t * M;
        if (v > hi) return false;
        out = v; return true;
    }

    // 固定和 T 反解 x：把同余式改写成 x*(q-p) ≡ T*q (mod 2^s)
    bool fixT(u128 T, u128 cb, u128 cc, u128 L, u128 U, int s, u128 &out) const {
        if (T < L || T > U) return false;
        int h = min((int)__builtin_ctzll(q - p), s);
        int sp = s - h;
        u128 gp = (u128)1 << h, Tq = T * (u128)q;      // T <= 2^59, q <= 2^30 -> 2^89
        if (Tq & (gp - 1)) return false;               // 需要 2^h | T*q
        u128 lo = T > cc ? T - cc : 0, hi = min(cb, T);
        if (lo > hi) return false;
        if (sp == 0) { out = lo; return true; }
        u128 Mp = (u128)1 << sp;
        u128 C = ((Tq >> h) % Mp) * invmod2((u128)((q - p) >> h), sp) % Mp;
        u128 t = C >= lo ? 0 : (lo - C + Mp - 1) / Mp, x = C + t * Mp;
        if (x > hi) return false;
        out = x; return true;
    }

    bool split(u128 ca, u128 cb, u128 cc, int r, u128 &X, u128 &Y) const {
        int s = max(0, r - 1 - (int)u);
        u128 half = (u128)1 << (r - 1);
        u128 L = (cb + cc > half) ? (cb + cc - half) : 0, U = half;

        if (s == 0) {                       // 无同余约束：随便取满足盒子的点
            u128 x = min(cb, U), y = min(cc, U - x);
            if (x + y < L) {
                u128 need = L - (x + y);
                u128 t = min(cb - x, need); x += t; need -= t;
                t = min(cc - y, need); y += t; need -= t;
                if (need) return false;
            }
            X = x; Y = y; return true;
        }
        // A/B/C: O(1) 特解
        if (L == 0) { X = 0; Y = 0; return true; }
        if (U <= cc) { X = 0; Y = U; return true; }
        if (U <= cb) { X = U; Y = 0; return true; }

        int kq = min(vq, s), mbq = s - kq, kp = min(vp, s), mbp = s - kp;
        u128 ivq = mbq ? invmod2((u128)(q >> vq), mbq) : 0;
        u128 ivp = mbp ? invmod2((u128)(p >> vp), mbp) : 0;
        u128 stepX = (u128)1 << max(0, kq - vp), stepY = (u128)1 << max(0, kp - vq);
        u128 M2 = (u128)1 << mbq, M1 = (u128)1 << mbp;
        u128 len = U - L;

        // D/E: 宽区间（区间长 >= 模数 -> 必命中）
        if (len >= M2) {
            u128 lo = (U > cc) ? (U - cc) : 0, hi = min(cb, L);
            u128 x = lo + (stepX - lo % stepX) % stepX, y;
            if (lo <= hi && x <= hi && fixX(x, cb, cc, L, U, s, mbq, ivq, y)) { X = x; Y = y; return true; }
        }
        if (len >= M1) {
            u128 lo = (U > cb) ? (U - cb) : 0, hi = min(cc, L);
            u128 y = lo + (stepY - lo % stepY) % stepY, x;
            if (lo <= hi && y <= hi && fixY(y, cb, cc, L, U, s, mbp, ivp, x)) { X = x; Y = y; return true; }
        }
        // F: 穷举最小的那一维（一定正确，只是可能慢）
        // F1: 固定 T —— 若存在 T 使得 x 的可行区间长度 |I(T)| >= M'（M' = 2^(s-h)），
        //     则该 T 下任意剩余类都必然落在区间内，直接 O(1) 出解。
        {
            int h = min((int)__builtin_ctzll(q - p), s);
            int sp = s - h;
            u128 Mp = (u128)1 << sp;                       // x 的模数
            u128 dT = (u128)1 << max(0, h - vq);           // 需要 dT | T
            // |I(T)| = min(cb,T) - max(0,T-cc) >= M'  <=>  T ∈ [M', cb+cc-M']
            u128 j1 = max(L, Mp), j2 = min(U, cb + cc - Mp);
            if (j1 <= j2) {
                u128 T = j1 + (dT - j1 % dT) % dT, x;
                if (T <= j2 && fixT(T, cb, cc, L, U, s, x)) { X = x; Y = T - x; return true; }
            }
            // F2: 在 [L,U] 上均匀扫 T。窄区间时合法解有很多（每个 T 的命中率约 |I(T)|/M'），
            //     扫一批几乎必然命中；且完全确定（不依赖随机数）。
            u128 lo_j = (L + dT - 1) / dT, hi_j = U / dT;  // T = dT * j
            if (hi_j >= lo_j) {
                u128 cnt = hi_j - lo_j + 1;
                u128 stepj = max((u128)1, cnt / 100000);
                for (u128 j = lo_j; j <= hi_j; j += stepj) {
                    u128 T = dT * j, x;
                    if (fixT(T, cb, cc, L, U, s, x)) { X = x; Y = T - x; return true; }
                }
            }
        }
        // F3: 枚举 T 的全部可能值（<= CAP 时）
        if (len + 1 <= CAP) {
            int h = min((int)__builtin_ctzll(q - p), s);
            u128 dT = (u128)1 << max(0, h - vq);
            u128 lo_j = (L + dT - 1) / dT, hi_j = U / dT;
            for (u128 j = lo_j; j <= hi_j; j++) {
                u128 x;
                if (fixT(dT * j, cb, cc, L, U, s, x)) { X = x; Y = dT * j - x; return true; }
            }
        }
        // F4: 枚举 x
        if (cb + 1 <= CAP) {
            for (u128 x = 0; x <= cb; x++) {
                u128 y;
                if (fixX(x, cb, cc, L, U, s, mbq, ivq, y)) { X = x; Y = y; return true; }
            }
        }
        // F5: 枚举 y
        if (cc + 1 <= CAP) {
            for (u128 y = 0; y <= cc; y++) {
                u128 x;
                if (fixY(y, cb, cc, L, U, s, mbp, ivp, x)) { X = x; Y = y; return true; }
            }
        }
        // G: 兜底候选（结构化 + 均布）
        u128 PAD = 64;
        for (int dir = 0; dir < 2; dir++) {
            u128 big = dir ? cc : cb;
            for (u128 i = 0; i <= min(big, PAD); i++) {
                u128 c1 = i, c2 = big - i, o;
                if (dir ? fixY(c1, cb, cc, L, U, s, mbp, ivp, o) : fixX(c1, cb, cc, L, U, s, mbq, ivq, o)) {
                    if (dir) { X = o; Y = c1; } else { X = c1; Y = o; } return true;
                }
                if (dir ? fixY(c2, cb, cc, L, U, s, mbp, ivp, o) : fixX(c2, cb, cc, L, U, s, mbq, ivq, o)) {
                    if (dir) { X = o; Y = c2; } else { X = c2; Y = o; } return true;
                }
            }
            for (int j = 1; j < 64; j++) {
                u128 c1 = big / 64 * j, o;
                if (dir ? fixY(c1, cb, cc, L, U, s, mbp, ivp, o) : fixX(c1, cb, cc, L, U, s, mbq, ivq, o)) {
                    if (dir) { X = o; Y = c1; } else { X = c1; Y = o; } return true;
                }
            }
        }
        return false;
    }
};

int main() {
    long long A = rd(), B = rd(), C = rd(), qn = rd();
    Solver S;
    S.init(A, B, C);
    for (long long qi = 0; qi < qn; qi++) {
        long long t = rd();
        i128 delta = -1;
        int k = -1;
        if (t >= A && t <= C && (t - A) % S.g == 0) {
            delta = (i128)((t - A) / S.g);
            k = S.minK(delta);
        }
        if (k < 0) { printf("-1\n"); fflush(stdout); continue; }
        if (k == 0) { printf("0\n"); fflush(stdout); continue; }
        printf("%d\n", k); fflush(stdout);

        u128 m;
        { int e = k - (int)S.u; m = e >= 0 ? (((u128)delta) << e) : (((u128)delta) >> (-e)); }
        u128 cb = (m % (u128)S.q) * (u128)S.inv % (u128)S.q;
        u128 cc = (m - cb * (u128)S.p) / (u128)S.q;
        u128 ca = (((u128)1) << k) - cb - cc;

        u128 curv = (u128)t;
        int r = k;
        for (int step = 0; step < k; step++) {
            u128 x, y;
            if (!S.split(ca, cb, cc, r, x, y)) {
                fprintf(stderr, "solve failed (ca=%llu cb=%llu cc=%llu r=%d)\n",
                        (unsigned long long)ca, (unsigned long long)cb,
                        (unsigned long long)cc, r);
                fflush(stdout);
                exit(1);
            }
            // 由 (x,y) 还原两个子节点的系数：child1 = (2^(r-1)-x-y, x, y)
            u128 ca1 = (((u128)1) << (r - 1)) - x - y, cb1 = x, cc1 = y;
            u128 vx = (ca1 * (u128)A + cb1 * (u128)B + cc1 * (u128)C) >> (r - 1);
            u128 vy = 2 * curv - vx;
            wr(vx); putchar(' '); wr(vy); putchar('\n'); fflush(stdout);
            if (step == k - 1) break;   // 最后一轮：交互器不再回数
            long long w = rd();
            if ((u128)w == vx) { ca = ca1; cb = cb1; cc = cc1; curv = vx; }
            else { ca -= ca1; cb -= cb1; cc -= cc1; curv = vy; }
            r--;
        }
    }
    return 0;
}
