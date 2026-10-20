#include<bits/stdc++.h>
using namespace std;
#define ll long long
const int maxn=155,mod=1e9+7;
ll jc[maxn],ny[maxn];
ll ksm(ll sum,int num){
    ll ans=1;
    while(num){
        if(num&1)ans=ans*sum%mod;
        sum=sum*sum%mod;
        num>>=1;
    }return ans;
}
void init(){
    jc[0]=1;for(int i=1;i<maxn;i++)jc[i]=jc[i-1]*i%mod;
    for(int i=0;i<maxn;i++)ny[i]=ksm(jc[i],mod-2);
}
ll C(int x,int y){
    if(y>x || y<0)return 0;
    return jc[x]*ny[y]%mod*ny[x-y]%mod;
}
int A[maxn],n;
ll F[maxn][maxn];
bool isF[maxn][maxn];
ll dp[maxn][maxn][maxn];
bool isdp[maxn][maxn][maxn];
ll sumdp[maxn][maxn][maxn];
bool issumdp[maxn][maxn][maxn];
ll dfs(int L,int R,int T);
ll getSumdp(int L,int R,int T){
    T=min(T,R-L+1);
    if(issumdp[L][R][T])return sumdp[L][R][T];
    issumdp[L][R][T]=1;
    if(T==0)return sumdp[L][R][T]=dfs(L,R,0);
    return sumdp[L][R][T]=(getSumdp(L,R,T-1)+dfs(L,R,T))%mod;
}
ll dfs(int L,int R,int T){
    if(T>(R-L+1))return 0;
    if(L>R)return T==0;
    if(T<=0)return 0;
    if(isdp[L][R][T])return dp[L][R][T];
    isdp[L][R][T]=1;
    ll ans=0;
    for(int i=L;i<=R;i++){
        if(A[i]==-1 || A[i]==T){
            ll s1=0,s2=0,w1=0,w2=0;
            // for(int j=0;j<=T-1;j++)s1+=dfs(L,i-1,j);
            // for(int j=0;j<=T-1;j++)w1+=dfs(i+1,R,j);
            s1=getSumdp(L,i-1,T-1);
            w1=getSumdp(i+1,R,T-1);
            s2=dfs(L,i-1,T-1);
            w2=dfs(i+1,R,T-1);
            s1%=mod;w1%=mod;
            ll sum=s1*w2+s2*w1-s2*w2%mod+mod;sum%=mod;
            ans+=sum*C(R-L,i-L);
            ans%=mod;
        }
    }
    // cerr<<"dfs "<<L<<" "<<R<<" "<<T<<" "<<ans<<endl;
    return dp[L][R][T]=ans;
}
ll solve(int l,int r){
    if(l>r)return 1;
    if(l!=1 && r!=n){
        ll ans=getSumdp(l,r,r-l+1);
        // for(int i=1;i<=n;i++)ans+=dfs(l,r,i);
        return ans%mod;
    }
    if(isF[l][r])return F[l][r];
    isF[l][r]=1;
    ll ans=0;
    for(int i=l;i<=r;i++){
        if(A[i]==0 || A[i]==-1){
            ll sum=solve(l,i-1)*solve(i+1,r)%mod;
            ans+=sum*C(r-l,i-l);
            ans%=mod;
        }
    }
    // cerr<<"solve "<<l<<" "<<r<<" "<<ans<<endl;
    return F[l][r]=ans;
}
int main(){
    int T;cin>>T;
    init();
    while(T--){
        cin>>n;
        for(int i=1;i<=n;i++)cin>>A[i];
        ll ans=solve(1,n);
        cout<<ans<<endl;
        for(int i=1;i<=n;i++)
            for(int j=1;j<=n;j++)
                for(int k=0;k<=n;k++)
                    isdp[i][j][k]=isF[i][j]=issumdp[i][j][k]=0;
    }
}