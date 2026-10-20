# 余镜（mirror）数据包

CCPC 2026 长春站 day1/mirror，TUACK 格式的完整出题包。

## 题目概要

给定序列 $a_1,\dots,a_n$ 与上界 $M$，求「$[l,r]$ 在模 $m$ 意义下回文」的
$(l,r,m)$ 对数（$1\le l<r\le n$，$2\le m\le M$，**单点区间不计入**）。

输入格式：第一行 $n,M$，第二行 $a_1,\dots,a_n$；输出一行一个整数。
数据范围：$1\le n\le 8000$，$2\le M\le 10^6$，$0\le a_i\le M$，时限 1.0 s，内存 512 MiB。
题面 `statement/zh-cn.md` 已按 color 题面格式写全（描述、输入输出格式、样例解释）。

标准做法：模 $m$ 回文 $\iff m$ 整除所有镜像差，故每个长度 $\ge 2$ 的区间的
可行 $m$ 数是「镜像差 gcd $D$ 的不小于 $2$ 的因子数」（$D=0$ 时为 $M-1$）；
同一中心向外扩展 $O(1)$ 递推 $D$，奇数中心的单点直接跳过，$\tau$ 用筛法预处理，
复杂度 $O(M\log M+n^2+n\log A)$
（running gcd 按中心摊销：每中心仅 $O(\log A)$ 次严格变小），
详见 `solution/zh-cn.md`。

## 目录结构

```
conf.yaml        TUACK 配置（数据配方、时限、users 名单）
gen.py           数据生成器（7 种模式：random/equal/pal/few/extreme/square/levels）
random_state     随机种子状态，dmk 靠它保证重新生成的数据完全一致（勿删）
test.py          一键验题脚本（见下）
data/            正式数据 1..51（.in/.ans，LF 行尾）
down/            下发样例 1（手写，LF 行尾，答案 3）
statement/       题面（color 同格式）
solution/        题解
rsy/             所有求解代码
  std/std.cpp    标准程序，O(M log M + n^2 + n log A)
  std/val.cpp    输入校验器（testlib 严格模式，按 LF 判定）
  std/testlib.h  校验器依赖
  bf/bf.cpp      按定义暴力（枚举 m 再数回文子区间，O(M·n^2)，用于对拍）
  wrong/         十个错解（见下）
.gitattributes   固定 *.in/*.ans 为 LF（防 core.autocrlf 检出时转 CRLF）
```

## 错解设计

| 程序 | 层 | 错误 | 得分 |
|---|---|---|---|
| `wrong_pal_only.cpp` | idea | 只统计原数组本身回文的区间 | 11.76 |
| `wrong_cubic.cpp` | complexity | 思路对，每区间重新 O(len) 求 gcd，O(n³) | 35.29 |
| `wrong_early_break.cpp` | complexity | 同上但 gcd=1 提前终止，中规模/M=2 能混过 | 47.06 |
| `wrong_manacher_m.cpp` | complexity | 对每个 m 各跑一次 Manacher，O(M·n) | 39.22 |
| `wrong_trial_div.cpp` | complexity | 思路对，但因子数用试除 O(√D)，总计 O(n²√M) | 78.43 |
| `wrong_zero.cpp` | implementation | 长度≥2 且 D=0 时贡献算成 0 而非 M-1 | 29.41 |
| `wrong_int.cpp` | implementation | 答案用 32 位无符号整数累加，超 $2^{32}$ 回绕 | 76.47 |
| `wrong_divisor.cpp` | implementation | 因子计数漏掉 D 本身 | 11.76 |
| `wrong_square_div.cpp` | implementation | 因子计数写成 `d*d < g`，漏掉完全平方数多出的 √D | 33.33 |
| `wrong_zero_break.cpp` | implementation | 提前终止条件写成 `g < 2`，丢掉 D=0 那类区间 | 29.41 |
| `bf/bf.cpp` | — | 按定义暴力 O(M·n²)，大数据超时 | 39.22 |

数据覆盖约束上下界（n=1/8000、M=2/1e6、a_i=0/M；n=1 点答案为 0），并含反例族：

- `equal` 全相等：答案达到理论上界 n(n−1)/2·(M−1) = 31,995,968,004,000
  （27/28 号），专门卡 32 位累加；few/extreme 的 n=8000 点答案也在
  $1.6\times10^{10}$ 量级，同样卡溢出（wrong_int 共挂 8 个点）；
