// 余镜 标准程序
//
// 只统计长度至少为 2 的区间（1 <= l < r <= n）。区间 [l,r] 在模 m 意义下回文
// <=> 对所有镜像位置 k（k + k' = l + r）都有 a_k ≡ a_k' (mod m)，
// 即 m 整除所有镜像差 |a_k - a_k'|。
// 记 c = l + r 为中心，D(l,r) 为这些镜像差的 gcd（所有镜像差均为 0 时 D = 0），则：
//   - D = 0：任意 m ∈ [2,M] 都可行，贡献 M - 1；
//   - D > 0：可行的 m 恰为 D 的不小于 2 的因子；又 D 整除某个 ≤ M 的非零差，
//     故 D ≤ M，贡献为 τ(D) - 1。
//
// 同一中心向外扩展时 D(l,r) = gcd(|a_l - a_r|, D(l+1,r-1))，可以 O(1) 递推；
// 所有中心共 O(n^2) 个区间。τ(·) 用筛法 O(M log M) 预处理。
// 总复杂度 O(M log M + n^2 + n log A)：running gcd 在每个中心只有 O(log A) 次
// 严格变小（每次至少减半，Euclid 迭代次数望远镜求和为 O(log A)），
// 结果不变的调用 g | d，一次取模即结束；故 gcd 总计 O(n^2 + n log A)。
// 答案不超过 n(n-1)/2 · (M-1) < 2^63。
//
// 注意 1：单点区间 [k,k] 不计入答案，奇数中心扫到 k = k' 时直接跳过。
// 注意 2：递推中一旦 g = 1，更外层区间的 D 恒为 1（贡献 0），可提前结束该中心。

#include <cstdio>

namespace io {
const int BUFSIZE = 1 << 22;
char buf[BUFSIZE];
int len = 0, pos = 0;
inline int gc() {
	if (pos == len) {
		len = (int)fread(buf, 1, BUFSIZE, stdin);
		pos = 0;
		if (len <= 0) return -1;
	}
	return buf[pos++];
}
inline int readInt() {
	int c = gc();
	while (c != -1 && (c < '0' || c > '9')) c = gc();
	int x = 0;
	while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
	return x;
}
}  // namespace io

static const int MAXN = 8005;
static const int MAXM = 1000005;

int n, M;
int a[MAXN];
int cnt[MAXM];  // cnt[d] = d 的不小于 2 的因子个数（d >= 1），cnt[0] 不用

inline int gcd(int x, int y) {
	while (y) { int t = x % y; x = y; y = t; }
	return x;
}

int main() {
	n = io::readInt();
	M = io::readInt();
	for (int i = 1; i <= n; ++i) a[i] = io::readInt();

	for (int i = 2; i <= M; ++i)
		for (int j = i; j <= M; j += i) ++cnt[j];

	long long ans = 0;
	// 枚举中心 c = l + r，从最内层向外扩展
	for (int c = 2; c <= 2 * n; ++c) {
		int lo = c - n > 1 ? c - n : 1;
		int hi = c >> 1;
		int g = 0;
		for (int k = hi; k >= lo; --k) {
			int j = c - k;
			if (k == j) continue;  // 单点区间不计入答案
			g = gcd(g, a[k] > a[j] ? a[k] - a[j] : a[j] - a[k]);
			ans += g == 0 ? (M - 1) : cnt[g];
			if (g == 1) break;  // 外层区间贡献均为 0
		}
	}

	printf("%lld\n", ans);
	return 0;
}
