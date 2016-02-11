#include "libMCell_cpp.h"
#include <stdio.h>
#include <math.h>

/*
void Shape::setPosition(int nx, int ny) {
  x = nx;
  y = ny;
}

void Shape::move(int dx, int dy) {
  x += dx;
  y += dy;
}

double Rectangle::area(void) {
  return width*height;
}

double Rectangle::perimeter(void) {
  return 2*width+2*height;
}

double Circle::area(void) {
  return M_PI*radius*radius;
}

double Circle::perimeter(void) {
  return 2*M_PI*radius;
}

void foo(int x) {
  printf("Called foo(int) : %d\n", x);
}

void foo(double x) {
  printf("Called foo(double) : %f\n", x);
}

void foo(char *s) {
  printf("Called foo(char *) : %s\n", s);
}

namespace Spam {
  void PointDebug(Point *p) {
    printf("Spam::Point(%d,%d)\n", p->x, p->y);
  }
};

void CoordDebug(Coord<int> *c) {
  printf("Coord<int>(%d,%d)\n",c->x, c->y);
}

void CoordDebug(Coord<double> *c) {
  printf("Coord<int>(%f,%f)\n",c->x, c->y);
}
*/


int mcell_iterations = 0;
int mcell_set_iterations(int iters) {
  printf ( "  * ** *** libMCell.mcell_set_mcell_iterations called with %d\n", iters );
  mcell_iterations = iters;
  return ( mcell_iterations );
}

double mcell_time_step = 0;
double mcell_set_time_step(double dt) {
  printf ( "  * ** *** libMCell.mcell_set_mcell_time_step called with %g\n", dt );
  mcell_time_step = dt;
  return ( mcell_time_step );
}

