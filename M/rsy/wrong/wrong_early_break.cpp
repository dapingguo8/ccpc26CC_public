// 余镜 错误程序 3：复杂度过高但极易混过（complexity 层，易混过）。
//
// 与 wrong_cubic 同为 O(n^3) 暴力，但扫描镜像位置时一旦 gcd 变成 1
// 就提前终止。随机大数据上几乎每个区间扫两三个位置就停，实际跑得
// 飞快，很容易混过随机构造的最大数据；但一旦镜像差长期不互质
// （例如所有值相等、或取值只有两种且差大于 1），提前终止永不触发，
// 退化为完整的 O(n^3)，在 n = 8000 时必然超时。
#include <cstdio>
#include <vector>

inline int gcd(int x, int y) {
	while (y) { int t = x % y; x = y; y = t; }
	return x;
}

int main() {
	int n, M;
	if (scanf("%d %d", &n, &M) != 2) return 0;
	std::vector<int> a(n + 1), cnt(M + 1, 0);
	for (int i = 1; i <= n; ++i) scanf("%d", &a[i]);

	for (int i = 2; i <= M; ++i)
		for (int j = i; j <= M; j += i) ++cnt[j];

	long long ans = 0;
	for (int l = 1; l <= n; ++l)
		for (int r = l + 1; r <= n; ++r) {  // 只统计长度 >= 2 的区间
			int g = 0;
			for (int k = l; k + k < l + r; ++k) {
				int d = a[k] > a[l + r - k] ? a[k] - a[l + r - k] : a[l + r - k] - a[k];
				g = gcd(g, d);
				if (g == 1) break;
			}
			ans += g == 0 ? (M - 1) : cnt[g];
		}
	printf("%lld\n", ans);
	return 0;
}
