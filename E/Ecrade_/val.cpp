#include <bits/stdc++.h>
#include "testlib.h"
using namespace std;

const int MAX_T = 1000;
const int MAX_SUM_N = 200000;

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);

    int T = inf.readInt(1, MAX_T, "T");
    inf.readEoln();

    int sum_n = 0;
    for (int tc = 1; tc <= T; ++tc) {
        setTestCase(tc);

        int n = inf.readInt(8, MAX_SUM_N, "n");
        inf.readSpace();
        int a1 = inf.readInt(0, n - 1, "a1");
        inf.readSpace();
        int a2 = inf.readInt(0, n - 1, "a2");
        inf.readSpace();
        int a3 = inf.readInt(0, n - 1, "a3");
        inf.readEoln();

        ensuref(a1 + a2 + a3 == n - 1, "a1 + a2 + a3 must equal n - 1");
        sum_n += n;
        ensuref(sum_n <= MAX_SUM_N, "sum of n must not exceed 200000");
    }

    inf.readEof();
    return 0;
}
