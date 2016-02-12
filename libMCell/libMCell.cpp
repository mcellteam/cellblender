/* File : libMCell.cpp */

#include "libMCell.h"

char *JSON_Element::get_json_name ( int type ) {
  if (type == JSON_VAL_UNDEF)  return ( "Undefined" );
  if (type == JSON_VAL_NULL)   return ( "Null" );
  if (type == JSON_VAL_TRUE)   return ( "True" );
  if (type == JSON_VAL_FALSE)  return ( "False" );
  if (type == JSON_VAL_NUMBER) return ( "Number" );
  if (type == JSON_VAL_STRING) return ( "String" );
  if (type == JSON_VAL_ARRAY)  return ( "Array" );
  if (type == JSON_VAL_OBJECT) return ( "Object" );
  if (type == JSON_VAL_KEYVAL) return ( "Key:Val" );
  return ( "Unknown" );
}







#define M_PI 3.14159265358979323846

/* Move the shape to a new location */
void Shape::move(double dx, double dy) {
  x += dx;
  y += dy;
}

int Shape::nshapes = 0;

double Circle::area() {
  return M_PI*radius*radius;
}

double Circle::perimeter() {
  return 2*M_PI*radius;
}

double Square::area() {
  return width*width;
}

double Square::perimeter() {
  return 4*width;
}


