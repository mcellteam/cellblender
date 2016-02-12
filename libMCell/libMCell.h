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
  int type;              // This tells what's in this block
  char *name;            // This is the key value when the type is in a dictionary
  int start;             // Index of first char in this element
  int end;               // Index of first char NOT in this element
  JSON_Element **subs; // Contains the array or object (dictionary) with last NULL

  static char *get_json_name ( int type );
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
