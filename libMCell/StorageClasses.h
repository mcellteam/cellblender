#ifndef StorageClasses_H
#define StorageClasses_H

/* Note that for some reason, Templated classes can't be easily separated from their headers. */
/* As a result, this class is one big file. */

#include <iostream>
#include <vector>
#include <cstdlib>
#include <string>
#include <string.h>
#include <stdexcept>

using namespace std;


template <class T> class ArrayStore {

 private:

  int capacity;
  T *item_array;

 public:

  ArrayStore<T>() {
    capacity = 0;
    item_array = NULL;
  }

  T &operator[](int index) {
    if (index >= capacity) {
      expand_capacity(index);
    }
    return item_array[index];
  }

  int get_size() {
    return ( capacity );
  }

  int append (T t) {
    expand_capacity(get_size());
    item_array[get_size()-1] = t;
  }

  void dump () {
    cout << "======== Begin Dump ========" << endl;
    cout << "A contains " << get_size() << " elements" << endl;
    for (int i=0; i<capacity; i++) {
      cout << "A[" << i << "] = " << item_array[i] << endl;
    }
    cout << "========= End Dump =========" << endl;
  }

 private:
  void expand_capacity ( int index ) {
    // Increase the capacity to include index
    int new_capacity = 1 + index;
    // cout << "Capacity: " << capacity << " -> " << new_capacity << endl;
    if (new_capacity > capacity) {
      T *new_item_array;
      new_item_array = (T *) malloc ( sizeof(T) * new_capacity );
      for (int i=0; i<capacity; i++) {
        new_item_array[i] = item_array[i];
      }
      T *old_item_array = item_array;
      item_array = new_item_array;
      if (old_item_array != NULL) free ( old_item_array );
      capacity = new_capacity;
    }
  }

};


template <class T> class MapStore {

 private:

  int capacity;
  int num_items;
  T *item_array;
  char **keys;

 public:

  MapStore<T>() {
    capacity = 0;
    num_items = 0;
    item_array = NULL;
    keys = NULL;
  }

  T &operator[](const char *key) {
    int index = get_or_make_index_of_key ( key );
    return item_array[index];
  }

  int get_num_items() {
    return ( num_items );
  }

  char *get_key(int i) {
    return ( keys[i] );
  }

  void dump () {
    cout << "======== Begin Dump ========" << endl;
    for (int i=0; i<num_items; i++) {
      cout << "D[" << keys[i] << "] = " << item_array[get_or_make_index_of_key(keys[i])] << endl;
    }
    cout << "========= End Dump =========" << endl;
  }

 private:

  void expand_capacity() {
    // Increase the capacity by some amount
    int new_capacity = 1 + (3 * capacity / 2);
    // cout << "Capacity: " << capacity << " -> " << new_capacity << endl;

    char **new_keys;
    T *new_item_array;

    new_keys = (char **) malloc ( sizeof(char *) * new_capacity );
    if (new_keys == NULL) throw "Unable to malloc space for a new_keys array.";
    new_item_array = (T *) malloc ( sizeof(T) * new_capacity );

    for (int i=0; i<capacity; i++) {
      new_keys[i] = keys[i];
      new_item_array[i] = item_array[i];
    }

    char **old_keys = keys;
    keys = new_keys;
    if (old_keys != NULL) free ( old_keys );

    T *old_item_array = item_array;
    item_array = new_item_array;
    if (old_item_array != NULL) free ( old_item_array );

    capacity = new_capacity;
  }

  int find_index_of_key ( const char *key ) {
    // Returns either a valid index or -1
    if ( (keys == NULL) || (num_items == 0) ) {
      return ( -1 );
    } else {
      int index =0;
      char *k;
      do {
        k = keys[index];
        if ( strcmp (key, k) == 0 ) {
          return ( index );
        }
        index += 1;
      } while ( index < num_items );
      return ( -1 );
    }
  }

  int get_or_make_index_of_key ( const char *key ) {
    int index = find_index_of_key(key);
    if (index < 0) {
      // Need to create an entry for this key, so resize the array if needed
      if ((num_items+1) >= capacity) {
        expand_capacity();
      }
      if (num_items >= capacity) throw "Number of items exceeds capacity.";
      // Allocate space for a copy of the new key and make the copy
      keys[num_items] = (char *) malloc ( strlen(key) + 1 );
      if (keys[num_items] == NULL) throw "Unable to malloc space for a new key.";
      strcpy ( keys[num_items], key );
      index = num_items;
      num_items += 1;
    }
    return ( index );
  }

};

