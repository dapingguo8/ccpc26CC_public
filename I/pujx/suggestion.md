# 事不过三验题反馈

### 题面问题

1. 【题目描述】限制 2：应该写成 $0\leq i<m-2$，$n$ 在前面表示了原串的长度，同时要定义一下 $m$

   ```
   你是对的，已修正
   ```

2. 【程序测试方式】启动命令建议把参数写成可选 `[<arguments>]`（C++ 只用程序即可运行）

   ```
   调整了一下描述
   ```

3. 【程序测试方式】对 $T$ 的描述为 "非负整数"，与题目中 $1\leq T$ 不一致，`testing_tool.py` 也同样判定的是 `if T < 0: raise ValueError(...)`

   ```
   这个其实无所谓，没改
   ```

### 题目建议

这道题感觉没有必要出成强制在线的，直接一股脑把输入全给出去，等选手程序处理完程序退出后（会自动 flush），再用交互器去操作验证也行

domjudge 实测（最大的一组测试点）：
- 强制在线版：0.654s CPU, 3.211s wall
- 修改后的：0.054s CPU, 0.066s wall

```
到时候我看看现场的用时是否会有较大差异，如果有问题的话会再调整，目前暂时没改
```

### 数据问题

编写 validator 测试：
- data/down 部分的 `1.in` 文件末尾均缺少换行，别的均通过

```
OK
```

强度部分：
- 各种情况枚举 $1\sim 13$ 的串把所有情况考虑的差不多了
- 最大的 $5\times10^5$ 的串按标程算法生成长度只有 $749922$，没有达到理论最大值，看情况要不要卡卡数组没开够的？

```
感觉不需要卡...
```



### `interactive_lib.cpp` 问题

|位置|问题|测试版修复||
|:---:|:---:|:---:|-----|
|两次运行都有|读入选手部分均没有读入字符串长度，只读了字符串|读取长度的时候直接限制了范围（第一次运行 $1\leq m\leq\lfloor\frac 32n\rfloor$，第二次运行只能读原串长度），读入字符串时直接用 `pattern` 限制读取长度为 $m/n$ 的 01 串|你是对的，我疏忽了...> <|
|第一次运行|题目明确要求 $m\geq 1$，未检测空串|同上解决|OK|
|第二次运行|`quitf` 内容没有 `compress`，恢复错误的时候 checker 输出的内容过长|用 `testlib` 的 `compress` 函数进行压缩|选手看不到错误信息，所以其实无所谓|
|第二次运行|恢复错误时没有 `(testcase ..)`|将两次运行统一改成 `setTestCase(i)`，出错 `testlib` 会自动增加|选手看不到错误信息，所以其实无所谓|

以下是我为了上 domjudge 测试改的一版 checker（修改内容如上所示，仍然是强制在线的），domjudge 上测试下来没啥问题，ccpcoj 上可能要现场改了（配过一版 ccpcoj，但不是最新的，没有通信题和新赛制的内容）

```cpp
#include"testlib.h"
using namespace std;
#define int long long
int np[1005];
signed main(signed argc, char ** argv){
	ios::sync_with_stdio(0);
	cin.tie(0);
	registerInteraction(argc,argv);
	int t=inf.readInt();
	int tp=inf.readInt();
	cout<<t<<' '<<tp<<endl;
	pair<string, string>pass[t+5];
	if(tp==1){
		
		for(int i=1;i<=t;i++){
			int n=inf.readLong();
			pass[i].first = inf.readToken();
		}
		for(int i=1;i<=t;i++){
			setTestCase(i);
			cout<<pass[i].first.length()<<endl;
			cout<<pass[i].first<<endl;
			int m=ouf.readInt(1,pass[i].first.length()*3/2);
			string s=ouf.readToken(format("[01]{%d}",m));
			for(int j=2;j<s.length();j++){
				if(s[j] == s[j - 1] and s[j] == s[j - 2]){
					quitf(_wa,"Encoded string contains three consecutive same bits.");
				}
			}
			pass[i].second = s;
		}
		ofstream next_pass(string(argv[3])+"/nextpass.in");
		next_pass<<t<<' '<<2<<endl;
		for(int i=1;i<=t;i++){
			next_pass<<pass[i].first<<' '<<pass[i].second<<endl;
		}
		return 42;
	}
	else{
		for(int i=1;i<=t;i++){
			pass[i].first = inf.readToken();
			pass[i].second = inf.readToken();
		}
		shuffle(pass+1,pass+t+1);
		for(int i=1;i<=t;i++){
			setTestCase(i);
			cout<<pass[i].second.size()<<endl;
			cout<<pass[i].second<<endl;
			int n=ouf.readInt(pass[i].first.length(),pass[i].first.length());
			string s=ouf.readToken(format("[01]{%d}",n));
			if(s != pass[i].first){
				quitf(_wa,"Recovery failed for %s --> %s", compress(pass[i].second).c_str(), compress(s).c_str());
			}
		}
	}
	quitf(_ok,"Successful Delivery!");
}
```