//by GPT-6

#include <bits/stdc++.h>

using namespace std;

constexpr int MOD = 998244353;
constexpr int MAX_STATES = 350;

int mod_pow(long long a, long long e) {
    long long r = 1;
    while (e > 0) {
        if (e & 1) r = r * a % MOD;
        a = a * a % MOD;
        e >>= 1;
    }
    return static_cast<int>(r);
}

vector<int> solve_linear(const vector<vector<int>> &base, const vector<int> &rhs) {
    const int n = static_cast<int>(base.size());
    vector<vector<int>> a(n, vector<int>(n + 1));
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) a[i][j] = base[i][j];
        a[i][n] = rhs[i];
    }

    for (int col = 0; col < n; ++col) {
        int pivot = col;
        while (pivot < n && a[pivot][col] == 0) ++pivot;
        if (pivot == n) throw runtime_error("singular moment matrix");
        swap(a[pivot], a[col]);

        const int inv = mod_pow(a[col][col], MOD - 2);
        for (int j = col; j <= n; ++j) {
            a[col][j] = static_cast<int>(1LL * a[col][j] * inv % MOD);
        }
        for (int i = 0; i < n; ++i) {
            if (i == col || a[i][col] == 0) continue;
            const int factor = a[i][col];
            for (int j = col; j <= n; ++j) {
                a[i][j] = static_cast<int>(
                    (a[i][j] - 1LL * factor * a[col][j]) % MOD
                );
                if (a[i][j] < 0) a[i][j] += MOD;
            }
        }
    }

    vector<int> answer(n);
    for (int i = 0; i < n; ++i) answer[i] = a[i][n];
    return answer;
}

int n, k;
vector<int> current_state;
vector<vector<int>> states;
bool too_large = false;

void generate_states(int pos, int remaining) {
    if (too_large) return;
    if (pos + 1 == k) {
        current_state[pos] = remaining;
        int positive = 0;
        for (int x : current_state) positive += (x > 0);
        if (positive > 1) {
            states.push_back(current_state);
            if (static_cast<int>(states.size()) > MAX_STATES) too_large = true;
        }
        return;
    }
    for (int x = 0; x <= remaining; ++x) {
        current_state[pos] = x;
        generate_states(pos + 1, remaining - x);
        if (too_large) return;
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n_input;
    if (!(cin >> n_input >> k)) return 2;
    if (n_input < 1 || n_input > 12 || k < 1 || k > 6) {
        cerr << "merge BF only accepts n<=12 and k<=6\n";
        return 2;
    }
    if (k > n_input) return 2;
    n = static_cast<int>(n_input);

    vector<int> initial(k);
    int initial_sum = 0;
    for (int &x : initial) {
        if (!(cin >> x) || x < 1 || x > n) return 2;
        initial_sum += x;
    }
    if (initial_sum != n) return 2;
    string extra;
    if (cin >> extra) return 2;

    int positive = 0;
    for (int x : initial) positive += (x > 0);
    if (positive <= 1) {
        cout << "0\n";
        return 0;
    }

    current_state.assign(k, 0);
    generate_states(0, n);
    if (too_large || states.empty()) {
        cerr << "merge BF state space is too large\n";
        return 2;
    }

    map<vector<int>, int> index;
    for (int i = 0; i < static_cast<int>(states.size()); ++i) {
        index[states[i]] = i;
    }
    auto it_initial = index.find(initial);
    if (it_initial == index.end()) return 2;

    const int s = static_cast<int>(states.size());
    vector<vector<int>> transition(s, vector<int>(s, 0));
    for (int row = 0; row < s; ++row) {
        const vector<int> &state = states[row];
        long long denominator = 0;
        for (int i = 0; i < k; ++i) {
            for (int j = 0; j < k; ++j) {
                if (i != j) denominator += 1LL * state[i] * state[j];
            }
        }
        const int inv_den = mod_pow(denominator % MOD, MOD - 2);
        for (int from = 0; from < k; ++from) {
            if (state[from] == 0) continue;
            for (int to = 0; to < k; ++to) {
                if (from == to || state[to] == 0) continue;
                vector<int> next = state;
                --next[from];
                ++next[to];
                auto it = index.find(next);
                if (it == index.end()) continue;  // absorbing state
                const int weight = static_cast<int>(
                    1LL * state[from] * state[to] % MOD
                );
                const int probability = static_cast<int>(
                    1LL * weight * inv_den % MOD
                );
                int &cell = transition[row][it->second];
                cell += probability;
                if (cell >= MOD) cell -= MOD;
            }
        }
    }

    vector<vector<int>> matrix(s, vector<int>(s, 0));
    for (int i = 0; i < s; ++i) {
        matrix[i][i] = 1;
        for (int j = 0; j < s; ++j) {
            matrix[i][j] -= transition[i][j];
            if (matrix[i][j] < 0) matrix[i][j] += MOD;
        }
    }

    vector<int> rhs_first(s, 1);
    vector<int> first;
    try {
        first = solve_linear(matrix, rhs_first);
    } catch (...) {
        return 2;
    }

    vector<int> rhs_second(s, 1);
    for (int i = 0; i < s; ++i) {
        long long expected_next = 0;
        for (int j = 0; j < s; ++j) {
            expected_next += 1LL * transition[i][j] * first[j] % MOD;
            if (expected_next >= (1LL << 62)) expected_next %= MOD;
        }
        rhs_second[i] = static_cast<int>((1 + 2 * (expected_next % MOD)) % MOD);
    }

    vector<int> second;
    try {
        second = solve_linear(matrix, rhs_second);
    } catch (...) {
        return 2;
    }

    const int id = it_initial->second;
    const long long variance =
        (second[id] - 1LL * first[id] * first[id]) % MOD;
    cout << (variance + MOD) % MOD << '\n';
    return 0;
}
