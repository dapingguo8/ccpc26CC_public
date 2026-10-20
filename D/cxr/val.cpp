#include "testlib.h"
#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll V=1ll<<40;
int main(int argc,char* argv[]){
    registerValidation(argc,argv);
    ll a=inf.readLong(0,V,"a");
    inf.readSpace();
    ll b=inf.readLong(0,V,"b");
    inf.readSpace();
    ll c=inf.readLong(0,V,"c");
    inf.readEoln();
    assert(a<b && b<c);
    int q=inf.readInt(1,1000,"q");
    inf.readEoln();
    for (int i=1;i<=q;++i){
        inf.readLong(0,V,"t");
        inf.readEoln();
    }
    inf.readEof();
}
