// Brute force for the interactive problem "average".
//
// It builds S_0, S_1, ... literally (all pairwise averages) and therefore only
// works for small a, b, c.  It is used to cross-check std on tiny inputs.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

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
    if (c - a > 60) {
        fprintf(stderr, "bf: value range too large for brute force\n");
        return 1;
    }
    const int MAXK = 16;
    vector<set<ll>> S;
    S.push_back({a, b, c});
    for (int k = 1; k <= MAXK; k++) {
        set<ll> cur = S[k - 1];
        vector<ll> lst(S[k - 1].begin(), S[k - 1].end());
        for (size_t i = 0; i < lst.size(); i++)
            for (size_t j = i; j < lst.size(); j++) {
                ll s = lst[i] + lst[j];
                if (s % 2 == 0) cur.insert(s / 2);
            }
        S.push_back(cur);
        if (cur == S[k - 1]) break;
    }
    for (ll qi = 0; qi < qn; qi++) {
        ll t = rd();
        int k = -1;
        for (size_t kk = 0; kk < S.size(); kk++)
            if (S[kk].count(t)) { k = (int)kk; break; }
        if (k < 0) { printf("-1\n"); fflush(stdout); continue; }
        if (k == 0) { printf("0\n"); fflush(stdout); continue; }
        printf("%d\n", k); fflush(stdout);
        ll cur = t;
        for (int r = k; r >= 1; r--) {
            ll x = -1, y = -1;
            for (ll u : S[r - 1]) {
                ll v = 2 * cur - u;
                if (S[r - 1].count(v)) { x = u; y = v; break; }
            }
            if (x < 0) { x = cur; y = cur; }
            printf("%lld %lld\n", x, y); fflush(stdout);
            ll w = rd();
            cur = w;
        }
    }
    return 0;
}
