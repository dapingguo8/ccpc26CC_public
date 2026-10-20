#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);

    const int MAX_T = 100000;
    const int MAX_SUM_N = 1000000;
    const int t = inf.readInt(1, MAX_T, "T");
    inf.readEoln();

    int sumN = 0;
    for (int tc = 1; tc <= t; ++tc) {
        setTestCase(tc);
        const std::string a = inf.readToken("[01]{1,1000000}", "A");
        inf.readEoln();
        sumN += static_cast<int>(a.size());
        ensuref(sumN <= MAX_SUM_N, "sum N exceeds %d", MAX_SUM_N);
    }
    inf.readEof();
}