- `square` 周期完全平方数（41-46 号），$a_i=(i\bmod L)^2$，镜像差
  $k^2-j^2=(k-j)(k+j)$ 恒含因子 $k+j$，分两种段长：
  - 长段 $L=1001$（41/42/46 号）：值取到 $1000^2=M$，产生大 D、多因子区间，
    命中 $a_i$ 上界；
  - 短固定周期 $L=40$（43/44/45 号）：严格周期性使跨周期差链保持公因子 2，
    n=8000 时约 63% 的区间 D>1，gcd=1 剪枝基本失效（43 号 std 的 gcd
    负担比长段点高约 40%）；实测偶数 L（或奇数且为 3 的倍数）此效应最强，
    素数 L（如 41/101）差链很快塌成 1，故段长不可随机化——随机段长会破坏
    相位对齐，D>1 比例降至 3% 以下；带相位的周期序列只是循环移位，
    D>1 结构不变，故统一从 $0^2$ 起（同时取到 $a_i=0$ 界）；
  - 44/45/46 为 n=2000，纳入 Python 独立重算；
- `levels` 分层取值（47-51 号）：$a_i$ 只取 $B$ 的倍数
  （$B=M/k$ 或由 `base` 直接指定），镜像差恒为 $B$ 的倍数，running gcd 频繁
  停在大值 $D$ 上，把「每区间试除 $O(\sqrt D)$ 数因子」的 `wrong_trial_div`
  从能混过 40/46 个点打到 40/51（新增的 47-51 号全挂，实测超时）：
  - 47/48 号（$n=8000$、$k=3$，即 $B=333333$）：gcd=1 剪枝彻底失效，
    $D$ 常取 $333333$ 的大倍数，$\tau(D)$ 与 $\sqrt D$ 同时变大；
  - 49/50 号（`base` $=720720$，高合成数）：取值只有 $\{0,720720\}$，
    $D\in\{0,720720\}$，其中 $\tau(720720)=240$ 为 $M\le10^6$ 内的极大值，
    专卡因子计数类实现错误；
  - 51 号（$k=6$）：同族但层级更细，`wrong_early_break`/`wrong_cubic`
    这类「gcd=1 才提前终止」的暴力在 47-51 上全部退化成完整扫描并超时；
  - 50 号为 $n=2000$，纳入 Python 独立重算；
  - 注意这批点的 $D$ 长期不互质，是标准解的最坏情形（$n=8000$ 时
    std 单线程约 0.8 s，见下「验证」）。
- `few` 两值且差 ≥ 2 使 gcd 永不为 1、`extreme` 只取 0/M 使 $D\in\{0,M\}$；
- 另有 8000 规模随机大数据、M=2 下界与 M=999983（素数）点。

## 重新生成数据

```powershell
python -m tuack.dmk -s i
```

注意：

- `random_state` 存在时数据完全可复现；
- `.in` 由 `gen.py` 以二进制方式直接写出，**恒为 LF**；
- dmk 的 run 步骤会把 std 的 stdout 以文本模式重定向写 `.ans`，
  Windows 下得到 **CRLF**，且批量起子进程偶发失败（`.ans` 为空）；
  此时用 Python 逐点跑 std 重写 `.ans`，并对 stdout 做
  `replace(b'\r\n', b'\n')`（MinGW 程序向管道输出也会把 `\n` 转成 `\r\n`）：

```powershell
python -c "import glob,os,subprocess;[open(p[:-3]+'.ans','wb').write(subprocess.run(['build/std.exe'],stdin=open(p,'rb'),stdout=subprocess.PIPE,check=True).stdout.replace(b'\r\n',b'\n')) for p in sorted(glob.glob('data/*.in'),key=lambda s:int(os.path.basename(s)[:-3]))+['down/1.in']]"
```

## 验证

```powershell
python test.py              # 完整验证（约几分钟）
python test.py --validate   # 只校验数据与答案
python test.py --only std   # 只评测 std
python test.py -j 4         # 并行评测
```

`test.py` 做三件事：

1. 用 `rsy/std/val.cpp`（testlib 严格模式，自动带 `-DFOR_LINUX` 编译）
   校验 `data/` 与 `down/` 全部输入；
2. 用与 std 无关的 Python 实现独立重算 `.ans` 并比对
   （$n\le 2500$ 的点全量重算，含各模式的中规模点 15-24 与 square 44-46、
   levels 50；更大的点 Python 过慢，只做格式与值域检查，其正确性由同构造
   中规模点与错解差异行为交叉保证）；
3. 按 `conf.yaml` 的 `users` 评测全部程序，写 `result.csv`，
   核对得分是否满足 `expected`（std `== 100`，其余 `< 100`）。

本机单线程实测（time limit 1.0 s）：最慢的测试点是 47/48 号（levels，$n=8000$），
std 约 **0.80 s**；其余各点 ≤ 0.65 s。这是标准解的最坏情形——$D$ 长期不互质、
gcd=1 剪枝失效，$n^2/2=3.2\times10^7$ 个区间全部要走一次 gcd。

## 行尾约定

本包所有 `.in`/`.ans` 统一 **LF**。校验器为 testlib 严格模式、按 LF 判定；
Windows 本地编译校验器必须加 `-DFOR_LINUX`（`test.py` 已自动处理，
Linux 评测机上该宏无影响）。`.gitattributes` 已固定数据文件的 `eol=lf`，
请勿删除 `random_state`，否则随机数据将换一批。
