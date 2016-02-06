/* File : JSON.c */

#include <time.h>
#include <math.h>


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

#include "JSON.h"

////////////////////////////////////////
///////  Some Helper Functions  ////////
////////////////////////////////////////


char *get_json_name ( enum json_type_enum type ) {
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


char *new_string_from_text ( char *text, int start, int end ) {
  char *substring;
  int n;
  n = end - start;
  substring = (char *) malloc (1+n);
  strncpy ( substring, &text[start], n );
  substring[n] = '\0';
  return (substring);
}


char *copy_string ( char *original ) {
  char *newstring=NULL;
  if (original != NULL) {
    int n;
    n = strlen(original);
    newstring = (char *) malloc (1+n);
    strcpy ( newstring, original );
  }
  return (newstring);
}


void print_indent ( int depth ) {
  int d;
  for (d=0; d<depth; d++) {
    printf ( "  " );
  }
}

////////////////////////////////////////
////////  Segment Parsing Code  ////////
////////////////////////////////////////

char *text=NULL;
int text_length=0;

int parse_segment ( int, int ); // Forward declaration needed here

typedef struct json_segment_struct {
  enum json_type_enum type;
  int start;
  int end;
  int depth;
  struct json_segment_struct *next;
} json_segment;

json_segment *first_segment = NULL;
json_segment *last_segment = NULL;

json_segment *append_new_segment ( int what, int start, int end, int depth ) {
  json_segment *new_segment;
  new_segment = (json_segment *) malloc ( sizeof(json_segment) );
  new_segment->type = what;
  new_segment->start = start;
  new_segment->end = end;
  new_segment->depth = depth;
  new_segment->next = NULL;
  if (first_segment == NULL) {
    first_segment = new_segment;
    last_segment = new_segment;
  } else {
    last_segment->next = new_segment;
    last_segment = new_segment;
  }
  return ( new_segment );
}

void print_segment(json_segment *s) {
  char *substring;
  int n;
  n = s->end - s->start;
  if (n > 80) n = 80;
  substring = (char *) malloc (1+n);
  strncpy ( substring, &text[s->start], n);
  substring[n] = '\0';
  printf ( "Segment: type=%s, start=%d, end=%d, depth=%d, s=%s\n", get_json_name(s->type), s->start, s->end, s->depth, substring );
  free (substring);
}

void dump_segments() {
  json_segment *s;
  s = first_segment;
  while (s != NULL) {
    char *substring;
    int n;
    n = s->end - s->start;
    if (n > 80) n = 80;
    substring = (char *) malloc (1+n);
    strncpy ( substring, &text[s->start], n);
    substring[n] = '\0';
    print_indent ( 1*s->depth );
    printf ( "Segment: type=%s, start=%d, end=%d, depth=%d, s=%s\n", get_json_name(s->type), s->start, s->end, s->depth, substring );
    free ( substring );
    s = s->next;
  }
}

int skip_chars ( const char *skip_set, int index, int depth ) {
  int i = index;
  while ( strchr(skip_set, text[i]) != NULL ) {
    i++;
    if (i >= text_length) {
      return ( -1 );
    }
  }
  // post_store_skipped ( json_segment.JSON_VAL_UNDEF, index, i, depth );
  return i;
}

int skip_whitespace ( int index, int depth ) {
  return ( skip_chars ( " \n\r\t", index, depth ) );
}
  
int skip_sepspace ( int index, int depth ) {
  return ( skip_chars ( ", \n\r\t", index, depth ) );
}

json_segment *store_new_segment ( int what, int start, int end, int depth ) {
  json_segment *js = append_new_segment ( what, start, end, depth );
  // printf ( "Stored %s at depth %d from %d to %d\n", get_json_name(what), depth, start, end );
  return js;
}

void update_segment(int what, int start, int end, int depth, json_segment *js) {
  js->type = what;
  js->start = start;
  js->end = end;
  js->depth = depth;
  // printf ( "Updated %s at depth %d from %d to %d\n", get_json_name(what), depth, start, end );
}


int parse_number ( int index, int depth ) {
  printf ( "parse_number (%d, %d)\n", index, depth );
  int end = index;
  while (strchr("0123456789.-+eE",text[end]) != NULL) {
    end++;
  }
  store_new_segment ( JSON_VAL_NUMBER, index, end, depth );
  printf ( "done parse_number (%d, %d) -> %d\n", index, depth, end );
  return (end);
}

int parse_string ( int index, int depth ) {
  printf ( "parse_string (%d, %d)\n", index, depth );
  int end = index+1;
  while (text[end] != '\"') {
    end++;
  }
  store_new_segment ( JSON_VAL_STRING, index, end+1, depth );
  printf ( "done parse_string (%d, %d) -> %d\n", index, depth, end+1 );
  return (end + 1);
}

int parse_keyval ( int index, int depth ) {
  printf ( "parse_keyval (%d, %d)\n", index, depth );
  json_segment *js = store_new_segment ( JSON_VAL_KEYVAL, index, index, depth );
  index = skip_whitespace ( index, depth );
  int end = index;
  end = parse_string ( end, depth );
  end = skip_whitespace ( end, depth );
  end = end + 1;  // This is the colon separator (:)
  end = parse_segment ( end, depth );
  update_segment ( JSON_VAL_KEYVAL, index, end, depth, js );
  printf ( "done parse_keyval (%d, %d) -> %d\n", index, depth, end );
  return (end);
}


int parse_object ( int index, int depth ) {
  printf ( "parse_object (%d, %d)\n", index, depth );
  json_segment *js = store_new_segment ( JSON_VAL_OBJECT, index, index, depth );
  int end = index+1;
  depth += 1;
  end = skip_whitespace ( end, depth );
  while (text[end] != '}') {
    end = parse_keyval ( end, depth );
    end = skip_sepspace ( end, depth );
  }
  depth += -1;
  update_segment ( JSON_VAL_OBJECT, index, end+1, depth, js );
  printf ( "done parse_object (%d, %d) -> %d\n", index, depth, end+1 );
  return (end + 1);
}

int parse_array ( int index, int depth ) {
  printf ( "parse_array (%d, %d)\n", index, depth );
  json_segment *js = store_new_segment ( JSON_VAL_ARRAY, index, index, depth );
  int end = index+1;
  depth += 1;
  end = skip_whitespace ( end, depth );
  while (text[end] != ']') {
    end = parse_segment ( end, depth );
    end = skip_sepspace ( end, depth );
  }
  depth += -1;
  update_segment ( JSON_VAL_ARRAY, index, end+1, depth, js );
  printf ( "done parse_array (%d, %d) -> %d\n", index, depth, end+1 );
  return (end + 1);
}


int parse_segment ( int index, int depth ) {
  printf ( "parse_segment (%d, %d)\n", index, depth );
  int start = skip_whitespace ( index, depth );
  if (start >= 0) {
    if ( text[start] == '{' ) {
      start = parse_object ( start, depth );
    } else if ( text[start] == '[' ) {
      start = parse_array ( start, depth );
    } else if ( text[start] == '\"' ) {
      start = parse_string ( start, depth );
    } else if ( strchr("-0123456789",text[start]) != NULL ) {
      start = parse_number ( start, depth );
    } else if ( strncmp ("null", &text[start], 4) == 0 ) {
      store_new_segment ( JSON_VAL_NULL, start, start+4, depth );
      start += 4;
    } else if ( strncmp ("true", &text[start], 4) == 0 ) {
      store_new_segment ( JSON_VAL_TRUE, start, start+4, depth );
      start += 4;
    } else if ( strncmp ("false", &text[start], 5) == 0 ) {
      store_new_segment ( JSON_VAL_FALSE, start, start+5, depth );
      start += 5;
    } else {
      printf ( "Unexpected char (%c) at %d in %s\n", text[start], start, text );
      printf ( "start = %d, text_length = %d\n", start, text_length );
      exit(1);
    }
  }
  printf ( "done parse_segment (%d, %d) -> %d\n", index, depth, start );
  return start;
}


////////////////////////////////////////
////////  Tree Generation Code  ////////
////////////////////////////////////////


void free_json_tree ( json_element *je ) {
  printf ( "free_json_tree is not implemented yet.\n" );
}



void dump_json_tree ( json_element *je, int max_len, int depth )
{

  print_indent ( depth );

  if (je->key_name == NULL) {
    printf ( "Element is %s", get_json_name(je->type) );
  } else {
    printf ( "Element at key \"%s\" is %s", je->key_name, get_json_name(je->type) );
  }

  if ( (je->type == JSON_VAL_ARRAY) || (je->type == JSON_VAL_OBJECT) ) {

    printf ( "\n" );
    json_element *j;
    int sub_num = 0;
    j = je->uv.sub_element_list[sub_num];
    while (j != NULL) {
      dump_json_tree ( j, max_len, depth+2 );
      sub_num += 1;
      j = je->uv.sub_element_list[sub_num];
    }

  } else {

    switch ( je->type)
    {
      case JSON_VAL_NULL:
        printf ( ",  Value is NULL\n" );
        break;
      case JSON_VAL_TRUE:
        printf ( ",  Value is TRUE\n" );
        break;
      case JSON_VAL_FALSE:
        printf ( ",  Value is FALSE\n" );
        break;
      case JSON_VAL_NUMBER:
        printf ( ",  Value is \"%s\"\n", je->uv.string_value );
        break;
      case JSON_VAL_STRING:
        printf ( ",  Value is \"%s\"\n", je->uv.string_value );
        break;
      default:
        printf ( ",  Value is unknown for this type\n" );
        break;
    }

  }
}


json_element *new_json_null ( char *key_name )
{
  json_element *je;
  je = (json_element *) malloc ( sizeof(json_element) );
  je->type = JSON_VAL_NULL;
  je->key_name = copy_string ( key_name );
  return ( je );
}

json_element *new_json_true ( char *key_name )
{
  json_element *je;
  je = (json_element *) malloc ( sizeof(json_element) );
  je->type = JSON_VAL_TRUE;
  je->key_name = copy_string ( key_name );
  return ( je );
}

json_element *new_json_false ( char *key_name )
{
  json_element *je;
  je = (json_element *) malloc ( sizeof(json_element) );
  je->type = JSON_VAL_FALSE;
  je->key_name = copy_string ( key_name );
  return ( je );
}

json_element *new_json_chars ( char *key_name, char *val, int type )
{
  json_element *je;
  je = (json_element *) malloc ( sizeof(json_element) );
  je->type = type;
  char *temp_s = (char *) malloc ( strlen(val) + 1 );
  strcpy ( temp_s, val );
  je->uv.string_value = temp_s;
  je->key_name = copy_string ( key_name );
  return ( je );
}

json_element *new_json_string ( char *key_name, char *val )
{
  return ( new_json_chars ( key_name, val, JSON_VAL_STRING ) );
}

json_element *new_json_number ( char *key_name, char *val )
{
  // A NUMBER is a character string until converted
  return ( new_json_chars ( key_name, val, JSON_VAL_NUMBER ) );
}


json_element *new_empty_json_collection ( char *key_name, int type )
{
  json_element *je;
  je = (json_element *) malloc ( sizeof(json_element) );
  je->type = type;
  je->uv.sub_element_list = (json_element **) malloc (1 * sizeof(json_element *) );
  je->uv.sub_element_list[0] = NULL;
  je->key_name = copy_string ( key_name );
  return ( je );
}

json_element *new_empty_json_array( char *key_name )
{
  return ( new_empty_json_collection ( key_name, JSON_VAL_ARRAY ) );
}

json_element *new_empty_json_object( char *key_name )
{
  return ( new_empty_json_collection ( key_name, JSON_VAL_OBJECT ) );
}


int length_of_json_collection ( json_element *collection )
{
  if ( (collection->type != JSON_VAL_ARRAY) && (collection->type != JSON_VAL_OBJECT) ) {
    return ( -1 );
  }
  int l = 0;
  while (collection->uv.sub_element_list[l] != NULL) {
    l += 1;
  }
  return ( l );
}


int length_of_json_array( json_element *array ) {
  return ( length_of_json_collection(array) );
}

int length_of_json_object( json_element *object ) {
  return ( length_of_json_collection(object) );
}

/* Collections:
    This code contains two kinds of collections: objects (dictionaries) and arrays.
    They are both stored in the json_element.uv.sub_element_list. In fact, they both
    use the same structure. The only difference is that an object (dictionary entry)
    is expected to have a non-null key_name stored in each item while an array does
    not. This means that the entries in an object can be accessed as if they were
    array entries.
    
    The storage layout is:
    
      sub_element_list: [ ptr0, ptr1, ptr2, ptr3, ptr4, .... ptrN ]
      
    Each "ptrX" in that list points to a json_element structure which contains its
    own name (key_name) which may be NULL or not. In a JSON object (dictionary)
    these values should not generally be NULL. Similarly, in a JSON array, these
    are expected to be NULL.
*/

int add_item_to_json_collection ( json_element *item, json_element *collection )
{
  if ( (collection->type != JSON_VAL_ARRAY) && (collection->type != JSON_VAL_OBJECT) ) {
    return ( -1 );
  }
  int original_count = length_of_json_collection ( collection );
  // Reallocate the sub-element list with room for one more item AND room for the terminating null!!
  json_element **new_subs = (json_element **) malloc ( (original_count + 1 + 1) * sizeof(json_element *) );\
  int num_copied = 0;
  // Copy the old values
  while (num_copied < original_count) {
    new_subs[num_copied] = collection->uv.sub_element_list[num_copied];
    num_copied += 1;
  }
  new_subs[num_copied] = item;
  num_copied += 1;
  new_subs[num_copied] = NULL;
  free ( collection->uv.sub_element_list );
  collection->uv.sub_element_list = new_subs;
  return ( 0 );
}



json_segment *this_segment = NULL;

void move_to_next_segment() {
  if (this_segment != NULL) {
    this_segment = this_segment->next;
  }
}


json_element *recurse_json_tree_from_segments ( char *text, char *name_of_next_object, int current_depth ) {
  json_element *this_element = NULL;
  while (this_segment != NULL) {
    printf ( "D:%d ", current_depth ); print_indent ( 2*this_segment->depth ); print_segment ( this_segment );
    if        (this_segment->type == JSON_VAL_UNDEF) {
      printf ( "\n\nError: Got JSON_VAL_UNDEF\n\n" );
      exit ( 2 );
    } else if (this_segment->type == JSON_VAL_NULL) {
      json_element *new_element = new_json_null(name_of_next_object);
      move_to_next_segment();
      return ( new_element );
    } else if (this_segment->type == JSON_VAL_TRUE) {
      json_element *new_element = new_json_true(name_of_next_object);
      move_to_next_segment();
      return ( new_element );
    } else if (this_segment->type == JSON_VAL_FALSE) {
      json_element *new_element = new_json_false(name_of_next_object);
      move_to_next_segment();
      return ( new_element );
    } else if (this_segment->type == JSON_VAL_NUMBER) {
      char *txt = new_string_from_text ( text, this_segment->start, this_segment->end );
      json_element *new_element = new_json_number(name_of_next_object,txt);
      move_to_next_segment();
      return ( new_element );
    } else if (this_segment->type == JSON_VAL_STRING) {
      char *txt = new_string_from_text ( text, (this_segment->start)+1, (this_segment->end)-1 );
      json_element *new_element = new_json_string(name_of_next_object,txt);
      move_to_next_segment();
      return ( new_element );
    } else if (this_segment->type == JSON_VAL_ARRAY) {
      json_element *array = new_empty_json_array(name_of_next_object);
      name_of_next_object = NULL;
      int array_depth = this_segment->depth;
      json_element *array_element;
      move_to_next_segment();
      if (this_segment == NULL) return ( array );
      while (this_segment->depth > array_depth) {
        array_element = recurse_json_tree_from_segments ( text, name_of_next_object, current_depth+1 );
        add_item_to_json_collection ( array_element, array );
        if (this_segment == NULL) break;
      }
      return ( array );
    } else if (this_segment->type == JSON_VAL_OBJECT) {
      json_element *object = new_empty_json_object(name_of_next_object);
      name_of_next_object = NULL;
      int object_depth = this_segment->depth;
      json_element *object_element;
      move_to_next_segment();
      char *this_name = NULL;
      if (this_segment == NULL) return ( object );
      while (this_segment->depth > object_depth) {
        if (this_segment->type != JSON_VAL_KEYVAL) {
          printf ( "Error: Object elements must be key/value pairs, got %s.\n", get_json_name(this_segment->type) );
          exit ( 5 );
        }
        move_to_next_segment();
        if (this_segment->type != JSON_VAL_STRING) {
          printf ( "Error: Object key elements must strings, got %s.\n", get_json_name(object_element->type) );
          exit ( 6 );
        }
        this_name = new_string_from_text ( text, (this_segment->start)+1, (this_segment->end)-1 );
        move_to_next_segment();
        object_element = recurse_json_tree_from_segments ( text, name_of_next_object, current_depth+1 );
        object_element->key_name = this_name;
        add_item_to_json_collection ( object_element, object );
        if (this_segment == NULL) break;
      }
      return ( object );
    } else if (this_segment->type == JSON_VAL_KEYVAL) {
      printf ( "Error: key/value pairs must be inside objects, got %s.\n", get_json_name(this_segment->type) );
      exit ( 5 );
    } else {
      printf ( "\n\nError: Got unknown segment type.\n\n" );
      exit ( 4 );
    }
  }
  printf ( "Should not return from here!!\n" );
  return ( this_element );
}

json_element *build_json_tree_from_segments ( char *text, json_segment *first_segment, json_element *parent ) {
  this_segment = first_segment;
  json_element *tree = recurse_json_tree_from_segments ( text, NULL, 0 );
  return ( tree );
}



// This code generates an example JSON structure based on hard coded values used in testing:

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



////////////////////////////////////////
/////  Functions for External Use  /////
////////////////////////////////////////

int json_get_int_value ( json_element *je ) {
  int return_value = 0;
  if (je->type == JSON_VAL_NUMBER) {
    sscanf ( je->uv.string_value, " %d", &return_value );
  } else if (je->type == JSON_VAL_STRING) {
    // printf ( "Warning: Expected a JSON Number, but got %s\n", get_json_name(je->type) );
    sscanf ( je->uv.string_value, " %d", &return_value );
  } else {
    printf ( "Error: Expected a JSON Number or String, but got %s\n", get_json_name(je->type) );
    exit(1);
  }
  return ( return_value );
}

double json_get_float_value ( json_element *je ) {
  double return_value = 0;
  if (je->type == JSON_VAL_NUMBER) {
    sscanf ( je->uv.string_value, "%lg", &return_value );
  } else if (je->type == JSON_VAL_STRING) {
    // printf ( "Warning: Expected a JSON Number, but got %s\n", get_json_name(je->type) );
    sscanf ( je->uv.string_value, "%lg", &return_value );
  } else {
    printf ( "Error: Expected a JSON Number or String, but got %s\n", get_json_name(je->type) );
    exit(1);
  }
  return ( return_value );
}

int json_get_bool_value ( json_element *je ) {
  if ( (je->type != JSON_VAL_TRUE) && (je->type != JSON_VAL_FALSE) ) {
    exit(623230);
  }
  if (je->type == JSON_VAL_TRUE) {
    return ( 1 );
  } else {
    return ( 0 );
  }
}

char *json_get_string_value ( json_element *je ) {
  if (je->type != JSON_VAL_STRING) {
    exit(7172365);
  }
  return ( je->uv.string_value );
}


json_element *parse_json_text ( char *text_to_parse )
{
  text = text_to_parse;           // Assign this to a global to simulate it being in the "class"?

      // These are some test cases ... uncomment one to use instead of the value passed in

      //text = "5";
      //text = " 5 ";
      //text = " [5] ";
      //text = " { \"Five\", 5 }";
      //text = "  {\"a\":5, \"b\":6.7, \"c\":\"C\", \"d\":null ,\"e\":true , \"f\" : false, \"g\":[1,2,\"x\",\"y\"] , \"h\" : { \"z\":99, \"subsub\":{\"one\":1,\"two\":2},\"zz\":{},\"ZZ\":[] }, \"exit\":\"X\" }  ";
      //text = "  {\"a\":5, \"b\":6.7, \"c\":\"C\", \"d\":null ,\"e\":true , \"f\" : false }  ";
      //text = "  {k1:99, k2:55, k3:null,  }  ";
      //text = "[ { \"abc\" : [5, 4, 3, \"abc\", {\"t\":true, \"f\":false, \"n\":null}, [\"x\", 11, [], 22, [true] ], 3, {\"k1\":1,\"k2\":2, \"k3\":3, \"k4\":4, \"k5\":5}, 9 ], \"end\":99 } ]";
      //text = "[5, 4, 3, \"abc\", true, false, null, 3]";
      //text = "{\"mcell\": {\"blender_version\": [2, 68, 0], \"api_version\": 0, \"reaction_data_output\": {\"mol_colors\": false, \"reaction_output_list\": [], \"plot_legend\": \"0\", \"combine_seeds\": true, \"plot_layout\": \" plot \"}}}";
      //text = "{ \"key\" : \"val\" }";
	    //text = " { \"ALL\" : [ 2, -1, {\"a\":1,\"b\":2,\"c\":3}, { \"mc\":[ { \"a\":0 }, 2, true, [9,[0,3],\"a\",3], false, null, 5, [1,2,3], \"xyz\" ], \"x\":\"y\" }, -3, 7 ] }  ";
	    //text = " { \"ALL\" : [\n 2, -1, {\"a\":1,\"b\":2,\"c\":3},\n { \"mc\":[ { \"a\":0 },\n 2, true, [9,[0,3],\"a\",3],\n false, null, 5, [1,2,3], \"xyz\" ],\n \"x\":\"y\" }, -3, 7 ] }  ";
	    //text = "{\"mc\":[{\"a\":0},2,true,[9,[0,3],\"a\",3],false,null,5,[1,2,3],\"xyz\"],\"x\":\"y\"}";
	    //text = "{\"mcell\": {\"blender_version\": [2, 68, 0], \"api_version\": 0, \"reaction_data_output\": {\"mol_colors\": false, \"reaction_output_list\": [], \"plot_legend\": \"0\", \"combine_seeds\": true, \"plot_layout\": \" plot \"}, \"define_molecules\": {\"molecule_list\": [{\"export_viz\": false, \"diffusion_constant\": \"1e-7\", \"data_model_version\": \"DM_2014_10_24_1638\", \"custom_space_step\": \"\", \"maximum_step_length\": \"\", \"mol_name\": \"a\", \"mol_type\": \"3D\", \"custom_time_step\": \"\", \"target_only\": false}, {\"export_viz\": false, \"diffusion_constant\": \"1e-7\", \"data_model_version\": \"DM_2014_10_24_1638\", \"custom_space_step\": \"\", \"maximum_step_length\": \"\", \"mol_name\": \"b\", \"mol_type\": \"3D\", \"custom_time_step\": \"\", \"target_only\": false}], \"data_model_version\": \"DM_2014_10_24_1638\"}, \"define_reactions\": {\"reaction_list\": []}, \"data_model_version\": \"DM_2014_10_24_1638\", \"define_surface_classes\": {\"surface_class_list\": []}, \"parameter_system\": {\"model_parameters\": []}, \"define_release_patterns\": {\"release_pattern_list\": []}, \"release_sites\": {\"release_site_list\": [{\"object_expr\": \"\", \"location_x\": \"0\", \"location_y\": \"0\", \"release_probability\": \"1\", \"stddev\": \"0\", \"quantity\": \"100\", \"pattern\": \"\", \"site_diameter\": \"0\", \"orient\": \"'\", \"name\": \"ra\", \"shape\": \"CUBIC\", \"quantity_type\": \"NUMBER_TO_RELEASE\", \"molecule\": \"a\", \"location_z\": \"0\"}, {\"object_expr\": \"\", \"location_x\": \"0\", \"location_y\": \".2\", \"release_probability\": \"1\", \"stddev\": \"0\", \"quantity\": \"100\", \"pattern\": \"\", \"site_diameter\": \"0\", \"orient\": \"'\", \"name\": \"rb\", \"shape\": \"CUBIC\", \"quantity_type\": \"NUMBER_TO_RELEASE\", \"molecule\": \"b\", \"location_z\": \"0\"}]}, \"modify_surface_regions\": {\"modify_surface_regions_list\": []}, \"initialization\": {\"center_molecules_on_grid\": false, \"iterations\": \"10\", \"warnings\": {\"missing_surface_orientation\": \"ERROR\", \"high_probability_threshold\": \"1.0\", \"negative_diffusion_constant\": \"WARNING\", \"degenerate_polygons\": \"WARNING\", \"lifetime_too_short\": \"WARNING\", \"negative_reaction_rate\": \"WARNING\", \"high_reaction_probability\": \"IGNORED\", \"missed_reactions\": \"WARNING\", \"lifetime_threshold\": \"50\", \"useless_volume_orientation\": \"WARNING\", \"missed_reaction_threshold\": \"0.0010000000474974513\", \"all_warnings\": \"INDIVIDUAL\"}, \"space_step\": \"\", \"radial_directions\": \"\", \"radial_subdivisions\": \"\", \"vacancy_search_distance\": \"\", \"time_step_max\": \"\", \"accurate_3d_reactions\": true, \"notifications\": {\"probability_report_threshold\": \"0.0\", \"varying_probability_report\": true, \"probability_report\": \"ON\", \"iteration_report\": true, \"progress_report\": true, \"molecule_collision_report\": false, \"box_triangulation_report\": false, \"release_event_report\": true, \"file_output_report\": false, \"partition_location_report\": false, \"all_notifications\": \"INDIVIDUAL\", \"diffusion_constant_report\": \"BRIEF\", \"final_summary\": true}, \"time_step\": \"5e-6\", \"interaction_radius\": \"\", \"surface_grid_density\": \"10000\", \"microscopic_reversibility\": \"OFF\", \"partitions\": {\"x_start\": \"-1.0\", \"x_step\": \"0.019999999552965164\", \"y_step\": \"0.019999999552965164\", \"y_end\": \"1.0\", \"recursion_flag\": false, \"z_end\": \"1.0\", \"x_end\": \"1.0\", \"z_step\": \"0.019999999552965164\", \"include\": false, \"y_start\": \"-1.0\"}}, \"model_objects\": {\"model_object_list\": [{\"name\": \"Cube\"}]}, \"geometrical_objects\": {\"object_list\": [{\"element_connections\": [[4, 5, 0], [5, 6, 1], [6, 7, 2], [7, 4, 3], [0, 1, 3], [7, 6, 4], [6, 2, 1], [6, 5, 4], [5, 1, 0], [7, 3, 2], [1, 2, 3], [4, 0, 3]], \"name\": \"Cube\", \"vertex_list\": [[-0.25, -0.25, -0.25], [-0.25, 0.25, -0.25], [0.25, 0.25, -0.25], [0.25, -0.25, -0.25], [-0.25, -0.25, 0.25], [-0.25, 0.25, 0.25], [0.25, 0.25, 0.25], [0.25, -0.25, 0.25]], \"location\": [0.0, 0.0, 0.0]}]}, \"viz_output\": {\"all_iterations\": true, \"step\": \"1\", \"end\": \"1\", \"export_all\": true, \"start\": \"0\"}, \"materials\": {\"material_dict\": {}}, \"cellblender_version\": \"0.1.54\", \"cellblender_source_sha1\": \"6a572dab58fa0f770c46ce3ac26b01f3a66f2096\"}}";
              //	char *text = "{\"mcell\": [3]}";        // OK
              //	char *text = "{\"mcell\": \"\"}";       // OK
              // 	char *text = "{\"mcell\": [ ]}";        // Fails with: Unexpected char (]) at 12 in {"mcell": [ ]}
              // 	char *text = "{\"mcell\": { }}";        // Fails with: Unexpected char (s) at 714 in {"mcell": { }}
              // 	char *text = "{\"mcell\": []}";         // Fails with segment fault

  text_length = strlen(text);

  printf ( "Parsing text of length %d\n", text_length );
  printf ( "Text: %s\n", text );

  parse_segment ( 0, 0 ); // This builds a linked list of segments stored in "first_segment"

  printf ( "Return from parse_segment\n" );

  dump_segments();

  json_element *root;

  root = new_empty_json_object("root");
  printf ( "Building JSON tree from segments ...\n" );
  root = build_json_tree_from_segments ( text, first_segment, root );
  printf ( "Back from building JSON tree from segments ...\n" );

  return ( root );
}

json_element *json_get_element_with_key ( json_element *tree, char *key ) {
  // printf ( "Top of json_get_element_with_key with key = %s\n", key );

  if (tree == NULL) {
    printf ( "Error: can't call json_get_element_with_key on NULL object\n" );
    exit( 72342 );
  }
  if (tree->type != JSON_VAL_OBJECT) {
    printf ( "Error: can't call json_get_element_with_key on non-dictionary object\n" );
    exit( 23239 );
  }

  json_element *e;
  int sub_num = 0;
  e = tree->uv.sub_element_list[sub_num];
  while ( (e != NULL) && (strcmp(e->key_name,key) != 0) ) {
    sub_num += 1;
    e = tree->uv.sub_element_list[sub_num];
  }

  //if (e != NULL) {
  //  printf ( "Found %s of type %s\n", key, get_json_name(e->type) );
  //}
  return ( e );
}

json_element *json_get_element_by_index ( json_element *tree, int index ) {
  // printf ( "Top of json_get_element_by_index with index = %d\n", index );

  if (tree == NULL) {
    printf ( "Error: can't call json_get_element_by_index on NULL object\n" );
    exit( 747442 );
  }
  if ((tree->type != JSON_VAL_ARRAY) && (tree->type != JSON_VAL_OBJECT)) {
    printf ( "Error: can't call json_get_element_by_index on non-collection object\n" );
    exit( 29230 );
  }

  json_element *e;
  e = tree->uv.sub_element_list[index];

  //if (e != NULL) {
  //  printf ( "Found %s of type %s\n", key, get_json_name(e->type) );
  //}
  return ( e );
}


/*
json_element *get_element_from_path ( json_element *tree, char *json_path ) {
  printf ( "Top of get_element_from_path with path = %s\n", json_path );

  return json_get_element_with_key ( tree, json_path );


  char *path = copy_string ( json_path );
  int first_dot = strchr ( path, '/' );
  if (first_dot < 0) {
  }
  path[first_dot] = '\0';

  json_element *e;
  int sub_num = 0;
  e = tree->uv.sub_element_list[sub_num];
  while ( (e != NULL) && (strcmp(e->key_name,path) != 0) ) {
    sub_num += 1;
    e = tree->uv.sub_element_list[sub_num];
  }

  if (e == NULL) return ( e );
  
  path = &path[first_dot+1];
  while ( (e!=NULL) && (strcmp(e->key_name,path) != 0) ) {
  free ( path );

  if (tree->key_name != NULL) {
    printf ( "Key = %d\n", tree->key_name );
  } else {
  }

  return ( NULL );
}
*/

/*
int json_tree_get_int ( json_element *tree, char *json_path ) {
  get_element_from_path ( tree, json_path );
  json_element *mcell = json_get_element_with_key ( tree, "mcell" );
  json_element *api_ver = json_get_element_with_key ( mcell, "api_version" );
  
  return ( 1234 );
}
*/
