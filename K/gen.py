# 纸带染色 数据生成器
#
# 用法：在题目目录下运行 python -m tuack.dmk
# 参数由 conf.yaml 的 args 与每个数据点的 args 提供：
#   n, m, q  输入规模
#   mode     构造方式，见下面 _build_ops 的说明
#
# 不使用 init()：数据配方直接写在 conf.yaml 的 data 字段里。
# 随机数使用全局 random，dmk 会把首次运行的 random_state 存盘，之后可复现。

from random import randint, randrange, choice

# mode 取值：
#   mixed    所有 x 在 [1,n] 均匀随机
#   prefix   全部是前缀操作
#   suffix   全部是后缀操作
#   extreme  x 只取 1 或 n
#   equal    x 只在 3 个取值里挑，制造大量并列极值
#   no_full  前缀 x 不超过 mid、后缀 x 不小于 mid+2，保证任何区间都不会覆盖整条纸带
#   full     大前缀配小后缀，几乎每个 r 都存在覆盖整条纸带的截断点
def _build_ops(n, m, mode):
	ops = []
	if mode == 'prefix':
		for _ in range(m):
			ops.append((0, randint(1, n)))
	elif mode == 'suffix':
		for _ in range(m):
			ops.append((1, randint(1, n)))
	elif mode == 'extreme':
		for _ in range(m):
			ops.append((randrange(2), choice([1, n])))
	elif mode == 'equal':
		xs = [randint(1, n) for _ in range(3)]
		for _ in range(m):
			ops.append((randrange(2), choice(xs)))
	elif mode == 'no_full':
		mid = (n - 1) // 2
		for _ in range(m):
			if randrange(2) == 0:
				ops.append((0, randint(1, mid)))
			else:
				ops.append((1, randint(mid + 2, n)))
	elif mode == 'full':
		for _ in range(m):
			if randrange(2) == 0:
				ops.append((0, randint(max(1, n - n // 4), n)))
			else:
				ops.append((1, randint(1, max(1, n // 4 + 1))))
	else:
		for _ in range(m):
			ops.append((randrange(2), randint(1, n)))
	return ops

# 询问：混合整段、单点、前缀、后缀与一般区间。
# qmode 控制询问分布：
#   mixed   默认，整段 / 单点 / 前缀 / 后缀 / 一般区间轮换
#   all     全部询问都是整段 [1, m]（配 no_full 时可把「逐询问从 r 往左扫」的
#           暴力逼成全窗口扫描，O(qm) 必然超时）
#   single  全部询问都是单点 [l, l]
def _build_queries(m, q, qmode='mixed'):
	if qmode == 'all':
		return [(1, m)] * q
	if qmode == 'single':
		return [(l, l) for l in (randint(1, m) for _ in range(q))]
	qs = []
	for i in range(q):
		t = i & 7
		if t == 0:
			l, r = 1, m
		elif t == 1:
			l = randint(1, m)
			r = l
		elif t == 2:
			l, r = 1, randint(1, m)
		elif t == 3:
			l, r = randint(1, m), m
		else:
			l = randint(1, m)
			r = randint(l, m)
		qs.append((l, r))
	return qs

def gen(fin, args, cont):
	n = args['n']
	m = args['m']
	q = args['q']
	mode = args['mode']
	if n < 4 and mode == 'no_full':
		mode = 'mixed'
	try:
		qmode = args['qmode']          # 可选参数
	except (KeyError, TypeError):
		qmode = 'mixed'

	ops = _build_ops(n, m, mode)
	qs = _build_queries(m, q, qmode)

	out = ['%d %d %d\n' % (n, m, q)]
	out.extend('%d %d\n' % (o, x) for o, x in ops)
	out.extend('%d %d\n' % (l, r) for l, r in qs)
	data = ''.join(out)
	# dmk 用文本模式打开文件，Windows 下会把 \n 转成 \r\n；
	# 本数据包统一 LF 行尾，因此绕过文本层直接写二进制。
	if hasattr(fin, 'buffer'):
		fin.buffer.write(data.encode('ascii'))
	else:
		fin.write(data)