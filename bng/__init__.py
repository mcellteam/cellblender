import bpy
from . import bng_operators
from . import sbml_operators
from . import external_operators
from . import bngl_to_data_model
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty,BoolProperty
#import logging
import os
import re

def findCellBlenderDirectory():
    for directory in os.path.sys.path:
        cellblenderDir = [x for x in os.listdir(directory) if 'cellblender' in x]
        if len(cellblenderDir) > 0:
            return directory + '{0}cellblender{0}'.format(os.sep)
   
    
class ImportBioNetGenData(bpy.types.Operator, ImportHelper):
    bl_idname = "bng.import_data"  
    bl_label = "Import External Model"
    bl_description = "Import BioNetGen or SBML encoded reaction network information"
 
    filename_ext = ".bngl,*.xml"

    filter_glob = StringProperty(
            default="*.bngl;*.xml",
            options={'HIDDEN'}
            )
            
    add_to_model_objects = BoolProperty(
	        name="Add to Model Objects",
	        description="Automatically add all meshes to the Model Objects list",
	        default=True,)


    def execute(self, context):
        if hasattr(external_operators.accessFile,"info"):
            del external_operators.accessFile.info
            
        if('.bngl') in self.filepath:
            bngfilepath = self.filepath         # bngl file path
            external_operators.filePath=findCellBlenderDirectory()+'bng{0}'.format(os.sep) + self.filepath.split(os.sep)[-1]
            print ( "Calling bng_operators.execute_bionetgen("+bngfilepath+")" )
            bng_operators.execute_bionetgen(self.filepath,context)
            print ( "Back from bng_operators.execute_bionetgen("+bngfilepath+")" )

        elif('.xml') in self.filepath:
            sbmlfilepath = self.filepath
            external_operators.filePath = sbmlfilepath
            # sbml file path
            #try:
            sbml_operators.execute_sbml2blender(sbmlfilepath,context,self.add_to_model_objects)
            #except:
             #   print('There is no spatial information')
            sbml_operators.execute_sbml2mcell(sbmlfilepath,context)
            print('Proceeding to import SBML file')
 
        
        print ( "Loading parameters from external model..." )
        bpy.ops.external.parameter_add()         # This processes all entries in the par_list parameter list
        print ( "Loading molecules from external model..." )
        bpy.ops.external.molecule_add()
        print ( "Loading reactions from external model..." )
        bpy.ops.external.reaction_add()
        print ( "Loading release sites from external model..." )
        bpy.ops.external.release_site_add()
        print ( "Done Loading external model" )
        if ('.xml') in self.filepath:
            #TODO:this is sbml only until we add this information on the bng side
            print("Loading reaction output ...")
            bpy.ops.external.reaction_output_add()


        ### TODO:
        ###
        ###  THIS ENTIRE SECTION IS A QUICK HACK TO HANDLE XML IMPORTING
        ###
        ###
        if ('.xml' in self.filepath) and ('mcell' in context.scene):
            # Note that searching for ".xml" in the filepath may not be reliable since it should end with .xml.
            # Keeping the same for now.
            print ( "Pulling object structure from XML file: " + self.filepath )
            
            mcell = context.scene.mcell

            xml_model_file = open ( self.filepath, 'r' )
            xml_model_text = xml_model_file.read()

            # First verify that it contains compartments (cheat by assuming no spaces for now)
            if ("<listOfCompartments>" in xml_model_text) and ("</listOfCompartments>" in xml_model_text):
                print ( "Model contains listOfCompartments" )

                # Get the lines between the listOfCompartments tags
                compartment_text = xml_model_text.split("<listOfCompartments>")[1].split("</listOfCompartments>")[0]
                lines = re.split(r'\n', compartment_text)

                # Remove comments and whitespace on ends
                for i in range(len(lines)):
                  l = lines[i]
                  if '#' in l:
                    lines[i] = l.split('#')[0].strip()

                # Remove any empty lines
                lines = [ l.strip() for l in lines if len(l.strip()) > 0 ]

                for l in lines:
                    print ( "  Compartment line: " + l )

                # Make a text block that looks like a BNGL file to be parsed by the object parser
                bngl_lines = []
                bngl_lines.append ( "begin model" )
                bngl_lines.append ( "begin compartments" )
                for l in lines:
                    # Convert an xml compartment line of the form: 
                    #   <compartment id="EC" spatialDimensions="3" size="27"/>
                    #   <compartmenread_data_model_from_bngl_textt id="PM" spatialDimensions="2" size="0.06" outside="EC"/>
                    #   <compartment id="CP" spatialDimensions="3" size="0.1" outside="PM"/>
                    # into a CBNGL compartment line of the form:
                    #   Name Dim  Size    [Parent]
                    #    EC   3    27
                    #    PM   2  6*0.01      EC
                    #    CP   3    0.1       PM
                    bngl_obj = {}
                    if 'id="' in l:
                        bngl_obj['id'] = l[l.find('id="')+4:].split('"')[0]
                        print ( "bngl object name = " + bngl_obj['id'] )
                    if 'outside="' in l:
                        bngl_obj['parent'] = l[l.find('outside="')+9:].split('"')[0]
                        print ( "bngl object parent = " + bngl_obj['parent'] )
                    if 'spatialDimensions="' in l:
                        bngl_obj['dim'] = l[l.find('spatialDimensions="')+19:].split('"')[0]
                        print ( "bngl object dim = " + bngl_obj['dim'] )
                    if 'size="' in l:
                        bngl_obj['size'] = l[l.find('size="')+6:].split('"')[0]
                        print ( "bngl object size = " + bngl_obj['size'] )
                    if 'parent' in bngl_obj:
                        bngl_lines.append  ( "  " + bngl_obj['id'] + " "  + bngl_obj['dim'] + " " + bngl_obj['size'] + " " + bngl_obj['parent'] )
                    else:
                        bngl_lines.append  ( "  " + bngl_obj['id'] + " "  + bngl_obj['dim'] + " " + bngl_obj['size'] )
                bngl_lines.append ( "end compartments" )
                bngl_lines.append ( "end model" )
                bngl_text = '\n'.join(bngl_lines) + '\n'
                
                print ( "Final file:\n" + bngl_text )
                
                print ( "Converting to a data model..." )
                dm = bngl_to_data_model.read_data_model_from_bngl_text(bngl_text)
                print ( "Done converting to a data model..." )
                
                ## Upgrade the data model that was just built
                print ( "Model Objects before upgrade = " + str(dm['mcell']['model_objects']) )
                print ( "Geometrical Objects before upgrade = " + str(dm['mcell']['geometrical_objects']) )


                print ( "Deleting all mesh objects" )
                mcell.model_objects.delete_all_mesh_objects(context)
                if "materials" in dm['mcell']:
                    print ( "Overwriting the materials properties" )
                    print ( "Building Materials from Data Model Materials" )
                    mcell.model_objects.build_materials_from_data_model_materials ( context, dm['mcell']['materials'] )
                if "geometrical_objects" in dm['mcell']:
                    print ( "Overwriting the geometrical_objects properties" )
                    print ( "Building Mesh Geometry from Data Model Geometry" )
                    mcell.model_objects.build_mesh_from_data_model_geometry ( context, dm['mcell']["geometrical_objects"] )
                print ( "Not fully implemented yet!!!!" )


                if "model_objects" in dm['mcell']:
                    print ( "Overwriting the model_objects properties" )
                    print ( "Building Model Objects from Data Model Objects" )
                    mcell.model_objects.build_properties_from_data_model ( context, dm['mcell']["model_objects"] )


            else:
                print ( "Model does not contain listOfCompartments" )


        return {'FINISHED'}

