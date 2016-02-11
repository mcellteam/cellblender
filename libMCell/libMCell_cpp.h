// libMCell_cpp.h

class MolInstance;


class MolSpecies {
 public:
  char *name;
  char *type;
  char type_code;
  double diffusion_const;
  MolInstance *instance_list;
  int num_instances;
  MolSpecies *next;
};


class ReleaseSite {
 public:
  MolSpecies *molecule_species;
  double loc_x;
  double loc_y;
  double loc_z;
  double quantity;
  ReleaseSite *next;
};


class MolInstance {
 public:
  MolSpecies *molecule_species;
  double x;
  double y;
  double z;
  MolInstance *next;
};

#include "JSON.h"


typedef json_element data_model_element;

int mcell_set_iterations(int iters);
double mcell_set_time_step(double dt);

/*
class Shape {
 public:
  int x,y;
  Shape() : x(0), y(0) { }
  virtual void   setPosition(int nx, int ny);
  virtual void   move(int dx, int dy);
  virtual double area(void) = 0;
  virtual double perimeter(void) = 0;
};

class Rectangle : public Shape {
 public:
  int width;
  int height;
  Rectangle(int width, int height) : width(width), height(height) { }
  virtual double area(void);
  virtual double perimeter(void);
};

class Circle : public Shape {
 public:
  int radius;
  Circle(int radius) : radius(radius) { }
  virtual double area(void);
  virtual double perimeter(void);
};

// Some overloaded functions

extern void foo(int x);
extern void foo(double x);
extern void foo(char *s);

// A namespace

namespace Spam {
  class Point {
  public:
    int x, y;
    Point(int x, int y) : x(x), y(y) { }
  };
  extern void PointDebug(Point *p);
};

// A simple template definition

template<class T> class Coord {
 public:
  T x, y;
  Coord(T x, T y) : x(x), y(y) { }
  void move(T dx, T dy) {
    x += dx;
    y += dy;
  }
};

// Some debugging functions for coords

extern void CoordDebug(Coord<int> *c);
extern void CoordDebug(Coord<double> *c);

*/






  
