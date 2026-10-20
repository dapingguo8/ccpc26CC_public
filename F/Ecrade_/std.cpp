#include <bits/stdc++.h>
using namespace std;

using int64 = long long;

const int64 MOD = 1000000007;

int64 power(int64 x, int64 y) {
    int64 result = 1;
    while (y > 0) {
        if (y & 1) result = result * x % MOD;
        x = x * x % MOD;
        y >>= 1;
    }
    return result;
}

int64 solve() {
    int n;
    cin >> n;

    vector<int> a(n);
    for (int &x : a) cin >> x;

    if ((a[0] != -1 && a[0] != 0) ||
        (a[n - 1] != -1 && a[n - 1] != 0)) return 0;

    vector<int64> inverse(n + 1), factorial(n + 1, 1);
    inverse[1] = 1;
    for (int i = 2; i <= n; ++i) {
        inverse[i] = MOD - MOD / i * inverse[MOD % i] % MOD;
        factorial[i] = factorial[i - 1] * i % MOD;
    }

    const int width = n + 1;
    vector<int64> f((size_t)width * width * (n + 1));
    vector<int64> g((size_t)width * width);

    auto F = [&](int l, int r, int h) -> int64 & {
        return f[((size_t)l * width + r) * (n + 1) + h];
    };
    auto G = [&](int l, int r) -> int64 & {
        return g[(size_t)l * width + r];
    };

    vector<int> zero_prefix(n + 1);
    for (int i = 0; i < n; ++i) {
        zero_prefix[i + 1] = zero_prefix[i] + (a[i] == 0);
    }

    for (int length = 1; length < n; ++length) {
        for (int l = 0; l + length < n; ++l) {
            int r = l + length;
            if (zero_prefix[r] - zero_prefix[l + 1] > 0) continue;
            if (length == 1) {
                F(l, r, 0) = G(l, r) = 1;
                continue;
            }

            int size = length - 1;
            for (int k = l + 1; k < r; ++k) {
                if (a[k] == 0) continue;

                int limit = length - 2;
                int64 left_sum = 0, right_sum = 0;
                int64 prev_left = 0, prev_right = 0;
                for (int z = 0; z <= limit; ++z) {
                    left_sum = (left_sum + F(l, k, z)) % MOD;
                    right_sum = (right_sum + F(k, r, z)) % MOD;
                    int64 delta = (left_sum * right_sum -
                                   prev_left * prev_right) % MOD;
                    if (delta < 0) delta += MOD;

                    int h = z + 1;
                    if (a[k] == -1 || a[k] == h) {
                        F(l, r, h) = (F(l, r, h) +
                                      delta * inverse[size]) % MOD;
                    }
                    prev_left = left_sum;
                    prev_right = right_sum;
                }
            }

            for (int h = 1; h <= length - 1; ++h) {
                G(l, r) = (G(l, r) + F(l, r, h)) % MOD;
            }
        }
    }

    vector<int64> left(n), right(n);
    left[0] = 1;
    for (int r = 1; r < n; ++r) {
        if (a[r] != -1 && a[r] != 0) continue;
        for (int l = 0; l < r; ++l) {
            left[r] = (left[r] + left[l] * G(l, r) % MOD * inverse[r]) % MOD;
        }
    }

    right[n - 1] = 1;
    for (int l = n - 2; l >= 0; --l) {
        if (a[l] != -1 && a[l] != 0) continue;
        for (int r = l + 1; r < n; ++r) {
            right[l] = (right[l] + G(l, r) * right[r] % MOD *
                        inverse[n - 1 - l]) % MOD;
        }
    }

    int64 peaks = 0;
    for (int i = 0; i < n; ++i) {
        if (a[i] == -1 || a[i] == 0) {
            peaks = (peaks + left[i] * right[i]) % MOD;
        }
    }
    return factorial[n] * inverse[n] % MOD * peaks % MOD;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int test_count;
    cin >> test_count;
    while (test_count--) cout << solve() << '\n';
    return 0;
}
