#include <bits/stdc++.h>
using namespace std;
typedef unsigned __int128 u128;
typedef __int128 i128;
const int MAXK = 100;
long long A, B, C, D, U, G, P, Q, INV;
u128 Q2U;

u128 lowmask(int s) {
    if (s <= 0) return 0;
    if (s >= 127) return ~(u128)0;
    return (((u128)1) << s) - 1;
}
u128 mulmod2(u128 a, u128 b, int s) {
    return (a * b) & lowmask(s);
}
u128 invmod2(u128 a, int s) {
    if (s <= 0) return 0;
    u128 x = 1; int bits = 1;
    while (bits < s) {
        int nb = min(bits * 2, s);
        u128 ax = mulmod2(a, x, nb);
        u128 t = (2 - ax) & lowmask(nb);
        x = mulmod2(x, t, nb);
        bits = nb;
    }
    return x & lowmask(s);
}
long long modinv(long long x, long long m) {
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
u128 pow2mod(long long e, long long md) {
    u128 r = 1 % (u128)md, b = 2 % (u128)md;
    while (e > 0) {
        if (e & 1) r = r * b % (u128)md;
        b = b * b % (u128)md;
        e >>= 1;
    }
    return r;
}
void init() {
    long long ba = B - A, ca = C - A;
    D = gcd(ba, ca);
    long long t = D; U = 0;
    while (t % 2 == 0) { t /= 2; U++; }
    G = t;
    P = ba / D; Q = ca / D;
    INV = modinv(P, Q);
    Q2U = (u128)Q << U;
}
bool valid(i128 delta, int r) {
    if (delta < 0) return false;
    if ((u128)delta > Q2U) return false;
    int e = r - (int)U;
    if (e >= 0) {
        u128 twoE = (u128)1 << e;
        u128 dm = (u128)delta % (u128)Q;
        u128 r0 = dm * pow2mod(e, Q) % (u128)Q;
        r0 = r0 * (u128)INV % (u128)Q;
        u128 rp = r0 * (u128)P;
        u128 need = (rp + twoE - 1) / twoE;
        if ((u128)delta < need) return false;
        u128 rqp = r0 * (u128)(Q - P);
        u128 Dd = Q2U - (u128)delta;
        u128 need2 = (rqp + twoE - 1) / twoE;
        if (need2 > Dd) return false;
        return true;
    } else {
        int sh = -e;
        if ((long long)delta % (1LL << sh) != 0) return false;
        i128 m = delta >> sh;
        u128 r0 = (u128)m % (u128)Q * (u128)INV % (u128)Q;
        u128 rp = r0 * (u128)P;
        if ((u128)m < rp) return false;
        u128 sm = r0 + ((u128)m - rp) / (u128)Q;
        return sm <= ((u128)1 << r);
    }
}
int minK(i128 delta) {
    for (int k = 0; k <= MAXK; k++) if (valid(delta, k)) return k;
    return -1;
}
struct Item { long long v; u128 ca, cb, cc, cnt; };
using Comp = array<u128, 3>;
// splitSeq 是尾递归，这里改成循环 + 复用缓冲：原来每层都要 new/delete 三个
// vector，1000 次深树询问（k≈60）会分配上千万次，实测要 2s 上下。
static vector<Item> seqBuf, nxtBuf, oddBuf, evenBuf;
void splitSeq(const vector<Item> &start, int x, Comp &c1, Comp &c2) {
    seqBuf = start;
    while (x > 1) {
        oddBuf.clear(); evenBuf.clear(); nxtBuf.clear();
        for (auto &it : seqBuf) {
            u128 evenCnt = it.cnt & ~(u128)1;
            if (evenCnt) nxtBuf.push_back({it.v, it.ca*2, it.cb*2, it.cc*2, evenCnt/2});
            if (it.cnt & 1) {
                Item rem = it; rem.cnt = 1;
                (it.v & 1 ? oddBuf : evenBuf).push_back(rem);
            }
        }
        for (vector<Item> *rem : {&oddBuf, &evenBuf})
            for (size_t i = 0; i + 1 < rem->size(); i += 2) {
                Item a = (*rem)[i], b = (*rem)[i+1];
                nxtBuf.push_back({(a.v + b.v)/2, a.ca+b.ca, a.cb+b.cb, a.cc+b.cc, 1});
            }
        seqBuf.swap(nxtBuf);
        x--;
    }
    // x == 1：按 cnt 从前往后切一半
    u128 total = 0;
    Comp tot = {0,0,0};
    for (auto &it : seqBuf) {
        total += it.cnt;
        tot[0] += it.ca * it.cnt;
        tot[1] += it.cb * it.cnt;
        tot[2] += it.cc * it.cnt;
    }
    u128 need = total / 2;
    Comp cc1 = {0,0,0};
    for (auto &it : seqBuf) {
        u128 take = min(it.cnt, need);
        cc1[0] += it.ca * take;
        cc1[1] += it.cb * take;
        cc1[2] += it.cc * take;
        need -= take;
        if (!need) break;
    }
    c1 = cc1;
    c2 = {tot[0]-cc1[0], tot[1]-cc1[1], tot[2]-cc1[2]};
}
void split(u128 ca, u128 cb, u128 cc, int r, u128 &ca1, u128 &cb1, u128 &cc1) {
    vector<Item> seq;
    if (ca) seq.push_back({A, 1, 0, 0, ca});
    if (cb) seq.push_back({B, 0, 1, 0, cb});
    if (cc) seq.push_back({C, 0, 0, 1, cc});
    Comp c1, c2;
    splitSeq(seq, r, c1, c2);
    ca1 = c1[0]; cb1 = c1[1]; cc1 = c1[2];
}
long long rd() {
    long long x = 0; int ch;
    while ((ch = getchar()) < '0' || ch > '9');
    while (ch >= '0' && ch <= '9') { x = x*10 + ch - '0'; ch = getchar(); }
    return x;
}
void wr(u128 x) {
    if (!x) { putchar('0'); return; }
    char buf[48]; int n = 0;
    while (x) { buf[n++] = '0' + x % 10; x /= 10; }
    while (n) putchar(buf[--n]);
}
int main() {
    A = rd(); B = rd(); C = rd(); long long qn = rd();
    init();
    while (qn--) {
        long long t = rd();
        i128 delta = -1; int k = -1;
        if (t >= A && t <= C && (t - A) % G == 0) {
            delta = (i128)((t - A) / G);
            k = minK(delta);
        }
        if (k < 0) { printf("-1\n"); fflush(stdout); continue; }
        if (k == 0) { printf("0\n"); fflush(stdout); continue; }
        printf("%d\n", k); fflush(stdout);
        u128 m;
        {
            int e = k - (int)U;
            if (e >= 0) m = ((u128)delta) << e;
            else m = ((u128)delta) >> (-e);
        }
        u128 cb = (m % (u128)Q) * (u128)INV % (u128)Q;
        u128 cc = (m - cb * (u128)P) / (u128)Q;
        u128 ca = (((u128)1) << k) - cb - cc;
        u128 curv = (u128)t;
        int r = k;
        for (int step = 0; step < k; step++) {
            u128 ca1, cb1, cc1;
            split(ca, cb, cc, r, ca1, cb1, cc1);
            u128 num = ca1 * (u128)A + cb1 * (u128)B + cc1 * (u128)C;
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