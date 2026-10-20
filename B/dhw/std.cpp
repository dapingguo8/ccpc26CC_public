#include<iostream>
#include<cstdio>
#include<cstring>
#include<vector>
#include<algorithm>
#include<queue>
using namespace std;
typedef long long ll;
int n,m,N,H,K,tot=0,fa[20005],l[10005],q[10005];vector<int> id[10005];
struct edge{int u,v,cap,flow,del;};vector<edge> E;vector<int> G[30050];
int pre[30050];ll dis[30050],h[30050];
struct pt{int id;ll d;pt(int x=0,ll y=0){id=x;d=y;}};
bool operator <(const pt &a1,const pt &a2){return a1.d>a2.d;}
void ins(int u,int v,int cap,int del)
{
	int m=E.size();
	E.push_back({u,v,cap,0,del});
	G[u].push_back(2*m);G[v].push_back(2*m+1);
}
pair<int,ll> sol(int s,int t)
{
	int num=N+H+n*m+3,mxf=0;ll cost=0;
	while(mxf<K)
	{
		memset(dis,127,sizeof(dis));
		memset(pre,-1,sizeof(pre));
		priority_queue<pt> q;
		dis[s]=0;q.push({s,0});
		while(!q.empty())
		{
			pt tmp=q.top();int now=tmp.id;ll d=tmp.d;q.pop();
			if(d!=dis[now]) continue;
			if(now==t) break;
			for(int cur:G[now])
			{
				const edge &dq=E[cur/2];int back=cur%2;
				if((back&&dq.flow==0)||(!back&&dq.flow==dq.cap)) continue;
				int to=dq.u+dq.v-now;ll c=(!back?1ll*dq.del*dq.flow:-1ll*dq.del*(dq.flow-1));
				ll nd=d+c+h[now]-h[to];
				if(nd<dis[to])
				{
					dis[to]=nd;pre[to]=cur;
					q.push({to,nd});
				}
			}
		}
		if(dis[t]>(1ll<<60)) break;
		for(int i=0;i<num;i++) h[i]+=min(dis[i],dis[t]);
		for(int now=t;now!=s;)
		{
			int cur=pre[now];edge &dq=E[cur/2];
			if(cur%2==0){cost+=1ll*dq.del*dq.flow;dq.flow++;now=dq.u;}
			else{cost-=1ll*dq.del*(dq.flow-1);dq.flow--;now=dq.v;}
		}
		mxf++;
	}
	return make_pair(mxf,cost);
}
int main()
{
	scanf("%d%d%d%d%d",&n,&m,&N,&H,&K);
	for(int i=1;i<=N+H;i++) scanf("%d",&fa[i]);
	for(int i=1;i<=N;i++) scanf("%d",&q[i]);
	for(int i=1;i<=H;i++)
	{
		scanf("%d",&l[i]);
		for(int j=0;j<l[i];j++)
		{
			int d,t;scanf("%d%d",&d,&t);
			id[i].push_back((d-1)*m+t);
		}
	}
	int s=N+H+n*m+1,t=s+1;ins(s,0,K,0);
	for(int i=1;i<=N;i++) ins(fa[i],i,K,q[i]-q[fa[i]]);
	for(int i=N+1;i<=N+H;i++) ins(fa[i],i,1,0);
	for(int i=1;i<=H;i++)
		for(int j=0;j<l[i];j++)
			ins(N+i,N+H+id[i][j],1,0);
	for(int i=1;i<=n*m;i++) ins(N+H+i,t,1,0);
	pair<int,ll> res=sol(s,t);
	if(res.first<K) printf("-1");else printf("%lld",res.second);
	return 0;
}