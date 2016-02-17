/* File : JSON.cpp */

#include <string.h>
#include <string>
#include <cctype>
#include <iostream>
#include <vector>
#include <unordered_map>

using namespace std;

#define JSON_VAL_UNDEF -1
#define JSON_VAL_NULL 0
#define JSON_VAL_TRUE 1
#define JSON_VAL_FALSE 2
#define JSON_VAL_NUMBER 3
#define JSON_VAL_STRING 4
#define JSON_VAL_ARRAY 5
#define JSON_VAL_OBJECT 6
#define JSON_VAL_KEYVAL 7


class json_element {
 public:
  /*
  const int JSON_VAL_UNDEF=-1;
  const int JSON_VAL_NULL=0;
  const int JSON_VAL_TRUE=1;
  const int JSON_VAL_FALSE=2;
  const int JSON_VAL_NUMBER=3;
  const int JSON_VAL_STRING=4;
  const int JSON_VAL_ARRAY=5;
  const int JSON_VAL_OBJECT=6;
  const int JSON_VAL_KEYVAL=7;
  */
  int type  = JSON_VAL_UNDEF;
  int start = 0;
  int end   = 0;
  int depth = 0;
  json_element(int what, int start, int end, int depth) {
    this->type = what;
    this->start = start;
    this->end = end;
    this->depth = depth;
  }
  void update_element(int what, int start, int end, int depth) {
    this->type = what;
    this->start = start;
    this->end = end;
    this->depth = depth;
  }
  string get_name () {
    if (type == JSON_VAL_UNDEF) return ( "Undefined" );
    if (type == JSON_VAL_NULL) return ( "NULL" );
    if (type == JSON_VAL_TRUE) return ( "True" );
    if (type == JSON_VAL_FALSE) return ( "False" );
    if (type == JSON_VAL_NUMBER) return ( "Number" );
    if (type == JSON_VAL_STRING) return ( "String" );
    if (type == JSON_VAL_ARRAY) return ( "Array" );
    if (type == JSON_VAL_OBJECT) return ( "Object" );
    if (type == JSON_VAL_KEYVAL) return ( "Key:Val" );
    return ( "Unknown" );
  }
};


class json_object;
class json_array;

class json_parser {
 public:

  const char *leading_number_chars = "-0123456789";
  const char *null_template = "null";
  const char *true_template = "true";
  const char *false_template = "false";

  char *text = NULL;
  vector<json_element *> elements;

  json_parser ( char *text ) {
    this->text = text;
    elements = vector<json_element *>();
  }

  void parse ( json_array *parent ) {	  
	  parse_element ( parent, 0, 0 );
  }

  json_element *pre_store_skipped ( int what, int start, int end, int depth ) {
    json_element *je = new json_element ( what, start, end, depth );
    elements.push_back(je);
    // System.out.println ( "Pre-Skipped " + what + " at depth " + depth + " from " + start + " to " + end );
    return je;
  }


  void post_store_skipped ( int what, int start, int end, int depth ) {
    json_element *je = new json_element ( what, start, end, depth );
    elements.push_back(je);
    // System.out.println ( "Post-Skipped " + what + " at depth " + depth + " from " + start + " to " + end );
  }

  void post_store_skipped ( int what, int start, int end, int depth, json_element *je ) {
    je->update_element ( what, start, end, depth );
    // System.out.println ( "Post-Skipped " + what + " at depth " + depth + " from " + start + " to " + end );
  }

  void dump ( int max_len ) {
    json_element *j;
    for (int i=0; i<elements.size(); i++) {
      j = elements.at(i);
      for (int d=0; d<j->depth; d++) {
        cout << "    ";
      }
      string text;
      text.assign (this->text);
      string display;
      if ( (j->end - j->start) <= max_len ) {
        display = text.substr(j->start,j->end-j->start);
      } else {
        display = text.substr(j->start,max_len-4);
      }
      // System.out.println ( "|-" + j.get_name() + " at depth " + j.depth + " from " + j.start + " to " + (j.end-1) + " = " + display );
    }
  }

  int skip_whitespace ( int index, int depth ) {
    int i = index;
    int max = strlen(text);
    while ( isspace(text[i]) ) {
      i++;
      if (i >= max) {
        return ( -1 );
      }
    }
    return i;
  }

  int skip_sepspace ( int index, int depth ) {
    int i = index;
    int max = strlen(text);
    while ( (text[i]==',') || isspace(text[i]) ) {
      i++;
      if (i >= max) {
        return ( -1 );
      }
    }
    return i;
  }


