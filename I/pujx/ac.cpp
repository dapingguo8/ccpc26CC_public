/*
    Created by Pujx on 2026/10/3.
*/
#pragma GCC optimize(2, 3, "Ofast", "inline")
#include <bits/stdc++.h>
using namespace std;
//#define endl '\n'
//#define int long long
//#define double long double
using i64 = long long;
using ui64 = unsigned long long;
//using i128 = __int128;
#define inf (int)0x3f3f3f3f3f3f3f3f
#define INF 0x3f3f3f3f3f3f3f3f
#define yn(x) cout << (x ? "yes" : "no") << endl
#define Yn(x) cout << (x ? "Yes" : "No") << endl
#define YN(x) cout << (x ? "YES" : "NO") << endl
#define mem(x, i) memset(x, i, sizeof(x))
#define cinarr(a, n) for (int _ = 1; _ <= n; _++) cin >> a[_]
#define cinstl(a) for (auto& _ : a) cin >> _
#define coutarr(a, n) for (int _ = 1; _ <= n; _++) cout << a[_] << " \n"[_ == n]
#define coutstl(a) for (const auto& _ : a) cout << _ << ' '; cout << endl
#define all(x) (x).begin(), (x).end()
#define ls (s << 1)
#define rs (s << 1 | 1)
#define ft first
#define se second
#define pii pair<int, int>
#ifdef DEBUG
    #include "debug.h"
#else
    #define dbg(...) void(0)
#endif

const int N = 2e5 + 5;
//const int M = 1e5 + 5;
const int mod = 998244353;
//const int mod = 1e9 + 7;
//template <typename T> T ksm(T a, i64 b) { T ans = 1; for (; b; a = 1ll * a * a, b >>= 1) if (b & 1) ans = 1ll * ans * a; return ans; }
//template <typename T> T ksm(T a, i64 b, T m = mod) { T ans = 1; for (; b; a = 1ll * a * a % m, b >>= 1) if (b & 1) ans = 1ll * ans * a % m; return ans; }

int a[N];
int n, m, t, k, q;

void encode() {
    string s, ans;
    cin >> n >> s;
    char ch = count(all(s), '0') > n / 2 ? '0' : '1';
    for (int i = 0; i < n; i++) {
        ans += string(1 + (ch != s[i]), ch ^ (i & 1));
    }
    cout << ans.length() << endl;
    cout << ans << endl;
}

void decode() {
    string s, ans;
    cin >> n >> s;
    s += ' ';
    for (int i = 0; i < n; i++) {
        if (s[i] != s[i + 1]) ans += s[0];
        else ans += s[0] ^ 1, i++;
    }
    cout << ans.length() << endl;
    cout << ans << endl;
}

signed main() {
#ifdef LOCAL
    freopen("C:\\Users\\admin\\CLionProjects\\Practice\\data.in", "r", stdin);
    freopen("C:\\Users\\admin\\CLionProjects\\Practice\\data.out", "w", stdout);
#endif
    ios::sync_with_stdio(false);
    cin.tie(0);
    cout.tie(0);
    int Case = 1, op;
    cin >> Case >> op;
    while (Case--) {
        if (op == 1) encode();
        else decode();
    }
    return 0;
}
/*
     _____   _   _       _  __    __
    |  _  \ | | | |     | | \ \  / /
    | |_| | | | | |     | |  \ \/ /
    |  ___/ | | | |  _  | |   }  {
    | |     | |_| | | |_| |  / /\ \
    |_|     \_____/ \_____/ /_/  \_\
*/