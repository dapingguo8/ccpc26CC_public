#include"testlib.h"
using namespace std;
#define int long long
int np[1005];
string _compress(string s){
	if(s.length()<=10)return s;
	return s.substr(0,5) + "..." + s.substr(s.length()-5, 5);
}
signed main(signed argc, char ** argv){
	ios::sync_with_stdio(0);
	cin.tie(0);
	registerInteraction(argc,argv);
	int t=inf.readInt();
	int tp=inf.readInt();
	cout<<t<<' '<<tp<<endl;
	pair<string, string>pass[t+5];
	if(tp==1){
		
		for(int i=1;i<=t;i++){
			int n=inf.readLong();
			pass[i].first = inf.readToken();
		}
		for(int i=1;i<=t;i++){
			setTestCase(i);
			cout<<pass[i].first.length()<<endl;
			cout<<pass[i].first<<endl;
			int m=ouf.readInt(1,pass[i].first.length()*3/2);
			string s=ouf.readToken();
			if(s.length() != m) quitf(_wa,"Incorrect string length.");
  			for(auto it:s){
  				if(it!='0' and it!='1'){
  					quitf(_wa,"Encoded string contains invalid character.");
  				}
  			}
			for(int j=2;j<s.length();j++){
				if(s[j] == s[j - 1] and s[j] == s[j - 2]){
					quitf(_wa,"Encoded string contains three consecutive same bits.");
				}
			}
			pass[i].second = s;
		}
		tout<<t<<' '<<2<<endl;
		for(int i=1;i<=t;i++){
			tout<<pass[i].first<<' '<<pass[i].second<<endl;
		}
		quitf(_ok,"First stage ended.");
	}
	else{
		for(int i=1;i<=t;i++){
			pass[i].first = inf.readToken();
			pass[i].second = inf.readToken();
		}
		shuffle(pass+1,pass+t+1);
		for(int i=1;i<=t;i++){
			setTestCase(i);
			cout<<pass[i].second.size()<<endl;
			cout<<pass[i].second<<endl;
			int n=ouf.readInt(pass[i].first.length(),pass[i].first.length());
			string s=ouf.readToken();
			if(s != pass[i].first){
				quitf(_wa,"Recovery failed for %s --> %s", _compress(pass[i].second).c_str(), _compress(s).c_str());
			}
		}
	}
	quitf(_ok,"Successful Delivery!");
}