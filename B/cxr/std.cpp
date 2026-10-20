#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef pair<ll,int> pr;
#define fr first
#define se second
#define mp make_pair
inline int read(){
    int x=0,w=1;
    char ch=0;
    while (ch>'9' || ch<'0'){
        if (ch=='-') w=-1;
        ch=getchar();
    }
    while (ch<='9' && ch>='0'){
        x=(x<<1)+(x<<3)+ch-'0';
        ch=getchar();
    }
    return x*w;
}
const int N=3e4+5;
const int M=8e4+5;
const ll inf=1e18;
int n,m,w,h,k,S,T;
int fa[N],val[N],pre[N];
ll dis[N],f[N],ans;
struct edge{
    int next,to,w,d;
    ll c;
}a[M];
int head[N],cnt=1;
inline void addedge(int u,int v,int w,int d,ll c){
    a[++cnt].to=v;
    a[cnt].next=head[u];
    head[u]=cnt;
    a[cnt].w=w;
    a[cnt].d=d;
    a[cnt].c=c;
}
inline void add(int u,int v,int w,int d){
    addedge(u,v,w,d,0);
    addedge(v,u,0,d,d);
}
priority_queue<pr,vector<pr>,greater<pr>>q;
inline bool dij(){
    q=priority_queue<pr,vector<pr>,greater<pr>>();
    for (int i=0;i<=T;++i) dis[i]=inf;
    dis[S]=0;
    q.push(mp(0,S));
    while (!q.empty()){
        int x=q.top().se;
        ll d=q.top().fr;
        q.pop();
        if (d!=dis[x]) continue;
        for (int i=head[x];i;i=a[i].next){
            if (!a[i].w) continue;
            int y=a[i].to;
            ll now=d+a[i].c+f[x]-f[y];
            if (dis[y]>now){
                dis[y]=now,pre[y]=i;
                q.push(mp(now,y));
            }
        }
    }
    if (dis[T]==inf) return 0;
    for (int i=0;i<=T;++i)
        if (dis[i]!=inf) f[i]+=dis[i];
    return 1;
}
int main(){
    n=read(),m=read(),w=read(),h=read(),k=read();
    S=w+h+n*m+1,T=S+1;
    for (int i=1;i<=w+h;++i) fa[i]=read();
    for (int i=1;i<=w;++i) val[i]=read();
    add(S,0,k,0);
    for (int i=1;i<=w+h;++i){
        if (i<=w) add(fa[i],i,k,val[i]-val[fa[i]]);
        else add(fa[i],i,1,0);
    }
    for (int i=1;i<=h;++i){
        int l=read();
        while (l--){
            int d=read(),t=read();
            add(w+i,w+h+(d-1)*m+t,1,0);
        }
    }
    for (int i=1;i<=n*m;++i)
        add(w+h+i,T,1,0);
    for (int j=1;j<=k;++j){
        if (!dij()) return puts("-1"),0;
        for (int x=T;x!=S;x=a[pre[x]^1].to){
            int i=pre[x];
            ans+=a[i].c;
            --a[i].w,++a[i^1].w;
            a[i].c+=a[i].d,a[i^1].c-=a[i].d;
        }
    }
    printf("%lld\n",ans);
    return 0;
}
