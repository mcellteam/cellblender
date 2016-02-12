#ifndef LIBMCELL_H
#define LIBMCELL_H

#include <stdlib.h>
#include <string.h>

/* File : libMCell.h */

#define JSON_VAL_UNDEF -1
#define JSON_VAL_NULL   0
#define JSON_VAL_TRUE   1
#define JSON_VAL_FALSE  2
#define JSON_VAL_NUMBER 3
#define JSON_VAL_STRING 4
#define JSON_VAL_ARRAY  5
#define JSON_VAL_OBJECT 6
#define JSON_VAL_KEYVAL 7


class JSON_Element {
 public:
  int type;            // This tells what's in this block
  char *name;          // This is the key value when the type is in a dictionary
  int start;           // Index of first char in this element
  int end;             // Index of first char NOT in this element
 public:   // Would like protected
  JSON_Element() {     // Constructor for all new JSON_Elements
    type = JSON_VAL_UNDEF;
    name = NULL;
    start = -1;
    end = -1;
  };

 public:
  static char *get_json_name ( int type );
  static JSON_Element *build_test_case ( int case_num );
};


class JSON_List_Element : public JSON_Element {
 public:
  JSON_Element **subs; // Contains the array or object (dictionary) with last NULL
  JSON_List_Element() {
    type = JSON_VAL_ARRAY;
    subs = NULL;
  };
  int count_subs();
  int append_element ( JSON_Element *je );
};


class JSON_Number_Element : public JSON_Element {
 public:
  int int_val=0;
  double double_val=0;
  JSON_Number_Element() : JSON_Element() {
    type = JSON_VAL_NUMBER;
  };
  JSON_Number_Element( int v ) : JSON_Number_Element() {
    int_val = v;
  };
  JSON_Number_Element( double v ) : JSON_Number_Element() {
    double_val = v;
  };
};






class Shape {
public:
  Shape() {
    nshapes++;
  }
  virtual ~Shape() {
    nshapes--;
  }
  double  x, y;
  void    move(double dx, double dy);
  virtual double area() = 0;
  virtual double perimeter() = 0;
  static  int nshapes;
};

class Circle : public Shape {
private:
  double radius;
public:
  Circle(double r) : radius(r) { }
  virtual double area();
  virtual double perimeter();
};

class Square : public Shape {
private:
  double width;
public:
  Square(double w) : width(w) { }
  virtual double area();
  virtual double perimeter();
};


#endif

