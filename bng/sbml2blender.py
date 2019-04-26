'''
Spatial SBML importer
Rohan Arepally
Jose Juan Tapia
Devin Sullivan
Taraz Buck
'''
from collections import defaultdict
from cellblender.utils import preserve_selection_use_operator
 
import sys
import bpy
import mathutils
import os
import xml.etree.ElementTree as ET
import shutil
import math


# Read all of the CSG Object types in a SBML file 
def readSBMLFileCSGObject(filePath):
    try:
        tree = ET.parse(filePath)
    except IOError:
        #logging.error('File not found during geometry loading')
        return
        
    root = tree.getroot()
    objects = []
    ns = {'spatial': 'http://www.sbml.org/sbml/level3/version1/spatial/version1'}
    spatial_prefix = '{' + ns['spatial'] + '}'
    
    for object in root.iter(spatial_prefix + 'csgObject'):
        id = object.get(spatial_prefix + 'id')
        domainType = object.get(spatial_prefix + 'domainType')
        for csgPrimitive in object.iter(spatial_prefix + 'csgPrimitive'):
            type        = csgPrimitive.get(spatial_prefix + 'primitiveType')
        
        for csgScale in object.iter(spatial_prefix + 'csgScale'):
            scaleX      = csgScale.get(spatial_prefix + 'scaleX')
            scaleY      = csgScale.get(spatial_prefix + 'scaleY')
            scaleZ      = csgScale.get(spatial_prefix + 'scaleZ')
        
        for csgRotation in object.iter(spatial_prefix + 'csgRotation'):
            rotateAxisX = csgRotation.get(spatial_prefix + 'rotateAxisX')
            rotateAxisY = csgRotation.get(spatial_prefix + 'rotateAxisY')
            rotateAxisZ = csgRotation.get(spatial_prefix + 'rotateAxisZ')
            # Use specification release 0.93 (Draft), December 2018
            rotateX = csgRotation.get(spatial_prefix + 'rotateX')
            rotateY = csgRotation.get(spatial_prefix + 'rotateY')
            rotateZ = csgRotation.get(spatial_prefix + 'rotateZ')
            rotateAngleInRadians = csgRotation.get(spatial_prefix + 'rotateAngleInRadians')
            if rotateAxisX is None and rotateX is not None:
                # Axis-angle representation to rotation matrix
                mat = mathutils.Matrix.Rotation(float(rotateAngleInRadians), 4, mathutils.Vector((float(rotateX), float(rotateY), float(rotateZ))))
                eul = mat.to_euler('XYZ')
                rotateAxisX = str(eul.x)
                rotateAxisY = str(eul.y)
                rotateAxisZ = str(eul.z)
        
        for csgTranslation in object.iter(spatial_prefix + 'csgTranslation'):
            translateX  = csgTranslation.get(spatial_prefix + 'translateX')
            translateY  = csgTranslation.get(spatial_prefix + 'translateY')
            translateZ  = csgTranslation.get(spatial_prefix + 'translateZ')

        print("domainType: "  + domainType)
        '''
        print("id: "          + id)
        print("type: "        + type)
        print("scaleX: "      + scaleX)
        print("scaleY: "      + scaleY)
        print("scaleZ: "      + scaleZ)
        print("rotateAxisX: " + rotateAxisX)
        print("rotateAxisY: " + rotateAxisY)
        print("rotateAxisZ: " + rotateAxisZ)
        print("translateX: "  + translateX)
        print("translateY: "  + translateY)
        print("translateZ: "  + translateZ)
	'''
        objects += [[id, type, scaleX, scaleY, scaleZ, rotateAxisX, rotateAxisY, rotateAxisZ,translateX, translateY, translateZ, domainType]]
    return objects

