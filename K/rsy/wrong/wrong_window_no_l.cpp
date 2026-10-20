// 纸带染色 错误程序 8：实现错误（implementation 层）——询问窗口左端忘记与 l 取 max。
//
// 思路与标准解一致（求 nxt[i] 与 full(r)），但回答询问 [l,r] 时直接在
// [full[r], r] 里数 nxt[i] > r 的个数，没有把左端与 l 取 max。
// 当 full[r] < l 时会把 i < l（不属于本次询问区间）的操作也算进去，答案偏大；
// 单点询问、短区间询问都会触发。本质是把「窗口下界」与「询问下界」混为一谈。
#include <cstdio>

static int o[500005], x[500005], nxt[500005], full[500005], stk[500005];
static int dqMax[500005], dqMin[500005];

int main() {
	int n, m, q;
	if (scanf("%d %d %d", &n, &m, &q) != 3) return 0;
	for (int i = 1; i <= m; ++i) scanf("%d %d", &o[i], &x[i]);
	const int INF = m + 1;
	for (int i = 1; i <= m; ++i) nxt[i] = INF;
	int top = 0;
	for (int i = 1; i <= m; ++i)
		if (o[i] == 0) { while (top > 0 && x[stk[top - 1]] <= x[i]) nxt[stk[--top]] = i; stk[top++] = i; }
	top = 0;
	for (int i = 1; i <= m; ++i)
		if (o[i] == 1) { while (top > 0 && x[stk[top - 1]] >= x[i]) nxt[stk[--top]] = i; stk[top++] = i; }

	int lo = 1, hMax = 0, tMax = 0, hMin = 0, tMin = 0;
	for (int r = 1; r <= m; ++r) {
		if (o[r] == 0) { while (tMax > hMax && x[dqMax[tMax - 1]] <= x[r]) --tMax; dqMax[tMax++] = r; }
		else { while (tMin > hMin && x[dqMin[tMin - 1]] >= x[r]) --tMin; dqMin[tMin++] = r; }
		while (lo < r) {
			int P = 0, S = n + 1;
			if (tMax > hMax) { P = x[dqMax[hMax]]; if (dqMax[hMax] == lo) P = (tMax - hMax >= 2) ? x[dqMax[hMax + 1]] : 0; }
			if (tMin > hMin) { S = x[dqMin[hMin]]; if (dqMin[hMin] == lo) S = (tMin - hMin >= 2) ? x[dqMin[hMin + 1]] : n + 1; }
			if (P >= S - 1) { if (tMax > hMax && dqMax[hMax] == lo) ++hMax; if (tMin > hMin && dqMin[hMin] == lo) ++hMin; ++lo; }
			else break;
		}
		int P = (tMax > hMax) ? x[dqMax[hMax]] : 0, S = (tMin > hMin) ? x[dqMin[hMin]] : n + 1;
		full[r] = (P >= S - 1) ? lo : 0;
	}

	for (int t = 0; t < q; ++t) {
		int l, r;
		scanf("%d %d", &l, &r);
		int A = full[r];                 // BUG: 未与 l 取 max
		if (A < 1) A = 1;
		int ans = 0;
		for (int i = A; i <= r; ++i) if (nxt[i] > r) ++ans;
		printf("%d\n", ans);
	}
	return 0;
}