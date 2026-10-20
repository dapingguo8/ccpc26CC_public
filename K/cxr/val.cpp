#include "testlib.h"
#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
int main(int argc,char* argv[]){
    registerValidation(argc,argv);
    int n=inf.readInt(1,1000000000,"n");
    inf.readSpace();
    int m=inf.readInt(1,500000,"m");
    inf.readSpace();
    int q=inf.readInt(1,500000,"q");
    inf.readEoln();
    for (int i=1;i<=m;++i){
        inf.readInt(0,1,"oi");
        inf.readSpace();
        inf.readInt(1,n,"xi");
        inf.readEoln();
    }
    for (int i=1;i<=q;++i){
        int l=inf.readInt(1,m,"lj");
        inf.readSpace();
        inf.readInt(l,m,"rj");
        inf.readEoln();
    }
    inf.readEof();
}
