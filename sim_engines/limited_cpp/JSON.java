import java.io.*;
import java.util.*;

////  Temporary Representation While Parsing  ////

class json_element {
  public static final int JSON_VAL_UNDEF=-1;
  public static final int JSON_VAL_NULL=0;
  public static final int JSON_VAL_TRUE=1;
  public static final int JSON_VAL_FALSE=2;
  public static final int JSON_VAL_NUMBER=3;
  public static final int JSON_VAL_STRING=4;
  public static final int JSON_VAL_ARRAY=5;
  public static final int JSON_VAL_OBJECT=6;
  public static final int JSON_VAL_KEYVAL=7;
  int type  = JSON_VAL_UNDEF;
  int start = 0;
  int end   = 0;
  int depth = 0;
  public json_element(int what, int start, int end, int depth) {
    this.type = what;
    this.start = start;
    this.end = end;
    this.depth = depth;
  }
  public void update_element(int what, int start, int end, int depth) {
    this.type = what;
    this.start = start;
    this.end = end;
    this.depth = depth;
  }
  public String get_name () {
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
}

class json_parser {
  String text = "";
  Vector<json_element> elements = new Vector<json_element>();
  
  json_parser(String text) {
    this.text = text;
    elements = new Vector<json_element>();
  }

  public void parse ( json_array parent ) {	  
	  parse_element ( parent, 0, 0 );
  }

  json_element pre_store_skipped ( int what, int start, int end, int depth ) {
    json_element je = new json_element ( what, start, end, depth );
    elements.addElement(je);
    // System.out.println ( "Pre-Skipped " + what + " at depth " + depth + " from " + start + " to " + end );
    return je;
  }

  void post_store_skipped ( int what, int start, int end, int depth ) {
    json_element je = new json_element ( what, start, end, depth );
    elements.addElement(je);
    // System.out.println ( "Post-Skipped " + what + " at depth " + depth + " from " + start + " to " + end );
  }

  void post_store_skipped ( int what, int start, int end, int depth, json_element je ) {
    je.update_element ( what, start, end, depth );
    // System.out.println ( "Post-Skipped " + what + " at depth " + depth + " from " + start + " to " + end );
  }

  public void dump ( int max_len ) {
    json_element j;
    for (int i=0; i<elements.size(); i++) {
      j = (json_element)(elements.elementAt(i));
      for (int d=0; d<j.depth; d++) {
        System.out.print ( "    " );
      }
      String display;
      if ( (j.end - j.start) <= max_len ) {
        display = text.substring(j.start,j.end);
      } else {
        display = text.substring(j.start,j.start+max_len-4) + " ...";
      }
      // System.out.println ( "|-" + j.get_name() + " at depth " + j.depth + " from " + j.start + " to " + (j.end-1) + " = " + display );
    }
  }

  int skip_whitespace ( int index, int depth ) {
    int i = index;
    int max = text.length();
    while ( Character.isWhitespace(text.charAt(i)) ) {
      i++;
      if (i >= max) {
        return ( -1 );
      }
    }
    return i;
  }

  int skip_sepspace ( int index, int depth ) {
    int i = index;
    int max = text.length();
    while ( (text.charAt(i)==',') || Character.isWhitespace(text.charAt(i)) ) {
      i++;
      if (i >= max) {
        return ( -1 );
      }
    }
    return i;
  }

  static final String leading_number_chars = "-0123456789";
  static final String null_template = "null";
  static final String true_template = "true";
  static final String false_template = "false";

