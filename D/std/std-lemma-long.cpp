// Strict reference solution for the interactive problem "average".
// Uses the pairing lemma recursively to split a node exactly.
#include <bits/stdc++.h>
using namespace std;

typedef __int128 i128;
typedef unsigned __int128 u128;

static const int MAX_K = 100;

static inline u128 lowmask(int s) {
    if (s <= 0) return 0;
    if (s >= 127) return ~(u128)0;
    return (((u128)1) << s) - 1;
}

static inline u128 mulmod2(u128 a, u128 b, int s) {
    return (a * b) & lowmask(s);
}

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

// ---------- 引理实现部分 ----------
struct Item {
    long long val;      // 当前元素的数值
    u128 ca, cb, cc;    // 它包含的原始 a/b/c 叶子数量
    u128 cnt;           // 这种元素有多少个
};

using Comp = array<u128, 3>;

// 引理：把 seq 分成两组，每组元素个数为 seq 元素总数的一半。
// 输入保证 sum(val * size) mod 2^x == 0。
// 返回两组的原始 a/b/c 组成。
pair<Comp, Comp> splitSeq(vector<Item> seq, int x) {
    if (x <= 1) {
        // 模 1 条件，任意按元素个数均分即可。
        u128 total = 0;
        Comp totalComp = {0, 0, 0};
        for (auto &it : seq) {
            total += it.cnt;
            totalComp[0] += it.ca * it.cnt;
            totalComp[1] += it.cb * it.cnt;
            totalComp[2] += it.cc * it.cnt;
        }
        u128 need = total / 2;
        Comp c1 = {0, 0, 0};
        for (auto &it : seq) {
            u128 take = it.cnt < need ? it.cnt : need;
            c1[0] += it.ca * take;
            c1[1] += it.cb * take;
            c1[2] += it.cc * take;
            need -= take;
            if (need == 0) break;
        }
        Comp c2 = {totalComp[0] - c1[0], totalComp[1] - c1[1], totalComp[2] - c1[2]};
        return {c1, c2};
    }

    vector<Item> newseq;
    vector<Item> oddRem, evenRem;

    for (auto &it : seq) {
        u128 evenCnt = it.cnt & ~(u128)1;
        if (evenCnt > 0) {
            Item ni;
            ni.val = it.val;
            ni.ca = it.ca * 2;
            ni.cb = it.cb * 2;
            ni.cc = it.cc * 2;
            ni.cnt = evenCnt / 2;
            newseq.push_back(ni);
        }
        if (it.cnt & 1) {
            Item rem = it;
            rem.cnt = 1;
            if (it.val & 1) oddRem.push_back(rem);
            else evenRem.push_back(rem);
        }
    }

    auto pairRem = [&](vector<Item> &rem) {
        for (size_t i = 0; i < rem.size(); i += 2) {
            Item a = rem[i], b = rem[i + 1];
            Item ni;
            ni.val = (a.val + b.val) / 2;
            ni.ca = a.ca + b.ca;
            ni.cb = a.cb + b.cb;
            ni.cc = a.cc + b.cc;
            ni.cnt = 1;
            newseq.push_back(ni);
        }
    };
    pairRem(oddRem);
    pairRem(evenRem);

    return splitSeq(newseq, x - 1);
}

// ---------- Solver ----------
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
            u128 need = (rp + twoE - 1) / twoE;
            if ((u128)delta < need) return false;
            u128 rqp = r0 * (u128)(q - p);
            u128 D = q2u - (u128)delta;
            u128 need2 = (rqp + twoE - 1) / twoE;
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

    // 新的严格 split：完全按照引理递归分组。
    void split(u128 ca, u128 cb, u128 cc, int r,
               u128 &ca1o, u128 &cb1o, u128 &cc1o) const {
        vector<Item> seq;
        if (ca) seq.push_back({a, 1, 0, 0, ca});
        if (cb) seq.push_back({b, 0, 1, 0, cb});
        if (cc) seq.push_back({c, 0, 0, 1, cc});

        auto res = splitSeq(seq, r);
        ca1o = res.first[0];
        cb1o = res.first[1];
        cc1o = res.first[2];
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
            if (step == k - 1) break;   // 最后一轮：交互器不再回数
            long long w = rd();
            if ((u128)w == x) { ca = ca1; cb = cb1; cc = cc1; curv = x; }
            else { ca -= ca1; cb -= cb1; cc -= cc1; curv = y; }
            r--;
        }
    }
    return 0;
}