#include<bits/stdc++.h>
using namespace std;
const int maxn=200005;
int T,n,m,dfns,flg;
int dfn[maxn],low[maxn],c[maxn],xx[maxn],yy[maxn],cut[maxn],ok[maxn],xr[maxn];
vector<int>v[maxn];
string a,b;
void tarjan(int x,int fa){
    dfn[x]=low[x]=++dfns,xr[x]=c[x];
    for(int i=0;i<v[x].size();i++){
        int k=v[x][i],y=xx[k]+yy[k]-x;
        if(dfn[y]==0){
        	tarjan(y,k),xr[x]^=xr[y],low[x]=min(low[x],low[y]);
        	if(low[y]>dfn[x])
        		cut[k]=1,ok[k]=xr[y];
        }
        else if(k!=fa)
			low[x]=min(low[x],dfn[y]);
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
        for(int i=0;i<=n;i++)
            if(dfn[i]==0){
				tarjan(i,-1);
                if(xr[i])
                	flg=1;
            }
        for(int i=1;i<=m;i++)
        	cout<<(flg==0&&(cut[i]==0||ok[i]==0)? '1':'0');
        cout<<'\n';
        dfns=flg=0;
        for(int i=0;i<=n;i++)
            dfn[i]=xr[i]=0,v[i].clear();
        for(int i=1;i<=m;i++)
        	cut[i]=ok[i]=0;
    }
    return 0;
}
