{{ self.title() }}

{{ s('description') }}

小 $\varepsilon$ 和小 $\omega$ 是两个珍惜彼此相伴时光的女孩子。小 $\omega$ 正在为小 $\varepsilon$ 准备一份礼物，并将它们记录为一个秘密数列 $a$，其中元素均为不超过 $2^k-1$ 的非负整数。

好奇的小 $\varepsilon$ 想提前了解这份惊喜，于是她询问了小 $\omega$ 一共 $m$ 个问题，其中第 $i$ 个问题为询问 $a_{x_i}$ 和 $a_{y_i}$ 的按位与的值。

小 $\omega$ 告诉了小 $\varepsilon$ 每个问题的答案，其中第 $i$ 个问题的答案为 $z_i$，即小 $\omega$ 告诉小 $\varepsilon$ 数列 $a$ 满足 $a_{x_i}\operatorname*{AND}a_{y_i}=z_i$，其中 $x\operatorname*{AND}y$ 表示 $x$ 和 $y$ 的按位与的值。

小 $\varepsilon$ 感觉自己被小 $\omega$ 调戏了，怀疑小 $\omega$ 只是在胡乱回答她，可能满足以上条件的数列 $a$ 并不存在！

因此她找到了你，你需要告诉小 $\varepsilon$ 满足上述条件的数列 $a$ 是否存在。进一步地，小 $\varepsilon$ 还想知道，如果这样的数列 $a$ 存在，它的所有元素之和的最小可能值是多少。

{{ s('input format') }}

第一行包含一个整数 $T$ $(1\le T\le 5\times 10^5)$，表示测试数据组数。

对于每组测试数据：

- 第一行包含三个整数 $n,m,k$（$1\le n\le 200000$，$0\le m\le 200000$，$1\le k\le 30$），表示数列 $a$ 的长度、问题的数量以及 $a$ 中元素的二进制长度上限。
- 接下来 $m$ 行，每行包含三个整数 $x_i,y_i,z_i$ $(1\le x_i,y_i\le n,0\le z_i<2^k)$，表示第 $i$ 个问题及其答案，注意 $x_i,y_i$ 可能相等。

保证单个测试点所有测试数据的 $n$ 的和与 $m$ 的和分别不超过 $5\times 10^5$。

{{ s('output format') }}

对于每组测试数据，若合法的 $a$ 不存在则输出 `-1`，否则输出一行一个非负整数，表示数列 $a$ 的所有元素之和的最小可能值。

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ self.title_sample_description() }}

对于第一组测试数据，$a$ 长度为 $3$ 且其中的每个元素均为 $0$ 或 $1$，并且有 $a_1\operatorname*{AND}a_2=0$，$a_1\operatorname*{AND}a_3=0$，$a_2\operatorname*{AND}a_3=1$，由于 $a_2\operatorname*{AND}a_3=1$，故 $a_2=1,a_3=1$，又由 $a_1\operatorname*{AND}a_2=0$ 知道 $a_1=0$，故 $a_1=0,a_2=1,a_3=1$，可以验证该数列满足全部条件，此时 $a$ 中所有元素的和为 $2$；

对于第二组测试数据，$z_1=z_2=2^{30}-1$，故可以唯一确定 $a_1=a_2=a_3=2^{30}-1$，此时 $a$ 中元素之和为 $3\times(2^{30}-1)$；

对于第三组测试数据，有 $a_1\operatorname*{AND}a_2=1$，$a_1\operatorname*{AND}a_3=1$，$a_2\operatorname*{AND}a_3=0$，由于 $a_1\operatorname*{AND}a_2=1$，故 $a_1=1,a_2=1$，又由 $a_1\operatorname*{AND}a_3=1$ 知道 $a_3=1$，与条件不符，故不存在这样的 $a$；

对于第四组测试数据，有 $a_1\operatorname*{AND}a_1=4514$，故 $a_1=4514$，在其余 $a_i(2\le i\le n)$ 都为 $0$ 时 $a$ 中元素总和最小，为 $4514$；

对于第五组测试数据，由于 $a_1\operatorname*{AND}a_1=5$，故 $a_1=5$，同理可得 $a_2=6$，可以验证此时 $a_3$ 为 $5$ 或 $7$，当 $a_3=5$ 时 $a$ 中所有元素的和为 $16$，可以证明这是最小的可能值。
