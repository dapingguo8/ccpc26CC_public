// 余镜 错误程序 10：实现错误（implementation 层）——提前终止条件写成 g < 2。
//
// 与标准解相同地中心扩展、running gcd 递推，但把「g == 1 就可以停」写成了
// 「g < 2 就停」。于是当 running gcd 变成 0（所有镜像差都为 0，即 D = 0）时
// 也会中断，丢掉外层区间应计的 M-1 贡献。
// 在全相等（equal）、两个值（few）、原序列回文（pal）等 D = 0 频繁出现的数据上
// 大量 WA。
#include <cstdio>

static int a[8005], cnt[1000005];

static inline int gcd(int x, int y) { while (y) { int t = x % y; x = y; y = t; } return x; }

int main() {
	int n, M;
	if (scanf("%d %d", &n, &M) != 2) return 0;
	for (int i = 1; i <= n; ++i) scanf("%d", &a[i]);
	for (int i = 2; i <= M; ++i)
		for (int j = i; j <= M; j += i) ++cnt[j];
	long long ans = 0;
	for (int c = 2; c <= 2 * n; ++c) {
		int lo = c - n > 1 ? c - n : 1, hi = c >> 1, g = 0;
		for (int k = hi; k >= lo; --k) {
			int j = c - k;
			if (k == j) continue;
			g = gcd(g, a[k] > a[j] ? a[k] - a[j] : a[j] - a[k]);
			ans += g == 0 ? (M - 1) : cnt[g];
			if (g < 2) break;              // BUG: g == 0 时也中断
		}
	}
	printf("%lld\n", ans);
	return 0;
}