class ImportCBNGL(bpy.types.Operator, ImportHelper):
    bl_idname = "cbngl.import_data"
    bl_label = "Import CBNGL Model"
    bl_description = "Import CBNGL model replacing the current model"

    filename_ext = ".bngl"

    filter_glob = StringProperty ( default="*.bngl", options={'HIDDEN'} )

    add_to_model_objects = BoolProperty(
	        name="Add to Model Objects",
	        description="Automatically add all meshes to the Model Objects list",
	        default=True,)

    def execute(self, context):
        bngfilepath = self.filepath         # bngl file path
        print ( "Loading CBNGL model from \"" + str(bngfilepath) )
        mcell_dm = bngl_to_data_model.read_data_model_from_bngl_file ( bngfilepath )
        mcell_dm = context.scene.mcell.upgrade_data_model ( mcell_dm['mcell'] )
        context.scene.mcell.build_properties_from_data_model ( context, mcell_dm, geometry=True, scripts=True )
        return {'FINISHED'}

def menu_func_bng_import(self, context):
    self.layout.operator("bng.import_data", text="BioNetGen/SBML Model (.bngl,.xml)")

def menu_func_cbng_import(self, context):
    self.layout.operator("cbngl.import_data", text="Compartmental BioNetGen Model (.bngl)")

def register():
    bpy.types.INFO_MT_file_import.append(menu_func_bng_import)
    bpy.types.INFO_MT_file_import.append(menu_func_cbng_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_cbng_import)
    bpy.types.INFO_MT_file_import.remove(menu_func_bng_import)

if __name__ == "__main__": 
    register()

