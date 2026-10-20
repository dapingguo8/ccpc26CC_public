// 纸带染色 标准程序
//
// 记第 i 次操作的区域为 A_i：o_i=0 时 A_i=[1,x_i]，o_i=1 时 A_i=[x_i,n]。
// 对询问 [l,r]，从后往前扫 i=r..l，令 U_i 为操作 i+1..r 覆盖区域的并，
// 则颜色 i 可见 <=> A_i 中存在不属于 U_i 的格子。
//
// 由于所有区域都是前缀或后缀，U_i=[1,P_i]∪[S_i,n]，
// 其中 P_i 是 i 之后前缀操作的最大 x（没有则为 0，此时 [1,0] 为空），
// S_i 是 i 之后后缀操作的最小 x（没有则为 n+1，此时 [n+1,n] 为空）。
//
// 于是 A_i⊆U_i <=> P_i>=S_i-1（此时 U_i 覆盖整条纸带），否则：
//   前缀操作 i 可见 <=> x_i > P_i
//   后缀操作 i 可见 <=> x_i < S_i
//
// 记 full(r) 为满足操作 full(r)..r 恰好覆盖整条纸带的最大下标（不存在为 0）。
// 因为 P_i>=S_i-1 关于 i 单调（i 越小 U_i 越大），所以对 i<full(r) 必有
// P_i>=S_i-1，颜色 i 不可见；而 i>=full(r) 时必有 P_i<S_i-1（否则
// ops[i+1..r] 也覆盖整条纸带，与 full(r) 最大矛盾）。
// 故对询问 [l,r] 只有 i∈[max(l,full(r)), r] 可能可见。
//
// 在该区间内，前缀颜色 i 可见 <=> x_i 严格大于 i 之后所有前缀操作的 x，
// 后缀颜色 i 可见 <=> x_i 严格小于 i 之后所有后缀操作的 x。
// 即：颜色 i 可见 <=> nxt[i] > r，其中
//   o_i=0 时 nxt[i] 是 i 之后第一个 x>=x_i 的前缀操作下标；
//   o_i=1 时 nxt[i] 是 i 之后第一个 x<=x_i 的后缀操作下标；
//   不存在则 nxt[i]=m+1（视为 +inf）。
//
// 于是答案 = #{ i : max(l,full(r)) <= i <= r 且 nxt[i] > r }。
// full(r) 用双指针 + 单调队列 O(m) 求出；询问按 r 从大到小离线，
// 用树状数组维护 { i : nxt[i] > r }，即可 O((m+q) log m) 回答全部询问。

#include <cstdio>
#include <cstring>
#include <algorithm>

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
	while (c >= '0' && c <= '9') {
		x = x * 10 + (c - '0');
		c = gc();
	}
	return x;
}
}  // namespace io

static const int MAXM = 500005;

int n, m, q;
int o[MAXM], x[MAXM], nxt[MAXM], full[MAXM];
int stk[MAXM];
int dqMax[MAXM], dqMin[MAXM];
int bit[MAXM];

inline void bitAdd(int i, int v) {
	for (; i <= m; i += i & (-i)) bit[i] += v;
}
inline int bitSum(int i) {
	int s = 0;
	for (; i > 0; i -= i & (-i)) s += bit[i];
	return s;
}

int main() {
	n = io::readInt();
	m = io::readInt();
	q = io::readInt();
	for (int i = 1; i <= m; ++i) {
		o[i] = io::readInt();
		x[i] = io::readInt();
	}

	const int INF = m + 1;
	for (int i = 1; i <= m; ++i) nxt[i] = INF;

	// 前缀操作：i 之后第一个 x>=x_i 的操作
	int top = 0;
	for (int i = 1; i <= m; ++i)
		if (o[i] == 0) {
			while (top > 0 && x[stk[top - 1]] <= x[i]) nxt[stk[--top]] = i;
			stk[top++] = i;
		}
	// 后缀操作：i 之后第一个 x<=x_i 的操作
	top = 0;
	for (int i = 1; i <= m; ++i)
		if (o[i] == 1) {
			while (top > 0 && x[stk[top - 1]] >= x[i]) nxt[stk[--top]] = i;
			stk[top++] = i;
		}

	// 双指针 + 单调队列求 full(r)
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
			// 试探窗口 [lo+1, r] 是否仍覆盖整条纸带
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
			} else {
				break;
			}
		}
		int P = (tMax > hMax) ? x[dqMax[hMax]] : 0;
		int S = (tMin > hMin) ? x[dqMin[hMin]] : n + 1;
		full[r] = (P >= S - 1) ? lo : 0;
	}

	// 询问按 r 从大到小离线处理
	static int head[MAXM + 2], ql[MAXM], qnxt[MAXM];
	for (int r = 0; r <= m + 1; ++r) head[r] = -1;
	for (int i = 0; i < q; ++i) {
		int l = io::readInt(), r = io::readInt();
		ql[i] = l;
		qnxt[i] = head[r];
		head[r] = i;
	}

	static int bhead[MAXM + 2], bnxt[MAXM];
	for (int t = 0; t <= m + 1; ++t) bhead[t] = -1;
	for (int i = 1; i <= m; ++i) {
		int t = (nxt[i] <= m) ? nxt[i] : (m + 1);
		bnxt[i] = bhead[t];
		bhead[t] = i;
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

	{
		static char obuf[1 << 22];
		int op = 0;
		for (int i = 0; i < q; ++i) {
			int v = ans[i];
			char tmp[12];
			int tl = 0;
			if (v == 0) tmp[tl++] = '0';
			while (v > 0) {
				tmp[tl++] = char('0' + v % 10);
				v /= 10;
			}
			while (tl > 0) obuf[op++] = tmp[--tl];
			obuf[op++] = '\n';
			if (op > (1 << 22) - 32) {
				fwrite(obuf, 1, op, stdout);
				op = 0;
			}
		}
		fwrite(obuf, 1, op, stdout);
	}
	return 0;
}