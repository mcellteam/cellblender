fceri_mcell3r_dm = {
  'api_version' : 0,
  'blender_version' : [2, 78, 0],
  'cellblender_source_sha1' : "ebdcc895cbda94998628153aed32f484653b1bf5",
  'cellblender_version' : "0.1.54",
  'data_model_version' : "DM_2017_06_23_1300",
  'define_molecules' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'molecule_list' : [
      {
        'bngl_component_list' : [
          {
            'cname' : "l",
            'cstates' : []
          },
          {
            'cname' : "l",
            'cstates' : []
          }
        ],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2017_06_19_1960",
        'diffusion_constant' : "8.51e-7",
        'display' : {
          'color' : [0.075, 0.55, 1.0],
          'emit' : 0.0,
          'glyph' : "Tetrahedron",
          'scale' : 1.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "Lig",
        'mol_type' : "3D",
        'target_only' : False
      },
      {
        'bngl_component_list' : [
          {
            'cname' : "U",
            'cstates' : []
          },
          {
            'cname' : "SH2",
            'cstates' : []
          }
        ],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2017_06_19_1960",
        'diffusion_constant' : "1.7e-7",
        'display' : {
          'color' : [1.0, 1.0, 0.0],
          'emit' : 1.0,
          'glyph' : "Sphere_2",
          'scale' : 2.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "Lyn",
        'mol_type' : "2D",
        'target_only' : False
      },
      {
        'bngl_component_list' : [
          {
            'cname' : "tSH2",
            'cstates' : []
          },
          {
            'cname' : "l",
            'cstates' : ['Y', 'pY']
          },
          {
            'cname' : "a",
            'cstates' : ['Y', 'pY']
          }
        ],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2017_06_19_1960",
        'diffusion_constant' : "8.51e-7",
        'display' : {
          'color' : [0.0082, 1.0, 0.0],
          'emit' : 2.0,
          'glyph' : "Cube",
          'scale' : 1.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "Syk",
        'mol_type' : "3D",
        'target_only' : False
      },
      {
        'bngl_component_list' : [
          {
            'cname' : "a",
            'cstates' : []
          },
          {
            'cname' : "b",
            'cstates' : ['Y', 'pY']
          },
          {
            'cname' : "g",
            'cstates' : ['Y', 'pY']
          }
        ],
        'custom_space_step' : "",
        'custom_time_step' : "",
        'data_model_version' : "DM_2017_06_19_1960",
        'diffusion_constant' : "1.7e-7",
        'display' : {
          'color' : [1.0, 0.27, 0.03],
          'emit' : 0.0,
          'glyph' : "Torus",
          'scale' : 4.0
        },
        'export_viz' : False,
        'maximum_step_length' : "",
        'mol_bngl_label' : "",
        'mol_name' : "Rec",
        'mol_type' : "2D",
        'target_only' : False
      }
    ]
  },
  'define_reactions' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'reaction_list' : [
      {
        'bkwd_rate' : "km1",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "kp1",
        'name' : "Rec(a) + Lig(l,l) <-> Rec(a!1).Lig(l!1,l)",
        'products' : "Rec(a!1).Lig(l!1,l)",
        'reactants' : "Rec(a) + Lig(l,l)",
        'rxn_name' : "",
        'rxn_type' : "reversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "kmL",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "kpL",
        'name' : "Rec(b~Y) + Lyn(U,SH2) <-> Rec(b~Y!1).Lyn(U!1,SH2)",
        'products' : "Rec(b~Y!1).Lyn(U!1,SH2)",
        'reactants' : "Rec(b~Y) + Lyn(U,SH2)",
        'rxn_name' : "",
        'rxn_type' : "reversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "pLb",
        'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~pY)",
        'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~pY)",
        'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~Y)",
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
        'fwd_rate' : "pLg",
        'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY)",
        'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY)",
        'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~Y)",
        'rxn_name' : "",
        'rxn_type' : "irreversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "kmLs",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "kpLs",
        'name' : "Rec(b~pY) + Lyn(U,SH2) <-> Rec(b~pY!1).Lyn(U,SH2!1)",
        'products' : "Rec(b~pY!1).Lyn(U,SH2!1)",
        'reactants' : "Rec(b~pY) + Lyn(U,SH2)",
        'rxn_name' : "",
        'rxn_type' : "reversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "pLbs",
        'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~pY)",
        'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~pY)",
        'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~Y)",
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
        'fwd_rate' : "pLgs",
        'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY)",
        'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY)",
        'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~Y)",
        'rxn_name' : "",
        'rxn_type' : "irreversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "kmS",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "kpS",
        'name' : "Rec(g~pY) + Syk(tSH2) <-> Rec(g~pY!1).Syk(tSH2!1)",
        'products' : "Rec(g~pY!1).Syk(tSH2!1)",
        'reactants' : "Rec(g~pY) + Syk(tSH2)",
        'rxn_name' : "",
        'rxn_type' : "reversible",
        'variable_rate' : "",
        'variable_rate_switch' : False,
        'variable_rate_text' : "",
        'variable_rate_valid' : False
      },
      {
        'bkwd_rate' : "",
        'data_model_version' : "DM_2014_10_24_1638",
        'fwd_rate' : "pLS",
        'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
        'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
        'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y)",
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
        'fwd_rate' : "pLSs",
        'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
        'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
        'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y)",
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
        'fwd_rate' : "pSS",
        'name' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
        'products' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
        'reactants' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y)",
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
        'fwd_rate' : "pSSs",
        'name' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
        'products' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
        'reactants' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y)",
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
        'fwd_rate' : "dm",
        'name' : "Rec(b~pY) -> Rec(b~Y)",
        'products' : "Rec(b~Y)",
        'reactants' : "Rec(b~pY)",
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
        'fwd_rate' : "dm",
        'name' : "Rec(g~pY) -> Rec(g~Y)",
        'products' : "Rec(g~Y)",
        'reactants' : "Rec(g~pY)",
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
        'fwd_rate' : "dm",
        'name' : "Syk(tSH2! + ,l~pY) -> Syk(tSH2! + ,l~Y)",
        'products' : "Syk(tSH2! + ,l~Y)",
        'reactants' : "Syk(tSH2! + ,l~pY)",
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
        'fwd_rate' : "dm",
        'name' : "Syk(tSH2! + ,a~pY) -> Syk(tSH2! + ,a~Y)",
        'products' : "Syk(tSH2! + ,a~Y)",
        'reactants' : "Syk(tSH2! + ,a~pY)",
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
        'fwd_rate' : "dc",
        'name' : "Syk(tSH2,l~pY) -> Syk(tSH2,l~Y)",
        'products' : "Syk(tSH2,l~Y)",
        'reactants' : "Syk(tSH2,l~pY)",
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
        'fwd_rate' : "dc",
        'name' : "Syk(tSH2,a~pY) -> Syk(tSH2,a~Y)",
        'products' : "Syk(tSH2,a~Y)",
        'reactants' : "Syk(tSH2,a~pY)",
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
        'data_model_version' : "DM_2014_10_24_1638",
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
            'name' : "wall"
          }
        ],
        'element_connections' : [
          [4, 5, 1],
          [5, 6, 2],
          [6, 7, 3],
          [7, 4, 0],
          [0, 1, 2],
          [7, 6, 5],
          [0, 4, 1],
          [1, 5, 2],
          [2, 6, 3],
          [3, 7, 0],
          [3, 0, 2],
          [4, 7, 5]
        ],
        'location' : [0.0, 0.0, 0.0],
        'material_names' : ['EC_mat'],
        'name' : "EC",
        'vertex_list' : [
          [-2.0, -1.25, -1.0],
          [-2.0, 1.25, -1.0],
          [2.0, 1.25, -1.0],
          [2.0, -1.25, -1.0],
          [-2.0, -1.25, 1.0],
          [-2.0, 1.25, 1.0],
          [2.0, 1.25, 1.0],
          [2.0, -1.25, 1.0]
        ]
      },
      {
        'define_surface_regions' : [
          {
            'include_elements' : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            'name' : "PM"
          }
        ],
        'element_connections' : [
          [0, 1, 2],
          [4, 7, 6],
          [0, 4, 5],
          [1, 5, 6],
          [2, 6, 7],
          [4, 0, 3],
          [3, 0, 2],
          [5, 4, 6],
          [1, 0, 5],
          [2, 1, 6],
          [3, 2, 7],
          [7, 4, 3]
        ],
        'location' : [0.0, 0.0, 0.0],
        'material_names' : ['CP_mat'],
        'name' : "CP",
        'vertex_list' : [
          [0.5, 0.5, -0.5],
          [0.5, -0.5, -0.5],
          [-0.5, -0.5, -0.5],
          [-0.5, 0.5, -0.5],
          [0.5, 0.5, 0.5],
          [0.5, -0.5, 0.5],
          [-0.5, -0.5, 0.5],
          [-0.5, 0.5, 0.5]
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
          'a' : 0.38,
          'b' : 0.73,
          'g' : 0.0,
          'r' : 0.8
        }
      },
      'EC_mat' : {
        'diffuse_color' : {
          'a' : 0.1,
          'b' : 0.43,
          'g' : 0.43,
          'r' : 0.43
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
        'name' : "EC",
        'parent_object' : "",
        'script_name' : ""
      },
      {
        'dynamic' : False,
        'dynamic_display_source' : "other",
        'membrane_name' : "PM",
        'name' : "CP",
        'parent_object' : "EC",
        'script_name' : ""
      }
    ]
  },
  'modify_surface_regions' : {
    'data_model_version' : "DM_2014_10_24_1638",
    'modify_surface_regions_list' : [
      {
        'data_model_version' : "DM_2015_11_06_1732",
        'name' : "Surface Class: reflect   Object: EC   Region: wall",
        'object_name' : "EC",
        'region_name' : "wall",
        'region_selection' : "SEL",
        'surf_class_name' : "reflect"
      },
      {
        'data_model_version' : "DM_2015_11_06_1732",
        'name' : "Surface Class: reflect   Object: EC   ALL",
        'object_name' : "EC",
        'region_name' : "",
        'region_selection' : "ALL",
        'surf_class_name' : "reflect"
      },
      {
        'data_model_version' : "DM_2015_11_06_1732",
        'name' : "Surface Class: reflect   Object: CP   Region: PM",
        'object_name' : "CP",
        'region_name' : "PM",
        'region_selection' : "SEL",
        'surf_class_name' : "reflect"
      },
      {
        'data_model_version' : "DM_2015_11_06_1732",
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
    'file_index' : 611,
    'file_name' : "",
    'file_num' : 1001,
    'file_start_index' : 0,
    'file_step_index' : 1,
    'file_stop_index' : 1000,
    'manual_select_viz_dir' : False,
    'render_and_save' : False,
    'seed_list' : [],
    'viz_enable' : True,
    'viz_list' : []
  },
  'parameter_system' : {
    'model_parameters' : [
      {
        'par_description' : "Avogadro number based on a volume size of 1 cubic um",
        'par_expression' : "6.022e8",
        'par_name' : "Nav",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.01",
        'par_name' : "rxn_layer_t",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Surface area",
        'par_expression' : "0.88/rxn_layer_t",
        'par_name' : "vol_wall",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "39",
        'par_name' : "vol_EC",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Surface area",
        'par_expression' : "0.01/rxn_layer_t",
        'par_name' : "vol_PM",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "1",
        'par_name' : "vol_CP",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Default: 6.0e3",
        'par_expression' : "6.0e3 * Scale_Totals",
        'par_name' : "Lig_tot",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Default: 4.0e2",
        'par_expression' : "4.0e2 * Scale_Totals",
        'par_name' : "Rec_tot",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Default: 2.8e2",
        'par_expression' : "2.8e2 * Scale_Totals",
        'par_name' : "Lyn_tot",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Default: 4e2",
        'par_expression' : "4e2 * Scale_Totals",
        'par_name' : "Syk_tot",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "0.00358 gives at least one each,   0.5 gives 2 of some",
        'par_expression' : "1",
        'par_name' : "Scale_Totals",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.000166057788110262*Nav",
        'par_name' : "kp1",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.00",
        'par_name' : "km1",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "1.66057788110262e-06/rxn_layer_t",
        'par_name' : "kp2",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.00",
        'par_name' : "km2",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.0166057788110262/rxn_layer_t",
        'par_name' : "kpL",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "20",
        'par_name' : "kmL",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.0166057788110262/rxn_layer_t",
        'par_name' : "kpLs",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.12",
        'par_name' : "kmLs",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.0166057788110262*Nav",
        'par_name' : "kpS",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.13",
        'par_name' : "kmS",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "30",
        'par_name' : "pLb",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "100",
        'par_name' : "pLbs",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "1",
        'par_name' : "pLg",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "3",
        'par_name' : "pLgs",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "30",
        'par_name' : "pLS",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "100",
        'par_name' : "pLSs",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "100",
        'par_name' : "pSS",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "200",
        'par_name' : "pSSs",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.1",
        'par_name' : "dm",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "",
        'par_expression' : "0.1",
        'par_name' : "dc",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Temperature, K",
        'par_expression' : "298.15",
        'par_name' : "T",
        'par_units' : "K",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Thickness of 2D compartment, um",
        'par_expression' : "rxn_layer_t",
        'par_name' : "h",
        'par_units' : "um",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Radius of a (spherical) molecule in 3D compartment, um",
        'par_expression' : "0.002564",
        'par_name' : "Rs",
        'par_units' : "um",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Radius of a (cylindrical) molecule in 2D compartment, um",
        'par_expression' : "0.0015",
        'par_name' : "Rc",
        'par_units' : "um",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Euler's constant",
        'par_expression' : "0.5722",
        'par_name' : "gamma",
        'par_units' : "",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Boltzmann constant, cm^2.kg/K.s^2",
        'par_expression' : "1.3806488e-19",
        'par_name' : "KB",
        'par_units' : "cm^2.kg/K.s^2",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Viscosity in compartment wall, kg/um.s",
        'par_expression' : "1e-9",
        'par_name' : "mu_wall",
        'par_units' : "kg/um.s",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Viscosity in compartment EC, kg/um.s",
        'par_expression' : "1e-9",
        'par_name' : "mu_EC",
        'par_units' : "kg/um.s",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Viscosity in compartment PM, kg/um.s",
        'par_expression' : "1e-9",
        'par_name' : "mu_PM",
        'par_units' : "kg/um.s",
        'sweep_enabled' : False,
      },
      {
        'par_description' : "Viscosity in compartment CP, kg/um.s",
        'par_expression' : "1e-9",
        'par_name' : "mu_CP",
        'par_units' : "kg/um.s",
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
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "LycFree",
        'mdl_string' : "COUNT[Lyn(U,SH2), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Lyn(U,SH2), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "RecPbeta",
        'mdl_string' : "COUNT[Rec(b~pY!?), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Rec(b~pY!?), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "RecMon",
        'mdl_string' : "COUNT[Rec(a!1).Lig(l!1,l), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Rec(a!1).Lig(l!1,l), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "RecDim",
        'mdl_string' : "COUNT[Rec(a!1).Lig(l!1,l!2).Rec(a!2), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Rec(a!1).Lig(l!1,l!2).Rec(a!2), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "RecRecLigLyn",
        'mdl_string' : "COUNT[Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b!3).Rec(a!1,b), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b!3).Rec(a!1,b), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "RecPgamma",
        'mdl_string' : "COUNT[Rec(g~pY),WORLD] + COUNT[Rec(g~pY!+), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Rec(g~pY),WORLD] + COUNT[Rec(g~pY!+), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "RecSyk",
        'mdl_string' : "COUNT[Rec(g~pY!1).Syk(tSH2!1), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Rec(g~pY!1).Syk(tSH2!1), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "RecSykPS",
        'mdl_string' : "COUNT[Rec(g~pY!1).Syk(tSH2!1,a~pY), WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Rec(g~pY!1).Syk(tSH2!1,a~pY), WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "Lig",
        'mdl_string' : "COUNT[Lig,WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Lig,WORLD]",
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      },
      {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2016_03_15_1800",
        'mdl_file_prefix' : "Lyn",
        'mdl_string' : "COUNT[Lyn,WORLD]",
        'molecule_name' : "",
        'name' : "MDL: COUNT[Lyn,WORLD]",
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
        'data_model_version' : "DM_2015_11_11_1717",
        'location_x' : "0",
        'location_y' : "0",
        'location_z' : "0",
        'molecule' : "Lig(l,l)@EC",
        'name' : "ligand_rel",
        'object_expr' : "EC[ALL] - CP[ALL]",
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
        'data_model_version' : "DM_2015_11_11_1717",
        'location_x' : "0",
        'location_y' : "0",
        'location_z' : "0",
        'molecule' : "Lyn(U,SH2)@PM",
        'name' : "lyn_rel",
        'object_expr' : "CP[PM]",
        'orient' : "'",
        'pattern' : "",
        'points_list' : [],
        'quantity' : "Lyn_tot",
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
        'molecule' : "Syk(tSH2,l~Y,a~Y)@CP",
        'name' : "syk_rel",
        'object_expr' : "CP",
        'orient' : "'",
        'pattern' : "",
        'points_list' : [],
        'quantity' : "Syk_tot",
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
        'molecule' : "Rec(a,b~Y,g~Y)@PM",
        'name' : "receptor_rel",
        'object_expr' : "CP[PM]",
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
    'run_limit' : "-1",
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


