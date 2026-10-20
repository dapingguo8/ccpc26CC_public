不难发现两个 $0$ 之间的区间的删除过程对应着一棵笛卡尔树，大小限制转化为：对于每条边都有所有子结点权值小于父结点权值。因此，若树的形态确定，则方案数即为 $\frac{n!}{\prod_u sz_u}$，其中 $sz_u$ 表示以 $u$ 为根的子数大小。

首先考虑一段区间被删完的情况。记 $F_{l,r,h}$ 为区间 $(l,r)$ 内所有位置都被删除、且最后一个被删位置的轮数为 $h$ 的 $\frac{1}{\prod_u sz_u}$ 总和。

若区间最后删除位置为 $k$，左右区间的最后轮数为 $x,y$，则 $h=1+\max(x,y)$。

令 $P_L(z)=\sum_{x\le z}F_{l,k,x}$，$P_R(z)=\sum_{y\le z}F_{k,r,y}$，则左右最大值恰为 $z$ 的贡献为 $P_L(z)P_R(z)-P_L(z-1)P_R(z-1)$。

有转移：
$$
F_{l,r,z+1}\leftarrow F_{l,r,z+1}+\dfrac{P_L(z)P_R(z)-P_L(z-1)P_R(z-1)}s
$$
其中，若 $a_k>0$，$z=a_k-1$；若 $a_k=-1$，$z$ 任意。

接下来处理 $0$。$0$ 位置上的值必须先严格递增后严格递减。

令 $L_i,R_i$ 分别表示峰值在位置 $i$ 时，左半部分和右半部分的总贡献，则 $L_i=\sum_{j<i}\frac{L_j\sum_hF_{j,i,h}}r$，$
R_i=\sum_{j>i}\frac{R_j\sum_h F_{i,j,h}}{n-1-i}$，答案即为 $n!\cdot n^{-1}\cdot \sum_iL_iR_i=(n-1)!\cdot \sum_iL_iR_i$。

时间复杂度为 $\mathcal O(\sum n^4)$。
