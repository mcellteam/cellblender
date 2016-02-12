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

  printf ( "Still need to free lots of stuff!!\n" );

  cout << endl << "C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C ++++++++++++ C" << endl;
  return ( 0 );
}

