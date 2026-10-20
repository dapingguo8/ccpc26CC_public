#include <cctype>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

// Usage: validator [input.in]; stdin if no filename is provided.
// Exit 0: valid, 1: invalid input, 2: usage/open error.
// Single test case. Check the prescribed line structure; accept LF/CRLF,
// horizontal whitespace, trailing blank lines and no final newline.
class Reader {
    istream &in;
public:
    int line = 0;
    explicit Reader(istream &input): in(input) {}
    void require(bool condition, const string &message) const {
        if (!condition) throw runtime_error("line " + to_string(line) + ": " + message);
    }
    vector<string> tokens() {
        string s;
        ++line;
        require(bool(getline(in, s)), "unexpected EOF");
        if (!s.empty() && s.back() == '\r') s.pop_back();
        istringstream parser(s);
        vector<string> result;
        string token;
        while (parser >> token) result.push_back(token);
        return result;
    }
    int integer(const string &s, int lo, int hi, const string &name) const {
        require(!s.empty(), "missing " + name);
        int value = 0;
        for (char c : s) {
            require(c >= '0' && c <= '9', name + " must be a decimal nonnegative integer");
            require(value < hi / 10 || (value == hi / 10 && c - '0' <= hi % 10),
                    name + " exceeds " + to_string(hi));
            value = value * 10 + (c - '0');
        }
        require(value >= lo, name + " must be >= " + to_string(lo));
        return value;
    }
    void eof() {
        string s;
        while (getline(in, s)) {
            ++line;
            for (unsigned char c : s)
                require(isspace(c) != 0, "extra content after the H course lines");
        }
    }
};

int main(int argc, char **argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    if (argc > 2) { cerr << "Usage: validator [input.in]\n"; return 2; }
    ifstream file;
    if (argc == 2) {
        file.open(argv[1], ios::binary);
        if (!file) { cerr << "Cannot open input file\n"; return 2; }
    }
    Reader r(argc == 2 ? static_cast<istream&>(file) : cin);
    try {
        auto first = r.tokens();
        r.require(first.size() == 5, "expected n m N H K");
        int n = r.integer(first[0], 1, 10000, "n");
        int m = r.integer(first[1], 1, 10000, "m");
        int N = r.integer(first[2], 1, 10000, "N");
        int H = r.integer(first[3], 1, 10000, "H");
        int K = r.integer(first[4], 2, 1000, "K");
        r.require(1LL * n * m <= 10000, "n*m exceeds 10000");
        auto parents = r.tokens();
        r.require(parents.size() == static_cast<size_t>(N + H), "expected N+H parents");
        vector<int> parent(N + H + 1), q(N + 1, 0);
        vector<vector<int>> children(N + 1);
        for (int v = 1; v <= N + H; ++v) {
            parent[v] = r.integer(parents[v - 1], 0, N, "fa_" + to_string(v));
            r.require(parent[v] != v, "node " + to_string(v) + " is its own parent");
            children[parent[v]].push_back(v);
        }
        auto weights = r.tokens();
        r.require(weights.size() == static_cast<size_t>(N), "expected N module weights");
        for (int v = 1; v <= N; ++v)
            q[v] = r.integer(weights[v - 1], 0, 1000000000, "q_" + to_string(v));
        // Read all weights before testing: parent labels need not be smaller.
        for (int v = 1; v <= N; ++v) {
            r.require(!children[v].empty(), "module " + to_string(v) + " has no children");
            r.require(q[v] >= q[parent[v]], "q decreases on edge to module " + to_string(v));
        }
        // Every non-root node has exactly one parent. Reachability from root
        // checks both connectedness and the absence of disconnected cycles.
        vector<int> order(1, 0);
        vector<char> seen(N + H + 1, false);
        seen[0] = true;
        for (size_t i = 0; i < order.size(); ++i) {
            int u = order[i];
            if (u > N) continue;
            for (int v : children[u]) {
                r.require(!seen[v], "cycle detected");
                seen[v] = true;
                order.push_back(v);
            }
        }
        r.require(order.size() == static_cast<size_t>(N + H + 1),
                  "parents do not form a tree rooted at 0 (unreachable nodes or cycle)");
        int totalOptions = 0;
        for (int i = 1; i <= H; ++i) {
            auto options = r.tokens();
            r.require(!options.empty(), "missing course " + to_string(i));
            int l = r.integer(options[0], 1, 10000, "l_" + to_string(i));
            r.require(options.size() == static_cast<size_t>(1 + 2 * l),
                      "course " + to_string(i) + " must contain l followed by l pairs");
            totalOptions += l;
            r.require(totalOptions <= 10000, "sum l_i exceeds 10000");
            for (int j = 0; j < l; ++j) {
                r.integer(options[1 + 2 * j], 1, n, "day for course " + to_string(i));
                r.integer(options[2 + 2 * j], 1, m, "period for course " + to_string(i));
            }
            // Repeated options are not prohibited by the current statement.
        }
        // K may exceed H or n*m: impossible instances are valid inputs.
        r.eof();
        cerr << "VALID: n=" << n << ", m=" << m << ", N=" << N
             << ", H=" << H << ", K=" << K << ", sum_l=" << totalOptions << '\n';
        return 0;
    } catch (const exception &e) {
        cerr << "INVALID: " << e.what() << '\n';
        return 1;
    }
}
