import copy

lv_rxn_lim_dm = {
  'api_version' : 0,
  'blender_version' : [2, 78, 0],
  'cellblender_source_sha1' : "d34986b7e98e0833a70d4bb6abffb0650da9cb05",
  'cellblender_version' : "0.1.54",
  'data_model_version' : "DM_2014_10_24_1638",
  'define_molecules' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'molecule_list' : [
      {
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2016_01_13_1930",
        'diffusion_constant' : "6e-6",
        'display' : {
          'color' : [0.0, 1.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Sphere_2",
          'scale' : 1.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "prey",
        'mol_type' : "3D",
        'target_only' : False
      },
      {
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2016_01_13_1930",
        'diffusion_constant' : "6e-6",
        'display' : {
          'color' : [1.0, 0.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Sphere_2",
          'scale' : 1.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "predator",
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
        'fwd_rate' : "1.29e5",
        'name' : "prey -> prey + prey",
        'products' : "prey + prey",
        'reactants' : "prey",
        'rxn_name' : "",
        'rxn_type' : "irreversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "1e8",
        'name' : "predator + prey -> predator + predator",
        'products' : "predator + predator",
        'reactants' : "predator + prey",
        'rxn_name' : "",
        'rxn_type' : "irreversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "1.3e5",
        'name' : "predator -> NULL",
        'products' : "NULL",
        'reactants' : "predator",
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
          [-0.25, -0.25, -0.005],
          [-0.25, -0.25, 0.005],
          [-0.25, 0.25, -0.005],
          [-0.25, 0.25, 0.005],
          [0.25, -0.25, -0.005],
          [0.25, -0.25, 0.005],
          [0.25, 0.25, -0.005],
          [0.25, 0.25, 0.005]
        ]
      }
    ]
  },
  'initialization' : {
    'accurate_3d_reactions' : True,
    'center_molecules_on_grid' : False,
    'data_model_version' : "DM_2014_10_24_1638",
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
      'include' : True,
      'recursion_flag' : False,
      'x_end' : "0.25",
      'x_start' : "-0.25",
      'x_step' : "0.02",
      'y_end' : "0.25",
      'y_start' : "-0.25",
      'y_step' : "0.02",
      'z_end' : "0.02",
      'z_start' : "-0.02",
      'z_step' : "0.02"
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
          'a' : 0.2,
          'b' : 0.8,
          'g' : 0.8,
          'r' : 0.8
        }
      }
    }
  },
  'model_objects' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'model_object_list' : [
      {
        'name' : "Cube"
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
    'file_index' : 325,
    'file_name' : "Scene.cellbin.325.dat",
    'file_num' : 501,
    'file_start_index' : 0,
    'file_step_index' : 1,
    'file_stop_index' : 500,
    'manual_select_viz_dir' : False,
    'render_and_save' : False,
    'seed_list' : ['seed_00001'],
    'viz_enable' : True,
    'viz_list' : ['mol_prey', 'mol_predator']
  },
  'parameter_system' : {
    'model_parameters' : [],
  },
  'reaction_data_output' : {
    'always_generate' : True,
    'combine_seeds' : True,
    'data_model_version' : "DM_2016_03_15_1800",
    'mol_colors' : False,
    'output_buf_size' : "",
    'plot_layout' : " plot ",
    'plot_legend' : "0",
    'reaction_output_list' : [
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "",
        'mdl_string' : "",
        'molecule_name' : "prey",
        'name' : "Count prey in World",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "Molecule"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "",
        'mdl_string' : "",
        'molecule_name' : "predator",
        'name' : "Count predator in World",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "Molecule"
      }
    ],
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
        'molecule' : "prey",
        'name' : "rel_prey",
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
        'molecule' : "predator",
        'name' : "rel_predator",
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
    'script_texts' : {},
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
        'name' : "PID: 10124, MDL: Scene.main.mdl, Seed: 1"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 10735, MDL: Scene.main.mdl, Seed: 1"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 11074, MDL: Scene.main.mdl, Seed: 1"
      }
    ],
    'run_limit' : "-1",
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

# diffusion limited case is almost the same
# copy dict so we can replace rate constants decrease shrink timestep
lv_diff_lim_dm = copy.deepcopy(lv_rxn_lim_dm)
lv_diff_lim_dm['define_reactions']['reaction_list'][0]['fwd_rate'] = "8.6e6"
lv_diff_lim_dm['define_reactions']['reaction_list'][1]['fwd_rate'] = "1e12"
lv_diff_lim_dm['define_reactions']['reaction_list'][2]['fwd_rate'] = "5e6"
lv_diff_lim_dm['initialization']['time_step'] = "1e-8"
