// 纸带染色 错误程序 5：复杂度不达标但很可能混过去的做法。
//
// 思路本身完全正确：对每个询问 [l,r]，从 r 往左扫，
// 维护 P = 已扫过的前缀操作的最大 x（没有为 0）、S = 已扫过的后缀操作的最小 x
// （没有为 n+1）。操作 i 可见当且仅当 x_i > P（前缀）或 x_i < S（后缀）；
// 一旦 P >= S - 1，说明 i+1..r 已经覆盖整条纸带，更早的操作不可能可见，
// 可以提前终止扫描。
//
// 问题在于复杂度：最坏情况（永不覆盖整条纸带 + 大量整段询问）是 O(mq)。
// 但随机数据下覆盖通常几步之内就发生，扫描早早就断掉了，
// 因此它能通过小数据、中等数据、甚至 5*10^5 的随机大数据，
// 只有专门构造的「永不覆盖整条纸带 + 整段询问」的大规模数据才能卡住它。
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
int o[MAXM], x[MAXM];

int main() {
	n = io::readInt(); m = io::readInt(); q = io::readInt();
	for (int i = 1; i <= m; ++i) { o[i] = io::readInt(); x[i] = io::readInt(); }

	static char obuf[1 << 22];
	int op = 0;
	for (int t = 0; t < q; ++t) {
		int l = io::readInt(), r = io::readInt();
		int P = 0, S = n + 1, ans = 0;
		for (int i = r; i >= l; --i) {
			if (o[i] == 0) {
				if (x[i] > P) { ++ans; P = x[i]; }
			} else {
				if (x[i] < S) { ++ans; S = x[i]; }
			}
			if (P >= S - 1) break;
		}
		char tmp[12];
		int tl = 0, v = ans;
		if (v == 0) tmp[tl++] = '0';
		while (v > 0) { tmp[tl++] = char('0' + v % 10); v /= 10; }
		while (tl > 0) obuf[op++] = tmp[--tl];
		obuf[op++] = '\n';
		if (op > (1 << 22) - 32) { fwrite(obuf, 1, op, stdout); op = 0; }
	}
	fwrite(obuf, 1, op, stdout);
	return 0;
}