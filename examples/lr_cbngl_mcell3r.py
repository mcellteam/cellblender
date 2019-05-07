lr_cbngl_mcell3r_dm = {
  "api_version": 0,
  "cellblender_version": "0.1.54",
  "data_model_version": "DM_2017_06_23_1300",
  "scripting": {
   "scripting_list": [],
   "dm_internal_file_name": "",
   "ignore_cellblender_data": False,
   "script_texts": {},
   "force_property_update": True,
   "data_model_version": "DM_2017_11_30_1830",
   "dm_external_file_name": ""
  },
  "model_language": "mcell3r",
  "simulation_control": {
   "name": "",
   "run_limit": "12",
   "processes_list": [],
   "export_format": "mcell_mdl_modular",
   "end_seed": "1",
   "start_seed": "1",
   "sim_engines": [
    {
     "plug_name": "MCell 3 with Dynamic Geometry",
     "plug_active": True,
     "parameter_layout": [
      [
       "MCell Path"
      ],
      [
       "Version",
       "Full Version",
       "Help",
       "Reset"
      ],
      [
       "Log File",
       "Error File"
      ]
     ],
     "plug_code": "MCELL3",
     "parameter_dictionary": {
      "MCell Path": {
       "desc": "MCell Path",
       "as": "filename",
       "icon": "SCRIPTWIN",
       "val": ""
      },
      "Log File": {
       "desc": "Log File name",
       "as": "filename",
       "icon": "EXPORT",
       "val": ""
      },
      "Output Detail (0-100)": {
       "desc": "Output Detail",
       "val": 20
      },
      "Error File": {
       "desc": "Error File name",
       "as": "filename",
       "icon": "EXPORT",
       "val": ""
      }
     }
    },
    {
     "plug_name": "Prototype Python Simulation",
     "plug_active": True,
     "parameter_layout": [
      [
       "Python Command"
      ],
      [
       "Output Detail (0-100)"
      ],
      [
       "Reaction Factor"
      ],
      [
       "Print Information",
       "Reset"
      ]
     ],
     "plug_code": "LIM_PYTHON",
     "parameter_dictionary": {
      "Reaction Factor": {
       "desc": "Decay Rate Multiplier",
       "icon": "ARROW_LEFTRIGHT",
       "val": 1.0
      },
      "Python Command": {
       "desc": "Command to run Python (default is python)",
       "as": "filename",
       "icon": "SCRIPTWIN",
       "val": ""
      },
      "Output Detail (0-100)": {
       "desc": "Amount of Information to Print (0-100)",
       "icon": "INFO",
       "val": 20
      }
     }
    },
    {
     "plug_name": "MCell 3 via Data Model",
     "plug_active": True,
     "parameter_layout": [
      [
       "MCell Path"
      ],
      [
       "Log File",
       "Error File"
      ],
      [
       "Version",
       "Full Version",
       "Help",
       "Reset"
      ]
     ],
     "plug_code": "MCELL3DM",
     "parameter_dictionary": {
      "MCell Path": {
       "desc": "MCell Path",
       "as": "filename",
       "icon": "SCRIPTWIN",
       "val": ""
      },
      "Log File": {
       "desc": "Log File name",
       "as": "filename",
       "icon": "EXPORT",
       "val": ""
      },
      "Output Detail (0-100)": {
       "desc": "Output Detail",
       "val": 20
      },
      "Error File": {
       "desc": "Error File name",
       "as": "filename",
       "icon": "EXPORT",
       "val": ""
      }
     }
    },
    {
     "plug_name": "MCell Rules",
     "plug_active": True,
     "parameter_layout": [
      [
       "Shared Path"
      ],
      [
       "MCellR Path"
      ],
      [
       "MCellRlib Path"
      ],
      [
       "BioNetGen Path"
      ],
      [
       "Output Detail (0-100)"
      ],
      [
       "Print Information",
       "Postprocess",
       "Reset"
      ]
     ],
     "plug_code": "MCELLR",
     "parameter_dictionary": {
      "BioNetGen Path": {
       "desc": "BioNetGen Path",
       "as": "filename",
       "icon": "OUTLINER_DATA_MESH",
       "val": "bng2/BNG2.pl"
      },
      "Shared Path": {
       "desc": "Shared Path",
       "as": "filename",
       "icon": "FORCE_LENNARDJONES",
       "val": "/nadata/cnl/home/bobkuczewski/proj/MCell/CellBlender_Versions/Blender-2.79-CellBlender/2.79/scripts/addons/cellblender/extensions"
      },
      "MCellRlib Path": {
       "desc": "MCellR Library Path",
       "as": "filename",
       "icon": "FORCE_LENNARDJONES",
       "val": "lib/"
      },
      "MCellR Path": {
       "desc": "MCellR Path",
       "as": "filename",
       "icon": "FORCE_LENNARDJONES",
       "val": "mcell"
      },
      "Output Detail (0-100)": {
       "desc": "Amount of Information to Print (0-100)",
       "icon": "INFO",
       "val": 20
      }
     }
    },
    {
     "plug_name": "cBNGL",
     "plug_active": True,
     "parameter_layout": [
      [
       "Shared Path"
      ],
      [
       "BioNetGen Path"
      ],
      [
       "ODE",
       "NFSIM",
       "SSA",
       "PLA"
      ],
      [
       "Output Detail (0-100)"
      ],
      [
       "Postprocess",
       "MDLString"
      ],
      [
       "Print Information",
       "Reset"
      ]
     ],
     "plug_code": "cBNGL",
     "parameter_dictionary": {
      "SSA": {
       "desc": "Simulate using Gillespie Stochastic Simulation Algorithm",
       "_i": 9,
       "val": True
      },
      "BioNetGen Path": {
       "desc": "BioNetGen Path",
       "as": "filename",
       "_i": 0,
       "icon": "OUTLINER_DATA_MESH",
       "val": "bionetgen/BNG2.pl"
      },
      "PLA": {
       "desc": "Simulate using Partitioned tau-Leaping Algorithm",
       "_i": 5,
       "val": False
      },
      "Output Detail (0-100)": {
       "desc": "Amount of Information to Print (0-100)",
       "icon": "INFO",
       "_i": 4,
       "val": 20
      },
      "ODE": {
       "desc": "Simulate using Ordinary Differential Equation Solver",
       "_i": 3,
       "val": False
      },
      "Shared Path": {
       "desc": "Shared Path",
       "as": "filename",
       "_i": 10,
       "icon": "FORCE_LENNARDJONES",
       "val": "/nadata/cnl/home/bobkuczewski/proj/MCell/CellBlender_Versions/Blender-2.79-CellBlender/2.79/scripts/addons/cellblender/sim_engines/cBNGL"
      },
      "MDLString": {
       "desc": "Use '_MDLString' as part of file name",
       "_i": 1,
       "val": True
      },
      "NFSIM": {
       "desc": "Simulate using Network-free Simulation Method",
       "_i": 2,
       "val": False
      }
     }
    },
    {
     "plug_name": "Prototype Smoldyn 2.48 Simulation",
     "plug_active": True,
     "parameter_layout": [
      [
       "Smoldyn Path"
      ],
      [
       "Auto Boundaries",
       "Set Cube Boundaries:",
       "bounding_cube_size"
      ],
      [
       "x_bound_min",
       "y_bound_min",
       "z_bound_min"
      ],
      [
       "x_bound_max",
       "y_bound_max",
       "z_bound_max"
      ],
      [
       "Graphics",
       "Command Line"
      ],
      [
       "Output Detail (0-100)"
      ],
      [
       "Postprocess",
       "Reset"
      ]
     ],
     "plug_code": "SMOLDYN248",
     "parameter_dictionary": {
      "z_bound_min": {
       "desc": "z boundary (minimum)",
       "val": -1.0
      },
      "y_bound_min": {
       "desc": "y boundary (minimum)",
       "val": -1.0
      },
      "z_bound_max": {
       "desc": "z boundary (maximum)",
       "val": 1.0
      },
      "y_bound_max": {
       "desc": "y boundary (maximum)",
       "val": 1.0
      },
      "Auto Boundaries": {
       "desc": "Compute boundaries from all geometric points",
       "val": True
      },
      "Graphics": {
       "desc": "Show Smoldyn Graphics",
       "val": False
      },
      "Command Line": {
       "desc": "Additional Command Line Parameters",
       "val": ""
      },
      "Output Detail (0-100)": {
       "desc": "Amount of Information to Print (0-100)",
       "icon": "INFO",
       "val": 20
      },
      "bounding_cube_size": {
       "desc": "Cube Boundary Size",
       "val": 2
      },
      "x_bound_min": {
       "desc": "x boundary (minimum)",
       "val": -1.0
      },
      "x_bound_max": {
       "desc": "x boundary (maximum)",
       "val": 1.0
      },
      "Smoldyn Path": {
       "desc": "Optional Path",
       "as": "filename",
       "icon": "SCRIPTWIN",
       "val": "//../../../../../smoldyn/smoldyn-2.51/cmake/smoldyn"
      }
     }
    },
    {
     "plug_name": "Prototype C++ Simulation",
     "plug_active": True,
     "parameter_layout": [
      [
       "Output Detail (0-100)"
      ],
      [
       "Print Information",
       "Reset"
      ]
     ],
     "plug_code": "LIM_CPP",
     "parameter_dictionary": {
      "C++ Path": {
       "desc": "Optional Path",
       "as": "filename",
       "icon": "SCRIPTWIN",
       "val": ""
      },
      "Decay Factor": {
       "desc": "Decay Rate Multiplier",
       "icon": "ARROW_LEFTRIGHT",
       "val": 1.0
      },
      "Output Detail (0-100)": {
       "desc": "Amount of Information to Print (0-100)",
       "icon": "INFO",
       "val": 20
      }
     }
    },
    {
     "plug_name": "Prototype Andreas 1",
     "plug_active": True,
     "parameter_layout": [
      [
       "Electric Species"
      ],
      [
       "Python Command"
      ],
      [
       "Output Detail (0-100)"
      ],
      [
       "Reaction Factor"
      ],
      [
       "Print Information",
       "Reset"
      ]
     ],
     "plug_code": "PROTO_ANDREAS_1",
     "parameter_dictionary": {
      "Reaction Factor": {
       "desc": "Decay Rate Multiplier",
       "icon": "ARROW_LEFTRIGHT",
       "val": 1.0
      },
      "Python Command": {
       "desc": "Command to run Python (default is python)",
       "as": "filename",
       "icon": "SCRIPTWIN",
       "val": ""
      },
      "Electric Species": {
       "desc": "Names of Electric Field Species (comma separated)",
       "val": ""
      },
      "Output Detail (0-100)": {
       "desc": "Amount of Information to Print (0-100)",
       "icon": "INFO",
       "val": 20
      }
     }
    }
   ],
   "data_model_version": "DM_2017_11_22_1617"
  },
  "mol_viz": {
   "color_list": [
    [
     0.800000011920929,
     0.0,
     0.0
    ],
    [
     0.0,
     0.800000011920929,
     0.0
    ],
    [
     0.0,
     0.0,
     0.800000011920929
    ],
    [
     0.0,
     0.800000011920929,
     0.800000011920929
    ],
    [
     0.800000011920929,
     0.0,
     0.800000011920929
    ],
    [
     0.800000011920929,
     0.800000011920929,
     0.0
    ],
    [
     1.0,
     1.0,
     1.0
    ],
    [
     0.0,
     0.0,
     0.0
    ]
   ],
   "render_and_save": False,
   "file_stop_index": 1000,
   "file_name": "Scene.cellbin.0966.dat",
   "file_start_index": 0,
   "file_dir": "tlbr_cbngl_files/mcell/output_data/viz_data/seed_00001",
   "viz_enable": True,
   "viz_list": [
    "mol_R",
    "mol_L"
   ],
   "file_num": 1001,
   "seed_list": [
    "seed_00001"
   ],
   "color_index": 0,
   "file_step_index": 1,
   "file_index": 966,
   "active_seed_index": 0,
   "manual_select_viz_dir": False,
   "data_model_version": "DM_2015_04_13_1700"
  },
  "define_molecules": {
   "molecule_list": [
    {
     "diffusion_constant": "1e-6",
     "export_viz": False,
     "target_only": False,
     "mol_name": "L",
     "custom_space_step": "",
     "bngl_component_list": [
      {
       "loc_z": "0",
       "rot_x": "0",
       "rot_index": 0,
       "rot_ang": "0",
       "loc_y": "0",
       "cname": "r",
       "is_key": False,
       "cstates": [],
       "rot_y": "0",
       "loc_x": "0",
       "rot_z": "0"
      },
      {
       "loc_z": "0",
       "rot_x": "0",
       "rot_index": 0,
       "rot_ang": "0",
       "loc_y": "0",
       "cname": "r",
       "is_key": False,
       "cstates": [],
       "rot_y": "0",
       "loc_x": "0",
       "rot_z": "0"
      },
      {
       "loc_z": "0",
       "rot_x": "0",
       "rot_index": 0,
       "rot_ang": "0",
       "loc_y": "0",
       "cname": "r",
       "is_key": False,
       "cstates": [],
       "rot_y": "0",
       "loc_x": "0",
       "rot_z": "0"
      }
     ],
     "display": {
      "color": [
       1.0,
       0.0,
       0.0
      ],
      "scale": 2.0,
      "glyph": "Torus",
      "emit": 0.0
     },
     "mol_bngl_label": "",
     "custom_time_step": "",
     "spatial_structure": "None",
     "mol_type": "3D",
     "description": "",
     "data_model_version": "DM_2018_10_16_1632",
     "maximum_step_length": ""
    },
    {
     "diffusion_constant": "1e-6",
     "export_viz": False,
     "target_only": False,
     "mol_name": "R",
     "custom_space_step": "",
     "bngl_component_list": [
      {
       "loc_z": "0",
       "rot_x": "0",
       "rot_index": 0,
       "rot_ang": "0",
       "loc_y": "0",
       "cname": "l",
       "is_key": False,
       "cstates": [],
       "rot_y": "0",
       "loc_x": "0",
       "rot_z": "0"
      },
      {
       "loc_z": "0",
       "rot_x": "0",
       "rot_index": 0,
       "rot_ang": "0",
       "loc_y": "0",
       "cname": "l",
       "is_key": False,
       "cstates": [],
       "rot_y": "0",
       "loc_x": "0",
       "rot_z": "0"
      }
     ],
     "display": {
      "color": [
       0.0,
       2.0,
       0.0
      ],
      "scale": 1.0,
      "glyph": "Sphere_1",
      "emit": 0.0
     },
     "mol_bngl_label": "",
     "custom_time_step": "",
     "spatial_structure": "None",
     "mol_type": "3D",
     "description": "",
     "data_model_version": "DM_2018_10_16_1632",
     "maximum_step_length": ""
    }
   ],
   "data_model_version": "DM_2014_10_24_1638",
   "molmaker": {
    "skip_rotation": False,
    "include_rotation": True,
    "dynamic_rotation": False,
    "molecule_text_name": "",
    "skip_fixed_comp_index": -1,
    "print_debug": False,
    "cellblender_colors": True,
    "comp_loc_text_name": "",
    "show_key_planes": True,
    "molcomp_list": [],
    "average_coincident": False,
    "molecule_definition": "",
    "skip_var_comp_index": -1,
    "make_materials": True,
    "data_model_version": "DM_2018_10_31_1510",
    "show_text_interface": False
   }
  },
  "viz_output": {
   "export_all": True,
   "step": "5",
   "all_iterations": True,
   "start": "0",
   "data_model_version": "DM_2014_10_24_1638",
   "end": "1000"
  },
  "cellblender_source_sha1": "11536c7bb15d6eb814b4a70fd0c69406990a7d31",
  "define_surface_classes": {
   "surface_class_list": [
    {
     "name": "reflect",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "surface_class_prop_list": [
      {
       "surf_class_orient": ";",
       "name": "Molec.: ALL_MOLECULES   Orient.: Ignore   Type: Reflective",
       "clamp_value": "0",
       "molecule": "",
       "surf_class_type": "REFLECTIVE",
       "affected_mols": "ALL_MOLECULES",
       "data_model_version": "DM_2015_11_08_1756"
      }
     ]
    }
   ],
   "data_model_version": "DM_2014_10_24_1638"
  },
  "model_objects": {
   "data_model_version": "DM_2018_01_11_1330",
   "model_object_list": [
    {
     "name": "CP",
     "script_name": "",
     "dynamic": False,
     "membrane_name": "PM",
     "parent_object": "EC",
     "object_source": "blender",
     "description": "",
     "dynamic_display_source": "script"
    },
    {
     "name": "EC",
     "script_name": "",
     "dynamic": False,
     "membrane_name": "",
     "parent_object": "",
     "object_source": "blender",
     "description": "",
     "dynamic_display_source": "script"
    }
   ]
  },
  "reaction_data_output": {
   "rxn_step": "",
   "mol_colors": False,
   "output_buf_size": "",
   "always_generate": True,
   "plot_layout": " plot ",
   "combine_seeds": True,
   "plot_legend": "0",
   "data_model_version": "DM_2016_03_15_1800",
   "reaction_output_list": [
    {
     "molecule_name": "",
     "mdl_file_prefix": "Lig",
     "mdl_string": "COUNT[L(r,r,r),WORLD]",
     "rxn_or_mol": "MDLString",
     "plotting_enabled": True,
     "data_file_name": "",
     "object_name": "",
     "name": "MDL: COUNT[L(r,r,r),WORLD]",
     "reaction_name": "",
     "region_name": "",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "count_location": "World"
    },
    {
     "molecule_name": "",
     "mdl_file_prefix": "Rec",
     "mdl_string": "COUNT[R(l,l),WORLD]",
     "rxn_or_mol": "MDLString",
     "plotting_enabled": True,
     "data_file_name": "",
     "object_name": "",
     "name": "MDL: COUNT[R(l,l),WORLD]",
     "reaction_name": "",
     "region_name": "",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "count_location": "World"
    }
   ]
  },
  "initialization": {
   "time_step": "1e-6",
   "notifications": {
    "partition_location_report": False,
    "molecule_collision_report": False,
    "progress_report": True,
    "probability_report": "ON",
    "iteration_report": True,
    "all_notifications": "INDIVIDUAL",
    "varying_probability_report": True,
    "box_triangulation_report": False,
    "file_output_report": False,
    "release_event_report": True,
    "probability_report_threshold": "0",
    "diffusion_constant_report": "BRIEF",
    "final_summary": True
   },
   "command_options": "",
   "surface_grid_density": "10000",
   "microscopic_reversibility": "OFF",
   "space_step": "",
   "time_step_max": "",
   "center_molecules_on_grid": False,
   "accurate_3d_reactions": True,
   "export_all_ascii": False,
   "data_model_version": "DM_2017_11_18_0130",
   "radial_subdivisions": "",
   "partitions": {
    "z_end": "1",
    "recursion_flag": False,
    "y_step": "0.02",
    "y_end": "1",
    "include": False,
    "x_end": "1",
    "z_start": "-1",
    "x_step": "0.02",
    "x_start": "-1",
    "y_start": "-1",
    "z_step": "0.02",
    "data_model_version": "DM_2016_04_15_1600"
   },
   "warnings": {
    "all_warnings": "INDIVIDUAL",
    "large_molecular_displacement": "WARNING",
    "useless_volume_orientation": "WARNING",
    "missed_reaction_threshold": "0.001",
    "missed_reactions": "WARNING",
    "negative_reaction_rate": "WARNING",
    "high_probability_threshold": "1",
    "negative_diffusion_constant": "WARNING",
    "high_reaction_probability": "IGNORED",
    "degenerate_polygons": "WARNING",
    "lifetime_threshold": "50",
    "missing_surface_orientation": "ERROR",
    "lifetime_too_short": "WARNING"
   },
   "radial_directions": "",
   "iterations": "1000",
   "vacancy_search_distance": "",
   "interaction_radius": ""
  },
  "materials": {
   "material_dict": {
    "EC_mat_1": {
     "diffuse_color": {
      "a": 0.10000000149011612,
      "r": 1.0,
      "g": 0.0,
      "b": 0.0
     }
    },
    "CP_mat_2": {
     "diffuse_color": {
      "a": 0.10000000149011612,
      "r": 0.0,
      "g": 2.0,
      "b": 0.0
     }
    }
   }
  },
  "parameter_system": {
   "model_parameters": [
    {
     "par_name": "cTot",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g1",
      "par_value": 0.84
     },
     "par_description": "",
     "par_expression": "0.84",
     "par_units": ""
    },
    {
     "par_name": "vol_wall",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g2",
      "par_value": 56.5695045056029
     },
     "par_description": "",
     "par_expression": "56.5695045056029",
     "par_units": ""
    },
    {
     "par_name": "rxn_layer_t",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g3",
      "par_value": 0.01
     },
     "par_description": "",
     "par_expression": "0.01",
     "par_units": ""
    },
    {
     "par_name": "Rec_tot",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g4",
      "par_value": 300.0
     },
     "par_description": "",
     "par_expression": "300",
     "par_units": ""
    },
    {
     "par_name": "vol_EC",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g5",
      "par_value": 39.0
     },
     "par_description": "",
     "par_expression": "39",
     "par_units": ""
    },
    {
     "par_name": "Lig_tot",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g6",
      "par_value": 400.0
     },
     "par_description": "",
     "par_expression": "400",
     "par_units": ""
    },
    {
     "par_name": "koff",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g7",
      "par_value": 0.01
     },
     "par_description": "",
     "par_expression": "0.01",
     "par_units": ""
    },
    {
     "par_name": "beta",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g8",
      "par_value": 50.0
     },
     "par_description": "",
     "par_expression": "50",
     "par_units": ""
    },
    {
     "par_name": "Nav",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g9",
      "par_value": 602200000.0
     },
     "par_description": "",
     "par_expression": "6.022e8",
     "par_units": ""
    },
    {
     "par_name": "kp1",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g10",
      "par_value": 100000000.0
     },
     "par_description": "",
     "par_expression": "1e8 + ( 0 * (cTot*koff)/(3.0*Lig_tot)*Nav )",
     "par_units": ""
    },
    {
     "par_name": "kp2",
     "_extras": {
      "par_valid": True,
      "par_id_name": "g11",
      "par_value": 0.0
     },
     "sweep_enabled": False,
     "par_description": "",
     "par_expression": "0 * 0.0016666667*Nav",
     "par_units": ""
    }
   ],
   "_extras": {
    "ordered_id_names": [
     "g2",
     "g6",
     "g7",
     "g5",
     "g4",
     "g1",
     "g3",
     "g9",
     "g8",
     "g10",
     "g11"
    ]
   }
  },
  "define_reactions": {
   "reaction_list": [
    {
     "description": "",
     "bkwd_rate": "",
     "rxn_name": "",
     "fwd_rate": "kp1",
     "variable_rate": "",
     "reactants": "R(l)+L(r,r,r)",
     "variable_rate_text": "",
     "name": "R(l)+L(r,r,r) -> L(r!1,r,r).R(l!1)",
     "products": "L(r!1,r,r).R(l!1)",
     "rxn_type": "irreversible",
     "variable_rate_valid": False,
     "data_model_version": "DM_2018_01_11_1330",
     "variable_rate_switch": False
    },
    {
     "description": "",
     "bkwd_rate": "",
     "rxn_name": "",
     "fwd_rate": "kp1",
     "variable_rate": "",
     "reactants": "R(l)+L(r,r,r!+)",
     "variable_rate_text": "",
     "name": "R(l)+L(r,r,r!+) -> L(r!1,r,r!+).R(l!1)",
     "products": "L(r!1,r,r!+).R(l!1)",
     "rxn_type": "irreversible",
     "variable_rate_valid": False,
     "data_model_version": "DM_2018_01_11_1330",
     "variable_rate_switch": False
    },
    {
     "description": "",
     "bkwd_rate": "",
     "rxn_name": "",
     "fwd_rate": "kp1",
     "variable_rate": "",
     "reactants": "R(l)+L(r,r!+,r!+)",
     "variable_rate_text": "",
     "name": "R(l)+L(r,r!+,r!+) -> L(r!1,r!+,r!+).R(l!1)",
     "products": "L(r!1,r!+,r!+).R(l!1)",
     "rxn_type": "irreversible",
     "variable_rate_valid": False,
     "data_model_version": "DM_2018_01_11_1330",
     "variable_rate_switch": False
    }
   ],
   "data_model_version": "DM_2014_10_24_1638"
  },
  "blender_version": [
   2,
   79,
   0
  ],
  "release_sites": {
   "release_site_list": [
    {
     "location_x": "0",
     "release_probability": "1",
     "molecule": "L(r,r,r)@CP",
     "pattern": "",
     "location_y": "0",
     "orient": "'",
     "object_expr": "CP[ALL]",
     "quantity_type": "NUMBER_TO_RELEASE",
     "points_list": [],
     "name": "Rel_Site_1",
     "location_z": "0",
     "quantity": "Lig_tot",
     "shape": "OBJECT",
     "stddev": "0",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "site_diameter": "0"
    },
    {
     "location_x": "0",
     "release_probability": "1",
     "molecule": "R(l,l)@CP",
     "pattern": "",
     "location_y": "0",
     "orient": "'",
     "object_expr": "CP[ALL]",
     "quantity_type": "NUMBER_TO_RELEASE",
     "points_list": [],
     "name": "Rel_Site_2",
     "location_z": "0",
     "quantity": "Rec_tot",
     "shape": "OBJECT",
     "stddev": "0",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "site_diameter": "0"
    }
   ],
   "data_model_version": "DM_2014_10_24_1638"
  },
  "define_release_patterns": {
   "release_pattern_list": [],
   "data_model_version": "DM_2014_10_24_1638"
  },
  "modify_surface_regions": {
   "modify_surface_regions_list": [
    {
     "region_selection": "ALL",
     "object_name": "EC",
     "name": "Surface Class: reflect   Object: EC   ALL",
     "surf_class_name": "reflect",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "region_name": ""
    },
    {
     "region_selection": "SEL",
     "object_name": "EC",
     "name": "Surface Class: reflect   Object: EC   Region: EC_outer_wall",
     "surf_class_name": "reflect",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "region_name": "EC_outer_wall"
    },
    {
     "region_selection": "ALL",
     "object_name": "CP",
     "name": "Surface Class: reflect   Object: CP   ALL",
     "surf_class_name": "reflect",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "region_name": ""
    },
    {
     "region_selection": "SEL",
     "object_name": "CP",
     "name": "Surface Class: reflect   Object: CP   Region: PM",
     "surf_class_name": "reflect",
     "description": "",
     "data_model_version": "DM_2018_01_11_1330",
     "region_name": "PM"
    }
   ],
   "data_model_version": "DM_2014_10_24_1638"
  },
  "geometrical_objects": {
   "object_list": [
    {
     "location": [
      0,
      0,
      0
     ],
     "define_surface_regions": [
      {
       "include_elements": [
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
       "name": "PM"
      }
     ],
     "name": "CP",
     "element_connections": [
      [
       3,
       0,
       1
      ],
      [
       7,
       2,
       3
      ],
      [
       5,
       6,
       7
      ],
      [
       1,
       4,
       5
      ],
      [
       2,
       4,
       0
      ],
      [
       7,
       1,
       5
      ],
      [
       3,
       2,
       0
      ],
      [
       7,
       6,
       2
      ],
      [
       5,
       4,
       6
      ],
      [
       1,
       0,
       4
      ],
      [
       2,
       6,
       4
      ],
      [
       7,
       3,
       1
      ]
     ],
     "vertex_list": [
      [
       -0.5,
       -0.5,
       -0.5
      ],
      [
       -0.5,
       -0.5,
       0.5
      ],
      [
       -0.5,
       0.5,
       -0.5
      ],
      [
       -0.5,
       0.5,
       0.5
      ],
      [
       0.5,
       -0.5,
       -0.5
      ],
      [
       0.5,
       -0.5,
       0.5
      ],
      [
       0.5,
       0.5,
       -0.5
      ],
      [
       0.5,
       0.5,
       0.5
      ]
     ],
     "material_names": [
      "CP_mat_2"
     ]
    },
    {
     "location": [
      0,
      0,
      0
     ],
     "define_surface_regions": [
      {
       "include_elements": [
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
       "name": "EC_outer_wall"
      }
     ],
     "name": "EC",
     "element_connections": [
      [
       3,
       0,
       1
      ],
      [
       7,
       2,
       3
      ],
      [
       5,
       6,
       7
      ],
      [
       1,
       4,
       5
      ],
      [
       2,
       4,
       0
      ],
      [
       7,
       1,
       5
      ],
      [
       3,
       2,
       0
      ],
      [
       7,
       6,
       2
      ],
      [
       5,
       4,
       6
      ],
      [
       1,
       0,
       4
      ],
      [
       2,
       6,
       4
      ],
      [
       7,
       3,
       1
      ]
     ],
     "vertex_list": [
      [
       -0.6299605369567871,
       -0.6299605369567871,
       -0.6299605369567871
      ],
      [
       -0.6299605369567871,
       -0.6299605369567871,
       0.6299605369567871
      ],
      [
       -0.6299605369567871,
       0.6299605369567871,
       -0.6299605369567871
      ],
      [
       -0.6299605369567871,
       0.6299605369567871,
       0.6299605369567871
      ],
      [
       0.6299605369567871,
       -0.6299605369567871,
       -0.6299605369567871
      ],
      [
       0.6299605369567871,
       -0.6299605369567871,
       0.6299605369567871
      ],
      [
       0.6299605369567871,
       0.6299605369567871,
       -0.6299605369567871
      ],
      [
       0.6299605369567871,
       0.6299605369567871,
       0.6299605369567871
      ]
     ],
     "material_names": [
      "EC_mat_1"
     ]
    }
   ]
  }
}