#ifdef RUN_STORAGE_CLASSES_MAIN

//  TEST CODE

class parent {
 public:
  int parent_int;
  parent () {
    parent_int = -1;
  }
  parent ( int p ) {
    parent_int = p;
  }
  virtual void dump() {
    cout << "Parent object with P val = " << parent_int << endl;
  }
};

class child : public parent {
 public:
  int child_int;
  child () : parent() {
    child_int = -2;
  }
  child ( int c ) : parent() {
    child_int = c;
  }
  child ( int p, int c ) : parent(p) {
    parent_int = p;
    child_int = c;
  }
  virtual void dump() {
    cout << "Child object with P val = " << parent_int << ", and C val = " << child_int << endl;
  }
};

int main()
{
  try {

    // These are a few different ways of making null-terminated strings:
    char ka[] = "cde";
    char *kp = (char *) "def";
    char *km = (char *) malloc(5); km[0]='e'; km[1]='f'; km[2]='g'; km[3]='\0';

    cout << "Testing MapStore<string>" << endl;
    MapStore<char *> S;
    S["abc"] = (char *)"ABC";
    S["xyz"] = (char *)"UVW";

    S.dump();

    cout << "Testing MapStore<double>" << endl;
    MapStore<double> D;
    D["a"] = 0.1;
    D["abc"] = 1.1;
    D["a"] = 0.2;
    D["bcd"] = 2.2;
    D[ka] = 3.3;
    D[kp] = 4.4;
    D[km] = 5.5;
    
    D["xyz"] = 55;

    D.dump();

    MapStore<parent *> P;
    P["p0"] = new parent();
    P["p1"] = new parent(1);
    P["p2"] = new parent(2);
    P["c0"] = new child();
    P["c1"] = new child(11);
    P["c2"] = new child(12,13);
    
    char *name = (char *) malloc ( 10 );
    for (int i=3; i<30; i++) {
      name[0] = 'c';
      name[1] = (char)('0'+i);
      name[2] = '\0';
      if ((i%4) == 0) {
        name[0] = 'p';
        P[name] = new parent ( i );
      } else {
        P[name] = new child (i,2*i);
      }
    }
    
    P.dump();
    
    int n = P.get_num_items();
    for (int i=0; i<n; i++) {
      cout << "Item " << i << " with key " << P.get_key(i) << ": ";
      P[P.get_key(i)]->dump();
    }

    cout << "Testing ArrayStore<string>" << endl;
    ArrayStore<char *> AS;
    AS[0] = (char *)"ABC";
    AS[1] = (char *)"UVW";
    
    AS.dump();

    cout << "Testing ArrayStore<double>" << endl;
    ArrayStore<double> AD;
    for (int i=0; i<11; i++) {
      AD[i] = 0.1 + (double)i*i;
    }
    AD[13] = 3.14159;
    AD[16] = 0.1 + (double)16*16;

    AD.dump();
    
    cout << "Try getting 20: " << AD[20] << endl;
    
    AD.dump();


    cout << "Testing ArrayStore<char>" << endl;
    ArrayStore<char> AB;
    for (int i=0; i<11; i++) {
      AB[i] = (char)(i*i);
    }
    AB[13] = (char)100;
    AB[16] = (char)200;
    
    AB.append ( (char)101 );
    AB.append ( (char)102 );
    AB.append ( (char)103 );

    for (int i=0; i<AB.get_size(); i++) {
      int cv = AB[i];
      cout << "Array[" << i << "] = " << cv << endl;
    }

  } catch (exception const& ex) {

    cerr << "*** Exception: " << ex.what() << endl;
    return -1;

  } catch (const char * ex) {

    cerr << "*** Exception: " << ex << endl;
    return -1;

  } catch ( ... ) {

    cerr << "*** Exception: Exception of unexpected type" << endl;
    return -1;

  }
  return 0;
}

#endif

#endif
