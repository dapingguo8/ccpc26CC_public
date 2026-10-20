{{ self.title() }}

## 题目简述

给定序列 $a_1,\dots,a_n$ 与上界 $M$。称区间 $[l,r]$（$l<r$）在模 $m$ 意义下回文，
当且仅当 $[a_l\bmod m,\dots,a_r\bmod m]$ 是回文序列。求所有 $1\le l<r\le n$ 与
$2\le m\le M$ 中，「$[l,r]$ 在模 $m$ 意义下回文」的对数，即

$$
\sum_{1\le l<r\le n}\ \sum_{2\le m\le M} f(l,r,m).
$$

单点区间 $l=r$ 不计入答案。

## 关键观察：模 $m$ 回文 $\iff m$ 整除所有镜像差

设 $c=l+r$ 为区间中心。$[l,r]$ 在模 $m$ 下回文，当且仅当对每对镜像位置
$k<k'$（$k+k'=c$）都有 $a_k\equiv a_{k'}\pmod m$，即

$$
m\ \Big|\ \gcd_{k+k'=c,\ k<k'}|a_k-a_{k'}|.
$$

记这个最大公约数为 $D(l,r)$（长度 $\ge 2$ 的区间至少有一对镜像位置；
所有镜像差都为 $0$ 时 $D=0$），则：

- $D=0$：所有镜像差全为 $0$，任意 $m\in[2,M]$ 都可行，贡献 $M-1$；
- $D>0$：可行的 $m$ 恰为 $D$ 的不小于 $2$ 的因子。注意 $D$ 整除某个非零差
  $|a_k-a_{k'}|\le M$，故 $D\le M$，因子不会超出上界，贡献为 $\tau(D)-1$。

## 递推：同一中心向外扩展

固定中心 $c$，区间每向外扩一层，只是多取一个差的 gcd：

$$
D(l,r)=\gcd\bigl(|a_l-a_r|,\ D(l+1,r-1)\bigr).
$$

因此对每个中心 $c=2,\dots,2n$，从最内层开始维护 running gcd 向外扫即可。
$\tau(\cdot)$ 用 $O(M\log M)$ 的筛法预处理。

**复杂度分析**：表面上每个区间做一次 gcd、共 $O(n^2)$ 次，而单次 gcd 最坏
$O(\log A)$，但按中心摊销后更优：

- running gcd 每次**严格变小**都至少减半（新值是旧值的真因子），故一个中心至多
  $O(\log A)$ 次严格变小；一次使 gcd 从 $g$ 变为 $g'<g$ 的 Euclid 算法，
  其迭代次数为 $O(1+\log(g/g'))$，对一条链望远镜求和为 $O(\log A)$；
- 结果**不变**的调用满足 $g\mid d$，第一次取模 $d\bmod g=0$ 即结束，$O(1)$。

所以每个中心 $O(\text{区间数}+\log A)$，gcd 总计 $O(n^2+n\log A)$，
总复杂度 $O\bigl(M\log M+n^2+n\log A\bigr)$，$n=8000$、$M=10^6$ 时约 $0.3$ 秒。
答案最大为 $\frac{n(n-1)}2(M-1)\approx 3.2\times 10^{13}$，需要 64 位整数。

**实现要点**：

1. 奇数中心最内层 $k=k'$ 是单点区间，不计入答案，直接跳过（跳过不影响
   running gcd，下一层 $g=\gcd(0,d)=d$ 仍正确）；
2. 递推中一旦 running gcd 变为 $1$，更外层区间的 $D$ 恒为 $1$
   （$\tau(1)-1=0$），可以直接结束当前中心。

## 验题

- `bf/bf.cpp`：完全按定义模拟——枚举每个 $m$，把序列取模后统计长度 $\ge 2$ 的
  回文子区间数，$O(M\cdot n^2)$，仅在小数据上运行，用于随机对拍，大数据必然
  超时，期望分 $<100$。
- `wrong/wrong_pal_only.cpp`（idea）：只统计「原数组本身就回文」的区间，
  没意识到取模可以制造回文。
- `wrong/wrong_cubic.cpp`（complexity）：推导正确但对每个区间重新 $O(r-l+1)$
  求 gcd，$O(n^3)$，最大数据超时。
- `wrong/wrong_early_break.cpp`（complexity，易混过）：同上但 gcd 变 $1$ 就提前终止，
  小中规模与 $M=2$ 大数据上能混过；`few`/`equal`/`extreme`/`square` 数据让镜像差
  长期不互质，提前终止永不触发，退化为完整 $O(n^3)$。
- `wrong/wrong_zero.cpp`（implementation）：漏掉长度 $\ge 2$ 且 $D=0$ 时应贡献
  $M-1$，算成 $0$。
- `wrong/wrong_divisor.cpp`（implementation）：试除统计因子时漏掉 $D$ 本身
  （$m=D$ 恒可行），每个 $D\ge 2$ 的区间少算 $1$。
- `wrong/wrong_int.cpp`（implementation）：累加器用 32 位无符号整数，
  最大答案约 $3.2\times 10^{13}$，溢出后按 $2^{32}$ 回绕。
- `wrong/wrong_manacher_m.cpp`（complexity）：思路正确，但对每个 $m\in[2,M]$
  各跑一次 Manacher 式的回文统计，$O(M\cdot n)$，大数据超时。
- `wrong/wrong_trial_div.cpp`（complexity，易混过）：中心扩展与 gcd 递推都正确，
  只是因子数用试除 $O(\sqrt D)$ 现算。随机大数据下 $D$ 很快塌成 $1$、
  提前终止生效，它甚至能混过 $n=8000$ 的随机/平方数点；只有 $D$ 长期取大值的
  `mode: levels` 才把它逼超时。
- `wrong/wrong_square_div.cpp`（implementation）：因子计数写成
  `for (d = 2; d * d < g; ++d)`，$g$ 为完全平方数时漏掉 $\sqrt g$ 这个因子。
- `wrong/wrong_zero_break.cpp`（implementation）：提前终止条件写成 $g<2$
  而非 $g=1$，当 $g=0$（所有镜像差均为 $0$、应贡献 $M-1$）时也提前结束，
  丢掉整段 $D=0$ 的区间。

数据中 `mode: equal`（全相等，$D\equiv 0$，答案达到理论上界）、`mode: few`
（只取两个值且差 $\ge2$，gcd 永不为 $1$）、`mode: extreme`（只取 $0$ 或 $M$，
$D\in\{0,M\}$）即为针对上述错解构造的反例族；`mode: square`（周期性完全平方数
$a_i=(i\bmod L)^2$，镜像差 $(k-j)(k+j)$ 恒含因子 $k+j$）在短固定周期 $L=40$
时让约 $63\%$ 的区间 $D>1$，gcd 剪枝失效，长段 $L=1001$ 则取到 $a_i=M$
并产生大 $D$ 多因子区间；`mode: levels`（$a_i$ 只取 $B$ 的倍数，$B=M/k$ 或
`base` 指定的高合成数）让 $D$ 长期停在大值上，是卡 `wrong_trial_div`
与 `wrong_early_break` 的关键反例族（47-51 号）。
