# 余镜 数据生成器
#
# 用法：在题目目录下运行 python -m tuack.dmk
# 参数由 conf.yaml 的 args 与每个数据点的 args 提供：
#   n, M   输入规模
#   mode   构造方式，见下面 _build 的说明
#
# 不使用 init()：数据配方直接写在 conf.yaml 的 data 字段里。
# 随机数使用全局 random，dmk 会把首次运行的 random_state 存盘，之后可复现。

from math import isqrt
from random import randint, randrange

# mode 取值：
#   random   a_i 在 [0, M] 均匀随机
#   equal    所有 a_i 相等（任何长度 >= 2 的区间在任意 m 下都回文，
#            答案 = n(n-1)/2 * (M-1)，达到理论上界 ~ n^2 M / 2，专门卡 32 位累加）
#   pal      原序列本身回文（a_i = a_{n+1-i}），正中附近的区间 D = 0
#   few      a_i 只取两个值 {v, v+d} 且 d >= 2：镜像差恒为 0 或 d，
#            gcd 永远不是 1，专门卡「gcd 变 1 就提前终止」的暴力
#   extreme  a_i 只取 0 或 M：镜像差恒为 0 或 M，D ∈ {0, M}，
#            同时命中 a_i 的上下界
#   square   周期性连续完全平方数段：a_i = (i mod L)^2（下标从 0 起），
#            L 由 args['seg'] 指定，缺省 floor(sqrt M)+1（长段，值取到 M）。
#            镜像差 k^2 - j^2 = (k-j)(k+j) 对同一中心恒含因子 k+j；严格周期性
#            使跨整数个周期的差链在代数上保持公因子，gcd 很难塌成 1，
#            「gcd=1 提前终止」类剪枝在此基本失效。
#            实测 L 为偶数（或奇数且为 3 的倍数）时最强（差链保持因子 2/3）：
#            n=8000、L=40 时约 63% 的区间 D>1；长段 L~1001 则提供大 D、
#            多因子并取到 a_i=M。两种规模/段长都配数据点。
#   levels   取值只落在 B 的倍数上（B = args['base']，未给则 B = M // args['k']）。
#            镜像差恒为 B 的倍数，running gcd 频繁取到大值 D：既让 τ(D) 变大
#            （考因子计数），又让 sqrt(D) 变大（把「每区间试除 O(sqrt D)」逼超时）。
#            base 取高合成数（如 720720）可同时最大化 τ(D)。
def _build(n, M, mode, seg=None, k=None, base=None):
	if mode == 'equal':
		v = randint(0, M)
		return [v] * n
	if mode == 'pal':
		half = [(randint(0, M)) for _ in range((n + 1) // 2)]
		return [half[i] if i < (n + 1) // 2 else half[n - 1 - i] for i in range(n)]
	if mode == 'few':
		d = randint(2, min(M, 7))
		v = randint(0, M - d)
		return [v if randrange(2) == 0 else v + d for _ in range(n)]
	if mode == 'extreme':
		a = [0 if randrange(2) == 0 else M for _ in range(n)]
		if n >= 2:
			a[0], a[-1] = 0, M  # 保证 a_i 的两个界都出现
		return a
	if mode == 'square':
		L = seg if seg else isqrt(M) + 1  # 段长（周期）：短周期 L=40 或长段 ~sqrt M+1
		return [(i % L) ** 2 for i in range(n)]
	if mode == 'levels':
		B = base if base else (M // k if k else M // 2)
		if B < 1:
			B = 1
		top = (M // B) * B
		lv = list(range(0, top + 1, B)) or [0]
		a = [lv[randrange(len(lv))] for _ in range(n)]
		if n >= 1:
			a[0] = 0
		if n >= 2:
			a[-1] = top
		return a
	return [randint(0, M) for _ in range(n)]

def gen(fin, args, cont):
	n = args['n']
	M = args['M']
	mode = args['mode']
	if M < 2:
		mode = 'random'
		M = 2
	if mode == 'few' and M < 2:
		mode = 'random'

	try:
		seg = args['seg']  # 可选参数，Getter 无 .get
	except (KeyError, TypeError):
		seg = None
	try:
		k = args['k']
	except (KeyError, TypeError):
		k = None
	try:
		base = args['base']
	except (KeyError, TypeError):
		base = None
	a = _build(n, M, mode, seg, k, base)

	data = '%d %d\n%s\n' % (n, M, ' '.join(map(str, a)))
	# dmk 用文本模式打开文件，Windows 下会把 \n 转成 \r\n；
	# 本数据包统一 LF 行尾，因此绕过文本层直接写二进制。
	if hasattr(fin, 'buffer'):
		fin.buffer.write(data.encode('ascii'))
	else:
		fin.write(data)
