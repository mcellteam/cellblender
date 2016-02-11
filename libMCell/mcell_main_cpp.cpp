#include "libMCell_cpp.h"
#include <stdio.h>
#include <math.h>

int main ( int argc, char *argv[] ) {
  printf ( "Hello World!!\n" );
  Circle c = Circle(2);
  printf ( "Area = %g\n", c.area() );
}
