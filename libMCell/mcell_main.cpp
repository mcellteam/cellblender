#include <iostream>
#include <string>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <math.h>

#include "libMCell.h"

using namespace std;

int main ( int argc, char *argv[] ) {
  cout << endl << "C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C" << endl;
  // Use a few C++ features
  string greeting = "Hello from C++!!\n";
  cout << greeting;
  
  cout << "JSON_VAL_NUMBER = " << JSON_VAL_NUMBER << " is a " << JSON_Element::get_json_name(JSON_VAL_NUMBER) << endl;

  JSON_List_Element *root = new JSON_List_Element;
  JSON_Element *child;

  child = new JSON_Number_Element(111);
  root->append_element ( child );

  child = new JSON_Number_Element(2.222);
  root->append_element ( child );

  child = new JSON_Element;
  root->append_element ( child );

  printf ( "Still need to free lots of stuff!!\n" );

  cout << endl << "C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C" << endl;
  return ( 0 );
}

