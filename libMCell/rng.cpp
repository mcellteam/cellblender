/* File : libMCell.cpp */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <math.h>

#include <iostream>
#include <string>

#include "rng.h"

double MCellRandomNumber::rng_gauss() {
  printf ( "  rng_gauss() called from rng.cpp\n" );
  return ( (drand48() + drand48() + drand48()) -1.5 );
};


