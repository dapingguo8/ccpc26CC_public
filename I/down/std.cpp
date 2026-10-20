#include<bits/stdc++.h>
using namespace std;
int main(){
    int t,r;
    cin>>t>>r;
    while(t--){
        int n;
        cin>>n;
        string s;
        cin>>s;
        if(r==1){
            string s1,s2;
            int c=0;
            for(auto it:s) {
                if(it=='0'){
                    s1+='0'+c;
                    s2+='1'-c;
                    s2+='1'-c;
                } else {
                    s1+='0'+c;
                    s1+='0'+c;
                    s2+='1'-c;
                }
                c^=1;
            }
            cout<<min(s1.length(),s2.length())<<endl;
            if(s1.length()>s2.length()){
                cout<<s2<<endl;
            } else {
                cout<<s1<<endl;
            }
        }
        else{
            s+='2';
            string ans;
            for(int i=0;i<n;i++){
                if(s[i]!=s[i+1]){
                    ans+=s[0];
                }
                else {
                    ans+=('0'+'1'-s[0]);
                    i++;
                }
            }
            cout<<ans.length()<<endl;
            cout<<ans<<endl;
        }
    }
}