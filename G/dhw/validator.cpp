#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// Standalone input validator, no testlib dependency.
// Usage: validator [input.in]; stdin when no filename is supplied.
// Exit 0 = valid; 1 = invalid input; 2 = usage/open error.
// Checks prescribed line structure; accepts LF/CRLF, horizontal whitespace,
// trailing blank lines, and a final line without a newline.
class Reader {
    istream &in;
public:
    int line = 0, test = 0;
    explicit Reader(istream &input): in(input) {}
    void require(bool condition, const string &message) const {
        if (!condition)
            throw runtime_error("test " + to_string(test) + ", line " +
                                to_string(line) + ": " + message);
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
            require(value <= hi, name + " exceeds " + to_string(hi));
        }
        require(value >= lo, name + " must be >= " + to_string(lo));
        return value;
    }
    string binary(int n, const string &name) {
        auto v = tokens();
        require(v.size() == 1, name + " must occupy one line with one token");
        require(v[0].size() == static_cast<size_t>(n), name + " length must equal n");
        for (char c : v[0]) require(c == '0' || c == '1', name + " contains a non-binary character");
        return v[0];
    }
    void eof() {
        string s;
        while (getline(in, s)) {
            ++line;
            for (unsigned char c : s)
                require(isspace(c) != 0, "extra content after the declared T test cases");
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
        r.require(first.size() == 1, "first line must contain only T");
        int T = r.integer(first[0], 1, 1000, "T");
        int sumN = 0, sumM = 0;
        for (r.test = 1; r.test <= T; ++r.test) {
            auto nm = r.tokens();
            r.require(nm.size() == 2, "expected n m");
            int n = r.integer(nm[0], 1, 200000, "n");
            int m = r.integer(nm[1], 1, 200000, "m");
            sumN += n; sumM += m;
            r.require(sumN <= 200000, "sum n exceeds 200000");
            r.require(sumM <= 200000, "sum m exceeds 200000");
            r.binary(n, "A");
            r.binary(n, "B");
            vector<pair<int,int>> intervals;
            intervals.reserve(m);
            for (int j = 0; j < m; ++j) {
                auto lr = r.tokens();
                r.require(lr.size() == 2, "expected l r for interval " + to_string(j + 1));
                int l = r.integer(lr[0], 1, n, "l");
                int right = r.integer(lr[1], l, n, "r");
                intervals.emplace_back(l, right);
            }
            sort(intervals.begin(), intervals.end());
            for (int j = 1; j < m; ++j)
                r.require(intervals[j] != intervals[j - 1],
                          "duplicate interval [" + to_string(intervals[j].first) + "," +
                          to_string(intervals[j].second) + "]");
        }
        r.test = T;
        r.eof();
        cerr << "VALID: T=" << T << ", sum_n=" << sumN << ", sum_m=" << sumM << '\n';
        return 0;
    } catch (const exception &e) {
        cerr << "INVALID: " << e.what() << '\n';
        return 1;
    }
}
