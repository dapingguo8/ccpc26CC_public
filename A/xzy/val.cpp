#include <bits/stdc++.h>

using namespace std;

[[noreturn]] void invalid(const string &message) {
    cerr << "invalid 2dmatrix input: " << message << '\n';
    exit(1);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    if (!(cin >> n >> m)) invalid("missing n or m");
    if (n < 1 || m < 1 || 1LL * n * m > 1000000) invalid("matrix dimensions are out of range");

    for (long long i = 0; i < 1LL * n * m; ++i) {
        long long x;
        if (!(cin >> x)) invalid("missing matrix entry");
        if (x < 0 || x > 1000000000LL) invalid("matrix entry is out of range");
    }

    string extra;
    if (cin >> extra) invalid("extra token after the input");
    return 0;
}
