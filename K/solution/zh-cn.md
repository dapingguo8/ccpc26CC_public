{{ self.title() }}

## 题目简述

有 $n$ 个格子的纸带，$m$ 次操作：第 $i$ 次操作用颜色 $i$ 覆盖前缀 $[1,x_i]$（$o_i=0$）或后缀 $[x_i,n]$（$o_i=1$）。$q$ 次询问 $[l,r]$，问只执行第 $l$ 到第 $r$ 次操作后纸带上可见的不同颜色数。答案是「可见的操作条数」，因为每次操作用一种独一无二的颜色。

## 记号

记第 $i$ 次操作的染色区域为

$$
A_i=\begin{cases}[1,x_i],&o_i=0,\\[2pt] [x_i,n],&o_i=1.\end{cases}
$$

颜色 $i$ 可见 $\iff A_i\nsubseteq U_i$，其中 $U_i=\bigcup_{i<j\le r}A_j$ 是它之后所有操作覆盖区域的并。

## 关键观察一：并集只有两个区间

因为所有 $A_j$ 都是前缀或后缀，$U_i$ 也一定是「一个前缀并上一个后缀」：

$$
U_i=[1,P_i]\cup[S_i,n],
$$

其中 $P_i$ 是 $i$ 之后所有**前缀**操作 $x_j$ 的最大值（没有前缀操作为 $0$），$S_i$ 是 $i$ 之后所有**后缀**操作 $x_j$ 的最小值（没有后缀操作为 $n+1$）。约定空区间 $[1,0]$ 与 $[n+1,n]$ 不覆盖任何格子。

于是

$$
A_i\subseteq U_i\iff P_i\ge S_i-1 ,
$$

此时 $U_i$ 已经覆盖了整条纸带，颜色 $i$ 一定不可见。当 $P_i<S_i-1$ 时 $U_i$ 中间有一段空白 $[P_i+1,S_i-1]$，而 $A_i$ 恰好伸进这段空白：

$$
o_i=0\text{ 时可见}\iff x_i>P_i,\qquad o_i=1\text{ 时可见}\iff x_i<S_i.
$$

## 关键观察二：不可见的是最前面的一段

注意 $i$ 越小，$U_i$ 越大（并集只增不减），所以「$P_i\ge S_i-1$」关于 $i$ 是单调的：若操作 $i+1\sim r$ 能覆盖整条纸带，那么 $i\sim r$ 一定也能。因此对每个 $r$，存在一个分界点

$$
\mathrm{full}(r)=\max\{i:A_i\text{ 被 } U_i \text{ 完全覆盖}\}
$$

（即「操作 $\mathrm{full}(r)\sim r$ 恰好能覆盖整条纸带」的最大下标，不存在则令 $\mathrm{full}(r)=0$）。任何 $i<\mathrm{full}(r)$ 的颜色都不可见，于是

$$
\text{询问 }[l,r]\text{ 只需考虑 } i\in\bigl[\max(l,\mathrm{full}(r)),\,r\bigr].
$$

**易错点**：下界是 $\max(l,\mathrm{full}(r))$ 而不是 $\max(l,\mathrm{full}(r)+1)$。下标 $\mathrm{full}(r)$ 的那次操作正好是「补上最后一块缺口」的操作，它必然可见，不能把它截掉。例如 $n=4$、四次操作为 $(0,2),(1,3),(0,4),(1,4)$、询问 $[1,4]$，正确下界是 $3$，用 $\mathrm{full}(r)+1=4$ 就会漏掉颜色 $3$。

## 关键观察三：窗口内可见 $\iff$「之后再没有能压制它的同类操作」

在窗口 $\bigl[\max(l,\mathrm{full}(r)),r\bigr]$ 内每个 $i$ 都满足 $P_i<S_i-1$，而「$x_i>P_i$」等价于「$i$ 之后没有前缀操作的 $x_j\ge x_i$」，「$x_i<S_i$」等价于「$i$ 之后没有后缀操作的 $x_j\le x_i$」。于是定义

$$
\mathrm{nxt}(i)=\begin{cases}
i \text{ 之后第一个 } x_j\ge x_i \text{ 的前缀操作下标},&o_i=0,\\
i \text{ 之后第一个 } x_j\le x_i \text{ 的后缀操作下标},&o_i=1,
\end{cases}
$$

不存在则取 $m+1$（视作 $+\infty$），那么

