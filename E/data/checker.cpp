#include <bits/stdc++.h>
#include "testlib.h"
using namespace std;

struct DSU {
    vector<int> parent;

    explicit DSU(int n) : parent(n + 1, -1) {}

    int find(int x) {
        return parent[x] < 0 ? x : parent[x] = find(parent[x]);
    }

    bool unite(int x, int y) {
        x = find(x);
        y = find(y);
        if (x == y) return false;
        if (parent[x] > parent[y]) swap(x, y);
        parent[x] += parent[y];
        parent[y] = x;
        return true;
    }
};

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);

    int T = inf.readInt();
    for (int tc = 1; tc <= T; ++tc) {
        int n = inf.readInt();
        int a[4];
        for (int k = 1; k <= 3; ++k) a[k] = inf.readInt();

        string first = ouf.readToken();
        if (first == "-1") {
            if (a[1] != 0 || a[3] != 0) {
                quitf(_wa, "case %d: a solution exists", tc);
            }
            continue;
        }

        vector<pair<int, int>> edges;
        try {
            edges.push_back({stoi(first), ouf.readInt()});
        } catch (...) {
            quitf(_wa, "case %d: invalid output", tc);
        }
        for (int i = 1; i < n - 1; ++i) {
            edges.push_back({ouf.readInt(), ouf.readInt()});
        }

        vector<int> order(n);
        for (int& x : order) x = ouf.readInt();

        DSU dsu(n);
        vector<vector<int>> graph(n + 1);
        for (auto [u, v] : edges) {
            if (u < 1 || u > n || v < 1 || v > n || u == v || !dsu.unite(u, v)) {
                quitf(_wa, "case %d: the given edges do not form a tree", tc);
            }
            graph[u].push_back(v);
            graph[v].push_back(u);
        }

        vector<int> seen(n + 1);
        for (int x : order) {
            if (x < 1 || x > n || seen[x]++) {
                quitf(_wa, "case %d: the sequence is not a permutation", tc);
            }
        }

        int log_n = 1;
        while ((1 << log_n) <= n) ++log_n;
        vector<vector<int>> up(log_n, vector<int>(n + 1));
        vector<int> depth(n + 1), bfs_order = {1};

        for (int i = 0; i < (int)bfs_order.size(); ++i) {
            int u = bfs_order[i];
            for (int v : graph[u]) {
                if (v == up[0][u]) continue;
                up[0][v] = u;
                depth[v] = depth[u] + 1;
                bfs_order.push_back(v);
            }
        }
        if ((int)bfs_order.size() != n) quitf(_wa, "case %d: disconnected tree", tc);

        for (int k = 1; k < log_n; ++k) {
            for (int v = 1; v <= n; ++v) {
                up[k][v] = up[k - 1][up[k - 1][v]];
            }
        }

        auto lca = [&](int x, int y) {
            if (depth[x] < depth[y]) swap(x, y);
            int diff = depth[x] - depth[y];
            for (int k = 0; k < log_n; ++k) {
                if (diff >> k & 1) x = up[k][x];
            }
            if (x == y) return x;
            for (int k = log_n - 1; k >= 0; --k) {
                if (up[k][x] != up[k][y]) {
                    x = up[k][x];
                    y = up[k][y];
                }
            }
            return up[0][x];
        };

        int count[4] = {};
        for (int i = 0; i + 1 < n; ++i) {
            int w = lca(order[i], order[i + 1]);
            int distance = depth[order[i]] + depth[order[i + 1]] - 2 * depth[w];
            if (distance < 1 || distance > 3) {
                quitf(_wa, "case %d: a consecutive distance is not in [1, 3]", tc);
            }
            ++count[distance];
        }

        for (int k = 1; k <= 3; ++k) {
            if (count[k] != a[k]) {
                quitf(_wa, "case %d: wrong number of distance-%d moves", tc, k);
            }
        }
    }

    if (!ouf.seekEof()) quitf(_wa, "extra output");
    quitf(_ok, "all constructions are valid");
}
