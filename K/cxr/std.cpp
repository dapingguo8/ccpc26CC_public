#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef pair<int,int> pr;
#define fr first
#define se second
#define mp make_pair
#define lowbit(x) (x&(-x))
const int N=5e5+5;
const int M=1<<20;
char buf[M],str[N*7];
char *p1=buf,*p2=buf;
int len;
inline char gc(){
    if (p1==p2 && (p2=(p1=buf)+fread(buf,1,M,stdin),p1==p2)) return EOF;
    return *p1++;
}
#define getchar() gc()
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
inline void write(int x){
    if (x>9) write(x/10);
    str[len++]=x%10+'0';
}
int n,m,q;
int o[N],x[N],lim[N],ans[N];
int sta[2][N],top[2],c[N];
pr a[N];
int head[N],cnt;
inline void ins(int l,int r){
    a[++cnt]=mp(l,head[r]);
    head[r]=cnt;
}
inline void add(int x,int k){
    for (int i=x;i<=m;i+=lowbit(i))
        c[i]+=k;
}
inline int sum(int x){
    int res=0;
    for (int i=x;i;i-=lowbit(i))
        res+=c[i];
    return res;
}
inline void init(){
    int l0=1,r0=0,l1=1,r1=0,l=1;
    for (int i=1;i<=m;++i){
        if (!o[i]){
            while (l0<=r0 && x[sta[0][r0]]<=x[i]) --r0;
            sta[0][++r0]=i;
        }else{
            while (l1<=r1 && x[sta[1][r1]]>=x[i]) --r1;
            sta[1][++r1]=i;
        }
        while (1){
            int u=(l0<=r0)?x[sta[0][l0]]:0;
            int v=(l1<=r1)?x[sta[1][l1]]:n+1;
            if (u<v-1) break;
            if (l0<=r0 && sta[0][l0]==l) ++l0;
            if (l1<=r1 && sta[1][l1]==l) ++l1;
            ++l;
        }
        lim[i]=l-1;
    }
}
int main(){
    n=read(),m=read(),q=read();
    for (int i=1;i<=m;++i)
        o[i]=read(),x[i]=read();
    init();
    for (int i=1;i<=q;++i){
        int l=read(),r=read();
        ins(l,r);
    }
    for (int i=1;i<=m;++i){
        int t=o[i];
        while (top[t] && (t?x[sta[t][top[t]]]>=x[i]:x[sta[t][top[t]]]<=x[i])){
            add(sta[t][top[t]],-1);
            --top[t];
        }
        sta[t][++top[t]]=i;
        add(i,1);
        for (int j=head[i];j;j=a[j].se)
            ans[j]=top[0]+top[1]-sum(max(a[j].fr,lim[i])-1);
    }
    for (int i=1;i<=q;++i){
        write(ans[i]);
        str[len++]='\n';
    }
    fwrite(str,1,len,stdout);
    return 0;
}
