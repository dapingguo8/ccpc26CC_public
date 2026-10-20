#include <bits/stdc++.h>

using namespace std;

[[noreturn]] void invalid(const string &message) {
    cerr << "invalid xor input: " << message << '\n';
    exit(1);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    if (!(cin >> T)) invalid("missing T");
    if (T < 1 || T > 1000) invalid("T is out of range");

    long long sum_n = 0;
    long long sum_m = 0;
    for (int tc = 0; tc < T; ++tc) {
        int n, m;
        if (!(cin >> n >> m)) invalid("missing n or m");
        if (n < 1) invalid("n is out of range");
        if (m < 1) invalid("m is out of range");
        if (1LL * m > 1LL * n * (n + 1) / 2) {
            invalid("too many distinct intervals");
        }
        sum_n += n;
        sum_m += m;
        if (sum_n > 200000 || sum_m > 200000) {
            invalid("sum of n or m exceeds the limit");
        }

        string A, B;
        if (!(cin >> A >> B)) invalid("missing A or B");
        if (static_cast<int>(A.size()) != n || static_cast<int>(B.size()) != n) {
            invalid("bit string has the wrong length");
        }
        for (char c : A) {
            if (c != '0' && c != '1') invalid("A is not a binary string");
        }
        for (char c : B) {
            if (c != '0' && c != '1') invalid("B is not a binary string");
        }

        set<pair<int, int>> seen;
        for (int i = 0; i < m; ++i) {
            int l, r;
            if (!(cin >> l >> r)) invalid("missing interval");
            if (l < 1 || r < 1 || l > r || r > n) {
                invalid("interval is out of range");
            }
            if (!seen.insert({l, r}).second) invalid("duplicate interval");
        }
    }

    string extra;
    if (cin >> extra) invalid("extra token after the input");
    return 0;
}