# Parse SBML Spatial arrayData
def parseSBMLSpatialArrayData(text, shape=None, compressed=False, dtype=float):
    """
    Only supports uncompressed 2D data
    """
    if compressed:
        raise(NotImplementedError)
    
    semicolon_count = text.count(';')
    if shape is None or (shape[0] is None and shape[1] is None):
        if semicolon_count == 0:
            raise(ValueError('shape is None and semicolon_count == 0'))
        shape = [semicolon_count, None]
    if shape[0] is None and semicolon_count > 0:
        shape = [semicolon_count, shape[1]]
    data = text.replace(';', ' ')
    data = data.split()
    if shape[0] is None and shape[1] is not None:
        shape = [len(data) // shape[1], shape[1]]
    elif shape[0] is not None and shape[1] is None:
        shape = [shape[0], length(data) // shape[0]]
    data2 = []
    for i in range(shape[0]):
        data2.append(tuple([dtype(data[j]) for j in range(i * shape[1], (i+1) * shape[1])]))
    return data2

# read parametric object data
def readSBMLFileParametricObject(filepath):
    print("\n")
    print("reading parametric SBML\n")
    tree = ET.parse(filepath)
    root = tree.getroot()
    objects = []
    ns = {'spatial': 'http://www.sbml.org/sbml/level3/version1/spatial/version1'}
    spatial_prefix = '{' + ns['spatial'] + '}'
    
    for object in root.iter(spatial_prefix + 'ParametricObject'):
        #id = object.get('spatialId') - old version D. Sullivan 10/25/14
        id = object.get(spatial_prefix + 'id')
        print("spid: "       + id)

        for polygonObject in object.iter(spatial_prefix + 'PolygonObject'):
            faces        = polygonObject.get(spatial_prefix + 'faces')
            vertices     = polygonObject.get(spatial_prefix + 'pointIndex')
            
            faces = parseSBMLSpatialArrayData(faces, dtype=int)
            vertices = parseSBMLSpatialArrayData(vertices)
        
            objects += [[id, faces, vertices]]
    
    for parametricGeometry in root.iter(spatial_prefix + 'parametricGeometry'):
        spatialPoints = list(parametricGeometry.iterfind(spatial_prefix + 'spatialPoints'))[0]
        listOfParametricObjects = list(parametricGeometry.iterfind(spatial_prefix + 'listOfParametricObjects'))[0]
        vertices = parseSBMLSpatialArrayData(spatialPoints.text, [None, 3])
        for parametricObject in listOfParametricObjects.iter(spatial_prefix + 'parametricObject'):
            id = parametricObject.get(spatial_prefix + 'id')
            polygonType = parametricObject.get(spatial_prefix + 'polygonType')
            print("spid: " + id)
            
            faces = parseSBMLSpatialArrayData(parametricObject.text, (None, 4 if polygonType == 'quadrilateral' else 3), dtype=int)
        
            objects += [[id, faces, vertices]]
    
    return objects

# all objects in blender scene are deleted. Should leave empty blender scene.
def resetScene():
    obj_list = [item.name for item in bpy.data.objects if item.type == "MESH"]
    
    for obj in obj_list:
    	bpy.data.objects[obj].select = True
    
    bpy.ops.object.delete()

# calculate the volume of a mesh 
def mesh_vol(mesh, t_mat):
    volume = 0.0
    for f in mesh.polygons:
        tv0 = mesh.vertices[f.vertices[0]].co * t_mat
        tv1 = mesh.vertices[f.vertices[1]].co * t_mat
        tv2 = mesh.vertices[f.vertices[2]].co * t_mat
        x0 = tv0.x
        y0 = tv0.y
        z0 = tv0.z
        x1 = tv1.x
        y1 = tv1.y
        z1 = tv1.z
        x2 = tv2.x
        y2 = tv2.y
        z2 = tv2.z
        det = x0*(y1*z2-y2*z1)+x1*(y2*z0-y0*z2)+x2*(y0*z1-y1*z0)
        volume = volume + det
    
    volume = volume/6.0
    return(volume)

# a sphere with dimensions x,y,z is added to the blender scene
def generateSphere(name, size, loc, rot):
    #pi = 3.1415
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, location=(float(loc[0]),float(loc[1]),float(loc[2])))
    obj = bpy.data.objects[bpy.context.active_object.name]
    scn = bpy.context.scene
    me = obj.data
    #obj.scale = (float(size[0])*0.25,float(size[1])*0.25,float(size[2])*0.2)
    obj.scale = (float(size[0]),float(size[1]),float(size[2]))
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = (float(rot[0]),float(rot[1]),float(rot[2]))
    obj.name = name
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj

# generates a cube in blender scene with dimensions x,y,z
def generateCube(name, size, loc):
    bpy.ops.mesh.primitive_cube_add(location=(float(loc[0]),float(loc[1]),float(loc[2])))
    obj = bpy.data.objects[bpy.context.active_object.name]
    scn = bpy.context.scene
    obj.select = True
    print(name)
    obj.name = name
    #obj.scale = (float(size[0])*0.25,float(size[1])*0.25,float(size[2])*0.2)
    obj.scale = (float(size[0]),float(size[1]),float(size[2]))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    #bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select = False
    return obj

# Approximation of the surface area of a sphere (Knud Thomsen's formula)
# dimensions x,y,z are in microns
def surface_area_sphere(x,y,z):
    p = 1.6075
    a = abs(x)
    b = abs(y)
    c = abs(z)
    first  = pow(a,p)*pow(b,p)
    second = pow(a,p)*pow(c,p)
    third  = pow(b,p)*pow(c,p)
    val    = ( (first + second + third)/3.0 )
    val    = pow(val, 1.0/p)
    return 4*(3.14)*val

# imports a mesh into the scene and returns the volume
def importMesh(name,directory):
    bpy.ops.import_scene.obj(filepath=directory)
    imported = bpy.context.selected_objects[0]
    imported.name = name
    #imported.scale = (0.2, 0.2, 0.25)
    imported.scale = (1, 1, 1)
    imported.rotation_euler = (0,0,0)
    return mesh_vol(imported.data, imported.matrix_world)

#generates mesh in blender using SBML file data
def generateMesh(objectData):
    verts = objectData[2]
    faces = objectData[1]
    id    = objectData[0]
    
    mesh_data = bpy.data.meshes.new(id)
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update(calc_edges=True)
    
    obj = bpy.data.objects.new(id, mesh_data)
    
    scene = bpy.context.scene
    scene.objects.link(obj)
    obj.select = True
    obj.rotation_euler = (0,0,0)
    #obj.scale = (0.05, 0.05, 0.04)
    obj.scale = (1, 1, 1)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.mesh.dissolve_degenerate()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj

# saves filename.blend to the directory specified
def saveBlendFile(directory,filename):
    print(filename)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(directory, filename + ".blend"))

