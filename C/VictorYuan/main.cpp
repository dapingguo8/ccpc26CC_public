#include <iostream>
using namespace std;
const int M=2e5+10;
int T,n,k,ans;
int f[M],a[M];
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    cin>>T;
    while(T--)
    {
        cin>>n>>k; ans=0;
        for(int i=0;i<=n+1;++i) f[i]=a[i]=0;
        for(int i=1;i<=n;i++)
        {
            cin>>a[i]; a[i]--;
            if(a[i]<k) f[(a[i]-(i%k)+k)%k]++; 
        }
        for(int i=0;i<k;++i) ans=max(ans,f[i]);
        cout<<n-ans<<'\n';
    }
    return 0;
}
 