/* File : libMCell.cpp */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <math.h>

#include <iostream>
#include <string>

#include <inttypes.h>

#include "rng.h"

double MCellRandomNumber::rng_gauss() {
  // printf ( "  rng_gauss() called from rng.cpp\n" );
  int n=16;
  double sum = 0.0;
  for (int i=0; i<n; i++) {
    sum += drand48();
  }
  return ( (sum - (n/2.0)) * 6 / n );  // The 6 should be 12, but 6 matches MCell
};

MCellRandomNumber_mrng::MCellRandomNumber_mrng ( uint32_t seed ) {
  uint32_t i;
  a = 0xf1ea5eed;
  b = c = d = seed;
  for (int i = 0; i < 20; ++i) {
    (void)generate();
  }
};

uint32_t MCellRandomNumber_mrng::generate() {
  uint32_t e;
  e = a - rot(b, 27);
  a = b ^ rot(c, 17);
  b = c + d;
  c = d + e;
  d = e + a;
  return d;
}


/* Simple Python testing:

# Should be able to run this from python to show rng_gauss distribution

import libMCell
r = libMCell.MCellRandomNumber()

cols = 200.0
bins = [ 0 for i in range(200) ]
for i in range(100000):
    bin = 100 + (10 * r.rng_gauss())
    bins[int(bin)] += 1

for i in range(200):
    s = ""
    if i == 100:
        s = s + '#'
    elif (i%10) == 0:
        s = s + "-"
    else:
        s = s + " "
    for j in range ( (int)(cols*bins[i]/bins[100]) ):
        s = s + "="
    print s

*/
