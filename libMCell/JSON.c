/* File : JSON.c */

#include <time.h>
#include <math.h>


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

#include "JSON.h"

#define PRINT_DEBUG 0

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


int skip_chars ( char *text, int text_length, const char *skip_set, int index, int depth ) {
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

int skip_whitespace ( char *text, int text_length, int index, int depth ) {
  return ( skip_chars ( text, text_length, " \n\r\t", index, depth ) );
}
  
int skip_sepspace ( char *text, int text_length, int index, int depth ) {
  return ( skip_chars ( text, text_length, ", \n\r\t", index, depth ) );
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

/* Collections:
    This code contains two kinds of collections: objects (dictionaries) and arrays.
    They are both stored in the json_element.subs list. In fact, they both use the same
    structure. The only difference is that an object (dictionary entry) is expected
    to have a non-null name stored in each element while an array does not. This means
    that the entries in an object can be accessed as if they were array entries.

    The storage layout is:
      sub_element_list: [ ptr0, ptr1, ptr2, ptr3, ptr4, .... ptrN ]

    Each "ptrX" in that list points to a json_element structure which contains its
    own name ("name") which may be NULL or not. In a JSON object (dictionary)
    these values should generally NOT be NULL. Similarly, in a JSON array, these
    are expected to be NULL.
*/


void dump_json_element_tree ( json_element *je, int max_len, int depth )
{
  print_indent ( depth );
  if (je->name == NULL) {
    printf ( "Element is %s", get_json_name(je->type) );
  } else {
    printf ( "Element at key \"%s\" is %s", je->name, get_json_name(je->type) );
  }
  printf ( ", from %d to %d", je->start, je->end );
  //print_indent ( depth );
  if ( (je->type == JSON_VAL_ARRAY) || (je->type == JSON_VAL_OBJECT) ) {
    json_element *j;
    int sub_num;
    sub_num = 0;
    j = je->subs[sub_num];
    printf ( ",  Value is [ " );
    while (j != NULL) {
      printf ( "%s ", get_json_name(j->type) );
      sub_num += 1;
      j = je->subs[sub_num];
    }
    printf ( "]\n" );
    sub_num = 0;
    j = je->subs[sub_num];
    while (j != NULL) {
      dump_json_element_tree ( j, max_len, depth+2 );
      sub_num += 1;
      j = je->subs[sub_num];
    }
  } else {
    char save;
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
        save = text[je->end];
        //printf ( "Adding a terminating null in place of \"%c\"\n", save );
        text[je->end] = '\0';
        //printf ( "Added terminating null to get \"%s\"\n", text );
        printf ( ",  Value is %s\n", &text[je->start] );
        text[je->end] = save;
        //printf ( "Removed terminating null\n" );
        break;
      case JSON_VAL_STRING:
        save = text[je->end];
        //printf ( "Adding a terminating null in place of \"%c\"\n", save );
        text[je->end] = '\0';
        printf ( ",  Value is \"%s\"\n", &text[je->start] );
        text[je->end] = save;
        //printf ( "Removed terminating null\n" );
        break;
      default:
        printf ( ",  Value is unknown for this type\n" );
        break;
    }
  }
}


void update_element ( json_element *element, int start, int end ) {
  element->start = start;
  element->end = end;
}

int length_of_json_element_collection ( json_element *collection )
{
  if ( (collection->type != JSON_VAL_ARRAY) && (collection->type != JSON_VAL_OBJECT) ) {
    printf ( "Error: Attempt to get length of a non-collection parent\n" );
    return ( -1 );
  }
  int l = 0;
  while (collection->subs[l] != NULL) {
    l += 1;
  }
  return ( l );
}

int length_of_json_array_element ( json_element *array ) {
  return ( length_of_json_element_collection(array) );
}

int length_of_json_object_element ( json_element *object ) {
  return ( length_of_json_element_collection(object) );
}

json_element *new_empty_json_leaf_element ( char *key_name, int type, int start, int end, int depth ) {
  #if PRINT_DEBUG
  if (key_name == NULL) {
    print_indent(depth);  printf ( "=>> new_empty_json_leaf_element at %d\n", start );
  } else {
    print_indent(depth);  printf ( "=>> new_empty_json_leaf_element named \"%s\"at %d\n", key_name, start );
  }
  #endif
  json_element *je;
  je = (json_element *) malloc ( sizeof(json_element) );
  je->type = type;
  je->start = start;
  je->end = end;
  je->subs = NULL;
  if (key_name == NULL) {
    je->name = NULL;
  } else {
    je->name = copy_string ( key_name );
  }
  return ( je );
}

json_element *new_empty_json_collection_element ( char *key_name, int type, int start, int end, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "=>> new_empty_json_collection_element at %d\n", start );
  #endif
  json_element *je = new_empty_json_leaf_element ( key_name, type, start, end, depth );
  je->subs = (json_element **) malloc (1 * sizeof(json_element *) );
  je->subs[0] = NULL;
  return ( je );
}

