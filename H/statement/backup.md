{{ self.title() }}

{{ s('background') }}

怎么又是数学题，贵校是数学王国吗？

{{ s('description') }}

$n$ 个人，分为 $k$ 个类别，一开始第 $i$ 类有 $s_i$ 个人。每一轮从所有类别不同的有序个人对 \((u,v)\) 中等概率随机选择一对，并把 \(u\) 的类别改为 \(v\) 的类别。

当只有唯一一种类别时过程结束，记 $\tau$ 为操作次数，求 $\operatorname{Var}(\tau)$ ，对 $998244353$ 取模。可以证明，答案写成最简分数形式后，分母不会是 $998244353$ 的倍数。

数据范围：$n\leqslant 10^9,k\leqslant \min(n,3\times 10^5),s_i\geqslant 1$。

{{ s('input format') }}

{{ self.input_file() }}

第一行两个正整数 $n,k$ 分别表示人数，以及类别数。

第二行 $k$ 个正整数，表示 $s_1,s_2,\cdots,s_k$。保证 $\sum_{i=1}^ks_i=n$。

{{ s('output format') }}

{{ self.output_file() }}

一行一个非负整数表示方差取模后的结果。

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ s('sample', 2) }}

{{ self.sample_text() }}