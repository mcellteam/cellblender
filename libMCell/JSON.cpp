/* File : JSON.cpp */

#include <string.h>
#include <string>
#include <cctype>
#include <iostream>
#include <vector>
#include <unordered_map>
#include <typeinfo>

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
      string local_text;
      local_text.assign (text);
      string display;
      if ( (j->end - j->start) <= max_len ) {
        display = local_text.substr(j->start,j->end-j->start);
      } else {
        display = local_text.substr(j->start,max_len-4);
      }
      cout << "|-" << j->get_name() << " at depth " << j->depth << " from " << j->start << " to " << (j->end-1) << " = " << display << endl;
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

  int parse_element ( void *parent, int index, int depth );
  int parse_keyval ( void *parent, int index, int depth );
  int parse_object ( void *parent, int index, int depth );
  int parse_array ( void *parent, int index, int depth );
  int parse_string ( void *parent, int index, int depth );
  int parse_number ( void *parent, int index, int depth );

};


////////////////   Internal Representation of Data after Parsing   /////////////////


//--> This was an attempt to get the typeid just one time for each object:  type_info json_object_type = typeid(new json_object());


class json_object : public unordered_map<string,void *> {
 public:
  virtual void print_self() {
    cout << "json_object" << endl;
    cout << "type = " << typeid(this).name() << endl;
  }
};

int global_depth = 0;

class json_array : public vector<void *> {
 public:
  virtual void print_self() {
    global_depth += 1;
    cout << "json_array is at " << this << endl;
    cout << "json_array contains " << this->size() << " elements" << endl;
    for (int i=0; i<this->size(); i++) {
      cout << "SUB OBJECT " << i << " at depth " << global_depth << " is a " << typeid(this[i]).name() << " at " << (void *)this << endl;
      this[i].print_self();
    }
    global_depth += -1;
    
    
    cout << "type.name = " << typeid(this).name() << endl;
    bool match = (typeid(this) == typeid(new json_array()));
    cout << "match = " << match << endl;
    match = (typeid(this) == typeid(new json_object()));
    cout << "match = " << match << endl;
    //cout << "type = " << typeid(this) << endl;
  }
};


class json_primitive {
 public:
  string text;
  virtual void print_self() {
    cout << "json_primitive" << endl;
  }
};

class json_number : public json_primitive {
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
  virtual void print_self() {
    cout << "json_number" << endl;
  }
};


class json_string : public json_primitive {
 public:
  json_string ( string s ) {
    this->text = s;
  }
  virtual void print_self() {
    cout << "json_string" << endl;
  }
};

class json_true : public json_primitive {
 public:
  json_true () { }
  json_true ( string s ) {
    this->text = s;
  }
  virtual void print_self() {
    cout << "json_true" << endl;
  }
};

class json_false : public json_primitive {
 public:
  json_false () { }
  json_false ( string s ) {
    this->text = s;
  }
  virtual void print_self() {
    cout << "json_false" << endl;
  }
};

class json_null : public json_primitive {
 public:
  json_null () { }
  json_null ( string s ) {
    this->text = s;
  }
  virtual void print_self() {
    cout << "json_null" << endl;
  }
};


////////////////////
// These are currently down here because I couldn't figure out how to forward reference the various json_type classes directly above
////////////////////

int json_parser::parse_element ( void *parent, int index, int depth ) {
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
      } else if ( strncmp ( null_template, &text[start], 4) == 0 ) {
        post_store_skipped ( JSON_VAL_NULL, start, start+4, depth );
        // Add a null object to the parent
        json_array *p = (json_array *)parent;
        json_null *val = new json_null;
        cout << "Created a json_null at " << (void *)val << " with parent at " << parent << endl;
        p->push_back( (void *)val );
        start += 4;
      } else if ( strncmp ( true_template, &text[start], 4) == 0 ) {
        post_store_skipped ( JSON_VAL_TRUE, start, start+4, depth );
        // Add a true object to the parent
        json_array *p = (json_array *)parent;
        json_true *val = new json_true;
        p->push_back( (void *)val );
        cout << "Created a json_true at " << (void *)val << " with parent at " << parent << endl;
        start += 4;
      } else if ( strncmp ( false_template, &text[start], 5) == 0 ) {
        post_store_skipped ( JSON_VAL_FALSE, start, start+5, depth );
        // Add a false object to the parent
        json_array *p = (json_array *)parent;
        json_false *val = new json_false;
        p->push_back( (void *)val );
        cout << "Created a json_false at " << (void *)val << " with parent at " << parent << endl;
        start += 5;
      } else {
        cout << "Unexpected char (" << text[start] << ") in " << text << endl;
      }
    }
    return start;
  }