$$
\boxed{\ \text{答案}=\#\{\,i:\max(l,\mathrm{full}(r))\le i\le r,\ \mathrm{nxt}(i)>r\,\}\ }
$$

注意这里必须是**严格**不等（前缀取 $\ge$、后缀取 $\le$）：若后面存在 $x_j=x_i$ 的同类操作，$A_j\subseteq A_i$，$A_i$ 会被 $A_j$ 完全盖住，颜色 $i$ 不可见。

## 算法

1. **求 $\mathrm{nxt}$**：对前缀操作和后缀操作分别扫一遍，用单调栈求出「右侧第一个 $\ge x_i$（或 $\le x_i$）的同类操作下标」，$O(m)$。
2. **求 $\mathrm{full}(r)$**：$r$ 递增，用双指针维护最靠左仍能覆盖整条纸带的 $l_0$，配合两个单调队列维护窗口内前缀 $x$ 的最大值与后缀 $x$ 的最小值，$O(m)$。
3. **离线回答询问**：把询问挂到各自的 $r$ 上，$r$ 从大到小枚举；当 $r$ 减小时把满足 $\mathrm{nxt}(i)>r$ 的位置 $i$ 加入树状数组（注意 $\mathrm{nxt}(i)=r$ 时也是「$\le r$」，要延迟到 $r-1$ 才加入）。对询问 $[l,r]$ 用前缀和差分回答 $\mathrm{BIT}.\mathrm{sum}(r)-\mathrm{BIT}.\mathrm{sum}(\max(l,\mathrm{full}(r))-1)$。

总时间复杂度 $O\bigl((m+q)\log m\bigr)$，空间复杂度 $O(m+q)$。

## 实现要点

- $n\le 10^9$ 不参与任何存储，只出现在 $\mathrm{full}$ 的判定中，无需离散化；真正用到 $n$ 的地方只有「没有后缀操作时 $S_i=n+1$」。
- 输入规模 $5\times10^5$ 行、输出 $5\times10^5$ 行，实测 $1.0$ 秒的时限下需要自带 `fread`/`fwrite` 缓冲，`cin`/`cout` 不关同步会超时。
- 答案范围是 $[1,r-l+1]$，用 `int` 即可，但树状数组内部的前缀和最大为 $m$，也在 `int` 范围内。

## 验题

- `bf/bf.cpp`：对每个询问直接模拟整条纸带再统计颜色种数，$O(q(n+m))$，仅在小数据上运行，用于随机对拍（$n\le 40$ 的随机数据上与 std 完全一致），大数据上会超时/超内存，因此期望分 $<100$。
- `wrong/wrong_no_cutoff.cpp`（idea）：用 $\max$ 时漏掉了 $\mathrm{full}(r)$ 的截断，只考虑 $[l,r]$，当询问窗口覆盖整条纸带时会多算。
- `wrong/wrong_greedy_stop.cpp`（idea）：从右往左扫并把 $x_i$ 更新的操作记为「新颜色」，一旦某次操作没更新极值就 `break`；但后面的操作仍可能因更早的操作而可见，构造如「前缀 $x=5,1,9$」的序列即错。
- `wrong/wrong_on2.cpp`（complexity）：除 $\mathrm{full}(r)$ 外与标准解相同，这里对每个 $r$ 从 $r$ 往左暴力扫到窗口覆盖整条纸带，最坏 $O(m^2)$，$m=5\times10^5$ 必超时。
- `wrong/wrong_per_query.cpp`（complexity，易混过）：对每个询问从 $r$ 往左扫并维护前缀最大 $P$/后缀最小 $S$（操作 $i$ 可见 $\iff x_i>P$ 或 $x_i<S$），一旦 $P\ge S-1$ 即提前终止。随机数据下几步就断，能混过包括 $5\times10^5$ 随机大数据在内的多数点；只有 `mode: no_full`（永不覆盖整条纸带）才让它退化成 $O(qm)$。
- `wrong/wrong_cutoff_plus_one.cpp`（implementation）：把下界取成 $\mathrm{full}(r)+1$，正好漏掉必然可见的颜色 $\mathrm{full}(r)$，会少算。
- `wrong/wrong_nonstrict.cpp`（implementation）：单调栈用严格不等号求 $\mathrm{nxt}$，在出现并列的 $x$ 时会多算（数据中 `mode: equal` / `mode: extreme` 专门构造了大量并列极值）。
- `wrong/wrong_own_point.cpp`（implementation）：只看端点 $x_i$ 是否落在当前 $(\max P,\min S)$ 内来判可见，忽略了区间内部的 $x$ 也会被同侧更靠里的操作遮挡。
- `wrong/wrong_window_no_l.cpp`（implementation）：询问窗口左端忘与 $l$ 取 $\max$（写成 $A=\mathrm{full}(r)$ 而非 $\max(l,\mathrm{full}(r))$），当 $l>\mathrm{full}(r)$ 时会多算。

数据中 `mode: equal` / `mode: extreme`（大量并列极值，卡 `wrong_nonstrict`）、
`mode: full`（几乎每个 $r$ 都有截断点）、`mode: no_full`（永不覆盖整条纸带）
是针对上述错解构造的反例族；其中 `no_full` 再配 `qmode: all`
（43-46 号，全部询问取整段 $[1,m]$）可把 `wrong_per_query` 的 $O(qm)$
最坏情形钉死。