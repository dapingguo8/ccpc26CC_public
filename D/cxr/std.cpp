#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 lll;
inline ll read(){
    ll x=0,w=1;
    int ch=0;
    while (ch>'9' || ch<'0'){
        if (ch=='-') w=-1;
        ch=getchar();
        if (ch==EOF) exit(0);
    }
    while (ch<='9' && ch>='0'){
        x=(x<<1)+(x<<3)+ch-'0';
        ch=getchar();
    }
    return x*w;
}
const int N=10;
int n;
ll val[3],d,p,q,inv;
lll c[3];
struct node{
    ll v;
    lll c[3],cnt;
}a[N],b[N],s[2];
ll exgcd(ll a,ll b,ll &x,ll &y){
    if (!b){
        x=1,y=0;
        return a;
    }
    ll d=exgcd(b,a%b,y,x);
    y-=a/b*x;
    return d;
}
inline int calc(ll t){
    if (t<val[0] || t>val[2]) return -1;
    lll lim=1;
    for (int k=0;k<=80;++k){
        lll m=lim*(t-val[0]);
        if (m%d==0){
            m/=d;
            c[1]=(m%q)*inv%q;
            if (m>=c[1]*p){
                c[2]=(m-c[1]*p)/q;
                c[0]=lim-c[1]-c[2];
                if (c[0]>=0) return k;
            }
        }
        lim<<=1;
    }
    return -1;
}
inline void solve(int k){
    int cnt=0;
    for (int i=0;i<3;++i){
        if (!c[i]) continue;
        a[++cnt].v=val[i],a[cnt].cnt=c[i];
        for (int j=0;j<3;++j) a[cnt].c[j]=(i==j);
    }
    for (int r=1;r<k;++r){
        int tot=0,vis[2]={0,0};
        for (int i=1;i<=cnt;++i){
            if (a[i].cnt>1){
                b[++tot]=a[i];
                b[tot].cnt>>=1;
                for (int j=0;j<3;++j) b[tot].c[j]<<=1;
            }
            if (a[i].cnt&1){
                int t=a[i].v&1;
                if (!vis[t]) s[t]=a[i],vis[t]=1;
                else{
                    b[++tot].v=(a[i].v+s[t].v)/2;
                    b[tot].cnt=1;
                    for (int j=0;j<3;++j)
                        b[tot].c[j]=a[i].c[j]+s[t].c[j];
                    vis[t]=0;
                }
            }
        }
        cnt=tot;
        for (int i=1;i<=cnt;++i) a[i]=b[i];
    }
}
int main(){
    for (int i=0;i<3;++i) val[i]=read();
    n=read();
    ll x,y;
    d=exgcd(val[1]-val[0],val[2]-val[0],x,y);
    p=(val[1]-val[0])/d,q=(val[2]-val[0])/d;
    inv=(x%q+q)%q;
    while (n--){
        ll t=read();
        int k=calc(t);
        printf("%d\n",k);
        fflush(stdout);
        for (int j=k;j>=1;--j){
            solve(j);
            ll u=a[1].v,v=2*t-u;
            printf("%lld %lld\n",u,v);
            fflush(stdout);
            if (j>1){
                ll t0=read();
                if (t0!=u && t0!=v) return 0;
                for (int i=0;i<3;++i){
                    if (t0==u) c[i]=a[1].c[i];
                    else c[i]-=a[1].c[i];
                }
                t=t0;
            }
        }
    }
    return 0;
}
