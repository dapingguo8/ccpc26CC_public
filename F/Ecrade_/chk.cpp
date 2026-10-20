#include <bits/stdc++.h>
using namespace std;

using int64 = long long;
const int64 MOD = 1000000007;

vector<int> erase_record(const vector<int> &p) {
    int n = (int)p.size();
    vector<int> alive(n), result(n);
    iota(alive.begin(), alive.end(), 0);
    for (int round = 1;; ++round) {
        vector<int> removed;
        for (int i = 1; i + 1 < (int)alive.size(); ++i) {
            if (p[alive[i]] < p[alive[i - 1]] &&
                p[alive[i]] < p[alive[i + 1]]) removed.push_back(alive[i]);
        }
        if (removed.empty()) return result;
        for (int x : removed) result[x] = round;
        vector<int> next;
        for (int x : alive) {
            if (find(removed.begin(), removed.end(), x) == removed.end()) {
                next.push_back(x);
            }
        }
        alive.swap(next);
    }
}

int main(int argc, char *argv[]) {
    mt19937_64 random_engine(2026081001);
    int rounds = (argc > 1 ? atoi(argv[1]) : 20000);
    for (int test = 1; test <= rounds; ++test) {
        int n = 2 + random_engine() % 8;
        vector<int> p(n);
        iota(p.begin(), p.end(), 1);
        shuffle(p.begin(), p.end(), random_engine);
        vector<int> real = erase_record(p);
        vector<int> a(n);
        for (int i = 0; i < n; ++i) {
            a[i] = (random_engine() % 4 == 0 ? -1 : real[i]);
            if (a[i] > 3) a[i] = -1;
        }
        vector<int64> expected(1);
        int answer = 0;
        vector<int> q(n);
        iota(q.begin(), q.end(), 1);
        do {
            vector<int> record = erase_record(q);
            bool ok = true;
            for (int i = 0; i < n; ++i) {
                if (a[i] != -1 && a[i] != record[i]) ok = false;
            }
            answer += ok;
        } while (next_permutation(q.begin(), q.end()));

        ofstream input("tmp.in");
        input << 1 << '\n' << n << '\n';
        for (int i = 0; i < n; ++i) input << a[i] << " \n"[i + 1 == n];
        input.close();
        if (system("std.exe < tmp.in > tmp.out")) return 1;
        ifstream output("tmp.out");
        int64 received;
        output >> received;
        if (received != answer % MOD) {
            cerr << "wrong answer on test " << test << '\n';
            cerr << n << '\n';
            for (int x : a) cerr << x << ' ';
            cerr << "\nexpected " << answer << ", received " << received << '\n';
            return 1;
        }
    }
    cout << "chk passed\n";
    return 0;
}