json_element *new_empty_json_array_element ( char *key_name, int start, int end, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "=>> new_empty_json_array_element at %d\n", start );
  #endif
  return ( new_empty_json_collection_element ( key_name, JSON_VAL_ARRAY, start, end, depth ) );
}

json_element *new_empty_json_object_element ( char *key_name, int start, int end, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "=>> new_empty_json_object_element at %d\n", start );
  #endif
  return ( new_empty_json_collection_element ( key_name, JSON_VAL_OBJECT, start, end, depth ) );
}

json_element *new_json_tfn_element ( char *key_name, json_type type, int start, int end, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "=>> new_empty_json_tfn_element at %d\n", start );
  #endif
  return ( new_empty_json_leaf_element ( key_name, type, start, end, depth ) );
}

json_element *new_json_strnum_element ( char *key_name, json_type type, int start, int end, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "=>> new_empty_json_strnum_element from %d to %d\n", start, end );
  #endif
  json_element *je = new_empty_json_leaf_element ( key_name, type, start, end, depth );
  return ( je );
}

int add_element_to_json_collection ( json_element *element, json_element *collection, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "... add_element_to_json_collection adding a %s element.\n", get_json_name(element->type) );
  #endif
  if (collection == NULL) return ( 0 );

  if ( (collection->type != JSON_VAL_ARRAY) && (collection->type != JSON_VAL_OBJECT) ) {
    printf ( "Error: Attempt to store and element in a non-collection parent\n" );
    return ( -1 );
  }
  int original_count = length_of_json_element_collection ( collection );
  // Reallocate the sub-element list with room for one more element AND room for the terminating NULL!!
  json_element **new_subs = (json_element **) malloc ( (original_count + 1 + 1) * sizeof(json_element *) );\
  int num_copied = 0;
  // Copy the old values
  while (num_copied < original_count) {
    new_subs[num_copied] = collection->subs[num_copied];
    num_copied += 1;
  }
  new_subs[num_copied] = element;
  num_copied += 1;
  new_subs[num_copied] = NULL;
  free ( collection->subs );
  collection->subs = new_subs;
  return ( 0 );
}


int parse_number_element ( json_element *parent, char *name, int index, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "parse_number_element (%d, %d)\n", index, depth );
  #endif
  int end = index;
  while (strchr("0123456789.-+eE",text[end]) != NULL) {
    // printf ( "  strchr(\"0123456789.-+eE\",%c) is not null\n", text[end] );
    end++;
  }
  json_element *je = new_json_strnum_element ( name, JSON_VAL_NUMBER, index, end, depth );
  add_element_to_json_collection ( je, parent, depth );
  //store_new_segment ( JSON_VAL_NUMBER, index, end, depth );
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "done parse_number_element (%d, %d) -> %d\n", index, depth, end );
  #endif
  return (end);
}

int parse_string_element ( json_element *parent, char *name, int index, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "parse_string_element (%d, %d)\n", index, depth );
  #endif
  int end = index+1;
  while (text[end] != '\"') {
    end++;
  }
  json_element *je = new_json_strnum_element ( name, JSON_VAL_STRING, index+1, end, depth );
  add_element_to_json_collection ( je, parent, depth );
  //store_new_segment ( JSON_VAL_STRING, index, end+1, depth );
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "done parse_string_element (%d, %d) -> %d\n", index+1, depth, end-1 );
  #endif
  return (end + 1);
}