  int parse_element ( Object parent, int index, int depth ) {
    int start = skip_whitespace ( index, depth );
    if (start >= 0) {
      if ( text.charAt(start) == '{' ) {
        // This will add an object object to the parent
        start = parse_object ( parent, start, depth );
      } else if ( text.charAt(start) == '[' ) {
        // This will add an array object to the parent
        start = parse_array ( parent, start, depth );
      } else if ( text.charAt(start) == '\"' ) {
        // This will add a string object to the parent
        start = parse_string ( parent, start, depth );
      } else if ( leading_number_chars.indexOf(text.charAt(start)) >= 0 ) {
        // This will add a number object to the parent
        start = parse_number ( parent, start, depth );
      } else if ( null_template.regionMatches(0,text,start,4) ) {
        post_store_skipped ( json_element.JSON_VAL_NULL, start, start+4, depth );
        // Add a null object to the parent
        json_array p = (json_array)parent;
        p.add ( new json_null() );
        start += 4;
      } else if ( true_template.regionMatches(0,text,start,4) ) {
        post_store_skipped ( json_element.JSON_VAL_TRUE, start, start+4, depth );
        // Add a true object to the parent
        json_array p = (json_array)parent;
        p.add ( new json_true() );
        start += 4;
      } else if ( false_template.regionMatches(0,text,start,5) ) {
        post_store_skipped ( json_element.JSON_VAL_FALSE, start, start+5, depth );
        // Add a false object to the parent
        json_array p = (json_array)parent;
        p.add ( new json_false() );
        start += 5;
      } else {
        System.out.println ( "Unexpected char (" + text.charAt(start) + ") in " + text );
      }
    }
    return start;
  }

  int parse_keyval ( Object parent, int index, int depth ) {

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
  }

  int parse_object ( Object parent, int index, int depth ) {
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
  }

  int parse_array ( Object parent, int index, int depth ) {
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
  }

  int parse_string ( Object parent, int index, int depth ) {
    int end = index+1;
    while (text.charAt(end) != '"') {
      end++;
    }
    post_store_skipped ( json_element.JSON_VAL_STRING, index, end+1, depth );

    json_array p = (json_array)parent;
    p.add ( new json_string(text.substring(index+1,end)) );

    return (end + 1);
  }

  int parse_number ( Object parent, int index, int depth ) {
    int end = index;
    String number_chars = "0123456789.-+eE";
    while (number_chars.indexOf(text.charAt(end)) >= 0 ) {
      end++;
    }
    post_store_skipped ( json_element.JSON_VAL_NUMBER, index, end, depth );

    json_array p = (json_array)parent;
    p.add ( new json_number(text.substring(index,end)) );

    return (end);
  }

}


////////////////   Internal Representation of Data after Parsing   /////////////////

class json_object extends HashMap<String,Object> {
}

class json_array extends ArrayList<Object> {
}

class json_primitive {
  public String text;
}

class json_number extends json_primitive {
  public double value = 0.0;
  public boolean as_int = false;
  json_number ( String s ) {
    this.text = s;
  }
  json_number ( int v ) {
    this.value = v;
    this.as_int = true;
  }
  json_number ( double v ) {
    this.value = v;
    this.as_int = false;
  }
}

class json_string extends json_primitive {
  json_string ( String s ) {
    this.text = s;
  }
}

class json_true extends json_primitive {
  json_true () { }
  json_true ( String s ) {
    this.text = s;
  }
}

class json_false extends json_primitive {
  json_false () { }
  json_false ( String s ) {
    this.text = s;
  }
}

class json_null extends json_primitive {
  json_null () { }
  json_null ( String s ) {
    this.text = s;
  }
}


public class JSON {
  static Class json_primitive_class = new json_primitive().getClass();
  static Class json_null_class = new json_null("").getClass();
  static Class json_true_class = new json_true("").getClass();
  static Class json_false_class = new json_false("").getClass();
  static Class json_string_class = new json_string("").getClass();
  static Class json_number_class = new json_number("").getClass();
  static Class json_array_class = new json_array().getClass();
  static Class json_object_class = new json_object().getClass();
  static Class string_class = new String("").getClass();

  static void indent ( int n ) {
    for (int i=0; i<n; i++) {
      System.out.print ( "  " );
    }
  }

