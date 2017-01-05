#ifndef JSON_H
#define JSON_H

typedef enum json_type_enum {
  JSON_VAL_UNDEF,
  JSON_VAL_NULL,
  JSON_VAL_TRUE,
  JSON_VAL_FALSE,
  JSON_VAL_NUMBER,
  JSON_VAL_STRING,
  JSON_VAL_ARRAY,
  JSON_VAL_OBJECT,
  JSON_VAL_KEYVAL
} json_type;

typedef struct json_element_struct {
  enum json_type_enum type;  // This tells what's in this block
  char *name;                // This is the key value when the type is in a dictionary
  int start;                 // Index of first char in this element
  int end;                   // Index of first char NOT in this element
  struct json_element_struct **subs; // Contains the array or object (dictionary) with last NULL
} json_element;


/*
typedef struct json_element_struct {
  enum json_type_enum type;  // This tells what's in this block
  char *key_name;            // This is the key value when the type is in a dictionary
  union {
    char *string_value;
    long int_value;
    double float_value;
    struct json_element_struct **sub_element_list;  // Contains the array or object (dictionary) with last NULL
  } uv; // Union Values
} json_element;
*/

extern json_element *parse_json_text ( char * );
extern void dump_json_tree ( json_element *, int, int );
extern void free_json_tree ( json_element * );
extern int json_tree_get_int ( json_element *, char * );
extern json_element *json_get_element_with_key ( json_element *, char * );
extern json_element *json_get_element_by_index ( json_element *, int );
extern char *json_get_string_value ( json_element * );
extern int json_get_int_value ( json_element * );
extern double json_get_float_value ( json_element * );
extern void dump_json_element_tree ( json_element *, int, int );

#endif
