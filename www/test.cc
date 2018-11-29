#include <iostream>
#include <vector>
#include <list>
#include <map>
#include <iterator>
using namespace std;
int main(int argc, char const *argv[])
{
    list<int> int_list;

    int x = 23;

    int * p = &x;

    int_list.push_back(*p);
    std::copy(int_list.begin(), int_list.end(), std::ostream_iterator<int>(std::cout, " "));

    int_list.erase(*p);
    std::cout<<"p="<<p<<" *p="<<*p<<endl;

    return 0;
}
