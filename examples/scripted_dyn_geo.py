scripted_dyn_geo_dm = {
  'api_version' : 0,
  'blender_version' : [2, 78, 0],
  'cellblender_source_sha1' : "0",
  'cellblender_version' : "0.1.54",
  'data_model_version' : "DM_2014_10_24_1638",
  'define_molecules' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'molecule_list' : [
      {
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2016_01_13_1930",
        'diffusion_constant' : "1e-5",
        'display' : {
          'color' : [0.0, 1.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Sphere_1",
          'scale' : 5.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "vm",
        'mol_type' : "3D",
        'target_only' : False
      }
    ]
  },
  'define_reactions' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'reaction_list' : []
  },
  'define_release_patterns' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'release_pattern_list' : []
  },
  'define_surface_classes' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'surface_class_list' : []
  },
  'geometrical_objects' : {
    'object_list' : [
      {
        'name' : "Cube",
        'location' : [0.0, 0.0, 0.0],
        'vertex_list': [ [1.0, 1.0, -1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [1.0, 1.0, 1.0], [1.0, -1.0, 1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, 1.0] ],
        'element_connections': [ [1, 2, 3], [7, 6, 5], [4, 5, 1], [5, 6, 2], [2, 6, 7], [0, 3, 7], [0, 1, 3], [4, 7, 5], [0, 4, 1], [1, 5, 2], [3, 2, 7], [4, 0, 7] ],
        'material_names' : ['Cube_mat']
      }
    ]
  },
  'initialization' : {
    'accurate_3d_reactions' : True,
    'center_molecules_on_grid' : False,
    'data_model_version' : "DM_2014_10_24_1638",
    'export_all_ascii' : False,
    'interaction_radius' : "",
    'iterations' : "500",
    'microscopic_reversibility' : "OFF",
    'notifications' : {
      'all_notifications' : "INDIVIDUAL",
      'box_triangulation_report' : False,
      'diffusion_constant_report' : "BRIEF",
      'file_output_report' : False,
      'final_summary' : True,
      'iteration_report' : True,
      'molecule_collision_report' : False,
      'partition_location_report' : False,
      'probability_report' : "ON",
      'probability_report_threshold' : "0",
      'progress_report' : True,
      'release_event_report' : True,
      'varying_probability_report' : True
    },
    'partitions' : {
      'data_model_version' : "DM_2016_04_15_1600",
      'include' : False,
      'recursion_flag' : False,
      'x_end' : "1",
      'x_start' : "-1",
      'x_step' : "0.05",
      'y_end' : "1",
      'y_start' : "-1",
      'y_step' : "0.05",
      'z_end' : "1",
      'z_start' : "-1",
      'z_step' : "0.05"
    },
    'radial_directions' : "",
    'radial_subdivisions' : "",
    'space_step' : "",
    'surface_grid_density' : "10000",
    'time_step' : "5e-6",
    'time_step_max' : "",
    'vacancy_search_distance' : "",
    'warnings' : {
      'all_warnings' : "INDIVIDUAL",
      'degenerate_polygons' : "WARNING",
      'high_probability_threshold' : "1",
      'high_reaction_probability' : "IGNORED",
      'lifetime_threshold' : "50",
      'lifetime_too_short' : "WARNING",
      'missed_reaction_threshold' : "0.001",
      'missed_reactions' : "WARNING",
      'missing_surface_orientation' : "ERROR",
      'negative_diffusion_constant' : "WARNING",
      'negative_reaction_rate' : "WARNING",
      'useless_volume_orientation' : "WARNING"
    }
  },
  'materials' : {
    'material_dict' : {
      'Cube_mat' : {
        'diffuse_color' : {
          'r' : 0.0,
          'g' : 0.8,
          'b' : 0.1,
          'a' : 0.2
        }
      }
    }
  },
  'model_objects' : {
    'data_model_version' : "DM_2017_03_16_1750",
    'model_object_list' : [
      {
        'dynamic' : True,
        'dynamic_display_source' : "files",
        'name' : "Cube",
        'script_name' : "dyn_geo.py"
      }
    ]
  },
  'modify_surface_regions' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'modify_surface_regions_list' : []
  },
  'mol_viz' : {
    'active_seed_index' : 0,
    'color_index' : 0,
    'color_list' : [
      [0.8, 0.0, 0.0],
      [0.0, 0.8, 0.0],
      [0.0, 0.0, 0.8],
      [0.0, 0.8, 0.8],
      [0.8, 0.0, 0.8],
      [0.8, 0.8, 0.0],
      [1.0, 1.0, 1.0],
      [0.0, 0.0, 0.0]
    ],
    'data_model_version' : "DM_2015_04_13_1700",
    'file_dir' : "",
    'file_index' : 456,
    'file_name' : "Scene.cellbin.456.dat",
    'file_num' : 501,
    'file_start_index' : 0,
    'file_step_index' : 1,
    'file_stop_index' : 500,
    'manual_select_viz_dir' : False,
    'render_and_save' : False,
    'seed_list' : ['seed_00001'],
    'viz_enable' : True,
    'viz_list' : ['mol_vm']
  },
  'parameter_system' : {
    'model_parameters' : [],
  },
  'reaction_data_output' : {
    'always_generate' : True,
    'combine_seeds' : True,
    'data_model_version' : "DM_2016_03_15_1800",
    'mol_colors' : True,
    'output_buf_size' : "",
    'plot_layout' : " plot ",
    'plot_legend' : "0",
    'reaction_output_list' : [],
    'rxn_step' : ""
  },
  'release_sites' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'release_site_list' : [
      {
        'data_model_version' : "DM_2015_11_11_1717",
        'location_x' : "0",
        'location_y' : "0",
        'location_z' : "0",
        'molecule' : "vm",
        'name' : "Release_Site_1",
        'object_expr' : "Cube",
        'orient' : "'",
        'pattern' : "",
        'points_list' : [],
        'quantity' : "1000",
        'quantity_type' : "NUMBER_TO_RELEASE",
        'release_probability' : "1",
        'shape' : "OBJECT",
        'site_diameter' : "0",
        'stddev' : "0"
      }
    ]
  },
  'scripting' : {
    'data_model_version' : "DM_2016_03_15_1900",
    'dm_external_file_name' : "",
    'dm_internal_file_name' : "",
    'force_property_update' : True,
    'script_texts' : {
      'dyn_geo.py': "# This script gets both its inputs and outputs from the environment:\n" \
               "#\n" \
               "#  frame_number is the frame number indexed from the start of the simulation\n" \
               "#  time_step is the amount of time between each frame (same as CellBlender's time_step)\n" \
               "#  points[] is a list of points where each point is a list of 3 doubles: x, y, z\n" \
               "#  faces[] is a list of faces where each face is a list of 3 integer indexes of points (0 based)\n" \
               "#  origin[] contains the x, y, and z values for the center of the object (points are relative to this).\n" \
               "#\n" \
               "# This script must fill out the points and faces lists for the time given by frame_number and time_step.\n" \
               "# CellBlender will call this function repeatedly to create the dynamic MDL and possibly during display.\n" \
               "\n" \
               "import math\n" \
               "\n" \
               "points.clear()\n" \
               "faces.clear()\n" \
               "\n" \
               "min_ztop = 1.0\n" \
               "max_ztop = 3.0\n" \
               "rad_bot = 1.0\n" \
               "rad_top = 0.25\n" \
               "period_frames = 200\n" \
               "\n" \
               "sx = sy = sz = rad_bot\n" \
               "h = ( 1 + math.sin ( math.pi * ((2*frame_number/period_frames) - 0.5) ) ) / 2\n" \
               "\n" \
               "zt = min_ztop + ( (max_ztop-min_ztop) * h )\n" \
               "rt = rt = rad_bot + ( h * (rad_top - rad_bot) )\n" \
               "\n" \
               "# These define the coordinates of the rectangular box\n" \
               "points.append ( [  sx,  sy, -sz ] )\n" \
               "points.append ( [  sx, -sy, -sz ] )\n" \
               "points.append ( [ -sx, -sy, -sz ] )\n" \
               "points.append ( [ -sx,  sy, -sz ] )\n" \
               "points.append ( [  rt,  rt,  zt ] )\n" \
               "points.append ( [  rt, -rt,  zt ] )\n" \
               "points.append ( [ -rt, -rt,  zt ] )\n" \
               "points.append ( [ -rt,  rt,  zt ] )\n" \
               "\n" \
               "# These define the faces of the rectangular box\n" \
               "faces.append ( [ 1, 2, 3 ] )\n" \
               "faces.append ( [ 7, 6, 5 ] )\n" \
               "faces.append ( [ 4, 5, 1 ] )\n" \
               "faces.append ( [ 5, 6, 2 ] )\n" \
               "faces.append ( [ 2, 6, 7 ] )\n" \
               "faces.append ( [ 0, 3, 7 ] )\n" \
               "faces.append ( [ 0, 1, 3 ] )\n" \
               "faces.append ( [ 4, 7, 5 ] )\n" \
               "faces.append ( [ 0, 4, 1 ] )\n" \
               "faces.append ( [ 1, 5, 2 ] )\n" \
               "faces.append ( [ 3, 2, 7 ] )\n" \
               "faces.append ( [ 4, 0, 7 ] )\n"
    },
    'scripting_list' : [],
    'show_data_model_scripting' : True,
    'show_simulation_scripting' : False
  },
  'simulation_control' : {
    'data_model_version' : "DM_2016_10_27_1642",
    'end_seed' : "1",
    'name' : "",
    'processes_list' : [
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 3405, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 3431, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 3695, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 3987, Seed: 1, 100%"
      }
    ],
    'run_limit' : "12",
    'start_seed' : "1"
  },
  'viz_output' : {
    'all_iterations' : True,
    'data_model_version' : "DM_2014_10_24_1638",
    'end' : "1",
    'export_all' : True,
    'start' : "0",
    'step' : "1"
  }
}


