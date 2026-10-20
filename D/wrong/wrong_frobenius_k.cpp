// WRONG solution (C++): declares feasibility as soon as the Frobenius bound
// m >= (p-1)(q-1) holds.  For small m (t close to a, b, c) the true minimal k
// is much smaller, so it reports a strictly larger k.
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

int main() {
    ll a = rd(), b = rd(), c = rd(), qn = rd();
    ll d = std::gcd(b - a, c - a);
    ll tmp = d; int u = 0;
    while (tmp % 2 == 0) { tmp /= 2; u++; }
    ll g = tmp;
    ll p = (b - a) / d, q = (c - a) / d;
    u128 thr = (u128)(p - 1) * (u128)(q - 1);

    for (ll qi = 0; qi < qn; qi++) {
        ll t = rd();
        if (t < a || t > c || (t - a) % g != 0) { printf("-1\n"); fflush(stdout); continue; }
        i128 delta = (i128)((t - a) / g);
        int k = -1;
        for (int kk = 0; kk <= MAX_K; kk++) {
            int e = kk - u;
            u128 m_ge;                       // whether 2^e*delta >= thr
            if (e >= 0) {
                u128 twoE = (u128)1 << e;
                u128 need = (thr + twoE - 1) / twoE;   // ceil(thr / 2^e)
                m_ge = ((u128)delta >= need);
            } else {
                int sh = -e;
                if (((ll)delta) % (1LL << sh) != 0) continue;
                u128 m = (u128)delta >> sh;
                m_ge = (m >= thr);
            }
            if (m_ge) { k = kk; break; }     // BUG: ignores exact feasibility
        }
        if (k < 0) { printf("-1\n"); fflush(stdout); continue; }
        if (k == 0) { printf("0\n"); fflush(stdout); continue; }
        printf("%d\n", k); fflush(stdout);
        for (int s = 0; s < k; s++) { printf("%lld %lld\n", a, c); fflush(stdout); if (s == k - 1) break; rd(); }
    }
    return 0;
}