int parse_keyval_element ( json_element *parent, char *name, int index, int depth ) {
  print_indent(depth);  printf ( "parse_keyval_element (%d, %d)\n", index, depth );
  //json_segment *js = store_new_segment ( JSON_VAL_KEYVAL, index, index, depth );
  index = skip_whitespace ( text, text_length, index, depth );
  int end = index;
  end = parse_string_element ( parent, NULL, end, depth );
  end = skip_whitespace ( text, text_length, end, depth );
  end = end + 1;  // This is the colon separator (:)
  //end = parse_segment ( end, depth );
  //update_segment ( JSON_VAL_KEYVAL, index, end, depth, js );
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "done parse_keyval_element (%d, %d) -> %d\n", index, depth, end );
  #endif
  return (end);
}


int old_parse_object_element ( json_element *parent, char *name, int index, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "parse_object_element (%d, %d)\n", index, depth );
  #endif
  /*
  json_segment *js = store_new_segment ( JSON_VAL_OBJECT, index, index, depth );
  int end = index+1;
  depth += 1;
  end = skip_whitespace ( text, text_length, end, depth );
  while (text[end] != '}') {
    end = parse_keyval ( end, depth );
    end = skip_sepspace ( text, text_length, end, depth );
  }
  depth += -1;
  update_segment ( JSON_VAL_OBJECT, index, end+1, depth, js );
  printf ( "done parse_object_element (%d, %d) -> %d\n", index, depth, end+1 );
  return (end + 1);
  */
  print_indent(depth);  printf ( "Error: can't parse objects yet!!\n" );
  exit ( 12 );
  return ( 0 );
}

int parse_object_element ( json_element *parent, char *name, int index, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "parse_object_element (%d, %d)\n", index, depth );
  #endif
  json_element *this_object = new_empty_json_object_element ( name, index, index, depth );

  int end = index+1;
  depth += 1;
  end = skip_whitespace ( text, text_length, end, depth );
  while (text[end] != '}') {
    // end = parse_segment ( end, depth );
    end = parse_element ( this_object, NULL, end, depth );
    end = skip_sepspace ( text, text_length, end, depth );
  }
  depth += -1;
  //update_element ( JSON_VAL_ARRAY, index, end+1, depth, js );
  update_element ( this_object, index, end+1 );
  add_element_to_json_collection ( this_object, parent, depth );

  #if PRINT_DEBUG
  print_indent(depth);  printf ( "done parse_object_element (%d, %d) -> %d\n", index, depth, end );
  #endif
  return (end+1);
}


int parse_array_element ( json_element *parent, char *name, int index, char endchar, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "parse_array_element (%d, %d)\n", index, depth );
  #endif
  // json_segment *js = store_new_segment ( JSON_VAL_ARRAY, index, index, depth );
  json_element *this_array = new_empty_json_array_element ( name, index, index, depth );

  int end = index+1;
  depth += 1;
  end = skip_whitespace ( text, text_length, end, depth );
  while (text[end] != endchar) {
    // end = parse_segment ( end, depth );
    end = parse_element ( this_array, NULL, end, depth );
    end = skip_sepspace ( text, text_length, end, depth );
  }
  depth += -1;
  //update_element ( JSON_VAL_ARRAY, index, end+1, depth, js );
  update_element ( this_array, index, end+1 );
  add_element_to_json_collection ( this_array, parent, depth );

  #if PRINT_DEBUG
  print_indent(depth);  printf ( "done parse_array_element (%d, %d) -> %d\n", index, depth, end );
  #endif
  return (end+1);
}

