/* File : libMCell.c */

#include <time.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "JSON.h"

double My_variable = 3.0;

int fact(int n) {
  if (n <= 1) return 1;
  else return n*fact(n-1);
}

int my_mod(int x, int y) {
  return (x%y);
}

double my_sin(double x) {
  return (sin(x));
}

char *get_time()
{
  time_t ltime;
  time(&ltime);
  return ctime(&ltime);
}

