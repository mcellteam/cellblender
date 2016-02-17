/* File : JSON.cpp */

#include <string>
#include <iostream>
#include <unordered_map>

using namespace std;

class json_element {
 public:
  const int JSON_VAL_UNDEF=-1;
  const int JSON_VAL_NULL=0;
  const int JSON_VAL_TRUE=1;
  const int JSON_VAL_FALSE=2;
  const int JSON_VAL_NUMBER=3;
  const int JSON_VAL_STRING=4;
  const int JSON_VAL_ARRAY=5;
  const int JSON_VAL_OBJECT=6;
  const int JSON_VAL_KEYVAL=7;
  int type  = JSON_VAL_UNDEF;
  int start = 0;
  int end   = 0;
  int depth = 0;
  json_element(int what, int start, int end, int depth) {
    this->type = what;
    this->start = start;
    this->end = end;
    this->depth = depth;
  }
  void update_element(int what, int start, int end, int depth) {
    this->type = what;
    this->start = start;
    this->end = end;
    this->depth = depth;
  }
  string get_name () {
    if (type == JSON_VAL_UNDEF) return ( "Undefined" );
    if (type == JSON_VAL_NULL) return ( "NULL" );
    if (type == JSON_VAL_TRUE) return ( "True" );
    if (type == JSON_VAL_FALSE) return ( "False" );
    if (type == JSON_VAL_NUMBER) return ( "Number" );
    if (type == JSON_VAL_STRING) return ( "String" );
    if (type == JSON_VAL_ARRAY) return ( "Array" );
    if (type == JSON_VAL_OBJECT) return ( "Object" );
    if (type == JSON_VAL_KEYVAL) return ( "Key:Val" );
    return ( "Unknown" );
  }
};



int main() {
  cout << "JSON C++ Parser" << endl;

  char *text = NULL;
  
  text = "{\"A\":true,\"mc\":[{\"a\":0.01},1e-5,2,true,[9,[0,3],\"a\",345],false,null,5,[1,2,3],\"xyz\"],\"x\":\"y\"}";

  json_element *je = new json_element(0,0,0,0);
  cout << "Hello!! " << je->JSON_VAL_ARRAY << endl;


  return ( 0 );
}


