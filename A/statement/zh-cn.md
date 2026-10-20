{{ self.title() }}

{{ s('background') }}

Yana、Mino、White、Huzz 从上海来到了长春，这次在他们面前的是一道纸笔问题。

{{ s('description') }}

给定一个 $n$ 行 $m$ 列的非负整数矩阵 $a_{i,j}$，你可以进行以下操作若干次：

- 选择一个列区间 $[l,r]$ 满足 $1\le l\le r\le m$，然后选定 $r-l+1$ 个行坐标 $p_l,p_{l+1},\dots,p_r$ 满足 $1\le p_l\le p_{l+1}\le \dots\le p_r\le n$，将 $a$ 中坐标为 $(p_l,l),(p_{l+1},l+1),\dots,(p_r,r)$ 的元素减去 $1$。

求将 $a$ 变为零矩阵所需的最少操作次数。

{{ s('input format') }}

输入的第一行包含两个正整数 $n,m$ $(1\le n,m\le 10^6,nm\le 10^6)$，代表矩阵 $a$ 的行数与列数。

接下来 $n$ 行，第 $i$ 行包含 $m$ 个非负整数 $a_{i,1},a_{i,2},\dots,a_{i,m}$ $(0\le a_{i,j}\le 10^9)$，表示矩阵 $a$ 的元素。

{{ s('output format') }}

输出一个整数，表示把矩阵 $a$ 变为零矩阵所需的最少操作次数。

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ s('sample', 2) }}

{{ self.sample_text() }}

{{ s('样例解释') }}

对于样例 1，可以证明将 $a$ 变为零矩阵至少需要 $7$ 次操作，以下是一种可行的最优方案：（图中同色圆点表示同一次操作选中的位置，对应颜色的数字表示操作的序号）

{{ img('sample.png', size = 1, align = 'middle', inline = False, label='fig:sample') }}