#include<bits/stdc++.h>
using namespace std;
const int maxn=1000005;
int n,m;
vector<int>a[maxn]; 
long long ans;
int main(){
	ios::sync_with_stdio(false);
	cin>>n>>m;
	for(int i=1;i<=n;i++){
		a[i].resize(m+1); 
		for(int j=1;j<=m;j++)
			cin>>a[i][j],ans+=a[i][j];
	}
	for(int j=1;j<m;j++){
		long long res=0,totl=0;
		for(int i=1;i<=n;i++){
			totl+=a[i][j];
			long long c=min(totl,0ll+a[i][j+1]);
			res+=c,totl-=c;
		}
		ans-=res;
	}
	printf("%lld\n",ans);
	return 0;
}
