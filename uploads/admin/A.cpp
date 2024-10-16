#include<bits/stdc++.h>
using namespace std;
const int INF = 1e9;
int main(){
    mt19937 rand(time(0));
    int n;cin>>n;
    int friends[n][3];
    for(int i=0;i<n;i++)
        for(int j=0;j<3;j++)
            cin>>friends[i][j],
            friends[i][j]--;
    int arr[n],index[n];
    for(int i=0;i<n;i++)
        arr[i]=i;
    int ans = INF;
    int T = 10000000;
    while(T--){
        int a = rand()%n;
        int b = rand()%n;
        while(a==b)
            b = rand()%n;
        swap(arr[a],arr[b]);
        int sum = 0;
        for(int i=0;i<n;i++)
            index[arr[i]]=i;
        for(int i=0;i<n;i++)
            for(int j=0;j<3;j++)
                sum+=abs(index[friends[arr[i]][j]]-i);
        if(sum<ans){
            ans = sum;
        }else{
            swap(arr[a],arr[b]);
        }
    }
    cout << ans/2;
}