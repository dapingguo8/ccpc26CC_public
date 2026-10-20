{{ self.title() }}

首先我们有 $\operatorname{Var}(\tau)=\mathbb E[\tau^2]-\mathbb E[\tau]^2$，也就是只需求一阶矩和二阶矩。

大家应该都可以看出这题需要构造势能函数（或者说，会使用停时定理），让我们 formalize 一下这道题的目标。令目前的状态为 $A$，下一步走到的状态为 $A'$，以及 $\mathbb E[\tau],\mathbb E[\tau^2]$ 分别对应的势能函数为 $u(A),v(A)$，那么：
$$
u(A)=1+\mathbb E[u(A')\mid A]\\
v(A)=2u(A)-1+\mathbb E[v(A')\mid A]
$$

接下来就是构造了。期望具有可加性，我们可以尝试用初等对称多项式来构造势能函数，对于状态 $A=(s_1,s_2,\cdots,s_k)$，令 $\sigma_2(A)=\sum_{i<j}s_is_j$：
$$
\mathbb E[\sigma_2(A_{t+1})\mid A_t]=\frac{\sum_{i<j}s_is_j(\sigma_2(A_t)-s_is_j+\frac12(s_{i}+1)(s_j-1)+\frac12(s_i-1)(s_j+1))}{\sum_{i<j}s_is_j}\\
=\frac1{\sigma_2(A_t)}\sum_{i<j}s_is_j(\sigma_2(A_t)-1)=\sigma_2(A_{t})-1
$$
可以发现这就是我们要找的 $u(A)$。接下来为了造 $u(A)$ 的一次项，我们平方一下：
$$
\mathbb E[\sigma_2(A_{t+1})^2\mid A_t]=\frac{\sum_{i<j}s_is_j(\frac12(\sigma_2(A_t)-s_i+s_j-1)^2+\frac12(\sigma_2(A_t)+s_i-s_j-1)^2)}{\sum_{i<j}s_is_j}\\
=\frac1{\sigma_2(A_t)}\sum_{i<j}s_is_j((\sigma_2(A_t)-1)^2+(s_i-s_j)^2)\\
=(\sigma_2(A_t)-1)^2+\frac1{\sigma_2(A_t)}\sum_{i<j}s_is_j(s_i-s_j)^2
$$
由对称多项式基本定理，通过一些手段，我们能凑出 $\sum_{i<j}s_is_j(s_i-s_j)^2=n^2\sigma_2(A_t)-4\sigma_2(A_t)^2+3n\sigma_3(A_t)$，于是：
$$
\mathbb E[\sigma_2(A_{t+1})^2\mid A_t]=\sigma_2(A_t)^2-6\sigma_2(A_t)+n^2+1+\frac{3n\sigma_3(A_t)}{\sigma_2(A_t)}
$$
根据期望的线性性，我们可以不用再担心常数项，但是仍需要修正 $\frac{\sigma_3(A_t)}{\sigma_2(A_t)}$ 项，不妨算一下 $\sigma_3(A_t)$ 的变化量。这里直接算比较麻烦，可以通过对称性发现只包含 $i,j$ 中一项的 $i'<j'<k'$ 变化量总和为零（一个加一一个减一）；对于同时包含 $i,j$ 的 $i'<j'<k'$ 贡献总和恰为 $s_is_j(n-s_i-s_j)$，所以有：
$$
\mathbb E[\sigma_3(A_{t+1})\mid A_t]=\frac{\sum_{i<j}s_is_j(\sigma_3(A_t)+(-s_is_j+\frac12(s_i+1)(s_j-1)+\frac12(s_i-1)(s_j+1))(n-s_i-s_j))}{\sum_{i<j}s_is_j}\\
=\frac1{\sigma_2(A_t)}\sum_{i<j}s_is_j(\sigma_3(A_t)-(n-s_i-s_j))=\sigma_3(A_{t})-\frac{3\sigma_3(A_t)}{\sigma_2(A_t)}
$$
于是我们就可以处理 $\frac{\sigma_3(A_t)}{\sigma_2(A_t)}$ 项了，可以解出来 $v(A)=\frac{(n^2-2)\sigma_2(A)+\sigma_2(A)^2+n\sigma_3(A)}{3}$。

那么 $\mathbb E[\tau]=\sigma_2(A),\operatorname{Var}[\tau]=\frac{(n^2-2)\sigma_2(A)-2\sigma_2(A)^2+n\sigma_3(A)}3$，其中 $\sigma_2(A),\sigma_3(A)$ 容易 $O(k)$ 求得。

我们也可以验算一下：
$$
\mathbb E[v(A_{t+1})\mid A_t]\\
=\frac13((n^2-2)(\sigma_2(A_t)-1)+\sigma_2(A_t)^2-6\sigma_2(A_t)+n^2+1+\frac{3n\sigma_3(A_t)}{\sigma_2(A_t)}+n(\sigma_3(A_t)-\frac{3\sigma_3(A_t)}{\sigma_2(A_t)}))\\
=v(A_t)+\frac13(-(n^2-2)-6\sigma_2(A_t)+n^2+1+\frac{3n\sigma_3(A_t)}{\sigma_2(A_t)}-n\frac{3\sigma_3(A_t)}{\sigma_2(A_t)})\\
=v(A_t)+1-2u(A_t)
$$
这符合我们对势能函数的要求。

---

一些正确性的补充说明：

令 $A_t$ 为第 $t$ 次操作后的状态对应的随机变量，以及 $\mathcal F_t$ 表示前 $t$ 步的全部信息。再设 $M_t=t^2+2tu(A_t)+v(A_t)$。对于未停止的状态 $A_t$，我们有：
$$
\mathbb E[M_{t+1}\mid \mathcal F_t]=(t+1)^2+2(t+1)\mathbb E[u(A_{t+1})\mid \mathcal F_t]+\mathbb E[v(A_{t+1})\mid \mathcal F_t]\\
=(t^2+2t+1)+2(t+1)(u(A_t)-1)+v(A_t)+1-2u(A_t)\\
=t^2+2tu(A_t)+v(A_t)=M_t
$$
更严格地，我们令 $T_t=\min(t,\tau),M_t=T_t^2+2T_tu(A_{T_t})+v(A_{T_t}),N_t=T_t+u(A_{T_t})$，可以类似地证明 $\mathbb E[M_{t+1}\mid \mathcal F_t]=M_t,\mathbb E[N_{t+1}\mid \mathcal F_t]=N_t$，即 $M_t,N_t$ 均为鞅。

此外，我们还需验证停时定理的适用条件——从任意非终止状态开始，以至少 $\varepsilon=(\frac1{n(n-1)})^{n-1}>0$ 的概率，我们会把所有人的类别改成同一个人的类别，这样过程就会结束。于是 $\tau$ 几乎必然有限，更进一步地：
$$
\mathbb E[\tau^2]\leqslant \sum_{r=0}^{\infty}((r+1)(n-1))^2(1-\varepsilon)^r<\infty
$$
记 $C_u,C_v$ 为 $u(A),v(A)$ 的上界，于是 $|M_t|\leqslant \tau^2+2\tau C_u+C_v\leqslant (1+2C_u)\tau^2+C_v$，即 $|M_t|$ 存在一个可积函数作为上界。

根据可选停时定理，$v(A_0)=\mathbb E[M_0]=\mathbb E[M_\tau]=\mathbb E[\tau^2]$，同理有 $u(A_0)=\mathbb E[N_0]=\mathbb E[N_\tau]=\mathbb E[\tau]$。
