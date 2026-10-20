// WRONG solution (C++): computes the correct minimal k, but the construction
// only tries the "peel a base value" splits
//     (v,v), (a,2v-a), (b,2v-b), (c,2v-c).
// Whenever the only legal split has two interior children (e.g. {0,1,7}, t=3
// needs (2,4)) every candidate fails and an invalid pair is printed.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 i128;
typedef unsigned __int128 u128;

static const int MAX_K = 100;

static ll rd() {
    int ch;
    do { ch = getchar(); if (ch == EOF) exit(0); } while (ch != '-' && (ch < '0' || ch > '9'));
    bool neg = false;
    if (ch == '-') { neg = true; ch = getchar(); }
    ll x = 0;
    while (ch >= '0' && ch <= '9') { x = x * 10 + (ch - '0'); ch = getchar(); }
    return neg ? -x : x;
}

static u128 pow2mod(ll e, ll md) {
    u128 r = 1 % (u128)md, b = 2 % (u128)md;
    while (e > 0) { if (e & 1) r = r * b % (u128)md; b = b * b % (u128)md; e >>= 1; }
    return r;
}

static ll modinv(ll x, ll m) {
    ll r0 = x, r1 = m; i128 s0 = 1, s1 = 0;
    while (r1) { ll qt = r0 / r1; ll t = r0 - qt * r1; r0 = r1; r1 = t; i128 s = s0 - (i128)qt * s1; s0 = s1; s1 = s; }
    ll res = (ll)(s0 % m); if (res < 0) res += m; return res;
}

int main() {
    ll a = rd(), b = rd(), c = rd(), qn = rd();
    ll d = std::gcd(b - a, c - a);
    ll tmp = d; int u = 0;
    while (tmp % 2 == 0) { tmp /= 2; u++; }
    ll g = tmp;
    ll p = (b - a) / d, q = (c - a) / d;
    ll inv = modinv(p, q);
    u128 q2u = (u128)q << u;

    auto valid = [&](i128 delta, int r) -> bool {
        if (delta < 0 || (u128)delta > q2u) return false;
        int e = r - u;
        if (e >= 0) {
            u128 twoE = (u128)1 << e;
            u128 dm = (u128)delta % (u128)q;
            u128 r0 = dm * pow2mod(e, q) % (u128)q;
            r0 = r0 * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            if ((u128)delta < (rp + twoE - 1) / twoE) return false;
            u128 rqp = r0 * (u128)(q - p);
            u128 D = q2u - (u128)delta;
            if ((rqp + twoE - 1) / twoE > D) return false;
            return true;
        } else {
            int sh = -e;
            if ((ll)delta % (1LL << sh) != 0) return false;
            i128 m = (i128)delta >> sh;
            u128 r0 = (u128)m % (u128)q * (u128)inv % (u128)q;
            u128 rp = r0 * (u128)p;
            if ((u128)m < rp) return false;
            return r0 + ((u128)m - rp) / (u128)q <= ((u128)1 << r);
        }
    };

    auto okValue = [&](ll w, int r) -> bool {
        if (w < a || w > c) return false;
        if ((w - a) % g != 0) return false;
        return valid((i128)((w - a) / g), r);
    };

    for (ll qi = 0; qi < qn; qi++) {
        ll t = rd();
        if (t < a || t > c || (t - a) % g != 0) { printf("-1\n"); fflush(stdout); continue; }
        i128 delta = (i128)((t - a) / g);
        int k = -1;
        for (int kk = 0; kk <= MAX_K; kk++) if (valid(delta, kk)) { k = kk; break; }
        if (k < 0) { printf("-1\n"); fflush(stdout); continue; }
        if (k == 0) { printf("0\n"); fflush(stdout); continue; }
        printf("%d\n", k); fflush(stdout);

        ll cur = t;
        for (int r = k; r >= 1; r--) {
            ll cand[4][2] = {{cur, cur}, {a, 2 * cur - a}, {b, 2 * cur - b}, {c, 2 * cur - c}};
            ll x = cur, y = cur;
            bool found = false;
            for (int i = 0; i < 4; i++) {
                ll ux = cand[i][0], uy = cand[i][1];
                if (okValue(ux, r - 1) && okValue(uy, r - 1)) { x = ux; y = uy; found = true; break; }
            }
            (void)found;   // if none matched we still print (cur,cur): rejected by interactor
            printf("%lld %lld\n", x, y); fflush(stdout);
            if (r == 1) break;                      // 最后一轮：交互器不再回数
            ll w = rd();
            cur = w;
        }
    }
    return 0;
}
