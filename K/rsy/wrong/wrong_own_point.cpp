// 纸带染色 错误程序 7：思路错误（idea 层）——只看自身端点是否被覆盖。
//
// 对每个询问从 r 往左扫，维护 P、S，错误地认为
//   「操作 i 可见 <=> 端点 x_i 没有被任何后续操作覆盖」，即 x_i > P 且 x_i < S。
// 实际条件是 A_i 中存在任意一点未被覆盖，比「端点未被覆盖」宽松：
// 例如前缀操作 i 的右端点 x_i 被后续前缀覆盖，但 A_i 靠近纸带另一侧仍可能暴露。
// 因此该贪心会漏计可见颜色。
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
			if (x[i] > P && x[i] < S) ++ans;   // 只看端点 x_i 是否被覆盖
			if (o[i] == 0) { if (x[i] > P) P = x[i]; }
			else { if (x[i] < S) S = x[i]; }
		}
		printf("%d\n", ans);
	}
	return 0;
}