#include<bits/stdc++.h>
using namespace std;
const int maxn=200005;
int T,n,m,stp,ban,xr,flg;
int c[maxn],xx[maxn],yy[maxn],vis[maxn];
string a,b;
vector<int>v[maxn];
void dfs(int x){
	if(vis[x]==stp)
		return ;
	xr^=c[x],vis[x]=stp;
	for(int i=0;i<v[x].size();i++){
		int k=v[x][i],y=xx[k]+yy[k]-x;
		if(vis[y]!=stp&&k!=ban)
			dfs(y);
	}
}
int main(){
    ios::sync_with_stdio(false);
    cin>>T;
    while(T--){
        cin>>n>>m>>a>>b;
        c[0]=0;
        for(int i=0;i<n;i++)
        	c[i+1]=(a[i]-'0')^(b[i]-'0');
        for(int i=0;i<n;i++)
        	c[i]^=c[i+1];
        for(int i=1,x,y;i<=m;i++)
            cin>>x>>y,x--,v[x].push_back(i),v[y].push_back(i),xx[i]=x,yy[i]=y;
        for(int i=1;i<=m;i++){
        	ban=i,stp++;
        	flg=0;
        	for(int i=0;i<=n&&flg==0;i++)
        		if(vis[i]!=stp){
        			xr=0;
        			dfs(i);
        			if(xr)
        				flg=1;
        		}
        	cout<<1-flg;
        }
        cout<<'\n';
        for(int i=0;i<=n;i++)
            v[i].clear();
    }
    return 0;
}
