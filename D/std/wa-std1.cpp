// std1.cpp —— 精简版 C++ 标程（交互题 "average"）
//
// 0 <= a < b < c <= 2^30，答案 k <= 60（u + 2*log2(q) <= 60，且 q*2^u <= 2^30）。
// 所有中间量都在 128 位内：系数 <= 2^60，m = cb*p + cc*q <= 2^90，
// 分裂时的模数 M = 2^(r-1-u) <= 2^59。
// 模数是 2 的幂：无符号 128 位乘法溢出即 mod 2^128，而 2^s | 2^128，
// 所以 (x*y) mod 2^s 直接写成 (x*y) & ((1<<s)-1) 即可，无需额外大数处理。
#include <bits/stdc++.h>
using namespace std;
typedef __int128 i128;
typedef unsigned __int128 u128;

static const int MAXK = 100;            // 答案上界为 60

static u128 mask(int s) { return s >= 128 ? ~(u128)0 : (((u128)1 << s) - 1); }
static u128 mul(u128 x, u128 y, int s) { return (x * y) & mask(s); }   // (x*y) mod 2^s

// 奇数 x 在 mod 2^s 下的逆元（Newton 提升，每轮位数翻倍）
static u128 inv2(u128 x, int s) {
    u128 r = 1;                          // 正确到 1 位
    for (int b = 1; b < s; ) { b = min(2 * b, s); r = mul(r, 2 - mul(x, r, b), b); }
    return r;
}

static long long rd() {
    int ch;
    do { ch = getchar(); if (ch < 0) exit(0); } while (ch != '-' && (ch < '0' || ch > '9'));
    bool neg = ch == '-';
    if (neg) ch = getchar();
    long long x = 0;
    for (; ch >= '0' && ch <= '9'; ch = getchar()) x = x * 10 + ch - '0';
    return neg ? -x : x;
}

struct Solver {
    long long a, b, c, g, p, q, inv;
    int u, vp, vq;                       // u = v2(d), vp = v2(p), vq = v2(q)
    u128 q2u;                            // q * 2^u，delta 的上界

    void init(long long A, long long B, long long C) {
        a = A; b = B; c = C;
        long long x = b - a, y = c - a, d = gcd(x, y), t = d;
        for (u = 0; !(t & 1); u++) t >>= 1;
        g = t; p = x / d; q = y / d;
        inv = egcd(p, q); q2u = (u128)q << u;
        vp = __builtin_ctzll(p); vq = __builtin_ctzll(q);
    }
    static long long egcd(long long x, long long m) {          // x^{-1} mod m
        long long r0 = x, r1 = m, s0 = 1, s1 = 0;
        while (r1) { long long t = r0 / r1, r = r0 - t * r1; r0 = r1; r1 = r;
                     long long s = s0 - t * s1; s0 = s1; s1 = s; }
        return (s0 % m + m) % m;
    }
    static u128 pow2mod(int e, long long m) {                  // 2^e mod m
        u128 r = 1 % (u128)m, t = 2 % (u128)m;
        for (; e; e >>= 1, t = t * t % (u128)m) if (e & 1) r = r * t % (u128)m;
        return r;
    }
    // a + g*dl 是否属于 S_r
    bool valid(long long dl, int r) const {
        if (dl < 0 || (u128)dl > q2u) return false;
        int e = r - u;
        u128 r0, rp, add;
        if (e < 0) {                                            // m = dl >> (-e)
            if (dl % (1LL << -e)) return false;
            u128 m = (u128)dl >> -e;
            r0 = m % (u128)q * (u128)inv % (u128)q; rp = r0 * (u128)p;
            return m >= rp && r0 + (m - rp) / (u128)q <= ((u128)1 << r);
        }
        // 不要直接算 2^e*dl（试探 k 偏大会溢出），用 ceil 除法比较
        r0 = ((u128)dl % (u128)q) * pow2mod(e, q) % (u128)q * (u128)inv % (u128)q;
        rp = r0 * (u128)p; add = ((u128)1 << e) - 1;
        if ((u128)dl < (rp + add) >> e) return false;           // m < r0*p
        return (r0 * (u128)(q - p) + add) >> e <= q2u - (u128)dl;
    }
    int minK(long long dl) const {
        for (int k = 0; k <= MAXK; k++) if (valid(dl, k)) return k;
        return -1;
    }