  int parse_element ( void *parent, int index, int depth ) {
    int start = skip_whitespace ( index, depth );
    if (start >= 0) {
      if ( text[start] == '{' ) {
        // This will add an object object to the parent
        start = parse_object ( parent, start, depth );
      } else if ( text[start] == '[' ) {
        // This will add an array object to the parent
        start = parse_array ( parent, start, depth );
      } else if ( text[start] == '\"' ) {
        // This will add a string object to the parent
        start = parse_string ( parent, start, depth );
      } else if ( strchr(leading_number_chars,text[start]) != NULL ) {
        // This will add a number object to the parent
        start = parse_number ( parent, start, depth );
      } else if ( strncmp ( null_template, &text[start], 4) ) {
        post_store_skipped ( JSON_VAL_NULL, start, start+4, depth );
        // Add a null object to the parent
        json_array *p = (json_array *)parent;
//fix        p.add ( new json_null() );
        start += 4;
      } else if ( strncmp ( true_template, &text[start], 4) ) {
        post_store_skipped ( JSON_VAL_TRUE, start, start+4, depth );
        // Add a true object to the parent
        json_array *p = (json_array *)parent;
//fix        p.add ( new json_true() );
        start += 4;
      } else if ( strncmp ( false_template, &text[start], 5) ) {
        post_store_skipped ( JSON_VAL_FALSE, start, start+5, depth );
        // Add a false object to the parent
        json_array *p = (json_array *)parent;
//fix        p.add ( new json_false() );
        start += 5;
      } else {
        cout << "Unexpected char (" << text[start] << ") in " << text << endl;
      }
    }
    return start;
  }


  int parse_keyval ( void *parent, int index, int depth ) {
/*
    json_array key_val = new json_array();

    json_element je = pre_store_skipped ( json_element.JSON_VAL_KEYVAL, index, index, depth );
    index = skip_whitespace ( index, depth );
    int end = index;
    end = parse_string ( key_val, end, depth );


    end = skip_whitespace ( end, depth );
    end = end + 1;  // This is the colon separator (:)
    end = parse_element ( key_val, end, depth );
    post_store_skipped ( json_element.JSON_VAL_KEYVAL, index, end, depth, je );

    json_object p = (json_object)parent;
    json_string s = (json_string)(key_val.get(0));
    p.put ( s.text, key_val.get(1) );

    return (end);
*/ return ( index + 1 );
  }

  int parse_object ( void *parent, int index, int depth ) {
/*
    json_element je = pre_store_skipped ( json_element.JSON_VAL_OBJECT, index, index, depth );
    int end = index+1;
    depth += 1;

    json_array p = (json_array)parent;
    json_object o = new json_object();
    p.add ( o );

    while (text.charAt(end) != '}') {
      end = parse_keyval ( o, end, depth );
      end = skip_sepspace ( end, depth );
    }
    depth += -1;
    post_store_skipped ( json_element.JSON_VAL_OBJECT, index, end+1, depth, je );
    return (end + 1);
*/ return ( index + 1 );
  }

  int parse_array ( void *parent, int index, int depth ) {
/*
    json_element je = pre_store_skipped ( json_element.JSON_VAL_ARRAY, index, index, depth );
    int end = index+1;
    depth += 1;

    json_array p = (json_array)parent;
    json_array child = new json_array();
    p.add ( child );

    while (text.charAt(end) != ']') {
      end = parse_element ( child, end, depth );
      end = skip_sepspace ( end, depth );
    }
    depth += -1;
    post_store_skipped ( json_element.JSON_VAL_ARRAY, index, end+1, depth, je );
    return (end + 1);
*/ return ( index + 1 );
  }

  int parse_string ( void *parent, int index, int depth ) {
/*
    int end = index+1;
    while (text.charAt(end) != '"') {
      end++;
    }
    post_store_skipped ( json_element.JSON_VAL_STRING, index, end+1, depth );

    json_array p = (json_array)parent;
    p.add ( new json_string(text.substring(index+1,end)) );

    return (end + 1);
*/ return ( index + 1 );
  }

  int parse_number ( void *parent, int index, int depth ) {
/*
    int end = index;
    String number_chars = "0123456789.-+eE";
    while (number_chars.indexOf(text.charAt(end)) >= 0 ) {
      end++;
    }
    post_store_skipped ( json_element.JSON_VAL_NUMBER, index, end, depth );

    json_array p = (json_array)parent;
    p.add ( new json_number(text.substring(index,end)) );

    return (end);
*/ return ( index + 1 );
  }


};


////////////////   Internal Representation of Data after Parsing   /////////////////


class json_object : unordered_map<string,void *> {
};


class json_array : vector<void *> {
};


class json_primitive {
 public:
  string text;
};

class json_number : json_primitive {
 public:
  double value = 0.0;
  bool as_int = false;
  json_number ( string s ) {
    this->text = s;
  }
  json_number ( int v ) {
    this->value = v;
    this->as_int = true;
  }
  json_number ( double v ) {
    this->value = v;
    this->as_int = false;
  }
};


class json_string : json_primitive {
 public:
  json_string ( string s ) {
    this->text = s;
  }
};

class json_true : json_primitive {
 public:
  json_true () { }
  json_true ( string s ) {
    this->text = s;
  }
};

class json_false : json_primitive {
 public:
  json_false () { }
  json_false ( string s ) {
    this->text = s;
  }
};

class json_null : json_primitive {
 public:
  json_null () { }
  json_null ( string s ) {
    this->text = s;
  }
};


int main() {
  cout << "JSON C++ Parser" << endl;

  char *text = "{\"A\":true,\"mc\":[{\"a\":0.01},1e-5,2,true,[9,[0,3],\"a\",345],false,null,5,[1,2,3],\"xyz\"],\"x\":\"y\"}";

  json_array top;
  json_parser p = json_parser(text);
  p.parse ( &top );

  json_element *je = new json_element(0,0,0,0);
  cout << "Hello!! " << JSON_VAL_ARRAY << endl;


  return ( 0 );
}


