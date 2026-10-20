// 余镜 错误程序 8：复杂度过高但常常跑得快（complexity 层）。
//
// 推导与标准解完全相同（中心扩展 running gcd 递推 D，g == 1 提前终止），
// 唯一的差别是每个区间的因子数用试除法 O(sqrt D) 现算。
// 复杂度上界 O(n^2 sqrt M)，但随机数据上 D 几乎立刻变成 1，提前终止让它飞快，
// 能混过 5*10^6 上下的随机/全相等数据；只有 D 经常取到大值的数据
// （levels 的 D 为 B 的倍数、extreme 的 D = M、square 长段的大 D）才会超时。
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
			if (g == 1) break;                 // 外层贡献恒为 0
			long long cnt = 0;                 // 试除统计 D 的不小于 2 的因子数
			for (long long d = 2; d * d <= g; ++d)
				if (g % d == 0) { if (d * d == g) ++cnt; else cnt += 2; }
			ans += cnt + 1;                    // 加上 D 自身
		}
	}
	printf("%lld\n", ans);
	return 0;
}