  static void dump_json_item ( Object item, int depth ) {
    // indent(depth); System.out.print ( "Dumping an item" );
    Class item_class = item.getClass();
    if (item_class == json_null_class) {
      indent(depth); System.out.println ( "Null" );
    } else if (item_class == json_true_class) {
      indent(depth); System.out.println ( "True" );
    } else if (item_class == json_false_class) {
      indent(depth); System.out.println ( "False" );
    } else if (item_class == json_number_class) {
      indent(depth); System.out.println ( "Number: " + ((json_number)item).text );
    } else if (item_class == json_string_class) {
      indent(depth); System.out.println ( "String: \"" + ((json_string)item).text + "\"" );
    } else if (item_class == json_array_class) {
      indent(depth); System.out.print ( "Array:\n" );
      json_array jo = (json_array)item;
      int i = 0;
      for (Object child : jo) {
        if (child == null) {
          System.out.println ( "List[" + i + "] = Null." );
        } else {
          dump_json_item ( child, depth+1 );
        }
      }
    } else if (item_class == json_object_class) {
      indent(depth); System.out.print ( "Object:\n" );
      json_object jo = (json_object)item;
      for (Object key : jo.keySet()) {
        if (key == null) {
          indent(depth); System.out.print ( " Key = Null." );
          System.exit(1);
        } else {
          indent(depth); System.out.print ( " Key = " + key + ":\n" );
          if (key.getClass() == string_class) {
            Object child = jo.get(key);
            dump_json_item ( child, depth+1 );
          } else {
            System.out.println ( "Non-String key!!!" );
            System.exit(1);
          }
        }
      }
    } else {
      System.out.print ( "Unknown primitive" );
    }
  }

	int w=600, h=400, num_rows=20, num_cols=30, diam=20;
	int num_cells=0;
	int cells[]=null;