int parse_element ( json_element *parent, char *name, int index, int depth ) {
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "parse_element (%d, %d)\n", index, depth );
  #endif
  int start = skip_whitespace ( text, text_length, index, depth );
  if (start >= 0) {
    if ( text[start] == '{' ) {
      #if PRINT_DEBUG
      print_indent(depth);  printf ( "--> parse_element found object starting at %d\n", start );
      #endif
      start = parse_object_element ( parent, name, start, depth+1 );
    } else if ( text[start] == '[' ) {
      #if PRINT_DEBUG
      print_indent(depth);  printf ( "--> parse_element found array starting at %d\n", start );
      #endif
      start = parse_array_element ( parent, name, start, ']', depth+1 );
    } else if ( text[start] == '\"' ) {
      #if PRINT_DEBUG
      print_indent(depth);  printf ( "--> parse_element found string starting at %d\n", start );
      #endif
      // This could be either a string or a key in a string/value object entry.
      // Parse this into a separate parent to store it, then look for the colon separator.
      json_element *string_parent = new_empty_json_array_element ( NULL, start, start, depth );
      int string_start = start;
      start = parse_string_element ( string_parent, name, string_start, depth );
      start = skip_whitespace ( text, text_length, start, depth );
      if (text[start] == ':') {
        // The string was a key
        #if PRINT_DEBUG
        printf ( "Got a key!!\n" );
        #endif
        json_element *name_element = string_parent->subs[0];
        int name_start = name_element->start + 0; // Account for the quote
        int name_end = name_element->end - 0;     // Account for the quote
        int len = name_end - name_start;
        char *key_name = (char *) malloc ( len + 1 );
        strncpy ( key_name, &text[name_start], len );
        key_name[len] = '\0';
        start = parse_element ( parent, key_name, start+1, depth );
      } else {
        // The string was a value, so use the previously saved "string_start" to reparse it
        #if PRINT_DEBUG
        printf ( "\nDidn't get a key!!\n" );
        #endif
        start = parse_string_element ( parent, name, string_start, depth );
      }
    } else if ( strchr("-0123456789",text[start]) != NULL ) {
      #if PRINT_DEBUG
      print_indent(depth);  printf ( "--> parse_element found number starting at %d\n", start );
      #endif
      start = parse_number_element ( parent, name, start, depth );
    } else if ( strncmp ("null", &text[start], 4) == 0 ) {
      #if PRINT_DEBUG
      print_indent(depth);  printf ( "--> parse_element found null from %d to %d\n", start, start+3 );
      #endif
      json_element *je = new_json_tfn_element ( name, JSON_VAL_NULL, start, start+3, depth );
      add_element_to_json_collection ( je, parent, depth );
      // store_new_segment ( JSON_VAL_NULL, start, start+4, depth );
      start += 4;
    } else if ( strncmp ("true", &text[start], 4) == 0 ) {
      #if PRINT_DEBUG
      print_indent(depth);  printf ( "--> parse_element found true from %d to %d\n", start, start+3 );
      #endif
      json_element *je = new_json_tfn_element ( name, JSON_VAL_TRUE, start, start+3, depth );
      add_element_to_json_collection ( je, parent, depth );
      // store_new_segment ( JSON_VAL_TRUE, start, start+4, depth );
      start += 4;
    } else if ( strncmp ("false", &text[start], 5) == 0 ) {
      #if PRINT_DEBUG
      print_indent(depth);  printf ( "--> parse_element found false from %d to %d\n", start, start+4 );
      #endif
      json_element *je = new_json_tfn_element ( name, JSON_VAL_FALSE, start, start+4, depth );
      add_element_to_json_collection ( je, parent, depth );
      // store_new_segment ( JSON_VAL_FALSE, start, start+5, depth );
      start += 5;
    } else {
      print_indent(depth);  printf ( "Unexpected char (%c) at %d in %s\n", text[start], start, text );
      print_indent(depth);  printf ( "start = %d, text_length = %d\n", start, text_length );
      exit(1);
    }
  }
  #if PRINT_DEBUG
  print_indent(depth);  printf ( "done parse_element (%d, %d) -> %d\n", index, depth, start );
  #endif
  return start;
}




////////////////////////////////////////
////////  Tree Generation Code  ////////
////////////////////////////////////////


void free_json_tree ( json_element *je ) {
  printf ( "free_json_tree is not implemented yet.\n" );
}



