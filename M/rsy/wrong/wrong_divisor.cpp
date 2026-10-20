// 余镜 错误程序 5：实现错误（implementation 层）——因子计数漏掉 D 本身。
//
// 中心扩展的框架与标准解相同，但手写的试除因子计数只枚举到 sqrt(D)，
// 把「D 本身」这个因子漏掉了（m = D 恒为可行解，因为 D 整除所有镜像差）。
// 于是每个 D >= 2 的区间都少算了 1。在所有镜像差全为 0 的数据上
// （例如所有值相等）结果碰巧正确，但只要存在 D >= 2 的区间就会出错。
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
int n, M;
int a[MAXN];

inline int gcd(int x, int y) {
	while (y) { int t = x % y; x = y; y = t; }
	return x;
}

// 统计 d 的不小于 2 的因子个数，但漏掉了 d 本身
inline int countDivisors(int d) {
	int s = 0;
	for (int i = 2; (long long)i * i <= d; ++i)
		if (d % i == 0) {
			s += 2;              // i 与 d/i
			if (i * i == d) --s; // 平方数去重
		}
	return s;  // 错误：还应 +1（d 本身，d >= 2 时）
}

int main() {
	n = io::readInt();
	M = io::readInt();
	for (int i = 1; i <= n; ++i) a[i] = io::readInt();

	long long ans = 0;
	for (int c = 2; c <= 2 * n; ++c) {
		int lo = c - n > 1 ? c - n : 1;
		int hi = c >> 1;
		int g = 0;
		for (int k = hi; k >= lo; --k) {
			int j = c - k;
			if (k == j) continue;  // 单点区间不计入答案
			g = gcd(g, a[k] > a[j] ? a[k] - a[j] : a[j] - a[k]);
			ans += g == 0 ? (M - 1) : countDivisors(g);
			if (g == 1) break;
		}
	}
	printf("%lld\n", ans);
	return 0;
}
