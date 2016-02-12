/* File : libMCell.c */

#include <time.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "JSON.h"

int iterations = 0;
int mcell_set_iterations(int iters) {
  printf ( "  * ** *** libMCell.mcell_set_iterations called with %d\n", iters );
  iterations = iters;
  return ( iterations );
}

double time_step = 0;
double mcell_set_time_step(double dt) {
  printf ( "  * ** *** libMCell.mcell_set_time_step called with %g\n", dt );
  time_step = dt;
  return ( time_step );
}

