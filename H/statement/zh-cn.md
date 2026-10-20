{{ self.title() }}

{{ s('background') }}

怎么又是数学题，贵校是数学王国吗？

{{ s('description') }}

给定正整数 $n,k$，现有 $n$ 个人，每个人手里分别拿着一个不大于 $k$ 的正整数。操作开始前，对正整数 $1\le j \le k$，有 $s_j$ 个人持有正整数 $j$。

接下来重复进行以下操作直至所有人手中的正整数均相等：

- 记第 $i$ 个人手里持有的正整数为 $w_i$，在所有满足 $1\le u,v\le n$ 且 $w_u\neq w_v$ 的正整数对 $(u,v)$ 中，等概率选择一对，记为 $(u_0,v_0)$。然后，将第 $u_0$ 个人手中的正整数 $w_{u_0}$ 改为 $w_{v_0}$。

记 $\tau$ 为操作轮数，求随机变量 $\tau$ 的方差 $\operatorname{Var}(\tau)$，对 $998244353$ 取模。

可以证明答案是有理数，且写成最简分数形式 $\frac{p}{q}$ 后，分母 $q$ 不会是 $998244353$ 的倍数。此时存在唯一的正整数 $1\le r <998244353$ 使得 $q\cdot r\equiv 1 \ (\bmod 998244353)$，那么你需要给出 $(p\cdot r) \bmod 998244353$ 的值。

对离散型随机变量 $\tau$ 以及其一系列取值 $x_1,x_2,\dots$，记 $\tau$ 取值为 $x_i$ 的概率 $P(\tau=x_i)=p_i$，并记 $\tau$ 的期望 $\sum\limits_{i\ge 1}x_ip_i=\mu$，则定义 $\tau$ 的方差 $\operatorname{Var}(\tau)=\sum\limits_{i\ge 1}(x_i-\mu)^2p_i$。

{{ s('input format') }}

输入的第一行包含两个正整数 $n,k$ $(1\le n \le 10^9,1\le k \le \min(n,3\times 10^5))$，分别表示人数，以及持有正整数的上界。

第二行包含 $k$ 个正整数 $s_1,s_2,\cdots,s_k$ $(1\le s_i\le n,\sum\limits_{i=1}^ks_i=n)$，代表持有每个正整数的人数。

{{ s('output format') }}

输出一行一个非负整数，表示 $\operatorname{Var}(\tau) \bmod 998244353$ 的结果。

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ s('sample', 2) }}

{{ self.sample_text() }}

{{ s('样例解释') }}

对于样例 1，第一次操作后必定有且仅有两人手中持有的正整数相同，不妨记他们手中的正整数为 $a$，并记另一人手中的正整数为 $b$。

接下来的操作必然为以下两种操作等概率选择其一：

- 选择一个手中持有正整数 $a$ 的人，将其手中的数改为 $b$；
- 选择一个手中持有正整数 $b$ 的人，将其手中的数改为 $a$；

如果选中后者，则操作结束；否则操作后的状态等价于操作前。

因此，可以得出 $\tau$ 的分布列为 $P(\tau=x)=\frac{1}{2^{x-1}},x=2,3,\dots$，据此求出 $\tau$ 的期望为 $\sum\limits_{x\ge 2}\frac{x}{2^{x-1}}=3$，代入计算方差可得 $\operatorname{Var}(\tau)=\sum\limits_{x\ge 2}\frac{(x-3)^2}{2^{x-1}}=2$。