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

  JSON_List_Element *root, *rootsub1;
  JSON_Element *child, *grandchild;

  root = new JSON_List_Element;

  child = new JSON_Number_Element(111);
  root->append_element ( child );

  child = new JSON_Number_Element(2.222);
  root->append_element ( child );

  child = new JSON_Element;
  root->append_element ( child );

  rootsub1 = new JSON_List_Element;

  grandchild = new JSON_Number_Element(0.1);
  rootsub1->append_element ( grandchild );

  grandchild = new JSON_Number_Element(0.2);
  rootsub1->append_element ( grandchild );

  grandchild = new JSON_Number_Element(0.3);
  rootsub1->append_element ( grandchild );

  root->append_element ( rootsub1 );

  child = new JSON_Number_Element(99);
  root->append_element ( child );

  cout << "List = " << root->to_string() << endl;

  printf ( "Still need to free lots of stuff!!\n" );

  cout << endl << "C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C" << endl;
  return ( 0 );
}