#distance between two strings
def levenshtein(s1, s2):
        l1 = len(s1)
        l2 = len(s2)
    
        matrix = [list(range(l1 + 1))] * (l2 + 1)
        for zz in range(l2 + 1):
          matrix[zz] = list(range(zz,zz + l1 + 1))
        for zz in list(range(0,l2)):
          for sz in list(range(0,l1)):
            if s1[sz] == s2[zz]:
              matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
            else:
              matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
        return matrix[l2][l1]
def common_prefix(strings):
    """ Find the longest string that is a prefix of all the strings.
    """
    if not strings:
        return ''
    prefix = strings[0]
    for s in strings:
        if len(s) < len(prefix):
            prefix = prefix[:len(s)]
        if not prefix:
            return ''
        for i in range(len(prefix)):
            if prefix[i] != s[i]:
                prefix = prefix[:i]
                break
    return prefix

# given SBML file create blender file of geometries described in SBML file
def sbml2blender(inputFilePath,addObjects):
    print("loading .xml file... " + inputFilePath)
    #extrapolate object data from SBML file
    csgObjects   = readSBMLFileCSGObject(inputFilePath)
    paramObjects = readSBMLFileParametricObject(inputFilePath)
    
    print("length of csgObjects: " + str(len(csgObjects)))
    print("length of paramObjects: " + str(len(paramObjects)))
    #generates sphere or bounding box in Blender
    
    #track average endosome size
    sum_size = 0.0 #sum of volumes
    n_size   = 0.0 #number of endosomes
    
    #track average endosome surface area
    sum_surf = 0.0
    n_surf   = 0.0
    
    
    
    csgObjectNames = []
    domainTypes = []
    name = []
    size = []
    location = []
    rotation = []
    domain = []
    ind = 0
    for csgobject in csgObjects:
        if( csgobject[1] == 'SOLID_SPHERE' or csgobject[1] == 'sphere'):
            name.append(csgobject[0])
            size.append([float(csgobject[2]), float(csgobject[3]), float(csgobject[4])])
            location.append([float(csgobject[8]), float(csgobject[9]), float(csgobject[10])])
            rotation.append([float(csgobject[5]), float(csgobject[6]), float(csgobject[7])])
            domain.append(csgobject[11])
            if domain[ind] not in domainTypes:
                domainTypes.append(domain[ind])
            csgObjectNames.append(domain[ind])
            sum_size += (4.0/3.0)*(3.14)*(size[ind][0])*(size[ind][1])*(size[ind][2])
            n_size   += 1
            sum_surf += surface_area_sphere(size[ind][0],size[ind][1],size[ind][2])
            n_surf += 1
            ind = ind + 1
    for domainType in domainTypes:
        ind = 0
        print(domainType)
        for csgObjectName in csgObjectNames:
            print(csgObjectName)
            if domain[ind]==domainType:
                print("match")
                obj = generateSphere(domainType+str(ind),size[ind],location[ind],rotation[ind])
            ind = ind + 1
        bpy.ops.object.select_pattern(pattern=domainType+'*')
        bpy.ops.object.join()
        obj.name = domainType
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.faces_shade_smooth()
        bpy.ops.object.mode_set(mode='OBJECT')
        if addObjects:
            preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)
        bpy.ops.object.select_all(action='DESELECT')


    namingPatterns = domainTypes

    print(namingPatterns)
    '''
    #bpy.ops.object.join()
    print("Here are the domains: ")
    print(csgObjectNames)
    #extract groups of strings with a lvenshtein distance less than 4
    csgObjectNames.sort()
    namingPatterns = []
        #   while len(csgObjectNames) > 0:
    for domainType in domainTypes:
        print(domainType)


    #namingPatterns.append([x for x in csgObjectNames if domainType==x])
    #csgObjectNames = [x for x in csgObjectNames if domainType==x]
    
    #extract common prefix for groups of strings
    namingPatterns = domainTypes
    print(namingPatterns)
    #namingPatterns = [common_prefix(x) for x in namingPatterns]

    #group objects by pattern - now domainType
    print(namingPatterns)
    for namingPattern in namingPatterns:
    #for domainType in domainTypes:
        print("Current domain: ")
        print(namingPattern)
        bpy.ops.object.select_name(name=format(namingPattern), extend=False)
        #bpy.ops.object.select_pattern(pattern='{0}*'.format(namingPattern), extend=False)
        #bpy.ops.object.select_pattern(pattern="devin2", extend=False)
        #bpy.ops.object.select_pattern(pattern="ivan1", extend=False)
        bpy.ops.object.join()
        obj = bpy.data.objects[bpy.context.active_object.name]
        #obj.name = namingPattern
        obj.name = namingPattern
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.faces_shade_smooth()
        bpy.ops.object.mode_set(mode='OBJECT')
        if addObjects:
            preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)
    
    #for name in csgObjectNames:
        #bpy.ops.object.select_by_type(type='MESH', extend=False)
        #bpy.ops.object.join()
    '''
    csgObjectNames = []
    for csgobject in csgObjects:
        if( csgobject[1] == 'SOLID_CUBE' or csgobject[1] == 'cube'):
            name      = csgobject[0]
            location  = [float(csgobject[2]), float(csgobject[3]), float(csgobject[4])]
            size      = [float(csgobject[2]), float(csgobject[3]), float(csgobject[4])]
            location  = [float(csgobject[8]), float(csgobject[9]), float(csgobject[10])]
            obj = generateCube(name,size,location)
            csgObjectNames.append(name)

