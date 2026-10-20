// 余镜 错解（implementation 层）：累加器只用 32 位无符号整数。
//
// 与 std.cpp 唯一的区别是答案累加到 unsigned int：真实答案最大可达
// n(n-1)/2 * (M-1) ≈ 3.2 * 10^13，超过 2^32 后按 2^32 回绕（无符号溢出是
// 良定义行为），在 equal 等答案较大的数据点上 WA；小数据（答案 < 2^32）
// 结果恰好正确，能混过小规模测试。
// 其余筛法、中心扩展、gcd 递推全部与 std 一致。

#include <cstdio>

namespace io {
const int BUFSIZE = 1 << 22;
char buf[BUFSIZE];
int len = 0, pos = 0;
inline int gc() {
	if (pos == len) {
		len = (int)fread(buf, 1, BUFSIZE, stdin);
		pos = 0;
		if (len <= 0) return -1;
	}
	return buf[pos++];
}
inline int readInt() {
	int c = gc();
	while (c != -1 && (c < '0' || c > '9')) c = gc();
	int x = 0;
	while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
	return x;
}
}  // namespace io

static const int MAXN = 8005;
static const int MAXM = 1000005;

int n, M;
int a[MAXN];
int cnt[MAXM];

inline int gcd(int x, int y) {
	while (y) { int t = x % y; x = y; y = t; }
	return x;
}

int main() {
	n = io::readInt();
	M = io::readInt();
	for (int i = 1; i <= n; ++i) a[i] = io::readInt();

	for (int i = 2; i <= M; ++i)
		for (int j = i; j <= M; j += i) ++cnt[j];

	unsigned int ans = 0;  // BUG：答案需要 64 位
	for (int c = 2; c <= 2 * n; ++c) {
		int lo = c - n > 1 ? c - n : 1;
		int hi = c >> 1;
		int g = 0;
		for (int k = hi; k >= lo; --k) {
			int j = c - k;
			if (k == j) continue;  // 单点区间不计入答案
			g = gcd(g, a[k] > a[j] ? a[k] - a[j] : a[j] - a[k]);
			ans += g == 0 ? (M - 1) : cnt[g];
			if (g == 1) break;
		}
	}

	printf("%u\n", ans);
	return 0;
}
