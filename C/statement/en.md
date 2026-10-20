{{ self.title() }}

{{ s('description') }}

Little $\varepsilon$ wrote a melody for Little $\omega$ to remember their shared memory. She represents each note by an integer indicating its pitch.

To Little $\varepsilon$, rising notes sound beautiful. Still learning to compose, she chose a phrase $a$ of length $k$ that is a cyclic shift of $[1,2,\ldots,k]$, and repeated it forever.

For example, when $k=4$, the phrase $a$ can be $[1,2,3,4]$, $[2,3,4,1]$, $[3,4,1,2]$, or $[4,1,2,3]$. The first $n$ notes of the repeated phrase form the original melody $b$. If $a=[2,3,4,1]$ and $n=10$, then $b=[2,3,4,1,2,3,4,1,2,3]$.

Before giving the melody to Little $\omega$, Little $\varepsilon$ decided to adjust a few notes. She could change the pitch at any position to any positive integer; each position whose pitch was changed counts as one adjusted note. Let $b'$ denote the score she gave to Little $\omega$. The original phrase $a$ has been lost, so Little $\omega$ knows only $n$, $k$, and $b'$.

Little $\omega$ is wondering about the minimum number of notes Little $\varepsilon$ had to adjust to obtain $b'$. Please help Little $\omega$ compute this value.

{{ s('input format') }}

{{ self.input_file() }}

The first line contains an integer $T$ ($1\le T\le 10^4$), the number of test cases. Each test case contains two lines:

- The first line contains two integers $n,k$ ($2\le k\le n\le 2\times 10^5$), the length of the score and the length of the repeated phrase.
- The second line contains $n$ integers $b'_1,b'_2,\ldots,b'_n$ ($1\le b'_i\le 10^9$), the pitches in the embellished score.

The sum of $n$ over all test cases in one input file does not exceed $2\times 10^5$.

{{ s('output format') }}

{{ self.output_file() }}

For each test case, output one non-negative integer: the minimum number of positions whose pitches were changed.

{{ s('sample', 1) }}

{{ self.sample_text() }}

{{ self.title_sample_description() }}

The first sample contains $3$ test cases.

- For the first test case, $a=[2,3,1]$ gives $b=[2,3,1,2,3,1]$, so no note needs to be changed.
- For the second test case, $a=[1,2,3]$ gives $b=[1,2,3,1,2]$. Changing only the last note to $3$ gives the answer $1$.
- For the third test case, $a=[4,1,2,3]$ gives $b=[4,1,2,3,4]$. Changing the second note to $3$ and the fourth note to $1$ gives the answer $2$.

{{ s('sample', 2) }}

{{ self.sample_text() }}