#            if addObjects:
#                preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)
    #extract groups of strings with a lvenshtein distance less than 4
    csgObjectNames.sort()
    namingPatterns = []
    while len(csgObjectNames) > 0:
        namingPatterns.append([x for x in csgObjectNames if levenshtein(csgObjectNames[0],x) <= 4])
        csgObjectNames = [x for x in csgObjectNames if levenshtein(csgObjectNames[0],x) > 4]

    #extract common prefix for groups of strings
    namingPatterns = [common_prefix(x) for x in namingPatterns]

    #group objects by pattern
    for namingPattern in namingPatterns:
        bpy.ops.object.select_pattern(pattern='{0}*'.format(namingPattern), extend=False)
        bpy.ops.object.join()
        obj = bpy.data.objects[bpy.context.active_object.name]
        obj.name = namingPattern
        if addObjects:
            preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)

   # print("The average endosome size is: " + str((sum_size/(n_size*1.0))))
   # print("The average endosome surface area is " + str((sum_surf/(n_surf*1.0))))
    
    for paramObject in paramObjects:
        obj = generateMesh(paramObject)
        if addObjects:
            preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, obj)

# main function, reads arguments and runs sbml2blender
if __name__ == '__main__':
    filenames = sys.argv[5:]
    resetScene()
    xml = filenames[0]
    try:
        print(filenames[1])
        print(filenames[2])
        # reset initial conditions
        importMesh('cell', os.path.join(os.getcwd(),filenames[0]))
        importMesh('nuc', os.path.join(os.getcwd(),filenames[1]))
    except:
        print('No meshes imported')
    sbml2blender(os.path.join(os.getcwd(), xml),False)

    outputFilePath = 'demo_sbml2blender'
    shutil.copyfile("test.blend", outputFilePath + ".blend")
    print('saving blend file to {0}'.format(outputFilePath))
    saveBlendFile(os.getcwd(), outputFilePath)

    
