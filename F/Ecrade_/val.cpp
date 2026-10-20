#include <bits/stdc++.h>
#include "testlib.h"
using namespace std;

int main(int argc, char *argv[]) {
    registerValidation(argc, argv);

    int test_count = inf.readInt(1, 200, "T");
    inf.readEoln();
    long long sum_n = 0;

    for (int test = 1; test <= test_count; ++test) {
        setTestCase(test);
        int n = inf.readInt(2, 100, "n");
        inf.readEoln();
        sum_n += n;
        ensuref(sum_n <= 400, "sum of n must not exceed 400");
        for (int i = 0; i < n; ++i) {
            inf.readInt(-1, n, format("a[%d]", i + 1));
            if (i + 1 < n) inf.readSpace();
            else inf.readEoln();
        }
    }
    inf.readEof();
    return 0;
}
