#include <bits/stdc++.h>

using namespace std;

[[noreturn]] void invalid(const string &message) {
    cerr << "invalid merge input: " << message << '\n';
    exit(1);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n;
    int k;
    if (!(cin >> n >> k)) invalid("missing n or k");
    if (n < 1 || n > 1000000000LL) invalid("n is out of range");
    if (k < 1 || k > 300000) invalid("k is out of range");
    if (k > n) invalid("positive class sizes require k <= n");

    long long sum = 0;
    for (int i = 0; i < k; ++i) {
        long long x;
        if (!(cin >> x)) invalid("missing class size");
        if (x < 1 || x > n) invalid("class size is out of range");
        sum += x;
        if (sum > n) invalid("class sizes already exceed n");
    }
    if (sum != n) invalid("class sizes do not sum to n");

    string extra;
    if (cin >> extra) invalid("extra token after the input");
    return 0;
}
