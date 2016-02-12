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


int JSON_List_Element::count_subs() {
  if ( (this->type != JSON_VAL_ARRAY) && (this->type != JSON_VAL_OBJECT) ) {
    return ( -1 );
  }
  if (this->subs == NULL) {
    return ( 0 );
  }
  int l = 0;
  while (this->subs[l] != NULL) {
    l += 1;
  }
  return ( l );
}


int JSON_List_Element::append_element ( JSON_Element *je ) {
  if ( (this->type != JSON_VAL_ARRAY) && (this->type != JSON_VAL_OBJECT) ) {
    return ( -1 );
  }
  int original_count = this->count_subs();
  // Reallocate the sub-element list with room for one more item AND room for the terminating null!!
  JSON_Element **new_subs = (JSON_Element **) malloc ( (original_count + 1 + 1) * sizeof(JSON_Element *) );
  int num_copied = 0;
  // Copy the old values
  while (num_copied < original_count) {
    new_subs[num_copied] = this->subs[num_copied];
    num_copied += 1;
  }
  new_subs[num_copied] = je;
  num_copied += 1;
  new_subs[num_copied] = NULL;
  free ( this->subs );
  this->subs = new_subs;
  return ( 0 );
}



JSON_Element *JSON_Element::build_test_case ( int case_num ) {
  JSON_Element *je = new JSON_Element;

/*
json_element *build_test_tree ()
{
  json_element *root, *tmp_object, *tmp_array_1, *tmp_array_2;

  root = new_empty_json_object( "TOP" );
  add_item_to_json_collection ( new_json_number ( "k1", "99" ), root );
  add_item_to_json_collection ( new_json_number ( "k2", "55" ), root );

  add_item_to_json_collection ( new_json_null( "k3" ), root );
    tmp_object = new_empty_json_object( "Object_1" );
    add_item_to_json_collection ( tmp_object, root );
    add_item_to_json_collection ( new_json_string( "1st_name", "Bill"), tmp_object );
    add_item_to_json_collection ( new_json_string("2nd_name", "Beth"), tmp_object );
  add_item_to_json_collection ( new_json_true("k5"), root );
  add_item_to_json_collection ( new_json_false("k6"), root );
  add_item_to_json_collection ( new_json_number("k7","987.321"), root );
  add_item_to_json_collection ( new_json_number("k8","123.456"), root );
    tmp_array_1 = new_empty_json_array( "Array_1" );
    add_item_to_json_collection ( tmp_array_1, root );
    add_item_to_json_collection ( new_json_string(NULL,"B1"), tmp_array_1 );
    add_item_to_json_collection ( new_json_string(NULL,"B2"), tmp_array_1 );
      tmp_array_2 = new_empty_json_array( "Array_1_sub_1" );
      add_item_to_json_collection ( tmp_array_2, tmp_array_1 );
      add_item_to_json_collection ( new_json_string(NULL,"B2a"), tmp_array_2 );
      add_item_to_json_collection ( new_json_string("name4B2b","B2b"), tmp_array_2 );
      add_item_to_json_collection ( new_json_string(NULL,"B2c"), tmp_array_2 );
    add_item_to_json_collection ( new_json_string(NULL,"B3"), tmp_array_1 );
    add_item_to_json_collection ( new_json_string(NULL,"B4"), tmp_array_1 );
  add_item_to_json_collection ( new_json_number ( "Neg_Num", "-12L" ), root );
  add_item_to_json_collection ( new_json_false( "var_rate_const" ), root );
  add_item_to_json_collection ( new_json_string(NULL,"abc"), root );
  add_item_to_json_collection ( new_json_number ( NULL, "57" ), root );
    tmp_object = new_empty_json_object( NULL );
    add_item_to_json_collection ( tmp_object, root );
    add_item_to_json_collection ( new_json_string(NULL,"xyz"), tmp_object );
    add_item_to_json_collection ( new_json_number(NULL,"1e22"), tmp_object );
  add_item_to_json_collection ( new_json_string(NULL,"Another String"), root );
  add_item_to_json_collection ( new_empty_json_array(NULL), root );
  add_item_to_json_collection ( new_json_string(NULL,"!!DONE!!"), root );


  printf ( "Length of the root object is %d\n", length_of_json_array(root) );
  return ( root );
}
*/

  return ( je );
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


