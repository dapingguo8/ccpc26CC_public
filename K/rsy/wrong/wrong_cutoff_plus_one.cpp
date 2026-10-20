// 纸带染色 错误程序 2：截断位置差一。
//
// 下标 full(r) 对应的那次操作恰好把纸带补全，它本身一定是可见的；
// 但本程序从 full(r)+1 开始统计，于是在 [l,r] 覆盖整条纸带时会少算一个颜色。
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
int stk[MAXM], dqMax[MAXM], dqMin[MAXM], bit[MAXM];

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
	int lo = 1, hMax = 0, tMax = 0, hMin = 0, tMin = 0;
	for (int r = 1; r <= m; ++r) {
		if (o[r] == 0) {
			while (tMax > hMax && x[dqMax[tMax - 1]] <= x[r]) --tMax;
			dqMax[tMax++] = r;
		} else {
			while (tMin > hMin && x[dqMin[tMin - 1]] >= x[r]) --tMin;
			dqMin[tMin++] = r;
		}
		while (lo < r) {
			int P = 0, S = n + 1;
			if (tMax > hMax) {
				P = x[dqMax[hMax]];
				if (dqMax[hMax] == lo) P = (tMax - hMax >= 2) ? x[dqMax[hMax + 1]] : 0;
			}
			if (tMin > hMin) {
				S = x[dqMin[hMin]];
				if (dqMin[hMin] == lo) S = (tMin - hMin >= 2) ? x[dqMin[hMin + 1]] : n + 1;
			}
			if (P >= S - 1) {
				if (tMax > hMax && dqMax[hMax] == lo) ++hMax;
				if (tMin > hMin && dqMin[hMin] == lo) ++hMin;
				++lo;
			} else break;
		}
		int P = (tMax > hMax) ? x[dqMax[hMax]] : 0;
		int S = (tMin > hMin) ? x[dqMin[hMin]] : n + 1;
		full[r] = (P >= S - 1) ? lo : 0;
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
			int A = ql[i], b = full[R] + 1;  // BUG: 应为 full[R]
			if (b > A) A = b;
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