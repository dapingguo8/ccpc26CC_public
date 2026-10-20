// 余镜 错误程序 4：实现错误（implementation 层）——漏掉 D = 0 的情况。
//
// 中心扩展的框架与标准解相同（单点区间同样跳过、不计入答案），但直接用
// cnt[g] 计入答案，忘记「长度 >= 2 的区间所有镜像差全为 0 时任意
// m ∈ [2,M] 都可行」，此时 g = 0 而 cnt[0] = 0，这些区间的贡献被算成 0
// 而非 M-1。在所有值相等（或整个区间关于每个中心都镜像相等）的数据上
// 答案直接为 0，错误必然暴露。
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
int a[MAXN], cnt[MAXM];

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
	for (int c = 2; c <= 2 * n; ++c) {
		int lo = c - n > 1 ? c - n : 1;
		int hi = c >> 1;
		int g = 0;
		for (int k = hi; k >= lo; --k) {
			int j = c - k;
			if (k == j) continue;  // 单点区间不计入答案（此处与 std 一致）
			g = gcd(g, a[k] > a[j] ? a[k] - a[j] : a[j] - a[k]);
			ans += cnt[g];  // 错误：长度 >= 2 且 g = 0 时贡献应为 M-1，这里算成 cnt[0] = 0
			if (g == 1) break;
		}
	}
	printf("%lld\n", ans);
	return 0;
}
