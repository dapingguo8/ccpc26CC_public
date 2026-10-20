// 余镜 输入校验器（validator，testlib 严格模式，按 LF 行尾检查）
//
// 依赖：testlib.h（与本文件同目录，取自本仓库 day1/average/data/chk/testlib.h）。
// 编译：g++ -O2 -std=c++17 -DFOR_LINUX -o val val.cpp
//   本数据包所有数据统一为 LF 行尾。testlib 的严格模式按平台判定行尾
//   （Windows 认 CRLF、其余平台认 LF），因此在 Windows 上本地校验时必须
//   定义 FOR_LINUX，让严格模式按 LF 判定；在 Linux 评测机上该宏无影响。
// 运行：./val < data.in
//
// 严格检查的内容（与 conf.yaml、statement/zh-cn.md 一致）：
//   第 1 行：n M        1 <= n <= 8000，2 <= M <= 10^6
//   第 2 行：a_1..a_n   0 <= a_i <= M，同一行内恰用一个空格分隔
//   行尾为 LF、第 2 行之后不得有多余内容。
#include "testlib.h"

int main(int argc, char *argv[]) {
	registerValidation(argc, argv);
	inf.strict = true;

	const int MAX_N = 8000;
	const int MAX_M = 1000000;

	int n = inf.readInt(1, MAX_N, "n");
	inf.readSpace();
	int M = inf.readInt(2, MAX_M, "M");
	inf.readEoln();

	for (int i = 1; i <= n; ++i) {
		inf.readInt(0, M, format("a_%d", i));
		if (i < n) inf.readSpace();
	}
	inf.readEoln();

	inf.readEof();
	return 0;
}
