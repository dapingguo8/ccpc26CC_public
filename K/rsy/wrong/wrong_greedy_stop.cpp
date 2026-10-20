// 纸带染色 错误程序 6：思路错误（idea 层）——贪心提前终止。
//
// 从 r 往左扫，维护 P = 后续前缀操作的最大 x、S = 后续后缀操作的最小 x，
// 但一遇到「当前操作不产生新颜色」就直接 break，误以为更靠左的操作也不可能可见。
// 反例：前缀操作依次为 x=5、x=1、x=9（从右往左），扫到 x=1 时因 1 <= P=5 就 break，
// 漏掉更左侧 x=9 > 5 的可见操作。
//
// 这是一个「看起来能提前剪枝、随机数据上跑得很快」的贪心，实际逻辑错误。
// 数据上几乎每个点都 WA，在 5*10^5 规模的大点上还会超时。
#include <cstdio>

static int o[500005], x[500005];

int main() {
	int n, m, q;
	if (scanf("%d %d %d", &n, &m, &q) != 3) return 0;
	for (int i = 1; i <= m; ++i) scanf("%d %d", &o[i], &x[i]);
	for (int t = 0; t < q; ++t) {
		int l, r;
		scanf("%d %d", &l, &r);
		int P = 0, S = n + 1, ans = 0;
		for (int i = r; i >= l; --i) {
			if (o[i] == 0) {
				if (x[i] > P) { ++ans; P = x[i]; }
				else break;
			} else {
				if (x[i] < S) { ++ans; S = x[i]; }
				else break;
			}
			if (P >= S - 1) break;
		}
		printf("%d\n", ans);
	}
	return 0;
}