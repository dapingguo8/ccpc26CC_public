#include<bits/stdc++.h>
using namespace std;
const int mod=998244353,inv3=(mod+1)/3;
int n,m,e1,e2,e3,ans;
int main(){
	ios::sync_with_stdio(false);
	cin>>n>>m;
	for(int i=1,x;i<=m;i++)
		cin>>x,e3=(e3+1ll*e2*x)%mod,e2=(e2+1ll*e1*x)%mod,e1=(e1+x)%mod;
	ans=1ll*(1ll*(1ll*n*n-2+mod)%mod*e2+2ll*(mod-e2)*e2+1ll*n*e3)%mod*inv3%mod;
	cout<<ans<<'\n';
	return 0;
}
