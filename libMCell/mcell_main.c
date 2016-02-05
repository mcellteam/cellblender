#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "JSON.h"

#include "libMCell.h"

int main ( void ) {

  printf ( "Hello World from Main!!\n" );
  
  /*
  printf ( "My variable = %g\n", My_variable );
  printf ( "5 factorial = %d\n", fact(5) );
  printf ( "25 mod 7 = %d\n", my_mod(25,7) );
  printf ( "sin(1.234) = %g\n", my_sin(1.234) );
  printf ( "Time = %s\n", get_time() );
  */
  

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
  
  // ##### Read in the data model itself

  data_model_element *dm; // Data Model Tree
  dm = parse_json_text ( file_text );

  dump_json_tree ( dm, 80, 0 );
  

  data_model_element *mcell = json_get_element_with_key ( dm, "mcell" );

  // API version = ['mcell']['api_version']
  data_model_element *api_ver = json_get_element_with_key ( mcell, "api_version" );

  printf ( "API int version = %d\n", json_get_int_value ( api_ver ) );

  // iterations = ['mcell']['initialization']['iterations']
  data_model_element *dm_init = json_get_element_with_key ( mcell, "initialization" );
  data_model_element *dm_iters = json_get_element_with_key ( dm_init, "iterations" );
  data_model_element *dm_time_step = json_get_element_with_key ( dm_init, "time_step" );
  
  char *str_val;

  int iters;
  str_val = json_get_string_value ( dm_iters );
  sscanf ( str_val, " %ld", &iters );
  mcell_set_iterations ( iters );

  double time_step;
  str_val = json_get_string_value ( dm_time_step );
  sscanf ( str_val, " %lg", &time_step );
  mcell_set_time_step ( time_step );

  data_model_element *reaction_data_output = json_get_element_with_key ( mcell, "reaction_data_output" );
  data_model_element *plot_layout = json_get_element_with_key ( reaction_data_output, "plot_layout" );

  printf ( "Plot Layout = \"%s\"\n", json_get_string_value ( plot_layout ) );

  free_json_tree ( dm );
  free ( file_text );

  return ( 0 );
}
