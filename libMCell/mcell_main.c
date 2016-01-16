#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "libMCell.h"

int main ( void ) {

  printf ( "Hello World from Main!!\n" );
  
  printf ( "My variable = %g\n", My_variable );
  printf ( "5 factorial = %d\n", fact(5) );
  printf ( "25 mod 7 = %d\n", my_mod(25,7) );
  printf ( "sin(1.234) = %g\n", my_sin(1.234) );
  printf ( "Time = %s\n", get_time() );

  return ( 0 );
}
