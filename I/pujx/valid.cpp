#include "testlib.h"
using namespace std;

signed main(int argc, char** argv) {
    registerValidation(argc, argv);

    addFeature("all 0");
    addFeature("all 1");
    addFeature("same");

    int t = inf.readInt(1, 20'000, "T");
    inf.readSpace();
    int r = inf.readInt(1, 1, "r");
    inf.readEoln();
    int sum = 0;

    for (int _ = 1; _ <= t; _++) {
        int n = inf.readInt(1, 500'000, "n");
        inf.readEoln();
        ensuref((sum += n) <= 500'000, "sum of n exceeds 500000");
        string s = inf.readToken(format("[01]{%d}", n), "s");
        inf.readEoln();

        if (s.find('0') == string::npos) feature("all 1");
        if (s.find('1') == string::npos) feature("all 0");
        if (count(s.begin(), s.end(), '0') == count(s.begin(), s.end(), '1'))
            feature("same");
    }

    inf.readEof();
}