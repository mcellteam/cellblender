# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 12:57:05 2014

@author: proto
"""

def update_parameters(geometry,compartmentList,volume,area):
    pass

def correct_volumes(context):
    mcell = context.scene.cell
    mobjsList = mcell.model_objects.object_list
    jfile = accessFile(filePath)        
    compartments = jfile['comp_list']
    for obj in mobjsList:
        
        instObj = bpy.data.objects[obj.name]
        mesh = instObj.data
        (edge_faces, edge_face_count) = cellblender_operators.make_efdict(mesh)
        t_mat = obj.matrix_world

        is_closed = cellblender_operators.check_closed(edge_face_count)
        is_manifold = cellblender_operators.check_manifold(edge_face_count)
        is_orientable = cellblender_operators.check_orientable(mesh, edge_faces, edge_face_count)
        volume = 0
        if is_orientable and is_manifold and is_closed:
            volume = cellblender_operators.mesh_vol(mesh, t_mat)
            if volume >= 0:
                mcell.meshalyzer.normal_status = "Outward Facing Normals"
            else:
                mcell.meshalyzer.normal_status = "Inward Facing Normals"
        area = 0
        for f in mesh.polygons:
            if not (len(f.vertices) == 3):
                mcell.meshalyzer.status = '***** Mesh Not Triangulated *****'
                mcell.meshalyzer.watertight = 'Mesh Not Triangulated'
                return {'FINISHED'}

            tv0 = mesh.vertices[f.vertices[0]].co * t_mat
            tv1 = mesh.vertices[f.vertices[1]].co * t_mat
            tv2 = mesh.vertices[f.vertices[2]].co * t_mat
            area = area + mathutils.geometry.area_tri(tv0,tv1,tv2)

        update_parameters(obj.name,compartments,volume,area)
