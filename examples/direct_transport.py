direct_transport_dm = {
  'api_version' : 0,
  'blender_version' : [2, 78, 0],
  'cellblender_source_sha1' : "c11f04dcaae5b8c08c3bff6844772df1879c8f63",
  'cellblender_version' : "0.1.54",
  'data_model_version' : "DM_2017_06_23_1300",
  'define_molecules' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'molecule_list' : [
      {
        'bngl_component_list' : [],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2017_06_19_1960",
        'diffusion_constant' : "1e-6",
        'display' : {
          'color' : [1.0, 0.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Sphere_1",
          'scale' : 4.5
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "v",
        'mol_type' : "3D",
        'target_only' : False
      },
      {
        'bngl_component_list' : [],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2017_06_19_1960",
        'diffusion_constant' : "1e-9",
        'display' : {
          'color' : [0.0, 1.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Torus",
          'scale' : 5.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "s",
        'mol_type' : "2D",
        'target_only' : False
      },
      {
        'bngl_component_list' : [],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2017_06_19_1960",
        'diffusion_constant' : "2e-6",
        'display' : {
          'color' : [0.0, 1.0, 1.0],
          'emit' : 2.0,
          'glyph' : "Cube",
          'scale' : 3.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "r",
        'mol_type' : "3D",
        'target_only' : False
      }
    ]
  },
  'define_reactions' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'reaction_list' : [
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "reaction_rate",
        'name' : "v@IN + s -> s + r@OUT",
        'products' : "s + r@OUT",
        'reactants' : "v@IN + s",
        'rxn_name' : "",
        'rxn_type' : "irreversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      }
    ]
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
        'define_surface_regions' : [
          {
            'include_elements' : [5, 11],
            'name' : "top"
          }
        ],
        'element_connections' : [
          [1, 2, 0],
          [3, 6, 2],
          [7, 4, 6],
          [5, 0, 4],
          [6, 0, 2],
          [3, 5, 7],
          [1, 3, 2],
          [3, 7, 6],
          [7, 5, 4],
          [5, 1, 0],
          [6, 4, 0],
          [3, 1, 5]
        ],
        'location' : [0.0, 0.0, 0.0],
        'material_names' : ['Cube_mat'],
        'name' : "Cube",
        'vertex_list' : [
          [-1.0, -1.0, -1.0],
          [-1.0, -1.0, 1.0],
          [-1.0, 1.0, -1.0],
          [-1.0, 1.0, 1.0],
          [1.0, -1.0, -1.0],
          [1.0, -1.0, 1.0],
          [1.0, 1.0, -1.0],
          [1.0, 1.0, 1.0]
        ]
      }
    ]
  },
  'initialization' : {
    'accurate_3d_reactions' : True,
    'center_molecules_on_grid' : False,
    'data_model_version' : "DM_2014_10_24_1638",
    'export_all_ascii' : False,
    'interaction_radius' : "",
    'iterations' : "1000",
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
      'x_start': "-4",
      'x_end': "4",
      'x_step': "0.5",
      'y_start': "-4",
      'y_end': "4",
      'y_step': "0.5",
      'z_start': "-4",
      'z_step': "0.5",
      'z_end': "4"
    },
    'radial_directions' : "",
    'radial_subdivisions' : "",
    'space_step' : "",
    'surface_grid_density' : "10000",
    'time_step' : "1e-6",
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
          'a' : 0.20000000298023224,
          'b' : 0.800000011920929,
          'g' : 0.800000011920929,
          'r' : 0.800000011920929
        }
      }
    }
  },
  'model_language' : "mcell4",
  'model_objects' : {
    'data_model_version' : "DM_2017_06_15_1755",
    'model_object_list' : [
      {
        'dynamic' : False,
        'dynamic_display_source' : "other",
        'membrane_name' : "",
        'name' : "Cube",
        'parent_object' : "",
        'script_name' : ""
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
      [0.800000011920929, 0.0, 0.0],
      [0.0, 0.800000011920929, 0.0],
      [0.0, 0.0, 0.800000011920929],
      [0.0, 0.800000011920929, 0.800000011920929],
      [0.800000011920929, 0.0, 0.800000011920929],
      [0.800000011920929, 0.800000011920929, 0.0],
      [1.0, 1.0, 1.0],
      [0.0, 0.0, 0.0]
    ],
    'data_model_version' : "DM_2015_04_13_1700",
    'file_dir' : "",
    'file_index' : 937,
    'file_name' : "Scene.cellbin.0937.dat",
    'file_num' : 1001,
    'file_start_index' : 0,
    'file_step_index' : 1,
    'file_stop_index' : 1000,
    'manual_select_viz_dir' : False,
    'render_and_save' : False,
    'seed_list' : ['seed_00001'],
    'viz_enable' : True,
    'viz_list' : ['mol_v', 'mol_s', 'mol_r']
  },
  'parameter_system' : {
    'model_parameters' : [
      {
        'par_description' : "",
        'par_expression' : "3e8",
        'par_name' : "reaction_rate",
        'par_units' : "",
        'sweep_enabled' : False,
      }
    ],
  },
  'reaction_data_output' : {
    'always_generate' : True,
    'combine_seeds' : True,
    'data_model_version' : "DM_2016_03_15_1800",
    'mol_colors' : False,
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
        'molecule' : "v",
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
      },
      {
        'data_model_version' : "DM_2015_11_11_1717",
        'location_x' : "0",
        'location_y' : "0",
        'location_z' : "0",
        'molecule' : "s",
        'name' : "Release_Site_2",
        'object_expr' : "Cube[top]",
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
    'script_texts' : {},
    'scripting_list' : [],
    'show_data_model_scripting' : True,
    'show_simulation_scripting' : False
  },
  'simulation_control' : {
    'data_model_version' : "DM_2016_10_27_1642",
    'end_seed' : "1",
    'name' : "",
    'processes_list' : [],
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


