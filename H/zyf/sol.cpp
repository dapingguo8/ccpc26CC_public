#include<bits/stdc++.h>
using namespace std;
const int mod=998244353;
const int iv3=(mod+1)/3;
const int maxn=1e6+10;
int n,k,a[maxn],s1,s2,s3,ans;
int main(){
    // freopen("zyf.in","r",stdin);
    // freopen("zyf.out","w",stdout);
    scanf("%d%d",&n,&k);
    for(int i=1;i<=k;i++) scanf("%d",&a[i]);
    for(int i=1;i<=k;i++){
        s3=(s3+1ll*a[i]*s2)%mod;
        s2=(s2+1ll*a[i]*s1)%mod;
        s1=(s1+a[i])%mod;
    }assert(s1==(n%mod));
    ans=(1ll*(1ll*n*n%mod-2+mod)%mod*s2-2ll*s2*s2+1ll*n*s3)%mod;
    ans=1ll*(ans+mod)*iv3%mod;
    printf("%d\n",ans);
    return 0;
}