// 纸带染色 输入校验器（validator，testlib 严格模式，按 LF 行尾检查）
//
// 依赖：testlib.h（与本文件同目录，取自本仓库 day1/average/data/chk/testlib.h）。
// 编译：g++ -O2 -std=c++17 -DFOR_LINUX -o val val.cpp
//   本数据包所有数据统一为 LF 行尾。testlib 的严格模式按平台判定行尾
//   （Windows 认 CRLF、其余平台认 LF），因此在 Windows 上本地校验时必须
//   定义 FOR_LINUX，让严格模式按 LF 判定；在 Linux 评测机上该宏无影响。
// 运行：./val < data.in
//   validator 固定从 stdin 读入测试数据；命令行只接受 testlib 自己的
//   --testset / --group / --testOverviewLogFileName 等选项，不接受文件名。
//
// 严格检查的内容（与 conf.yaml、statement/zh-cn.md 一致）：
//   第 1 行：n m q        1 <= n <= 10^9，1 <= m, q <= 5 * 10^5
//   接下来 m 行：o_i x_i   o_i ∈ {0, 1}，1 <= x_i <= n
//   接下来 q 行：l_j r_j   1 <= l_j <= r_j <= m
//   同一行内恰用一个空格分隔、行尾为 LF、最后一个询问之后不得有多余内容。
#include "testlib.h"

int main(int argc, char *argv[]) {
    registerValidation(argc, argv);
    inf.strict = true;

    const int MAX_N = 1000000000;
    const int MAX_MQ = 500000;

    int n = inf.readInt(1, MAX_N, "n");
    inf.readSpace();
    int m = inf.readInt(1, MAX_MQ, "m");
    inf.readSpace();
    int q = inf.readInt(1, MAX_MQ, "q");
    inf.readEoln();

    for (int i = 1; i <= m; ++i) {
        inf.readInt(0, 1, format("o_%d", i));
        inf.readSpace();
        inf.readInt(1, n, format("x_%d", i));
        inf.readEoln();
    }

    for (int j = 1; j <= q; ++j) {
        int l = inf.readInt(1, m, format("l_%d", j));
        inf.readSpace();
        int r = inf.readInt(1, m, format("r_%d", j));
        inf.readEoln();
        ensuref(l <= r, "询问 %d：l = %d 大于 r = %d", j, l, r);
    }

    inf.readEof();
    return 0;
}