	public static void main ( String args[] ) throws Exception {

	  System.out.println ( "JSON Parser" );

	  String text = null;

	  for (String arg : args) {
	    if ( arg.startsWith ( "f=") ) {
	      File f = new File ( arg.substring(2) );
	      char chars[] = new char[(int)(f.length())];
  		  BufferedReader fr = new BufferedReader ( new InputStreamReader ( new FileInputStream ( arg.substring(2) ) ) );
  		  fr.read(chars, 0, (int)(f.length()));
	      text = new String ( chars );
	    }
	  }

	  if ( text == null ) {
	    //text = "{ \"key\" : \"val\" }";
	    //text = " { \"ALL\" : [ 2, -1, {\"a\":1,\"b\":2,\"c\":3}, { \"mc\":[ { \"a\":0 }, 2, true, [9,[0,3],\"a\",3], false, null, 5, [1,2,3], \"xyz\" ], \"x\":\"y\" }, -3, 7 ] }  ";
	    //text = " { \"ALL\" : [\n 2, -1, {\"a\":1,\"b\":2,\"c\":3},\n { \"mc\":[ { \"a\":0 },\n 2, true, [9,[0,3],\"a\",3],\n false, null, 5, [1,2,3], \"xyz\" ],\n \"x\":\"y\" }, -3, 7 ] }  ";
	    text = "{\"A\":true,\"mc\":[{\"a\":0.01},1e-5,2,true,[9,[0,3],\"a\",345],false,null,5,[1,2,3],\"xyz\"],\"x\":\"y\"}";
	    //text = "\n{\"mcell\": {\"blender_version\": [2, 68, 0], \"api_version\": 0, \"reaction_data_output\": {\"mol_colors\": false, \"reaction_output_list\": [], \"plot_legend\": \"0\", \"combine_seeds\": true, \"plot_layout\": \" plot \"}, \"define_molecules\": {\"molecule_list\": [{\"export_viz\": false, \"diffusion_constant\": \"1e-7\", \"data_model_version\": \"DM_2014_10_24_1638\", \"custom_space_step\": \"\", \"maximum_step_length\": \"\", \"mol_name\": \"a\", \"mol_type\": \"3D\", \"custom_time_step\": \"\", \"target_only\": false}, {\"export_viz\": false, \"diffusion_constant\": \"1e-7\", \"data_model_version\": \"DM_2014_10_24_1638\", \"custom_space_step\": \"\", \"maximum_step_length\": \"\", \"mol_name\": \"b\", \"mol_type\": \"3D\", \"custom_time_step\": \"\", \"target_only\": false}], \"data_model_version\": \"DM_2014_10_24_1638\"}, \"define_reactions\": {\"reaction_list\": []}, \"data_model_version\": \"DM_2014_10_24_1638\", \"define_surface_classes\": {\"surface_class_list\": []}, \"parameter_system\": {\"model_parameters\": []}, \"define_release_patterns\": {\"release_pattern_list\": []}, \"release_sites\": {\"release_site_list\": [{\"object_expr\": \"\", \"location_x\": \"0\", \"location_y\": \"0\", \"release_probability\": \"1\", \"stddev\": \"0\", \"quantity\": \"100\", \"pattern\": \"\", \"site_diameter\": \"0\", \"orient\": \"'\", \"name\": \"ra\", \"shape\": \"CUBIC\", \"quantity_type\": \"NUMBER_TO_RELEASE\", \"molecule\": \"a\", \"location_z\": \"0\"}, {\"object_expr\": \"\", \"location_x\": \"0\", \"location_y\": \".2\", \"release_probability\": \"1\", \"stddev\": \"0\", \"quantity\": \"100\", \"pattern\": \"\", \"site_diameter\": \"0\", \"orient\": \"'\", \"name\": \"rb\", \"shape\": \"CUBIC\", \"quantity_type\": \"NUMBER_TO_RELEASE\", \"molecule\": \"b\", \"location_z\": \"0\"}]}, \"modify_surface_regions\": {\"modify_surface_regions_list\": []}, \"initialization\": {\"center_molecules_on_grid\": false, \"iterations\": \"10\", \"warnings\": {\"missing_surface_orientation\": \"ERROR\", \"high_probability_threshold\": \"1.0\", \"negative_diffusion_constant\": \"WARNING\", \"degenerate_polygons\": \"WARNING\", \"lifetime_too_short\": \"WARNING\", \"negative_reaction_rate\": \"WARNING\", \"high_reaction_probability\": \"IGNORED\", \"missed_reactions\": \"WARNING\", \"lifetime_threshold\": \"50\", \"useless_volume_orientation\": \"WARNING\", \"missed_reaction_threshold\": \"0.0010000000474974513\", \"all_warnings\": \"INDIVIDUAL\"}, \"space_step\": \"\", \"radial_directions\": \"\", \"radial_subdivisions\": \"\", \"vacancy_search_distance\": \"\", \"time_step_max\": \"\", \"accurate_3d_reactions\": true, \"notifications\": {\"probability_report_threshold\": \"0.0\", \"varying_probability_report\": true, \"probability_report\": \"ON\", \"iteration_report\": true, \"progress_report\": true, \"molecule_collision_report\": false, \"box_triangulation_report\": false, \"release_event_report\": true, \"file_output_report\": false, \"partition_location_report\": false, \"all_notifications\": \"INDIVIDUAL\", \"diffusion_constant_report\": \"BRIEF\", \"final_summary\": true}, \"time_step\": \"5e-6\", \"interaction_radius\": \"\", \"surface_grid_density\": \"10000\", \"microscopic_reversibility\": \"OFF\", \"partitions\": {\"x_start\": \"-1.0\", \"x_step\": \"0.019999999552965164\", \"y_step\": \"0.019999999552965164\", \"y_end\": \"1.0\", \"recursion_flag\": false, \"z_end\": \"1.0\", \"x_end\": \"1.0\", \"z_step\": \"0.019999999552965164\", \"include\": false, \"y_start\": \"-1.0\"}}, \"model_objects\": {\"model_object_list\": [{\"name\": \"Cube\"}]}, \"geometrical_objects\": {\"object_list\": [{\"element_connections\": [[4, 5, 0], [5, 6, 1], [6, 7, 2], [7, 4, 3], [0, 1, 3], [7, 6, 4], [6, 2, 1], [6, 5, 4], [5, 1, 0], [7, 3, 2], [1, 2, 3], [4, 0, 3]], \"name\": \"Cube\", \"vertex_list\": [[-0.25, -0.25, -0.25], [-0.25, 0.25, -0.25], [0.25, 0.25, -0.25], [0.25, -0.25, -0.25], [-0.25, -0.25, 0.25], [-0.25, 0.25, 0.25], [0.25, 0.25, 0.25], [0.25, -0.25, 0.25]], \"location\": [0.0, 0.0, 0.0]}]}, \"viz_output\": {\"all_iterations\": true, \"step\": \"1\", \"end\": \"1\", \"export_all\": true, \"start\": \"0\"}, \"materials\": {\"material_dict\": {}}, \"cellblender_version\": \"0.1.54\", \"cellblender_source_sha1\": \"6a572dab58fa0f770c46ce3ac26b01f3a66f2096\"}}";
	    //text = "1, 2, 3";
		}

    json_array top = new json_array();
	  json_parser p = new json_parser( text );
	  p.parse ( top );
	  
	  dump_json_item ( top, 0 );

	}

}
