#include<bits/stdc++.h>
using namespace std;
string S;int N;
vector<int>V;
int solve(){
    V.clear();
    for(int i=0;i<N;i++){
        if(S[i]=='1'){
            int Num=1,now=i;
            while(now+2<N && S[now+1]=='0' && S[now+2]=='1'){
                Num++;now+=2;
            }V.push_back(Num);
            i=now;
        }
    }
    if(V[0]*2-1==N)return N;
    if(V.size()==1)return V[0]*2-1+(S[0]=='0')+(S.back()=='0');
    int ALL=0,Best=0;
    for(int x:V)ALL+=x,Best=max(Best,x);
    int Ans=max(ALL%2,Best*2-ALL);
    if(((V[0]-(Best-(ALL-Best-V[0]))>=Ans || V[0]==Best) && S[0]=='1')
     ||((V.back()-(Best-(ALL-Best-V.back()))>=Ans || V.back()==Best) && S.back()=='1'))
        return max(1,Ans*2);
    return Ans*2+1;
}
int main(){
    int T;cin>>T;
    while(T--){
        cin>>S;N=S.size();
        int all0=1;
        for(int i=0;i<N;i++)
            if(S[i]=='1')all0=0;
        if(all0){puts("1");continue;}
        int Ans=solve();
        printf("%d\n",Ans);
    }
}
