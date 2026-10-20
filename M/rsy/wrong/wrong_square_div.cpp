// 余镜 错误程序 9：实现错误（implementation 层）——完全平方数因子漏算。
//
// 复杂度正确 O(n^2 log)，前四行推导与标准解相同，但因子计数写成
// 「枚举 d < sqrt(D) 成对计数、再加 D 自身」，漏掉 D 恰为完全平方数时
// 多出来的那一个 sqrt(D) 因子。当某个区间的 D 是完全平方数（>= 4）时少算 1。
// 随机数据里长度 2 的区间 D = |a_i - a_{i+1}| 本身就常是完全平方数，
// 因此该 off-by-one 会被随机数据抓住。
#include <cstdio>

static int a[8005];

static inline int gcd(int x, int y) { while (y) { int t = x % y; x = y; y = t; } return x; }

int main() {
	int n, M;
	if (scanf("%d %d", &n, &M) != 2) return 0;
	for (int i = 1; i <= n; ++i) scanf("%d", &a[i]);
	long long ans = 0;
	for (int c = 2; c <= 2 * n; ++c) {
		int lo = c - n > 1 ? c - n : 1, hi = c >> 1, g = 0;
		for (int k = hi; k >= lo; --k) {
			int j = c - k;
			if (k == j) continue;
			g = gcd(g, a[k] > a[j] ? a[k] - a[j] : a[j] - a[k]);
			if (g == 0) { ans += M - 1; continue; }
			if (g == 1) break;
			long long cnt = 0;
			for (long long d = 2; d * d < g; ++d)   // BUG: 完全平方数时漏掉 d*d==D
				if (g % d == 0) cnt += 2;
			ans += cnt + 1;
		}
	}
	printf("%lld\n", ans);
	return 0;
}