    // ---- 分裂：解 x*p + y*q ≡ 0 (mod 2^s) 并满足盒子/和约束 -------------------
    // 固定 cb'=x 求 cc'：需 2^k | x*p（k = min(vq,s)），解模 2^mb（mb = s-k）
    bool fixX(u128 x, u128 cb, u128 cc, u128 L, u128 U, int s, int mb, u128 ivq, u128 &out) const {
        if (x > cb || x > U) return false;
        int k = s - mb;
        u128 xp = x * (u128)p;                                   // <= 2^60
        if (xp & mask(k)) return false;
        u128 M = (u128)1 << mb;
        u128 C = mb ? (M - mul((xp >> k) & (M - 1), ivq, mb)) & (M - 1) : 0;
        u128 lo = L > x ? L - x : 0, hi = min(cc, U - x);
        if (lo > hi) return false;
        u128 t = C >= lo ? 0 : (lo - C + M - 1) / M, v = C + t * M;
        if (v > hi) return false;
        out = v; return true;
    }
    // 固定 cc'=y 求 cb'：需 2^k | y*q（k = min(vp,s)）
    bool fixY(u128 y, u128 cb, u128 cc, u128 L, u128 U, int s, int mb, u128 ivp, u128 &out) const {
        if (y > cc || y > U) return false;
        int k = s - mb;
        if (mul(y, (u128)q, k)) return false;
        u128 M = (u128)1 << mb;
        u128 B = (mul(y, (u128)q, s) >> k) & (M - 1);
        u128 C = mb ? (M - mul(B, ivp, mb)) & (M - 1) : 0;
        u128 lo = L > y ? L - y : 0, hi = min(cb, U - y);
        if (lo > hi) return false;
        u128 t = C >= lo ? 0 : (lo - C + M - 1) / M, v = C + t * M;
        if (v > hi) return false;
        out = v; return true;
    }
    // 把深度 r、系数 (ca,cb,cc) 的节点分裂为子节点 1 的系数 (A,B,C)
    void split(u128 ca, u128 cb, u128 cc, int r, u128 &A, u128 &B, u128 &C) const {
        int s = max(0, r - 1 - u);
        u128 half = (u128)1 << (r - 1);
        u128 L = cb + cc > half ? cb + cc - half : 0, U = half;
        if (!s) {                                               // 无同余约束：贪心填满
            A = min(ca, U); u128 t = U - A;
            B = min(cb, t); t -= B;
            C = min(cc, t);
            return;
        }
        int kq = min(vq, s), mbq = s - kq, kp = min(vp, s), mbp = s - kp;
        u128 ivq = mbq ? inv2((u128)(q >> vq), mbq) : 0;         // q>>vq 为奇数
        u128 ivp = mbp ? inv2((u128)(p >> vp), mbp) : 0;
        u128 stepX = (u128)1 << max(0, kq - vp);                 // 合法 cb' 的步长
        u128 stepY = (u128)1 << max(0, kp - vq);                 // 合法 cc' 的步长
        u128 wloX = U > cc ? U - cc : 0, whiX = min(cb, L);      // 此时 T 区间恰为 [L,U]
        u128 wloY = U > cb ? U - cb : 0, whiY = min(cc, L);

        for (int dir = 0; dir < 2; dir++) {
            u128 big = dir ? cc : cb, step = dir ? stepY : stepX;
            u128 wlo = dir ? wloY : wloX, whi = dir ? whiY : whiX;
            auto go = [&](u128 cand) -> bool {
                if (cand > big) return false;
                u128 other;
                bool ok = dir ? fixY(cand, cb, cc, L, U, s, mbp, ivp, other)
                              : fixX(cand, cb, cc, L, U, s, mbq, ivq, other);
                if (!ok) return false;
                B = dir ? other : cand; C = dir ? cand : other; A = half - B - C;
                return true;
            };
            const u128 PAD = 64;
            for (u128 i = 0; i <= min(big, PAD); i++) if (go(i) || go(big - i)) return;
            if (go(big / 2) || go(big / 2 + 1)) return;
            // 宽区间：区间长度 >= 模数，任何合法取值都必然成功
            if (wlo <= whi) {
                u128 x = wlo + (step - wlo % step) % step;
                for (int t = 0; t < 4 && x <= whi; t++, x += step) if (go(x)) return;
            }
            for (int j = 1; j < 64; j++) if (go(big / 64 * j)) return;   // 均布候选
            if (big <= 2000000)                                          // 兜底全搜
                for (u128 i = 0; i <= big; i++) if (go(i)) return;
        }
        // 候选集里找不到合法分裂。本写法已知会在 data/35~38 上走到这里
        // （见 README 第七节）；基于引理的正确做法见 std-lemma.cpp。
        fprintf(stderr, "split failed (ca=%llu cb=%llu cc=%llu r=%d)\n",
                (unsigned long long)ca, (unsigned long long)cb,
                (unsigned long long)cc, r);
        fflush(stdout);
        exit(1);
    }
};

int main() {
    long long A = rd(), B = rd(), C = rd(), qn = rd();
    Solver S;
    S.init(A, B, C);
    for (long long n = qn; n--; ) {
        long long t = rd();
        int k = -1;
        if (t >= S.a && t <= S.c && (t - S.a) % S.g == 0) k = S.minK((t - S.a) / S.g);
        printf("%d\n", k); fflush(stdout);
        if (k <= 0) continue;                                    // -1 或 0
        long long dl = (t - S.a) / S.g;
        u128 m = k >= S.u ? (u128)dl << (k - S.u) : (u128)dl >> (S.u - k);
        u128 cb = m % (u128)S.q * (u128)S.inv % (u128)S.q;
        u128 cc = (m - cb * (u128)S.p) / (u128)S.q;
        u128 ca = ((u128)1 << k) - cb - cc, v = (u128)t;
        for (int r = k; r >= 1; r--) {
            u128 A, B, C;
            S.split(ca, cb, cc, r, A, B, C);
            u128 x = (A * (u128)S.a + B * (u128)S.b + C * (u128)S.c) >> (r - 1);
            u128 y = 2 * v - x;
            printf("%lld %lld\n", (long long)x, (long long)y); fflush(stdout);
            if (r == 1) break;                                    // 最后一轮：交互器不再回数
            if ((u128)rd() == x) { ca = A; cb = B; cc = C; v = x; }
            else { ca -= A; cb -= B; cc -= C; v = y; }
        }
    }
    return 0;
}
