#include "testlib.h"
#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
const int N=2e4+5;
int cnt,sum;
int fa[N],q[N];
vector<int>g[N];
stack<int>s;
int main(int argc,char* argv[]){
    registerValidation(argc,argv);
    int n=inf.readInt(1,10000,"n");
    inf.readSpace();
    int m=inf.readInt(1,10000,"m");
    inf.readSpace();
    int w=inf.readInt(1,10000,"W");
    inf.readSpace();
    int h=inf.readInt(1,10000,"H");
    inf.readSpace();
    inf.readInt(2,1000,"K");
    inf.readEoln();
    assert(n*m<=10000);
    for (int i=1;i<=w+h;++i){
        fa[i]=inf.readInt(0,w,"fai");
        g[fa[i]].push_back(i);
        if (i!=w+h) inf.readSpace();
        else inf.readEoln();
    }
    for (int i=1;i<=w;++i){
        q[i]=inf.readInt(0,1000000000,"qi");
        if (i!=w) inf.readSpace();
        else inf.readEoln();
    }
    for (int i=1;i<=w;++i){
        assert(q[i]>=q[fa[i]]);
        assert(!g[i].empty());
    }
    s.push(0);
    while (!s.empty()){
        int x=s.top();
        s.pop();
        ++cnt;
        for (int i=0,sz=g[x].size();i<sz;++i)
            s.push(g[x][i]);
    }
    assert(cnt==w+h+1);
    for (int i=1;i<=h;++i){
        int l=inf.readInt(1,10000,"li");
        sum+=l;
        assert(sum<=10000);
        for (int j=1;j<=l;++j){
            inf.readSpace();
            inf.readInt(1,n,"dij");
            inf.readSpace();
            inf.readInt(1,m,"tij");
        }
        inf.readEoln();
    }
    inf.readEof();
}
