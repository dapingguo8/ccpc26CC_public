// 纸带染色 错误程序 4：思路正确但复杂度过高（complexity 层）。
//
// 除 full(r) 的求法外与标准解完全相同：这里对每个 r 从 r 往左暴力扫描，
// 直到窗口 [i,r] 恰好覆盖整条纸带为止，最坏 O(m^2)。
// 小数据（m <= 数万）上结果与标准解一致，但在 m = 5*10^5 的最大数据上
// 必然超时，因此只有在放大规模时才会被杀（scale_escalation）。
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

static const int MAXM = 500005;
int n, m, q;
int o[MAXM], x[MAXM], nxt[MAXM], full[MAXM];
int stk[MAXM], bit[MAXM];

inline void bitAdd(int i, int v) { for (; i <= m; i += i & (-i)) bit[i] += v; }
inline int bitSum(int i) { int s = 0; for (; i > 0; i -= i & (-i)) s += bit[i]; return s; }

int main() {
	n = io::readInt(); m = io::readInt(); q = io::readInt();
	for (int i = 1; i <= m; ++i) { o[i] = io::readInt(); x[i] = io::readInt(); }
	const int INF = m + 1;
	for (int i = 1; i <= m; ++i) nxt[i] = INF;
	int top = 0;
	for (int i = 1; i <= m; ++i)
		if (o[i] == 0) {
			while (top > 0 && x[stk[top - 1]] <= x[i]) nxt[stk[--top]] = i;
			stk[top++] = i;
		}
	top = 0;
	for (int i = 1; i <= m; ++i)
		if (o[i] == 1) {
			while (top > 0 && x[stk[top - 1]] >= x[i]) nxt[stk[--top]] = i;
			stk[top++] = i;
		}

	// full[r]：从 r 往左暴力扩展窗口 [i,r]，找到最大的、恰好覆盖整条纸带的 i。
	// 覆盖性关于左端点 i 单调（i 越小窗口越大），因此从 r 递减扫到第一个成立处即可。
	// 单次 r 最坏 O(r)，总计 O(m^2)。
	for (int r = 1; r <= m; ++r) {
		int P = 0, S = n + 1;
		full[r] = 0;
		for (int i = r; i >= 1; --i) {
			if (o[i] == 0) { if (x[i] > P) P = x[i]; }
			else { if (x[i] < S) S = x[i]; }
			if (P >= S - 1) { full[r] = i; break; }
		}
	}

	static int head[MAXM + 2], ql[MAXM], qnxt[MAXM];
	for (int r = 0; r <= m + 1; ++r) head[r] = -1;
	for (int i = 0; i < q; ++i) {
		int l = io::readInt(), r = io::readInt();
		ql[i] = l; qnxt[i] = head[r]; head[r] = i;
	}
	static int bhead[MAXM + 2], bnxt[MAXM];
	for (int t = 0; t <= m + 1; ++t) bhead[t] = -1;
	for (int i = 1; i <= m; ++i) {
		int t = (nxt[i] <= m) ? nxt[i] : (m + 1);
		bnxt[i] = bhead[t]; bhead[t] = i;
	}
	static int ans[MAXM];
	for (int R = m; R >= 1; --R) {
		int t = (R == m) ? (m + 1) : (R + 1);
		for (int i = bhead[t]; i != -1; i = bnxt[i]) bitAdd(i, 1);
		for (int i = head[R]; i != -1; i = qnxt[i]) {
			int A = ql[i] > full[R] ? ql[i] : full[R];
			ans[i] = bitSum(R) - bitSum(A - 1);
		}
	}
	static char obuf[1 << 22];
	int op = 0;
	for (int i = 0; i < q; ++i) {
		int v = ans[i], tl = 0;
		char tmp[12];
		if (v == 0) tmp[tl++] = '0';
		while (v > 0) { tmp[tl++] = char('0' + v % 10); v /= 10; }
		while (tl > 0) obuf[op++] = tmp[--tl];
		obuf[op++] = '\n';
		if (op > (1 << 22) - 32) { fwrite(obuf, 1, op, stdout); op = 0; }
	}
	fwrite(obuf, 1, op, stdout);
	return 0;
}