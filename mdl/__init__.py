import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

class ImportMDLData(bpy.types.Operator, ImportHelper):
    bl_idname = "mdl.import_parameters" 
    bl_label = "Import MDL Parameters"
    bl_description = "Import MDL Parameters"
 
    filename_ext = ".mdl"

    filter_glob = StringProperty(default="*.mdl",options={'HIDDEN'},)

    def execute(self, context):
        """ Simple (and not guaranteed to work!!) parsing of parameters from an MDL file """
        print ( "Loading parameters from an MDL file: " + self.filepath )
        mcell = context.scene.mcell
        f = open ( self.filepath, 'r' )
        bracket_depth = 0
        # Read each line of the file
        par_list = []
        for line in f:
            # Keep track of bracket nesting depth to only pull parameters from the top level
            if ('{' in line) and not ('}' in line):
                # We've gotten an opening bracket (and not an open/close pair) on this line
                bracket_depth += 1
            elif ('}' in line) and not ('{' in line):
                # We've gotten a closing bracket (and not an open/close pair) on this line
                bracket_depth += -1
            if (bracket_depth == 0) and (not ('{' in line)) and (not ('}' in line)):
                # We're at the top level on a line with no brackets
                if '=' in line:
                    # This is likely to be a parameter assignment so split it at the equal sign
                    parts = line.split('=',1)
                    if len(parts) >= 2:
                        # Check for strings on the right hand side (can't put a string in a parameter)
                        if parts[1].strip()[0] != '"':
                            # Not a string, so assume this is an assignment
                            vname = parts[0].strip()
                            expr = ""
                            desc = ""
                            units = ""
                            # Find the comment index to get the description and units
                            ci = parts[1].find("/*")
                            if ci < 0:
                                # No comment, just assign value
                                expr = parts[1].strip()
                            else:
                                # Comment found, so split into description and units by the comma
                                expr = parts[1][0:ci].strip()
                                comment = parts[1][ci:].strip()[2:][:-2].strip()
                                if comment.find(',') < 0:
                                    # No comma, so assume it's all description
                                    desc = comment
                                else:
                                    # Assume the convention that a comma separates the description and units
                                    split_comment = comment.split(',',1)
                                    desc = split_comment[0].strip()
                                    units = split_comment[1].strip()
                            print ( vname + " = " + expr + " : " + desc + " (" + units + ")" )
                            par_list.append ( {'par_name':vname, 'par_expression':expr, 'par_units':units, 'par_description':desc} )
                            # mcell.general_parameters.add_parameter_with_values ( vname, expr, units, desc )

        mcell.parameter_system.add_general_parameters_from_list ( context, par_list )

        print ( "Done loading parameters from MDL file." )
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator("mdl.import_parameters", text="MCell MDL Parameters (.mdl)")



classes = (
            ImportMDLData,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)


#def register():
#    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

#def unregister():
#    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