json_element *parse_json_text ( char *text_to_parse ) {
  text = text_to_parse;           // Assign this to a global to simulate it being in the "class"?
/*
      // These are some test cases ... uncomment one to use instead of the value passed in
      //      012345678901234567890123456789012345678990123345678901
      //text = "[ 2, true, [false, null], true, false, \"abc\", 3, 5 ]";
      //text = "[ 2, true, [false,\"x\",8,[]], null, \"abc\", 3, 5, []]";
      //text = "[5]";
      //text = " 5 ";
      //text = "[0.5,1.2,3e-6]";
      //text = " [5] ";
      //text = " { \"Five\": 5 }";
      // text = " { \"Five\": 5, \"Six\" :[6,66],\"Sev\" : 7, \"Sub\" : {\"eight\":8, \"nine\":9}, \"Ten\", 10 }";
      //text = "  {\"a\":5, \"b\":6.7, \"c\":\"C\", \"d\":null ,\"e\":true , \"f\" : false, \"g\":[1,2,\"x\",\"y\"] , \"h\" : { \"z\":99, \"subsub\":{\"one\":1,\"two\":2},\"zz\":{},\"ZZ\":[] }, \"exit\":\"X\" }  ";
      //text = "  {\"a\":5, \"b\":6.7, \"c\":\"C\", \"d\":null ,\"e\":true , \"f\" : false }  ";
      //text = "  {\"k1\":99, \"k2\":\"xyz\", \"k3\":null  }  ";
      //text = "[ { \"abc\" : [5, 4, 3, \"abc\", {\"t\":true, \"f\":false, \"n\":null}, [\"x\", 11, [], 22, [true] ], 3, {\"k1\":1,\"k2\":2, \"k3\":3, \"k4\":4, \"k5\":5}, 9 ], \"end\":99 } ]";
      //text = "[5, 4, 3, \"abc\", true, false, null, 3]";
      //text = "{\"mcell\": {\"blender_version\": [2, 68, 0], \"api_version\": 0, \"reaction_data_output\": {\"mol_colors\": false, \"reaction_output_list\": [], \"plot_legend\": \"0\", \"combine_seeds\": true, \"plot_layout\": \" plot \"}}}";
      //text = "{ \"key\" : \"val\" }";
	    //text = " { \"ALL\" : [ 2, -1, {\"a\":1,\"b\":2,\"c\":3}, { \"mc\":[ { \"a\":0 }, 2, true, [9,[0,3],\"a\",3], false, null, 5, [1,2,3], \"xyz\" ], \"x\":\"y\" }, -3, 7 ] }  ";
	    //text = " { \"ALL\" : [\n 2, -1, {\"a\":1,\"b\":2,\"c\":3},\n { \"mc\":[ { \"a\":0 },\n 2, true, [9,[0,3],\"a\",3],\n false, null, 5, [1,2,3], \"xyz\" ],\n \"x\":\"y\" }, -3, 7 ] }  ";
	    //text = "{\"mc\":[{\"a\":0},2,true,[9,[0,3],\"a\",3],false,null,5,[1,2,3],\"xyz\"],\"x\":\"y\"}";
	    text = "{\"mcell\": {\"blender_version\": [2, 68, 0], \"api_version\": 0, \"reaction_data_output\": {\"mol_colors\": false, \"reaction_output_list\": [], \"plot_legend\": \"0\", \"combine_seeds\": true, \"plot_layout\": \" plot \"}, \"define_molecules\": {\"molecule_list\": [{\"export_viz\": false, \"diffusion_constant\": \"1e-7\", \"data_model_version\": \"DM_2014_10_24_1638\", \"custom_space_step\": \"\", \"maximum_step_length\": \"\", \"mol_name\": \"a\", \"mol_type\": \"3D\", \"custom_time_step\": \"\", \"target_only\": false}, {\"export_viz\": false, \"diffusion_constant\": \"1e-7\", \"data_model_version\": \"DM_2014_10_24_1638\", \"custom_space_step\": \"\", \"maximum_step_length\": \"\", \"mol_name\": \"b\", \"mol_type\": \"3D\", \"custom_time_step\": \"\", \"target_only\": false}], \"data_model_version\": \"DM_2014_10_24_1638\"}, \"define_reactions\": {\"reaction_list\": []}, \"data_model_version\": \"DM_2014_10_24_1638\", \"define_surface_classes\": {\"surface_class_list\": []}, \"parameter_system\": {\"model_parameters\": []}, \"define_release_patterns\": {\"release_pattern_list\": []}, \"release_sites\": {\"release_site_list\": [{\"object_expr\": \"\", \"location_x\": \"0\", \"location_y\": \"0\", \"release_probability\": \"1\", \"stddev\": \"0\", \"quantity\": \"100\", \"pattern\": \"\", \"site_diameter\": \"0\", \"orient\": \"'\", \"name\": \"ra\", \"shape\": \"CUBIC\", \"quantity_type\": \"NUMBER_TO_RELEASE\", \"molecule\": \"a\", \"location_z\": \"0\"}, {\"object_expr\": \"\", \"location_x\": \"0\", \"location_y\": \".2\", \"release_probability\": \"1\", \"stddev\": \"0\", \"quantity\": \"100\", \"pattern\": \"\", \"site_diameter\": \"0\", \"orient\": \"'\", \"name\": \"rb\", \"shape\": \"CUBIC\", \"quantity_type\": \"NUMBER_TO_RELEASE\", \"molecule\": \"b\", \"location_z\": \"0\"}]}, \"modify_surface_regions\": {\"modify_surface_regions_list\": []}, \"initialization\": {\"center_molecules_on_grid\": false, \"iterations\": \"10\", \"warnings\": {\"missing_surface_orientation\": \"ERROR\", \"high_probability_threshold\": \"1.0\", \"negative_diffusion_constant\": \"WARNING\", \"degenerate_polygons\": \"WARNING\", \"lifetime_too_short\": \"WARNING\", \"negative_reaction_rate\": \"WARNING\", \"high_reaction_probability\": \"IGNORED\", \"missed_reactions\": \"WARNING\", \"lifetime_threshold\": \"50\", \"useless_volume_orientation\": \"WARNING\", \"missed_reaction_threshold\": \"0.0010000000474974513\", \"all_warnings\": \"INDIVIDUAL\"}, \"space_step\": \"\", \"radial_directions\": \"\", \"radial_subdivisions\": \"\", \"vacancy_search_distance\": \"\", \"time_step_max\": \"\", \"accurate_3d_reactions\": true, \"notifications\": {\"probability_report_threshold\": \"0.0\", \"varying_probability_report\": true, \"probability_report\": \"ON\", \"iteration_report\": true, \"progress_report\": true, \"molecule_collision_report\": false, \"box_triangulation_report\": false, \"release_event_report\": true, \"file_output_report\": false, \"partition_location_report\": false, \"all_notifications\": \"INDIVIDUAL\", \"diffusion_constant_report\": \"BRIEF\", \"final_summary\": true}, \"time_step\": \"5e-6\", \"interaction_radius\": \"\", \"surface_grid_density\": \"10000\", \"microscopic_reversibility\": \"OFF\", \"partitions\": {\"x_start\": \"-1.0\", \"x_step\": \"0.019999999552965164\", \"y_step\": \"0.019999999552965164\", \"y_end\": \"1.0\", \"recursion_flag\": false, \"z_end\": \"1.0\", \"x_end\": \"1.0\", \"z_step\": \"0.019999999552965164\", \"include\": false, \"y_start\": \"-1.0\"}}, \"model_objects\": {\"model_object_list\": [{\"name\": \"Cube\"}]}, \"geometrical_objects\": {\"object_list\": [{\"element_connections\": [[4, 5, 0], [5, 6, 1], [6, 7, 2], [7, 4, 3], [0, 1, 3], [7, 6, 4], [6, 2, 1], [6, 5, 4], [5, 1, 0], [7, 3, 2], [1, 2, 3], [4, 0, 3]], \"name\": \"Cube\", \"vertex_list\": [[-0.25, -0.25, -0.25], [-0.25, 0.25, -0.25], [0.25, 0.25, -0.25], [0.25, -0.25, -0.25], [-0.25, -0.25, 0.25], [-0.25, 0.25, 0.25], [0.25, 0.25, 0.25], [0.25, -0.25, 0.25]], \"location\": [0.0, 0.0, 0.0]}]}, \"viz_output\": {\"all_iterations\": true, \"step\": \"1\", \"end\": \"1\", \"export_all\": true, \"start\": \"0\"}, \"materials\": {\"material_dict\": {}}, \"cellblender_version\": \"0.1.54\", \"cellblender_source_sha1\": \"6a572dab58fa0f770c46ce3ac26b01f3a66f2096\"}}";
      //	text = "{\"mcell\": [3]}";        // OK
      //	text = "{\"mcell\": \"\"}";       // OK
      // 	text = "{\"mcell\": [ ]}";        // Fails with: Unexpected char (]) at 12 in {"mcell": [ ]}
      // 	text = "{\"mcell\": { }}";        // Fails with: Unexpected char (s) at 714 in {"mcell": { }}
      // 	text = "{\"mcell\": []}";         // Fails with segment fault
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

char *dyn_text = (char *) malloc (strlen(text)+1);
strcpy ( dyn_text, text );
text = dyn_text;
*/
  text_length = strlen(text);

  printf ( "Parsing text of length %d\n", text_length );
  // printf ( "Text: %s\n", text );

  json_element *root_element = new_empty_json_array_element ( NULL, 0, text_length-1, 0 );

  parse_element ( root_element, NULL, 0, 0 );

  // dump_json_element_tree ( root_element, 80, 1 );

  printf ( "\n\n==========\n\n" );

  return ( root_element );
}


