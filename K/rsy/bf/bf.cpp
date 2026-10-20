// 纸带染色 暴力程序：对每个询问直接模拟纸带，统计可见颜色数。
// 复杂度 O(q * (n + m))，只能在 n, m, q 很小的数据上运行，用于对拍验证。
#include <cstdio>
#include <vector>
#include <set>

int main() {
	int n, m, q;
	if (scanf("%d %d %d", &n, &m, &q) != 3) return 0;
	std::vector<int> o(m + 1), x(m + 1);
	for (int i = 1; i <= m; ++i) scanf("%d %d", &o[i], &x[i]);

	// 内存安全阀：纸带要开 n+1 个 int，n=1e9 时会申请 4 GiB，直接放弃。
	// 暴力解本就只能在很小的数据上运行，大数据上判为错误答案即可。
	if (n > 2000000) {
		fprintf(stderr, "n too large for the brute force\n");
		return 0;
	}

	std::vector<int> tape(n + 1, 0);
	for (int t = 0; t < q; ++t) {
		int l, r;
		scanf("%d %d", &l, &r);
		for (int c = 0; c <= n; ++c) tape[c] = 0;
		for (int i = l; i <= r; ++i) {
			if (o[i] == 0) {
				for (int c = 1; c <= x[i]; ++c) tape[c] = i;
			} else {
				for (int c = x[i]; c <= n; ++c) tape[c] = i;
			}
		}
		std::set<int> seen;
		for (int c = 1; c <= n; ++c)
			if (tape[c] != 0) seen.insert(tape[c]);
		printf("%d\n", (int)seen.size());
	}
	return 0;
}