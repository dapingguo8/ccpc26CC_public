#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    while (T--) {
        int n, k;
        cin >> n >> k;
        vector<int> cnt(k, 0);
        for (int i = 1; i <= n; ++i) {
            int x;
            cin >> x;
            if (x <= k) ++cnt[(x - i % k + k) % k];
        }
        int best = 0;
        for (int v : cnt) best = max(best, v);
        cout << n - best << '\n';
    }
    return 0;
}