////////////////////////////////////////
/////  Functions for External Use  /////
////////////////////////////////////////

int json_get_int_value ( json_element *je ) {
  int return_value = 0;
  char save;
  if (je->type == JSON_VAL_NUMBER) {
    save = text[je->end];
    text[je->end] = '\0';
    sscanf ( &text[je->start], " %d", &return_value );
    text[je->end] = save;
  } else if (je->type == JSON_VAL_STRING) {
    // printf ( "Warning: Expected a JSON Number, but got %s\n", get_json_name(je->type) );
    save = text[je->end];
    text[je->end] = '\0';
    sscanf ( &text[je->start], " %d", &return_value );
    text[je->end] = save;
  } else {
    printf ( "Error: Expected a JSON Number or String, but got %s\n", get_json_name(je->type) );
    exit(1);
  }
  return ( return_value );
}

double json_get_float_value ( json_element *je ) {
  double return_value = 0;
  char save;
  if (je->type == JSON_VAL_NUMBER) {
    save = text[je->end];
    text[je->end] = '\0';
    sscanf ( &text[je->start], " %lg", &return_value );
    text[je->end] = save;
  } else if (je->type == JSON_VAL_STRING) {
    // printf ( "Warning: Expected a JSON Number, but got %s\n", get_json_name(je->type) );
    save = text[je->end];
    text[je->end] = '\0';
    sscanf ( &text[je->start], " %lg", &return_value );
    text[je->end] = save;
  } else {
    printf ( "Error: Expected a JSON Number or String, but got %s\n", get_json_name(je->type) );
    exit(1);
  }
  return ( return_value );
}

