#include <algorithm>
#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;

// Exhaustive search over strings, independent of std.cpp's formula.
// At most O(2^N) binary strings of length <= N can occur. Including
// substring construction and hashing: O(N^3 * 2^N) time, O(N * 2^N) space.
// Intended for small cases (for example, N <= 20).
unordered_map<string, int> memo;

int solve(const string& s) {
    const auto it = memo.find(s);
    if (it != memo.end()) return it->second;

    const int n = static_cast<int>(s.size());
    int best = n;  // Performing zero operations is allowed.
    for (int mid = 1; mid < n && best > 1; ++mid) {
        // Expand around every gap to enumerate all even palindromes.
        for (int l = mid - 1, r = mid;
             l >= 0 && r < n && s[l] == s[r]; --l, ++r) {
            const string next = s.substr(0, l) + '0' + s.substr(r + 1);
            best = min(best, solve(next));
            // Every operation leaves a nonempty string.
            if (best == 1) break;
        }
    }
    memo.emplace(s, best);
    return best;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    if (!(cin >> t)) return 0;
    while (t--) {
        string s;
        cin >> s;
        memo.clear();
        cout << solve(s) << '\n';
    }
}
