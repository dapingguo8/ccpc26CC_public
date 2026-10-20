{{ self.title() }}

## Forced bits

Call $p$ a bit-subset of $q$ if $p\operatorname{AND}q=p$: every bit set in $p$ is also set in $q$.

An equation $a_x\operatorname{AND}a_y=z$ forces every set bit of $z$ to be set in both $a_x$ and $a_y$. Initialize $b_i=0$ for every index. While reading an equation $(x,y,z)$, update
$$
b_x\gets b_x\operatorname{OR}z,\qquad b_y\gets b_y\operatorname{OR}z.
$$
Thus $b_i$ is the bitwise OR of the values of all equations incident to $i$, with the OR of an empty set defined as $0$. For every feasible sequence $a$, $b_i$ is a bit-subset of $a_i$. Also, $b_i<2^k$, because every input value uses only the lowest $k$ bits.

## Feasibility

Store every equation. Only after all equations have been read and every $b_i$ has been finalized, verify each equality $b_x\operatorname{AND}b_y=z$ once. Checking during construction is insufficient: later equations can force additional bits.

Every set bit of $z$ is already present in both $b_x$ and $b_y$. Therefore, if an equality fails, their AND has an extra set bit that is zero in $z$. Since every feasible $a_x$ and $a_y$ would contain all bits of $b_x$ and $b_y$, that extra bit would remain set in $a_x\operatorname{AND}a_y$, a contradiction. In this case no feasible sequence exists, and we output `-1`.

If every equality holds, $b$ itself is feasible.

## Minimum sum and uniqueness

For every feasible $a$, the bit-subset relation gives $a_i\ge b_i$ for every index, so
$$
\sum_{i=1}^{n}a_i\ge\sum_{i=1}^{n}b_i.
$$
Consequently, a feasible $b$ attains the minimum sum. Moreover, if $a\ne b$, at least one element contains an additional set bit and is strictly larger, while no other element is smaller. Its sum is then strictly larger. Hence the minimum-sum sequence is unique, although other feasible sequences may exist.

Self-equations, repeated equations, and reversed pairs need no special handling. An isolated index has candidate value $0$, and if $m=0$, the unique minimum-sum sequence is all zeros.

## Complexity and implementation

Construct the candidates, verify the stored equations, and sum the candidates in $O(n+m)$ time per test case, using $O(n+m)$ memory. Word-sized bitwise operations take constant time because $k\le30$.

Use a signed 64-bit accumulator: the sum can be as large as $200000(2^{30}-1)=214748364600000$. Read only $T$ on the first line and use buffered standard input/output. There is no independent upper limit on $T$; each input file satisfies $\sum n\le5\times10^5$ and $\sum m\le5\times10^5$. The total running time is $O(\sum n+\sum m)$.

The independent oracle in `std/bitwise.cpp` instead processes each bit separately: mark both endpoints of every equation whose value has that bit set, then reject any zero-bit equation whose two endpoints are both marked. Unmarked endpoints stay zero. Summing the marked endpoints with their bit weights gives the same minimum in $O(k(n+m))$ time and $O(n+m)$ memory.
