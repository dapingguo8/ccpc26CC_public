// 余镜 错误程序 1：题意理解错误（idea 层）。
//
// 误以为只有「本身就已经回文」的区间才有贡献，完全没意识到取模可以让
// 本来不回文的区间变得回文。对原数组回文的区间贡献 M-1，其余贡献 0。
// 在所有值相等的数据上结果碰巧正确，但例如 a=[1,3], M=2 时
// 区间 [1,2] 在模 2 下为 [1,1] 回文，这里却算成 0。
// （中心扩展实现，O(n^2)，保证它被杀的原因是答案错误而不是超时。）
#include <cstdio>
#include <vector>

int main() {
	int n, M;
	if (scanf("%d %d", &n, &M) != 2) return 0;
	std::vector<int> a(n + 1);
	for (int i = 1; i <= n; ++i) scanf("%d", &a[i]);

	long long ans = 0;
	for (int c = 2; c <= 2 * n; ++c) {
		int lo = c - n > 1 ? c - n : 1;
		int hi = c >> 1;
		for (int k = hi; k >= lo; --k) {
			if (k == c - k) continue;  // 单点区间不计入答案
			if (a[k] != a[c - k]) break;
			ans += M - 1;
		}
	}
	printf("%lld\n", ans);
	return 0;
}
