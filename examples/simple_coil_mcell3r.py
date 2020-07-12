simple_coil_mcell3r_dm = {
  'api_version' : 0,
  'blender_version' : [2, 79, 0],
  'cellblender_source_sha1' : "4b73cdc5909c9ccb346653a419b5bf2c0b77f9a9",
  'cellblender_version' : "0.1.54",
  'data_model_version' : "DM_2017_06_23_1300",
  'define_molecules' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'molecule_list' : [
      {
        'bngl_component_list' : [
          {
            'cname' : "a",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "0.01",
            'loc_y' : "0.0",
            'loc_z' : "0.0",
            'rot_ang' : "0",
            'rot_index' : 3,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          },
          {
            'cname' : "b",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "-0.005",
            'loc_y' : "0.00866",
            'loc_z' : "0.0",
            'rot_ang' : "0",
            'rot_index' : 3,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          },
          {
            'cname' : "c",
            'cstates' : [],
            'is_key' : False,
            'loc_x' : "-0.005",
            'loc_y' : "-0.00866",
            'loc_z' : "0.0",
            'rot_ang' : "0",
            'rot_index' : 3,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          },
          {
            'cname' : "k",
            'cstates' : [],
            'is_key' : True,
            'loc_x' : "0.01",
            'loc_y' : "0",
            'loc_z' : "0.03",
            'rot_ang' : "0",
            'rot_index' : -1,
            'rot_x' : "0",
            'rot_y' : "0",
            'rot_z' : "0"
          }
        ],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2018_10_16_1632",
        'description' : "",
        'diffusion_constant' : "1e-5",
        'display' : {
          'color' : [1.0, 0.0, 0.0],
          'emit' : 0.0,
          'glyph' : "Sphere_1",
          'scale' : 1.5
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "A",
        'mol_type' : "3D",
        'spatial_structure' : "XYZRef",
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
      'molcomp_list' : [
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "m",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "A",
          'peer_list' : "1,2,3,4"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "a",
          'peer_list' : "0"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "b",
          'peer_list' : "0"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 6,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "c",
          'peer_list' : "0"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "k",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "k",
          'peer_list' : "0"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "m",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "A",
          'peer_list' : "6,7,8,9"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 3,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "a",
          'peer_list' : "5"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "b",
          'peer_list' : "5"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 11,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "c",
          'peer_list' : "5"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "k",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "k",
          'peer_list' : "5"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "m",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "A",
          'peer_list' : "11,12,13,14"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 8,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "a",
          'peer_list' : "10"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "b",
          'peer_list' : "10"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 16,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "c",
          'peer_list' : "10"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "k",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "k",
          'peer_list' : "10"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "m",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "A",
          'peer_list' : "16,17,18,19"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 13,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "a",
          'peer_list' : "15"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "b",
          'peer_list' : "15"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 21,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "c",
          'peer_list' : "15"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "k",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "k",
          'peer_list' : "15"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "m",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "A",
          'peer_list' : "21,22,23,24"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 18,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "a",
          'peer_list' : "20"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "b",
          'peer_list' : "20"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 26,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "c",
          'peer_list' : "20"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "k",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "k",
          'peer_list' : "20"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "m",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "A",
          'peer_list' : "26,27,28,29"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : 23,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "a",
          'peer_list' : "25"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "b",
          'peer_list' : "25"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "c",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "c",
          'peer_list' : "25"
        },
        {
          'alert_string' : "",
          'angle' : 0.0,
          'bond_index' : -1,
          'coords' : [0.0, 0.0, 0.0],
          'field_type' : "k",
          'graph_string' : "",
          'has_coords' : False,
          'is_final' : False,
          'key_index' : -1,
          'key_list' : "",
          'name' : "k",
          'peer_list' : "25"
        }
      ],
      'molecule_definition' : "A.A.A.A.A.A",
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
        'fwd_rate' : "1e9",
        'name' : "A(a)+A(c) -> A(a!1).A(c!1)",
        'products' : "A(a!1).A(c!1)",
        'reactants' : "A(a)+A(c)",
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
        'location' : [0, 0, 0],
        'material_names' : ['CP_mat'],
        'name' : "CP",
        'vertex_list' : [
          [-0.5, -0.5, -0.5000001192092896],
          [-0.5, -0.5, 0.5000001192092896],
          [-0.5, 0.5, -0.5000001192092896],
          [-0.5, 0.5, 0.5000001192092896],
          [0.5, -0.5, -0.5000001192092896],
          [0.5, -0.5, 0.5000001192092896],
          [0.5, 0.5, -0.5000001192092896],
          [0.5, 0.5, 0.5000001192092896]
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
    'iterations' : "5000",
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
      'CP_mat' : {
        'diffuse_color' : {
          'a' : 0.15000000596046448,
          'b' : 0.800000011920929,
          'g' : 0.800000011920929,
          'r' : 0.800000011920929
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
        'name' : "Surface Class: reflect   Object: CP   ALL",
        'object_name' : "CP",
        'region_name' : "",
        'region_selection' : "ALL",
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
    'file_index' : 4999,
    'file_name' : "Scene.cellbin.4999.dat",
    'file_num' : 5001,
    'file_start_index' : 0,
    'file_step_index' : 1,
    'file_stop_index' : 5000,
    'manual_select_viz_dir' : False,
    'render_and_save' : False,
    'seed_list' : ['seed_00001'],
    'viz_enable' : True,
    'viz_list' : ['mol_volume_proxy', 'mol_A']
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
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "Count something (required by MCellR)",
        'mdl_file_prefix' : "Mol",
        'mdl_string' : "COUNT[A(a,b,c), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[A(a,b,c), WORLD]",
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
        'molecule' : "A(a,b,c)@CP",
        'name' : "rel_A",
        'object_expr' : "CP[ALL]",
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
        'name' : "PID: 17686, Seed: 1"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 17713, Seed: 1"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 17887, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 18076, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 18296, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 18557, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 18662, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 18781, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 18818, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 19000, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 19109, Seed: 1, 100%"
      },
      {
        'data_model_version' : "DM_2015_04_23_1753",
        'name' : "PID: 19307, Seed: 1, 100%"
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
            'val' : "Blender-2.79-CellBlender/2.79/scripts/addons/cellblender/extensions"
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
            'val' : True
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
            'val' : False
          },
          'Shared Path' : {
            'as' : "filename",
            'desc' : "Shared Path",
            'icon' : "FORCE_LENNARDJONES",
            'val' : "Blender-2.79-CellBlender/2.79/scripts/addons/cellblender/sim_engines/cBNGL"
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
    'end' : "1",
    'export_all' : True,
    'start' : "0",
    'step' : "1"
  }
}

