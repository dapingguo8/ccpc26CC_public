// WRONG solution (C++): ignores u = v2(d), i.e. it takes g = d instead of
// g = d / 2^u.  Every instance with u > 0 is mis-handled (wrong -1 answers and
// wrong k).  The descent is deliberately dummy: the answer is already fatal.
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

static bool feas(i128 delta, int k, int u, ll p, ll q, ll inv, u128 q2u) {
    if (delta < 0 || (u128)delta > q2u) return false;
    int e = k - u;
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
        if ((ll)delta % (1LL << sh) != 0) return false;
        i128 m = (i128)delta >> sh;
        u128 r0 = (u128)m % (u128)q * (u128)inv % (u128)q;
        u128 rp = r0 * (u128)p;
        if ((u128)m < rp) return false;
        u128 sm = r0 + ((u128)m - rp) / (u128)q;
        return sm <= ((u128)1 << k);
    }
}

int main() {
    ll a = rd(), b = rd(), c = rd(), qn = rd();
    ll d = std::gcd(b - a, c - a);
    int u = 0;          // BUG: should be v2(d)
    ll g = d;           // BUG: should be d >> u
    ll p = (b - a) / d, q = (c - a) / d;
    ll inv = modinv(p, q);
    u128 q2u = (u128)q << u;

    for (ll qi = 0; qi < qn; qi++) {
        ll t = rd();
        if (t < a || t > c || (t - a) % g != 0) { printf("-1\n"); fflush(stdout); continue; }
        i128 delta = (i128)((t - a) / g);
        int k = -1;
        for (int kk = 0; kk <= MAX_K; kk++)
            if (feas(delta, kk, u, p, q, inv, q2u)) { k = kk; break; }
        if (k < 0) { printf("-1\n"); fflush(stdout); continue; }
        if (k == 0) { printf("0\n"); fflush(stdout); continue; }
        printf("%d\n", k); fflush(stdout);
        for (int s = 0; s < k; s++) { printf("%lld %lld\n", a, c); fflush(stdout); if (s == k - 1) break; rd(); }
    }
    return 0;
}
