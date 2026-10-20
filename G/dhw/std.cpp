#include<iostream>
#include<cstdio>
#include<cstring>
using namespace std;
int T,n,m,tot,ans[200005],fir[200005],nxt[400005],to[400005];char a[200005],b[200005];
int ok,tim,dfn[200005],low[200005],fe[200005],sub[200005];
void ins(int x,int y)
{
	to[tot]=y;
	nxt[tot]=fir[x];
	fir[x]=tot++;
}
void tarjan(int fa,int now)
{
	dfn[now]=low[now]=++tim;
	for(int i=fir[now];i>=0;i=nxt[i])
	{
		int v=to[i],id=i/2;
		if(v==fa) continue;
		if(!dfn[v]) fe[v]=id,tarjan(now,v);
		else low[now]=min(low[now],dfn[v]);
	}
	if(fa<0){if(sub[now]) ok=0;}
	else
	{
		if(low[now]>dfn[fa]&&sub[now]) ans[fe[now]]=0;
		low[fa]=min(low[fa],low[now]);
		sub[fa]^=sub[now];
	}
}
int main()
{
	ios::sync_with_stdio(false);
	cin>>T;
	while(T--)
	{
		tot=tim=0;ok=1;
		memset(fir,-1,sizeof(fir));
		memset(fe,-1,sizeof(fe));
		memset(dfn,0,sizeof(dfn));
		memset(low,0,sizeof(low));
		cin>>n>>m;cin>>a;cin>>b;
		for(int i=1;i<=m;i++)
		{
			int l,r;
			cin>>l>>r;
			ins(l-1,r);ins(r,l-1);
		}
		int las=0;
		for(int i=0;i<n;i++)
		{
			int cur=(a[i]!=b[i]);
			sub[i]=las^cur;las=cur;
		}
		sub[n]=las;
		for(int i=0;i<m;i++) ans[i]=1;
		for(int i=0;i<=n;i++)
		{
			if(dfn[i]) continue;
			tarjan(-1,i);
		}
		if(!ok){for(int i=1;i<=m;i++) cout<<'0';cout<<'\n';}
		else{for(int i=0;i<m;i++) cout<<ans[i];cout<<'\n';}
	}
	return 0;
}
