// 余镜 暴力程序：完全按定义模拟——枚举每个 m，把序列对 m 取模后
// 逐中心扩展统计回文子区间数。复杂度 O(M · n^2)，
// 只能在 n、M 都很小的数据上运行，用于对拍验证。
#include <cstdio>
#include <vector>

int main() {
	int n, M;
	if (scanf("%d %d", &n, &M) != 2) return 0;
	std::vector<int> a(n + 1), b(n + 1);
	for (int i = 1; i <= n; ++i) scanf("%d", &a[i]);

	long long ans = 0;
	for (int m = 2; m <= M; ++m) {
		for (int i = 1; i <= n; ++i) b[i] = a[i] % m;
		// 统计 b[1..n] 中长度 >= 2 的回文子区间数：枚举中心 c = l + r 向外扩展
		for (int c = 2; c <= 2 * n; ++c) {
			int lo = c - n > 1 ? c - n : 1;
			int hi = c >> 1;
			for (int k = hi; k >= lo; --k) {
				if (k == c - k) continue;  // 单点区间不计入
				if (b[k] != b[c - k]) break;
				++ans;
			}
		}
	}
	printf("%lld\n", ans);
	return 0;
}
