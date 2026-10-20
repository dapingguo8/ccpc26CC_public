{{ self.title() }}

{{ s('description') }}

Little $\varepsilon$ and Little $\omega$ are two girls who cherish the time they spend together. Little $\omega$ is preparing a gift for Little $\varepsilon$, recording it as a secret sequence $a$ whose elements are non-negative integers no greater than $2^k-1$.

Curious about the surprise, Little $\varepsilon$ asks Little $\omega$ a total of $m$ questions. The $i$-th question asks for the bitwise AND of $a_{x_i}$ and $a_{y_i}$.

Little $\omega$ gives an answer to every question. Her answer to the $i$-th question is $z_i$; in other words, she claims that the sequence $a$ satisfies $a_{x_i}\operatorname*{AND}a_{y_i}=z_i$, where $x\operatorname*{AND}y$ denotes the bitwise AND of $x$ and $y$.

Little $\varepsilon$ feels that Little $\omega$ is teasing her and suspects that she is simply making up the answers. Perhaps no sequence $a$ satisfies all these conditions!

So she turns to you for help. Determine whether a sequence $a$ satisfying all the conditions exists. If it does, Little $\varepsilon$ also wants to know the minimum possible sum of all its elements.

{{ s('input format') }}

{{ self.input_file() }}

The first line contains a positive integer $T$, the number of test cases.

For each test case:

- The first line contains three integers $n,m,k$ ($1\le n\le 200000$, $0\le m\le 200000$, $1\le k\le 30$), the sequence length, the number of equations, and the bit-length limit.
- Each of the next $m$ lines contains three integers $x_i,y_i,z_i$ ($1\le x_i,y_i\le n$, $0\le z_i<2^k$), specifying one equation.

The sum of $n$ over all test cases in one input file does not exceed $5\times 10^5$, and the sum of $m$ does not exceed $5\times 10^5$.

{{ s('output format') }}

{{ self.output_file() }}

For each test case, output one line containing `-1` if no sequence satisfies all equations. Otherwise, output the minimum possible sum of its elements. The answer may exceed the range of a signed 32-bit integer; use a signed 64-bit integer.

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ self.title_sample_description() }}

The first sample contains $3$ test cases.

- In the first test case, $a=[0,1,1]$ satisfies all equations and has the minimum sum $2$.
- In the second test case, the first two equations have value $1$ and force $a_1=a_2=a_3=1$, since $k=1$. Thus $a_2\operatorname{AND}a_3=1$, contradicting the third equation, whose value is $0$. No valid sequence exists.
- In the third test case, the self-equations force $a_1=5$ and $a_2=6$. The equation $a_1\operatorname{AND}a_3=5$ allows $a_3=5$ or $7$; choosing $5$ gives the minimum sum $16$.

{{ s('sample', 2) }}

{{ self.sample_text() }}

{{ self.title_sample_description() }}

The second sample contains $5$ test cases.

- The first test case gives different values for the same pair, so it is impossible.
- In the second test case, $a_1=4514$ is forced; every other element can be $0$, giving sum $4514$.
- In the third test case, the repeated self-equations force $a=[2,3,4]$, giving sum $9$.
- In the fourth test case, all three elements must equal $2^{30}-1$, giving sum $3221225469$.
- In the fifth test case, there are no equations; setting every element to $0$ gives sum $0$.
