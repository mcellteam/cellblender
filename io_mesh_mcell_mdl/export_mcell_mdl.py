# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Copyright (C) 2012: Tom Bartol, bartol@salk.edu
# Contributors: Tom Bartol

"""
This script exports MCell MDL files from Blender,
and is a component of CellBlender.
"""

import bpy
import os
import re



def createRegDict(obj):

  scn = bpy.context.scene
  reg_dict = {}
  obj_regs = obj.mcell.regions.region_list
  for reg in obj_regs:
    reg_dict[reg.name] = obj.data['mcell']['regions'][reg.name].to_list()

  return reg_dict



def save(operator, context, filepath=""):

  scn = context.scene
  mc = context.scene.mcell

  file = open(filepath, "w", encoding="utf8", newline="\n")
  filedir = os.path.dirname(filepath)

  # Export Model Initialization:
  file.write('ITERATIONS = %d\n' %(mc.initialization.iterations))
  file.write('TIME_STEP = %g\n\n' %(mc.initialization.time_step))

  # Export Molecules:
  if mc.project_settings.export_format == 'mcell_mdl_modular':
    file.write('INCLUDE_FILE = \"%s.molecules.mdl\"\n\n' % (mc.project_settings.base_name))
    filepath = ('%s/%s.molecules.mdl' % (filedir,mc.project_settings.base_name))
    tmp_file = open(filepath, "w", encoding="utf8", newline="\n")
    save_molecules(context,tmp_file)
    tmp_file.close()
  else:
    save_molecules(context,file)

  # Include MDL file to define surface classes
  if mc.surface_classes.include:
    file.write('INCLUDE_FILE = \"%s.surface_classes.mdl\"\n\n' % (mc.project_settings.base_name))

  # Export Reactions:
  if mc.project_settings.export_format == 'mcell_mdl_modular':
    file.write('INCLUDE_FILE = \"%s.reactions.mdl\"\n\n' % (mc.project_settings.base_name))
    filepath = ('%s/%s.reactions.mdl' % (filedir,mc.project_settings.base_name))
    tmp_file = open(filepath, "w", encoding="utf8", newline="\n")
    save_reactions(context,tmp_file)
    tmp_file.close()
  else:
    save_reactions(context,file)

  # Export Model Geometry:
  if mc.project_settings.export_format == 'mcell_mdl_modular':
    file.write('INCLUDE_FILE = \"%s.geometry.mdl\"\n\n' % (mc.project_settings.base_name))
    filepath = ('%s/%s.geometry.mdl' % (filedir,mc.project_settings.base_name))
    tmp_file = open(filepath, "w", encoding="utf8", newline="\n")
    save_geometry(context,tmp_file)
    tmp_file.close()
  else:
    save_geometry(context,file)

  # Include MDL file to modify surface regions
  if mc.mod_surf_regions.include:
    file.write('INCLUDE_FILE = \"%s.mod_surf_regions.mdl\"\n\n' % (mc.project_settings.base_name))
        
  # Instantiate Model Geometry and Release sites:
  obj_list = mc.model_objects.object_list
  rel_list = mc.release_sites.mol_release_list
  if (len(obj_list) > 0) | (len(rel_list) > 0):
    file.write('INSTANTIATE %s OBJECT\n' %(scn.name)) 
    file.write('{\n')
    obj_list = mc.model_objects.object_list
    if len(obj_list) > 0:
      for obj_item in obj_list:
        file.write('  %s OBJECT %s {}\n' % (obj_item.name,obj_item.name))

    rel_list = mc.release_sites.mol_release_list
    if len(rel_list) > 0:
      for rel_item in rel_list:
        file.write('  %s RELEASE_SITE\n' % (rel_item.name))
        file.write('  {\n')
        if (rel_item.shape == 'CUBIC') | (rel_item.shape == 'SPHERICAL') | (rel_item.shape == 'SPHERICAL_SHELL'):
          file.write('   SHAPE = %s\n' % (rel_item.shape))
          file.write('   LOCATION = [%g, %g, %g]\n' % (rel_item.location[0],rel_item.location[1],rel_item.location[2]))
        if (rel_item.shape == 'OBJECT'):
          inst_obj_expr = instance_object_expr(context,rel_item.object_expr)
          file.write('   SHAPE = %s\n' % (inst_obj_expr))

        file.write('   MOLECULE = %s\n' % (rel_item.molecule))
        if rel_item.quantity_type == 'NUMBER_TO_RELEASE':
          file.write('   NUMBER_TO_RELEASE = %d\n' % (int(rel_item.quantity)))
        elif rel_item.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
          file.write('   GAUSSIAN_RELEASE_NUMBER\n')
          file.write('      {\n')
          file.write('        NUMBER = %g\n' % (rel_item.quantity))
          file.write('        STDDEV = %g\n' % (rel_item.stddev))
          file.write('      }\n')
        elif rel_item.quantity_type == 'DENSITY':
          mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)((',)|(,')|(;)|(,*)|('*))$"
          m = re.match(mol_filter,rel_item.molecule)
          mol_name = m.group(1)
          if mc.molecules.molecule_list[mol_name].type == '2D':
            file.write('   DENSITY = %g\n' %(rel_item.quantity))
          else:
            file.write('   CONCENTRATION = %g\n' %(rel_item.quantity))
        if (rel_item.shape == 'CUBIC') | (rel_item.shape == 'SPHERICAL') | (rel_item.shape == 'SPHERICAL_SHELL'):
          file.write('   SITE_DIAMETER = %g\n' % (rel_item.diameter))

        file.write('   RELEASE_PROBABILITY = %g\n' % (rel_item.probability))
        if rel_item.pattern != '':
          file.write('   RELEASE_PATTERN = %s\n' % (rel_item.pattern))

        file.write('  }\n')

    file.write('}\n\n')

  # Include MDL files for viz and reaction output:
  if mc.viz_output.include:
    file.write('INCLUDE_FILE = \"%s.viz_output.mdl\"\n\n' % (mc.project_settings.base_name))
  if mc.rxn_output.include:
    file.write('INCLUDE_FILE = \"%s.rxn_output.mdl\"\n\n' % (mc.project_settings.base_name))

  return {'FINISHED'}



def save_molecules(context,file):

  mc = context.scene.mcell

  # Export Molecules:
  mol_list = mc.molecules.molecule_list
  if len(mol_list) > 0:
    file.write('DEFINE_MOLECULES\n')
    file.write('{\n')
    for mol_item in mol_list:
      file.write('  %s\n' %(mol_item.name))
      file.write('  {\n')
      if mol_item.type == '2D':
        file.write('    DIFFUSION_CONSTANT_2D = %g\n' %(mol_item.diffusion_constant))
      else:
        file.write('    DIFFUSION_CONSTANT_3D = %g\n' %(mol_item.diffusion_constant))
      if mol_item.custom_time_step > 0:
        file.write('    CUSTOM_TIME_STEP = %g\n' %(mol_item.custom_time_step))
      elif mol_item.custom_space_step > 0:
        file.write('    CUSTOM_SPACE_STEP = %g\n' %(mol_item.custom_space_step))
      if mol_item.target_only:
        file.write('    TARGET_ONLY\n')
      file.write('  }\n')
    file.write('}\n\n')

  return



def save_reactions(context,file):

  mc = context.scene.mcell

  # Export Reactions:
  rxn_list = mc.reactions.reaction_list
  if len(rxn_list) > 0:
    file.write('DEFINE_REACTIONS\n')
    file.write('{\n')
    for rxn_item in rxn_list:
      file.write('  %s ' %(rxn_item.name))
      if rxn_item.type == 'irreversible':
        file.write('[%g]' %(rxn_item.fwd_rate))
      else:
        file.write('[>%g, <%g]' %(rxn_item.fwd_rate,rxn_item.bkwd_rate))
      if rxn_item.rxn_name != '':
        file.write(' : %s\n' % (rxn_item.rxn_name))
      else:
        file.write('\n')
    file.write('}\n\n')

  return



def save_geometry(context,file):

  scn = context.scene
  mc = context.scene.mcell

  # Export Model Geometry:
  obj_list = mc.model_objects.object_list
  if len(obj_list) > 0:

    for obj_item in obj_list:
      obj = bpy.data.objects[obj_item.name]
      if obj.type == 'MESH':
        scn.objects.active = obj
#        obj.select = True
        bpy.ops.object.mode_set(mode='OBJECT')
        file.write('%s POLYGON_LIST\n' % (obj.name))
        file.write('{\n')

        file.write('  VERTEX_LIST\n')
        file.write('  {\n')
        mesh = obj.data
        t_mat = obj.matrix_world
        verts = mesh.vertices
        for v in verts:
          t_vec = v.co * t_mat
          file.write('    [ %.15g, %.15g, %.15g ]\n' % (t_vec.x, t_vec.y, t_vec.z))
        file.write('  }\n')

        file.write('  ELEMENT_CONNECTIONS\n')
        file.write('  {\n')
        faces = mesh.faces
        for f in faces:
          file.write('    [ %d, %d, %d ]\n' % (f.vertices[0], f.vertices[1], f.vertices[2]))
        file.write('  }\n')

        reg_dict = createRegDict(obj)
        if reg_dict:
          file.write('  DEFINE_SURFACE_REGIONS\n')
          file.write('  {\n')
          reg_names = [k for k in reg_dict.keys()]
          reg_names.sort()
          for reg in reg_names:
            file.write('    %s\n' % (reg))
            file.write('    {\n')
            file.write('      ELEMENT_LIST = '+str(reg_dict[reg])+'\n' )
            file.write('    }\n')

          file.write('  }\n')

        file.write('}\n\n')

  return



def instance_object_expr(context,expr):

  scn = context.scene

  token_spec = [
    ("ID",      r"[A-Za-z]+[0-9A-Za-z_.]*(\[[A-Za-z]+[0-9A-Za-z_.]*\])?"),  # Identifiers
    ("PAR",     r"[\(\)]"),    # Parentheses
    ("OP",      r"[\+\*\-]"),  # Boolean operators
    ("SKIP",    r"[ \t]"),     # Skip over spaces and tabs
  ]
  tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
  get_token = re.compile(tok_regex).match
  inst_expr = ''
  pos = line_start = 0
  m = get_token(expr)
  while m is not None:
    typ = m.lastgroup
    if typ != 'SKIP':
      val = m.group(typ)
      if typ == 'ID':
        val = scn.name + '.' + val
      elif typ == 'OP':
        val = ' ' + val + ' '
      inst_expr = inst_expr + val

    pos = m.end()
    m = get_token(expr, pos)
  if pos != len(expr):
#    raise RuntimeError('Unexpected character %r' %(s[pos]))
    pass

  return inst_expr