int json_parser::parse_keyval ( void *parent, int index, int depth ) {

//////////////// NOTE: Should probably use std::pair to store these key/value pairs!!!!

    json_array *key_val = new json_array();

    json_element *je = pre_store_skipped ( JSON_VAL_KEYVAL, index, index, depth );
    index = skip_whitespace ( index, depth );
    int end = index;
    end = parse_string ( key_val, end, depth );

    end = skip_whitespace ( end, depth );
    end = end + 1;  // This is the colon separator (:)
    end = parse_element ( key_val, end, depth );
    post_store_skipped ( JSON_VAL_KEYVAL, index, end, depth, je );

    json_object *p = (json_object *)parent;
    json_string *s = (json_string *)(key_val->at(0));
    // cout << "Key = " << s->text << endl;
    p->insert ( { s->text, (void *)(key_val->at(1)) } );

    cout << "Created a json_keyval with parent at " << parent << endl;

    return (end);
  }




int json_parser::parse_object ( void *parent, int index, int depth ) {
    json_element *je = pre_store_skipped ( JSON_VAL_OBJECT, index, index, depth );
    int end = index+1;
    depth += 1;

    json_array *p = (json_array *)parent;
    json_object *o = new json_object();
    p->push_back ( (void *)o );

    cout << "Created a json_object at " << (void *)o << " with parent at " << parent << endl;

    while (text[end] != '}') {
      end = parse_keyval ( o, end, depth );
      end = skip_sepspace ( end, depth );
    }
    depth += -1;
    post_store_skipped ( JSON_VAL_OBJECT, index, end+1, depth, je );

    return (end + 1);
  }



int json_parser::parse_array ( void *parent, int index, int depth ) {

    json_element *je = pre_store_skipped ( JSON_VAL_ARRAY, index, index, depth );
    int end = index+1;
    depth += 1;

    json_array *p = (json_array *)parent;
    json_array *child = new json_array();
    p->push_back ( (void *)child );

    cout << "Created a json_array at " << (void *)child << " with parent at " << parent << endl;

    while (text[end] != ']') {
      end = parse_element ( child, end, depth );
      end = skip_sepspace ( end, depth );
    }
    depth += -1;
    post_store_skipped ( JSON_VAL_ARRAY, index, end+1, depth, je );
    return (end + 1);
  }


int json_parser::parse_string ( void *parent, int index, int depth ) {
    int end = index+1;
    while (text[end] != '"') {
      end++;
    }
    post_store_skipped ( JSON_VAL_STRING, index, end+1, depth );

    json_array *p = (json_array *)parent;

    string local_text;
    local_text.assign (text);

    string sub_string = local_text.substr(index+1,end-index);
    
    json_string *val = new json_string(sub_string);
    p->push_back( (void *)val );

    cout << "Created a json_string at " << (void *)val << " with parent at " << parent << endl;

    return (end + 1);
  }


int json_parser::parse_number ( void *parent, int index, int depth ) {
    int end = index;
    const char *number_chars = "0123456789.-+eE";
    while ( strchr(number_chars,text[end]) != NULL ) {
      end++;
    }
    post_store_skipped ( JSON_VAL_NUMBER, index, end, depth );

    json_array *p = (json_array *)parent;

    string local_text;
    local_text.assign (text);

    string sub_string = local_text.substr(index,end-index);
    
    json_number *val = new json_number(sub_string);
    p->push_back( (void *)val );

    cout << "Created a json_string at " << (void *)val << " with parent at " << parent << endl;

    return (end);
  }


int main() {
  cout << "JSON C++ Parser" << endl;

  //char *text = "{\"A\":true,\"mc\":[{\"a\":0.01},1e-5,2,true,[9,[0,3],\"a\",345],false,null,5,[1,2,3],\"xyz\"],\"x\":\"y\"}";
  char *text = "[9,[0,3],{\"a\":5}]";

  json_array top;
  json_parser p = json_parser(text);
  p.parse ( &top );
  p.dump(90);

  top.print_self();

  json_element *je = new json_element(0,0,0,0);
  cout << "Hello!! " << JSON_VAL_ARRAY << endl;


  return ( 0 );
}


