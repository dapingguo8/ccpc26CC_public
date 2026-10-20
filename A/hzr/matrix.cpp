#include<bits/stdc++.h>
#define ll long long
using namespace std;
const int maxn=1000010;
vector<ll>V[maxn],Num[maxn];
int n,m;
ll solve(){
    ll Ans=0;
    for(int i=1;i<=n;i++){
        for(int j=1;j<=m;j++){
            ll nowNum=Num[i][j]+V[i][j-1];
            ll Need=V[i][j];
            if(Need>nowNum){
                Ans+=Need-nowNum;
                nowNum=0;
            }else nowNum-=Need;
            if(i<n)Num[i+1][j]=nowNum;
        }
    }
    return Ans;
}
int main(){
    cin>>n>>m;
    for(int i=1;i<=n;i++){
        V[i].resize(m+2);
        Num[i].resize(m+2);
        for(int j=1;j<=m;j++){
            int x;
            scanf("%d",&x);
            V[i][j]=x;
        }
    }
    ll Ans=solve();
    cout<<Ans<<endl;
}