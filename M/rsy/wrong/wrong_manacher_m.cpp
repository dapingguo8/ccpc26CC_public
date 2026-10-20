// 余镜 错误程序 7：复杂度过高（complexity 层）——对每个 m 单独统计回文子区间。
//
// 思路正确：对每个 m，把 b_i = a_i mod m 取出来后，用 Manacher 统计长度 >= 2 的
// 回文子串个数，累加即答案。但复杂度 O(M·n)：M = 10^6、n = 8000 时约 8*10^9，
// 在 n >= 2000、M = 10^6 的数据点上必然超时。
// 用于封堵「枚举所有 m 单独处理」这类思路——它要求做到优于 O(M·n)。
#include <cstdio>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
	int n, M;
	if (scanf("%d %d", &n, &M) != 2) return 0;
	vector<int> a(n);
	for (int i = 0; i < n; ++i) scanf("%d", &a[i]);
	vector<int> b(n), d1(n), d2(n);
	long long ans = 0;
	for (int m = 2; m <= M; ++m) {
		for (int i = 0; i < n; ++i) b[i] = a[i] % m;
		long long cnt = 0;
		int l = 0, r = -1;
		for (int i = 0; i < n; ++i) {         // 奇数长度
			int k = (i > r) ? 1 : min(d1[l + r - i], r - i + 1);
			while (i - k >= 0 && i + k < n && b[i - k] == b[i + k]) ++k;
			d1[i] = k;
			if (i + k - 1 > r) { l = i - k + 1; r = i + k - 1; }
			cnt += k;
		}
		l = 0; r = -1;
		for (int i = 0; i < n; ++i) {         // 偶数长度
			int k = (i > r) ? 0 : min(d2[l + r - i + 1], r - i + 1);
			while (i - k - 1 >= 0 && i + k < n && b[i - k - 1] == b[i + k]) ++k;
			d2[i] = k;
			if (i + k - 1 > r) { l = i - k; r = i + k - 1; }
			cnt += k;
		}
		ans += cnt - n;                        // 去掉长度 1 的子区间
	}
	printf("%lld\n", ans);
	return 0;
}