bl_info = {
  "version": "0.1",
  "name": "Tutorial Maker",
  'author': 'Bob',
  "location": "Properties > Scene",
  "category": "Blender Experiments"
  }

import bpy
from bpy.props import *

class CREATE_OT_tutorial(bpy.types.Operator):
    bl_idname = "create.tutorial"
    bl_label = "Create Tutorial"
    bl_description = ("Create a Tutorial")

    def execute(self, context):
        bpy.ops.mesh.primitive_cone_add()
        return{'FINISHED'}

class CreateTutorialPanel(bpy.types.Panel):
    bl_label = "Create Tutorial"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    def draw(self, context):
        row = self.layout.row()
        row.operator("create.tutorial")

def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)

def unregister():
    print ("Unregistering ", __name__)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

