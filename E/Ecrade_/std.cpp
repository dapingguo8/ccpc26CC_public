#include <bits/stdc++.h>
using namespace std;

struct Answer {
    vector<pair<int, int>> edges;
    vector<int> order;
};

Answer construct_answer(int n, int a, int b, int c) {
    Answer ans;
    vector<int> order;
    int vertices = 0;
    int current = 0, old_p = 0, old_q = 0;
    int base_a = 0, base_b = 0, base_c = 0;

    auto set_base = [&](vector<pair<int, int>> edges, vector<int> path,
                        int x, int p, int q, int ca, int cb, int cc) {
        ans.edges = move(edges);
        order = move(path);
        vertices = (int)order.size();
        current = x;
        old_p = p;
        old_q = q;
        base_a = ca;
        base_b = cb;
        base_c = cc;
    };

    if (c == 0) {
        if (b == 0) {
            for (int i = 1; i < n; ++i) ans.edges.push_back({i, i + 1});
            for (int i = 1; i <= n; ++i) order.push_back(i);
            ans.order = move(order);
            return ans;
        }

        vertices = b + 2;
        for (int i = 1; i < vertices; ++i) ans.edges.push_back({i, i + 1});
        for (int i = 1; i <= vertices; i += 2) order.push_back(i);
        for (int i = (vertices % 2 == 0 ? vertices : vertices - 1); i >= 2; i -= 2) {
            order.push_back(i);
        }

        current = 2;
        old_p = 1;
        old_q = 3;
        base_a = 1;
        base_b = b;
    } else if (a > 0 && b > 0) {
        set_base({{1, 2}, {2, 3}, {1, 4}}, {1, 2, 4, 3},
                 3, 2, 1, 1, 1, 1);
    } else if (a >= 2) {
        set_base({{1, 2}, {2, 3}, {1, 4}}, {1, 2, 3, 4},
                 4, 1, 2, 2, 0, 1);
    } else if (a == 1) {
        set_base({{1, 2}, {2, 3}, {1, 4}, {1, 6}, {4, 5}},
                 {1, 2, 5, 6, 3, 4}, 4, 1, 2, 1, 0, 4);
    } else if (b >= 2) {
        set_base({{1, 2}, {2, 3}, {1, 4}}, {1, 3, 4, 2},
                 2, 1, 4, 0, 2, 1);
    } else if (b == 1) {
        set_base({{1, 2}, {2, 3}, {1, 5}, {1, 7}, {3, 4}, {5, 6}},
                 {1, 4, 2, 6, 7, 3, 5}, 5, 1, 2, 0, 1, 5);
    } else {
        set_base({{1, 2}, {2, 3}, {3, 4}, {2, 5}, {1, 6}, {6, 7}, {1, 8}},
                 {1, 4, 5, 6, 3, 8, 7, 2}, 2, 3, 4, 0, 0, 7);
    }

    int add_one = a - base_a;
    int add_two = b - base_b;
    int add_three = c - base_c;

    for (int i = 0; i < add_one; ++i) {
        int vertex = ++vertices;
        ans.edges.push_back({current, vertex});
        order.push_back(vertex);
        current = vertex;
    }

    int p, q;
    if (add_one == 0) {
        p = old_p;
        q = old_q;
    } else if (add_one == 1) {
        p = order[(int)order.size() - 2];
        q = old_p;
    } else {
        p = order[(int)order.size() - 2];
        q = order[(int)order.size() - 3];
    }

    for (int i = 0; i < add_two; ++i) {
        int vertex = ++vertices;
        ans.edges.push_back({p, vertex});
        order.push_back(vertex);
    }

    int last_anchor = p;
    for (int i = 0; i < add_three; ++i) {
        int anchor = (last_anchor == p ? q : p);
        int vertex = ++vertices;
        ans.edges.push_back({anchor, vertex});
        order.push_back(vertex);
        last_anchor = anchor;
    }

    ans.order = move(order);
    return ans;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;
    while (T--) {
        int n, a, b, c;
        cin >> n >> a >> b >> c;

        if (a == 0 && c == 0) {
            cout << -1 << '\n';
            continue;
        }

        Answer ans = construct_answer(n, a, b, c);
        for (auto [u, v] : ans.edges) cout << u << ' ' << v << '\n';
        for (int i = 0; i < n; ++i) {
            cout << ans.order[i] << " \n"[i + 1 == n];
        }
    }
    return 0;
}
