{{ self.title() }}

{{ s('description') }}

小 R 在整理一面由 $n$ 块镜片组成的折镜时发现：对序列 $a_1,\dots,a_n$ 和整数 $m\ge 2$ 取模后，有些区间会变成回文。

对正整数 $l,r,m$ $(1\le l\le r\le n)$，如果 $[a_l\bmod m,\ a_{l+1}\bmod m,\ \dots,\ a_r\bmod m]$ 是回文序列（即 $(a_i \bmod m)=(a_{r+l-i}\bmod m)$ 对 $l\le i \le r$ 均成立），则定义 $f(l,r,m)=1$，否则定义 $f(l,r,m)=0$。

给定上界 $M$，请你求出：
$$
\sum_{1\le l<r\le n}\ \sum_{2\le m\le M} f(l,r,m)
$$

{{ s('input format') }}

第一行包含两个整数 $n,M$ $(1\le n \le 8000, 2\le M \le 10^6)$，分别代表序列长度与模数上界。

第二行包含 $n$ 个整数 $a_1,a_2,\dots,a_n$ $(0\le a_i \le M)$，代表序列 $a$。

{{ s('output format') }}

输出一行一个整数，即所求的答案 $\sum\limits_{1\le l<r\le n}\ \sum\limits_{2\le m\le M} f(l,r,m)$。

答案可能很大，请注意使用 64 位整数。

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ self.title_sample_description() }}

共有以下 $3$ 组 $(l,r,m)$ 使得 $f(l,r,m)=1$：

- $(l,r,m)=(1,2,2)$：此时 $[a_1\bmod 2,\ a_2\bmod 2]=[1,1]$ 是回文序列。
- $(l,r,m)=(3,4,2)$：此时 $[a_3\bmod 2,\ a_4\bmod 2]=[0,0]$ 是回文序列。
- $(l,r,m)=(2,5,2)$：此时 $[a_2\bmod 2,\ a_3\bmod 2,\ a_4\bmod 2,\ a_5\bmod 2]=[1,0,0,1]$ 是回文序列。

对于 $(l,r,m)=(2,5,3)$，$[a_2\bmod 3,\ a_3\bmod 3,\ a_4\bmod 3,\ a_5\bmod 3]=[0,2,1,0]$ 不是回文序列，因此 $f(2,5,3)=0$。
