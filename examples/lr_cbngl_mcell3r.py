lr_cbngl_mcell3r_dm = {
  'api_version' : 0,
  'blender_version' : [2, 79, 0],
  'cellblender_source_sha1' : "2bdb483e629e9383d81b2bfc4e30d02de954a3db",
  'cellblender_version' : "0.1.54",
  'data_model_version' : "DM_2017_06_23_1300",
  'define_molecules' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'molecule_list' : [
      {
        'bngl_component_list' : [
          {
            'cname' : "r",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "0",
            'loc_y' : "0",
            'loc_z' : "0",
            'rot_ang' : "0",
            'rot_index' : 0,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          },
          {
            'cname' : "r",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "0",
            'loc_y' : "0",
            'loc_z' : "0",
            'rot_ang' : "0",
            'rot_index' : 0,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          },
          {
            'cname' : "r",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "0",
            'loc_y' : "0",
            'loc_z' : "0",
            'rot_ang' : "0",
            'rot_index' : 0,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          }
        ],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2018_10_16_1632",
        'description' : "",
        'diffusion_constant' : "1e-6",
        'display' : {
          'color' : [1.0, 0.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Torus",
          'scale' : 2.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "L",
        'mol_type' : "3D",
        'spatial_structure' : "None",
        'target_only' : False
      },
      {
        'bngl_component_list' : [
          {
            'cname' : "l",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "0",
            'loc_y' : "0",
            'loc_z' : "0",
            'rot_ang' : "0",
            'rot_index' : 0,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          },
          {
            'cname' : "l",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "0",
            'loc_y' : "0",
            'loc_z' : "0",
            'rot_ang' : "0",
            'rot_index' : 0,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          }
        ],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2018_10_16_1632",
        'description' : "",
        'diffusion_constant' : "1e-6",
        'display' : {
          'color' : [0.0, 2.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Sphere_1",
          'scale' : 1.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "R",
        'mol_type' : "3D",
        'spatial_structure' : "None",
        'target_only' : False
      }
    ],
    'molmaker' : {
      'average_coincident' : False,
      'cellblender_colors' : True,
      'comp_loc_text_name' : "",
      'data_model_version' : "DM_2018_10_31_1510",
      'dynamic_rotation' : False,
      'include_rotation' : True,
      'make_materials' : True,
      'molcomp_list' : [],
      'molecule_definition' : "",
      'molecule_text_name' : "",
      'print_debug' : False,
      'show_key_planes' : True,
      'show_text_interface' : False,
      'skip_fixed_comp_index' : -1,
      'skip_rotation' : False,
      'skip_var_comp_index' : -1
    }
  },
  'define_reactions' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'reaction_list' : [
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'fwd_rate' : "kp1",
        'name' : "R(l)+L(r,r,r) -> L(r!1,r,r).R(l!1)",
        'products' : "L(r!1,r,r).R(l!1)",
        'reactants' : "R(l)+L(r,r,r)",
        'rxn_name' : "",
        'rxn_type' : "irreversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'fwd_rate' : "kp1",
        'name' : "R(l)+L(r,r,r!+) -> L(r!1,r,r!+).R(l!1)",
        'products' : "L(r!1,r,r!+).R(l!1)",
        'reactants' : "R(l)+L(r,r,r!+)",
        'rxn_name' : "",
        'rxn_type' : "irreversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'fwd_rate' : "kp1",
        'name' : "R(l)+L(r,r!+,r!+) -> L(r!1,r!+,r!+).R(l!1)",
        'products' : "L(r!1,r!+,r!+).R(l!1)",
        'reactants' : "R(l)+L(r,r!+,r!+)",
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
    'surface_class_list' : [
      {
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'name' : "reflect",
        'surface_class_prop_list' : [
          {
            'affected_mols' : "ALL_MOLECULES",
            'clamp_value' : "0",
            'data_model_version' : "DM_2015_11_08_1756",
            'molecule' : "",
            'name' : "Molec.: ALL_MOLECULES   Orient.: Ignore   Type: Reflective",
            'surf_class_orient' : ";",
            'surf_class_type' : "REFLECTIVE"
          }
        ]
      }
    ]
  },
  'geometrical_objects' : {
    'object_list' : [
      {
        'define_surface_regions' : [
          {
            'include_elements' : [
              0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              10,
              11
            ],
            'name' : "PM"
          }
        ],
        'element_connections' : [
          [3, 0, 1],
          [7, 2, 3],
          [5, 6, 7],
          [1, 4, 5],
          [2, 4, 0],
          [7, 1, 5],
          [3, 2, 0],
          [7, 6, 2],
          [5, 4, 6],
          [1, 0, 4],
          [2, 6, 4],
          [7, 3, 1]
        ],
        'location' : [0, 0, 0],
        'material_names' : ['CP_mat_2'],
        'name' : "CP",
        'vertex_list' : [
          [-0.5, -0.5, -0.5],
          [-0.5, -0.5, 0.5],
          [-0.5, 0.5, -0.5],
          [-0.5, 0.5, 0.5],
          [0.5, -0.5, -0.5],
          [0.5, -0.5, 0.5],
          [0.5, 0.5, -0.5],
          [0.5, 0.5, 0.5]
        ]
      },
      {
        'define_surface_regions' : [
          {
            'include_elements' : [
              0,
              1,
              2,
              3,
              4,
              5,
              6,
              7,
              8,
              9,
              10,
              11
            ],
            'name' : "EC_outer_wall"
          }
        ],
        'element_connections' : [
          [3, 0, 1],
          [7, 2, 3],
          [5, 6, 7],
          [1, 4, 5],
          [2, 4, 0],
          [7, 1, 5],
          [3, 2, 0],
          [7, 6, 2],
          [5, 4, 6],
          [1, 0, 4],
          [2, 6, 4],
          [7, 3, 1]
        ],
        'location' : [0, 0, 0],
        'material_names' : ['EC_mat_1'],
        'name' : "EC",
        'vertex_list' : [
          [-0.6299605369567871, -0.6299605369567871, -0.6299605369567871],
          [-0.6299605369567871, -0.6299605369567871, 0.6299605369567871],
          [-0.6299605369567871, 0.6299605369567871, -0.6299605369567871],
          [-0.6299605369567871, 0.6299605369567871, 0.6299605369567871],
          [0.6299605369567871, -0.6299605369567871, -0.6299605369567871],
          [0.6299605369567871, -0.6299605369567871, 0.6299605369567871],
          [0.6299605369567871, 0.6299605369567871, -0.6299605369567871],
          [0.6299605369567871, 0.6299605369567871, 0.6299605369567871]
        ]
      }
    ]
  },
  'initialization' : {
    'accurate_3d_reactions' : True,
    'center_molecules_on_grid' : False,
    'command_options' : "",
    'data_model_version' : "DM_2017_11_18_0130",
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
      'x_end' : "1",
      'x_start' : "-1",
      'x_step' : "0.02",
      'y_end' : "1",
      'y_start' : "-1",
      'y_step' : "0.02",
      'z_end' : "1",
      'z_start' : "-1",
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
      'large_molecular_displacement' : "WARNING",
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
      'CP_mat_2' : {
        'diffuse_color' : {
          'a' : 0.10000000149011612,
          'b' : 0.0,
          'g' : 2.0,
          'r' : 0.0
        }
      },
      'EC_mat_1' : {
        'diffuse_color' : {
          'a' : 0.10000000149011612,
          'b' : 0.0,
          'g' : 0.0,
          'r' : 1.0
        }
      }
    }
  },
  'model_language' : "mcell3r",
  'model_objects' : {
    'data_model_version' : "DM_2018_01_11_1330",
    'model_object_list' : [
      {
        'description' : "",
        'dynamic' : False,
        'dynamic_display_source' : "script",
        'membrane_name' : "PM",
        'name' : "CP",
        'object_source' : "blender",
        'parent_object' : "EC",
        'script_name' : ""
      },
      {
        'description' : "",
        'dynamic' : False,
        'dynamic_display_source' : "script",
        'membrane_name' : "",
        'name' : "EC",
        'object_source' : "blender",
        'parent_object' : "",
        'script_name' : ""
      }
    ]
  },
  'modify_surface_regions' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'modify_surface_regions_list' : [
      {
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'name' : "Surface Class: reflect   Object: EC   ALL",
        'object_name' : "EC",
        'region_name' : "",
        'region_selection' : "ALL",
        'surf_class_name' : "reflect"
      },
      {
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'name' : "Surface Class: reflect   Object: EC   Region: EC_outer_wall",
        'object_name' : "EC",
        'region_name' : "EC_outer_wall",
        'region_selection' : "SEL",
        'surf_class_name' : "reflect"
      },
      {
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'name' : "Surface Class: reflect   Object: CP   ALL",
        'object_name' : "CP",
        'region_name' : "",
        'region_selection' : "ALL",
        'surf_class_name' : "reflect"
      },
      {
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'name' : "Surface Class: reflect   Object: CP   Region: PM",
        'object_name' : "CP",
        'region_name' : "PM",
        'region_selection' : "SEL",
        'surf_class_name' : "reflect"
      }
    ]
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
    'file_index' : 984,
    'file_name' : "Scene.cellbin.0984.dat",
    'file_num' : 1001,
    'file_start_index' : 0,
    'file_step_index' : 1,
    'file_stop_index' : 1000,
    'manual_select_viz_dir' : False,
    'render_and_save' : False,
    'seed_list' : ['seed_00001'],
    'viz_enable' : True,
    'viz_list' : ['mol_R', 'mol_L']
  },
  'parameter_system' : {
    'model_parameters' : [
      {
        'par_description' : "",
        'par_expression' : "0.84",
        'par_name' : "cTot",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "56.5695045056029",
        'par_name' : "vol_wall",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "0.01",
        'par_name' : "rxn_layer_t",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "300",
        'par_name' : "Rec_tot",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "39",
        'par_name' : "vol_EC",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "400",
        'par_name' : "Lig_tot",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "0.01",
        'par_name' : "koff",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "50",
        'par_name' : "beta",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "6.022e8",
        'par_name' : "Nav",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "1e8 + ( 0 * (cTot*koff)/(3.0*Lig_tot)*Nav )",
        'par_name' : "kp1",
        'par_units' : "",
      },
      {
        'par_description' : "",
        'par_expression' : "0 * 0.0016666667*Nav",
        'par_name' : "kp2",
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
    'reaction_output_list' : [
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'mdl_file_prefix' : "Lig",
        'mdl_string' : "COUNT[L(r,r,r),WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[L(r,r,r),WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'mdl_file_prefix' : "Rec",
        'mdl_string' : "COUNT[R(l,l),WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[R(l,l),WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      }
    ],
    'rxn_step' : ""
  },
  'release_sites' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'release_site_list' : [
      {
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'location_x' : "0",
        'location_y' : "0",
        'location_z' : "0",
        'molecule' : "L(r,r,r)@CP",
        'name' : "Rel_Site_1",
        'object_expr' : "CP[ALL]",
        'orient' : "'",
        'pattern' : "",
        'points_list' : [],
        'quantity' : "Lig_tot",
        'quantity_type' : "NUMBER_TO_RELEASE",
        'release_probability' : "1",
        'shape' : "OBJECT",
        'site_diameter' : "0",
        'stddev' : "0"
      },
      {
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'location_x' : "0",
        'location_y' : "0",
        'location_z' : "0",
        'molecule' : "R(l,l)@CP",
        'name' : "Rel_Site_2",
        'object_expr' : "CP[ALL]",
        'orient' : "'",
        'pattern' : "",
        'points_list' : [],
        'quantity' : "Rec_tot",
        'quantity_type' : "NUMBER_TO_RELEASE",
        'release_probability' : "1",
        'shape' : "OBJECT",
        'site_diameter' : "0",
        'stddev' : "0"
      }
    ]
  },
  'scripting' : {
    'data_model_version' : "DM_2017_11_30_1830",
    'dm_external_file_name' : "",
    'dm_internal_file_name' : "",
    'force_property_update' : True,
    'ignore_cellblender_data' : False,
    'script_texts' : {},
    'scripting_list' : []
  },
  'simulation_control' : {
    'data_model_version' : "DM_2017_11_22_1617",
    'end_seed' : "1",
    'export_format' : "mcell_mdl_modular",
    'name' : "",
    'processes_list' : [
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 37098, Seed: 1, 100%"
      }
    ],
    'run_limit' : "12",
    'sim_engines' : [
      {
        'parameter_dictionary' : {
          'Error File' : {
            'as' : "filename",
            'desc' : "Error File name",
            'icon' : "EXPORT",
            'val' : ""
          },
          'Log File' : {
            'as' : "filename",
            'desc' : "Log File name",
            'icon' : "EXPORT",
            'val' : ""
          },
          'MCell Path' : {
            'as' : "filename",
            'desc' : "MCell Path",
            'icon' : "SCRIPTWIN",
            'val' : ""
          },
          'Output Detail (0-100)' : {
            'desc' : "Output Detail",
            'val' : 20
          }
        },
        'parameter_layout' : [
          ['MCell Path'],
          ['Version', 'Full Version', 'Help', 'Reset'],
          ['Log File', 'Error File']
        ],
        'plug_active' : True,
        'plug_code' : "MCELL3",
        'plug_name' : "MCell 3 with Dynamic Geometry"
      },
      {
        'parameter_dictionary' : {
          'Output Detail (0-100)' : {
            'desc' : "Amount of Information to Print (0-100)",
            'icon' : "INFO",
            'val' : 20
          },
          'Python Command' : {
            'as' : "filename",
            'desc' : "Command to run Python (default is python)",
            'icon' : "SCRIPTWIN",
            'val' : ""
          },
          'Reaction Factor' : {
            'desc' : "Decay Rate Multiplier",
            'icon' : "ARROW_LEFTRIGHT",
            'val' : 1.0
          }
        },
        'parameter_layout' : [
          ['Python Command'],
          ['Output Detail (0-100)'],
          ['Reaction Factor'],
          ['Print Information', 'Reset']
        ],
        'plug_active' : True,
        'plug_code' : "LIM_PYTHON",
        'plug_name' : "Prototype Python Simulation"
      },
      {
        'parameter_dictionary' : {
          'Error File' : {
            'as' : "filename",
            'desc' : "Error File name",
            'icon' : "EXPORT",
            'val' : ""
          },
          'Log File' : {
            'as' : "filename",
            'desc' : "Log File name",
            'icon' : "EXPORT",
            'val' : ""
          },
          'MCell Path' : {
            'as' : "filename",
            'desc' : "MCell Path",
            'icon' : "SCRIPTWIN",
            'val' : ""
          },
          'Output Detail (0-100)' : {
            'desc' : "Output Detail",
            'val' : 20
          }
        },
        'parameter_layout' : [
          ['MCell Path'],
          ['Log File', 'Error File'],
          ['Version', 'Full Version', 'Help', 'Reset']
        ],
        'plug_active' : True,
        'plug_code' : "MCELL3DM",
        'plug_name' : "MCell 3 via Data Model"
      },
      {
        'parameter_dictionary' : {
          'BioNetGen Path' : {
            'as' : "filename",
            'desc' : "BioNetGen Path",
            'icon' : "OUTLINER_DATA_MESH",
            'val' : "bng2/BNG2.pl"
          },
          'MCellR Path' : {
            'as' : "filename",
            'desc' : "MCellR Path",
            'icon' : "FORCE_LENNARDJONES",
            'val' : "mcell"
          },
          'MCellRlib Path' : {
            'as' : "filename",
            'desc' : "MCellR Library Path",
            'icon' : "FORCE_LENNARDJONES",
            'val' : "lib/"
          },
          'Output Detail (0-100)' : {
            'desc' : "Amount of Information to Print (0-100)",
            'icon' : "INFO",
            'val' : 20
          },
          'Shared Path' : {
            'as' : "filename",
            'desc' : "Shared Path",
            'icon' : "FORCE_LENNARDJONES",
            'val' : "/nadata/cnl/home/bobkuczewski/proj/MCell/CellBlender_Versions/Blender-2.79-CellBlender/2.79/scripts/addons/cellblender/extensions"
          }
        },
        'parameter_layout' : [
          ['Shared Path'],
          ['MCellR Path'],
          ['MCellRlib Path'],
          ['BioNetGen Path'],
          ['Output Detail (0-100)'],
          ['Print Information', 'Postprocess', 'Reset']
        ],
        'plug_active' : True,
        'plug_code' : "MCELLR",
        'plug_name' : "MCell Rules"
      },
      {
        'parameter_dictionary' : {
          'BioNetGen Path' : {
            'as' : "filename",
            'desc' : "BioNetGen Path",
            'icon' : "OUTLINER_DATA_MESH",
            'val' : "bionetgen/BNG2.pl"
          },
          'MDLString' : {
            'desc' : "Use '_MDLString' as part of file name",
            'val' : True
          },
          'NFSIM' : {
            'desc' : "Simulate using Network-free Simulation Method",
            'val' : False
          },
          'ODE' : {
            'desc' : "Simulate using Ordinary Differential Equation Solver",
            'val' : False
          },
          'Output Detail (0-100)' : {
            'desc' : "Amount of Information to Print (0-100)",
            'icon' : "INFO",
            'val' : 20
          },
          'PLA' : {
            'desc' : "Simulate using Partitioned tau-Leaping Algorithm",
            'val' : False
          },
          'SSA' : {
            'desc' : "Simulate using Gillespie Stochastic Simulation Algorithm",
            'val' : True
          },
          'Shared Path' : {
            'as' : "filename",
            'desc' : "Shared Path",
            'icon' : "FORCE_LENNARDJONES",
            'val' : "/nadata/cnl/home/bobkuczewski/proj/MCell/CellBlender_Versions/Blender-2.79-CellBlender/2.79/scripts/addons/cellblender/sim_engines/cBNGL"
          }
        },
        'parameter_layout' : [
          ['Shared Path'],
          ['BioNetGen Path'],
          ['ODE', 'NFSIM', 'SSA', 'PLA'],
          ['Output Detail (0-100)'],
          ['Postprocess', 'MDLString'],
          ['Print Information', 'Reset']
        ],
        'plug_active' : True,
        'plug_code' : "cBNGL",
        'plug_name' : "cBNGL"
      },
      {
        'parameter_dictionary' : {
          'Auto Boundaries' : {
            'desc' : "Compute boundaries from all geometric points",
            'val' : True
          },
          'Command Line' : {
            'desc' : "Additional Command Line Parameters",
            'val' : ""
          },
          'Graphics' : {
            'desc' : "Show Smoldyn Graphics",
            'val' : False
          },
          'Output Detail (0-100)' : {
            'desc' : "Amount of Information to Print (0-100)",
            'icon' : "INFO",
            'val' : 20
          },
          'Smoldyn Path' : {
            'as' : "filename",
            'desc' : "Optional Path",
            'icon' : "SCRIPTWIN",
            'val' : "//../../../../../smoldyn/smoldyn-2.51/cmake/smoldyn"
          },
          'bounding_cube_size' : {
            'desc' : "Cube Boundary Size",
            'val' : 2
          },
          'x_bound_max' : {
            'desc' : "x boundary (maximum)",
            'val' : 1.0
          },
          'x_bound_min' : {
            'desc' : "x boundary (minimum)",
            'val' : -1.0
          },
          'y_bound_max' : {
            'desc' : "y boundary (maximum)",
            'val' : 1.0
          },
          'y_bound_min' : {
            'desc' : "y boundary (minimum)",
            'val' : -1.0
          },
          'z_bound_max' : {
            'desc' : "z boundary (maximum)",
            'val' : 1.0
          },
          'z_bound_min' : {
            'desc' : "z boundary (minimum)",
            'val' : -1.0
          }
        },
        'parameter_layout' : [
          ['Smoldyn Path'],
          ['Auto Boundaries', 'Set Cube Boundaries:', 'bounding_cube_size'],
          ['x_bound_min', 'y_bound_min', 'z_bound_min'],
          ['x_bound_max', 'y_bound_max', 'z_bound_max'],
          ['Graphics', 'Command Line'],
          ['Output Detail (0-100)'],
          ['Postprocess', 'Reset']
        ],
        'plug_active' : True,
        'plug_code' : "SMOLDYN248",
        'plug_name' : "Prototype Smoldyn 2.48 Simulation"
      },
      {
        'parameter_dictionary' : {
          'C++ Path' : {
            'as' : "filename",
            'desc' : "Optional Path",
            'icon' : "SCRIPTWIN",
            'val' : ""
          },
          'Decay Factor' : {
            'desc' : "Decay Rate Multiplier",
            'icon' : "ARROW_LEFTRIGHT",
            'val' : 1.0
          },
          'Output Detail (0-100)' : {
            'desc' : "Amount of Information to Print (0-100)",
            'icon' : "INFO",
            'val' : 20
          }
        },
        'parameter_layout' : [
          ['Output Detail (0-100)'],
          ['Print Information', 'Reset']
        ],
        'plug_active' : True,
        'plug_code' : "LIM_CPP",
        'plug_name' : "Prototype C++ Simulation"
      },
      {
        'parameter_dictionary' : {
          'Electric Species' : {
            'desc' : "Names of Electric Field Species (comma separated)",
            'val' : ""
          },
          'Output Detail (0-100)' : {
            'desc' : "Amount of Information to Print (0-100)",
            'icon' : "INFO",
            'val' : 20
          },
          'Python Command' : {
            'as' : "filename",
            'desc' : "Command to run Python (default is python)",
            'icon' : "SCRIPTWIN",
            'val' : ""
          },
          'Reaction Factor' : {
            'desc' : "Decay Rate Multiplier",
            'icon' : "ARROW_LEFTRIGHT",
            'val' : 1.0
          }
        },
        'parameter_layout' : [
          ['Electric Species'],
          ['Python Command'],
          ['Output Detail (0-100)'],
          ['Reaction Factor'],
          ['Print Information', 'Reset']
        ],
        'plug_active' : True,
        'plug_code' : "PROTO_ANDREAS_1",
        'plug_name' : "Prototype Andreas 1"
      }
    ],
    'start_seed' : "1"
  },
  'viz_output' : {
    'all_iterations' : True,
    'data_model_version' : "DM_2014_10_24_1638",
    'end' : "1000",
    'export_all' : True,
    'start' : "0",
    'step' : "5"
  }
}

