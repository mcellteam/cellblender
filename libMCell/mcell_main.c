#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "libMCell.h"

#include "JSON.h"

int main ( void ) {

  printf ( "Hello World from Main!!\n" );
  
  printf ( "My variable = %g\n", My_variable );
  printf ( "5 factorial = %d\n", fact(5) );
  printf ( "25 mod 7 = %d\n", my_mod(25,7) );
  printf ( "sin(1.234) = %g\n", my_sin(1.234) );
  printf ( "Time = %s\n", get_time() );
  

  char *file_name = "dm.json";

  printf ( "JSON Parsing of \"%s\":\n", file_name );

  FILE *f = fopen ( file_name, "r" );

  long file_length;
  fseek (f, 0L, SEEK_END);
  file_length = ftell(f);

  char *file_text = (char *) malloc ( file_length + 2 );

  fseek (f, 0L, SEEK_SET);
  fread ( file_text, 1, file_length, f );

  fclose(f);

  file_text[file_length] = '\0'; // Be sure to null terminate!!
  
  json_element *json_tree;
  json_tree = parse_json_text ( file_text );
  
  dump_json_tree ( json_tree, 80, 0 );
  
  free_json_tree ( json_tree );
  free ( file_text );

  

  return ( 0 );
}
