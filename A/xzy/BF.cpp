#include <bits/stdc++.h>

using namespace std;

// Exhaustive state-search checker for tiny 2dmatrix instances.
// An operation decreases a nonempty path by one.  The row of the selected
// cell is nondecreasing while the column increases by one at every step.
// The total sum strictly decreases, so memoized recursion is exact.
int n, m;
vector<vector<int>> operations;
map<vector<int>, int> memo;

int solve(const vector<int> &state) {
    auto found = memo.find(state);
    if (found != memo.end()) return found->second;

    bool empty = true;
    for (int x : state) {
        if (x != 0) {
            empty = false;
            break;
        }
    }
    if (empty) return 0;

    int answer = numeric_limits<int>::max() / 4;
    for (const vector<int> &op : operations) {
        bool usable = true;
        for (int i = 0; i < static_cast<int>(state.size()); ++i) {
            if (op[i] > state[i]) {
                usable = false;
                break;
            }
        }
        if (!usable) continue;

        vector<int> next = state;
        for (int i = 0; i < static_cast<int>(state.size()); ++i) {
            next[i] -= op[i];
        }
        answer = min(answer, 1 + solve(next));
    }
    memo[state] = answer;
    return answer;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    if (!(cin >> n >> m)) return 2;
    if (n < 1 || m < 1 || n > 5 || m > 6 || n * m > 12) {
        cerr << "2dmatrix BF only accepts n*m<=12, n<=5, m<=6\n";
        return 2;
    }

    vector<int> initial(n * m);
    long long total = 0;
    for (int &x : initial) {
        if (!(cin >> x) || x < 0) return 2;
        total += x;
    }
    string extra;
    if (cin >> extra) return 2;
    if (total > 45) {
        cerr << "2dmatrix BF only accepts total sum<=45\n";
        return 2;
    }

    set<vector<int>> unique_operations;
    for (int left = 0; left < m; ++left) {
        for (int right = left; right < m; ++right) {
            vector<int> rows(right - left + 1, 0);
            function<void(int, int)> enumerate = [&](int pos, int minimum_row) {
                if (pos == static_cast<int>(rows.size())) {
                    vector<int> op(n * m, 0);
                    for (int offset = 0; offset < static_cast<int>(rows.size()); ++offset) {
                        op[rows[offset] * m + left + offset] = 1;
                    }
                    unique_operations.insert(op);
                    return;
                }
                for (int row = minimum_row; row < n; ++row) {
                    rows[pos] = row;
                    enumerate(pos + 1, row);
                }
            };
            enumerate(0, 0);
        }
    }
    operations.assign(unique_operations.begin(), unique_operations.end());

    memo.clear();
    cout << solve(initial) << '\n';
    return 0;
}
