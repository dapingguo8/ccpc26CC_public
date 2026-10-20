// 余镜 错误程序 2：思路正确但复杂度过高（complexity 层）。
//
// 推导与标准解一致（镜像差的 gcd + 因子计数），但对每个区间都重新
// O(r-l+1) 扫描镜像位置求 gcd，没有任何递推，总计 O(n^3)。
// 小数据（n <= 数百）上结果与标准解一致，但在 n = 8000 的最大数据上
// 必然超时，因此只有在放大规模时才会被杀（scale_escalation）。
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
			}
			ans += g == 0 ? (M - 1) : cnt[g];
		}
	printf("%lld\n", ans);
	return 0;
}
