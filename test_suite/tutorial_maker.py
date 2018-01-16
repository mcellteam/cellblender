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
    """Process actions after a delay so the screen can respond to commands"""
    bl_idname = "create.tutorial"
    bl_label = "Create Tutorial Slides"
    bl_options = {'REGISTER'}

    _timer = None
    _count = 0

    def modal(self, context, event):
        if event.type == 'TIMER':
            print ( "Timer event" )

            if self._count > 0:

                fname = "tutorial_maker_image_" + str(self._count) + ".png"
                print ( "Saving file: " + fname )
                alt_context = {
                    'region'  : None,
                    'area'    : None,
                    'window'  : bpy.context.window,
                    'scene'   : bpy.context.scene,
                    'screen'  : bpy.context.window.screen
                }
                bpy.ops.screen.screenshot(alt_context, filepath=fname, full=True)

                bpy.data.materials['Material'].diffuse_color[0] = self._count % 2 # red
                bpy.data.materials['Material'].diffuse_color[1] = (self._count >> 1) % 2 # green
                bpy.data.materials['Material'].diffuse_color[2] = (self._count >> 2) % 2 # blue
                # just a silly way of forcing a screen update. ¯\_(ツ)_/¯
                color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
                color.h += 0.01
                color.h -= 0.01
                self._count += -1

            else:

                self.cancel(context)

        return {'PASS_THROUGH'}

    def execute(self, context):
        print ( "Inside tutorial.execute with context = " + str(context) )
        delay = 2.0
        print ( "Setting timer to delay of " + str(delay) )
        wm = context.window_manager
        self._count = 5
        self._timer = wm.event_timer_add(delay, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


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

