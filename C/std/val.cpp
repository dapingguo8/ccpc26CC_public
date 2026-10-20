#include <bits/stdc++.h>
using namespace std;

[[noreturn]] void invalid(const string &msg) {
    cerr << "invalid repeater input: " << msg << '\n';
    exit(1);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long T;
    if (!(cin >> T)) invalid("missing T");
    if (T < 1 || T > 10000) invalid("T out of range");

    long long sum_n = 0;
    for (long long t = 0; t < T; ++t) {
        long long n, k;
        if (!(cin >> n >> k)) invalid("missing n or k");
        if (n < 2 || k < 2 || k > n || n > 200000) invalid("n, k out of range");
        sum_n += n;
        if (sum_n > 200000) invalid("sum of n out of range");
        for (long long i = 0; i < n; ++i) {
            long long x;
            if (!(cin >> x)) invalid("missing b'");
            if (x < 1 || x > 1000000000LL) invalid("b' out of range");
        }
    }

    string extra;
    if (cin >> extra) invalid("extra token after input");
    return 0;
}
