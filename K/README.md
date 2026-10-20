# 纸带染色（color）数据包

CCPC 2026 长春站 day1/color，TUACK 格式的完整出题包。

## 题目概要

长度为 $n$ 的纸带依次进行 $m$ 次染色（`o=0` 染前缀 $[1,x]$，`o=1` 染后缀 $[x,n]$），
$q$ 个询问 $[l,r]$：只执行第 $l\sim r$ 次操作后可见颜色数。
$1\le n\le 10^9$，$1\le m,q\le 5\times 10^5$，时限 1.0 s，内存 512 MiB。

标准做法：单调栈求 `nxt[i]` + 双指针/单调队列求 `full(r)` + 树状数组离线，
复杂度 $O((m+q)\log m)$，详见 `solution/zh-cn.md`。

## 目录结构

```
conf.yaml        TUACK 配置（数据配方、时限、users 名单）
gen.py           数据生成器（操作 7 种模式：mixed/prefix/suffix/extreme/equal/no_full/full；
                 询问分布 qmode：mixed/all/single）
random_state     随机种子状态，dmk 靠它保证重新生成的数据完全一致（勿删）
test.py          一键验题脚本（见下）
data/            正式数据 1..46（.in/.ans，LF 行尾）
down/            下发样例 1（手写，LF 行尾）
statement/       题面
solution/        题解
rsy/             所有求解代码
  std/std.cpp    标准程序，O((m+q) log m)
  std/val.cpp    输入校验器（testlib 严格模式，按 LF 判定）
  std/testlib.h  校验器依赖
  bf/bf.cpp      暴力（n > 2e6 时主动放弃，用于对拍）
  wrong/         八个错解（见下）
.gitattributes   固定 *.in/*.ans 为 LF（防 core.autocrlf 检出时转 CRLF）
```

## 错解设计

| 程序 | 层 | 错误 | 得分 |
|---|---|---|---|
| `wrong_no_cutoff.cpp` | idea | 漏掉 `full(r)` 截断 | 39.13 |
| `wrong_greedy_stop.cpp` | idea | 从右往左扫，一遇到不产生新颜色的操作就 break | 8.70 |
| `wrong_on2.cpp` | complexity | 思路对，`full(r)` 暴力扫描 O(m²) | 65.22 |
| `wrong_per_query.cpp` | complexity | 逐询问从右往左扫 + 提前终止，极易混过随机大数据 | 65.22 |
| `wrong_cutoff_plus_one.cpp` | implementation | 截断差一 | 39.13 |
| `wrong_nonstrict.cpp` | implementation | `nxt` 比较取严格不等号 | 47.83 |
| `wrong_own_point.cpp` | implementation | 只用端点 $x_i$ 是否落在 $[\max P,\min S]$ 内判可见 | 17.39 |
| `wrong_window_no_l.cpp` | implementation | 询问窗口左端忘与 $l$ 取 max（`A = full[r]`） | 13.04 |

数据覆盖约束上下界（n=1/1e9、m=1/5e5、q=1/5e5），并含反例族
（`equal` 并列极值、`full` 全覆盖、`no_full` 永不覆盖）与 5e5 规模随机大数据。

- **`no_full` + `qmode: all`（43-46 号）**：操作永不覆盖整条纸带（前缀 $x\le mid$、
  后缀 $x\ge mid+2$），且全部询问都取成整段 $[1,m]$。永不覆盖让
  `wrong_per_query` 失去唯一的提前终止机会，整段询问又让它每次询问都得扫满
  整个窗口，于是退化成确定的 $O(qm)$：43/44 号（$n=10^9$、$m=q=5\times10^5$）
  必然超时（41/42 号因 mixed 询问里也含约 $1/8$ 的整段询问而同样超时，
  43/44 把这条死路彻底钉死）；45/46 号是同构造的中规模点
  （$n=1000$、$m=q=2\times10^4$），顺带把 `wrong_nonstrict` 也一并卡掉。

## 重新生成数据

```powershell
python -m tuack.dmk -s i
```

注意：
- `random_state` 存在时数据完全可复现；
- `.in` 由 `gen.py` 以二进制方式直接写出，**恒为 LF**；
- dmk 的 run 步骤在 Windows 上批量起子进程偶发失败（`.ans` 为空），
  此时直接跑 `python test.py`，或手动用 std 逐点重跑 `.ans`。

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
2. 用与 std 无关的 Python 实现独立重算所有 `.ans` 并比对；
3. 按 `conf.yaml` 的 `users` 评测全部程序，写 `result.csv`，
   核对得分是否满足 `expected`（std `== 100`，其余 `< 100`）。

## 行尾约定

本包所有 `.in`/`.ans` 统一 **LF**。校验器为 testlib 严格模式、按 LF 判定；
Windows 本地编译校验器必须加 `-DFOR_LINUX`（`test.py` 已自动处理，
Linux 评测机上该宏无影响）。`.gitattributes` 已固定数据文件的 `eol=lf`，
请勿删除 `random_state`，否则随机数据将换一批。
