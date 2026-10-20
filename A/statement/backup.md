{{ self.title() }}

{{ s('background') }}

怎么又是【占位】题，贵校是【占位】王国吗？

{{ s('description') }}

给定一个 \(n\) 行 \(m\) 列的非负整数矩阵 $a_{i,j}$

一次操作选择一个连续的列区间 \([l,r]\)，并在每一列中选择一个格子。若第 \(j\) 列选择的是第 \(p_j\) 行，则必须满足

$$
1\le l\le r\le m,\qquad
1\le p_l\le p_{l+1}\le\cdots\le p_r\le n.1\le l\le r\le m,\qquad
1\le p_l\le p_{l+1}\le\cdots\le p_r\le n.
$$

随后把选中的所有格子都减去 \(1\)。操作开始前，所有选中的格子都必须为正。

换句话说，一次操作从左向右经过一段连续的列，所在行可以保持不变，也可以向下跳过若干行，但不能向上移动。

求把整个矩阵变为零矩阵所需的最少操作次数。

数据范围：\(1\le n,m\)，\(nm\le10^6\)，且 \(0\le a_{i,j}\le10^9\)。

{{ s('input format') }}

{{ self.input_file() }}

第一行包含两个整数 $n,m$ $(1\le n,m\le 10^6,nm\le 10^6)$，代表矩阵 $a$ 的行数与列数。

接下来 \(n\) 行，第 $i$ 行包含 \(m\) 个整数 $a_{i,1},a_{i,2},\dots,a_{i,m}$，表示矩阵 $a$ 的元素。

{{ s('output format') }}

{{ self.output_file() }}

输出一个整数，表示把矩阵 $a$ 变为零矩阵所需的最少操作次数。

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ s('sample', 2) }}

{{ self.sample_text() }}