int json_get_bool_value ( json_element *je ) {
  if ( (je->type != JSON_VAL_TRUE) && (je->type != JSON_VAL_FALSE) ) {
    printf ( "Call of json_get_bool_value on element that's neither True nor False.\n" );
    exit(1);
  }
  if (je->type == JSON_VAL_TRUE) {
    return ( 1 );
  } else {
    return ( 0 );
  }
}

char *json_get_string_value ( json_element *je ) {
  char *return_value = NULL;
  char save;
  if (je->type != JSON_VAL_STRING) {
    printf ( "Call of json_get_string_value on element that's not a string.\n" );
    exit(1);
  }
  save = text[je->end];
  text[je->end] = '\0';
  return_value = (char *) malloc ( 1 + je->end - je->start );
  strcpy ( return_value, &text[je->start] );
  text[je->end] = save;
  return ( return_value );
}


json_element *json_get_element_with_key ( json_element *tree, char *key ) {
  // printf ( "Top of json_get_element_with_key with key = %s\n", key );

  if (tree == NULL) {
    printf ( "Error: can't call json_get_element_with_key on NULL object\n" );
    return ( NULL );
    exit(1);
  }
  if (tree->type != JSON_VAL_OBJECT) {
    printf ( "Error: can't call json_get_element_with_key on non-dictionary object\n" );
    exit(1);
  }

  json_element *e;
  int sub_num = 0;
  e = tree->subs[sub_num];
  while ( (e != NULL) && (strcmp(e->name,key) != 0) ) {
    sub_num += 1;
    e = tree->subs[sub_num];
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
    exit(1);
  }
  if ((tree->type != JSON_VAL_ARRAY) && (tree->type != JSON_VAL_OBJECT)) {
    printf ( "Error: can't call json_get_element_by_index on non-collection object\n" );
    exit(1);
  }

  json_element *e;
  e = tree->subs[index];

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

