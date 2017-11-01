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

import os
import subprocess
import sys

plug_code = "OPENGL"
plug_name = "OpenGL Control"
plug_complete = 0.6


def reset():
    print ( "Resetting" )

def info():
    print ( "Print OpenGL Information" )

parameter_dictionary = {
  'OpenGL Path': {'val': "", 'as':'filename', 'desc':"Optional Path", 'icon':'SCRIPTWIN'},
  'Print OpenGL Information': {'val': info, 'desc':"Print information"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['OpenGL Path'],
  ['Print OpenGL Information', 'Reset']
]


# This runner class will cause this module to be recognized as supporting runner objects
class runner:

    def __init__ ( self, runner_module, engine ):  # Note: couldn't use __module__ to get this information for some reason
        print ( "Module contains " + str(dir(runner_module)) )
        self.name = runner_module.plug_name
        self.engine = engine
        self.par_dict = {}
        if 'parameter_dictionary' in dir(runner_module):
            # Make a deep copy of the engine module's parameter dictionary since it may be changed while running
            for k in runner_module.parameter_dictionary.keys():
              self.par_dict[k] = runner_module.parameter_dictionary[k].copy()

    def get_status_string ( self ):
        stat = self.name
        if 'engine' in dir(self):
            if 'get_status_string' in dir(self.engine):
                stat = stat + " running " + self.engine.get_status_string()
            else:
                stat = stat + " running " + self.engine.name
        return stat

    def run_commands ( self, commands ):
        print ( "Running commands inside runner class" )
        sp_list = []
        window_num = 0
        for cmd in commands:
            command_list = [ os.path.join(os.path.dirname(os.path.realpath(__file__)),"SimControl") ]
            command_list.append ( "x=%d" % ((50*(1+window_num))%500) ),
            command_list.append ( "y=%d" % ((40*(1+window_num))%400) ),
            command_list.append ( ":" ),
            if type(cmd) == type('str'):
                # This command is a string, so just append it
                command_list.append ( cmd )
                sp_list.append ( subprocess.Popen ( command_list, stdout=None, stderr=None ) )
            elif type(cmd) == type({'a':1}):
                # This command is a dictionary, so use its keys:
                command_list.append ( cmd['cmd'] )  # The dictionary must contain a 'cmd' key
                if 'args' in cmd:
                    for arg in cmd['args']:
                        command_list.append ( arg )
                if 'wd' in cmd:
                    sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=None, stderr=None ) )
                else:
                    sp_list.append ( subprocess.Popen ( command_list, stdout=None, stderr=None ) )
            window_num += 1
        return sp_list



# Temporarily disable this because the engines have changed.
#def run_engine ( engine_module, data_model, project_dir ):
#    print ( "Calling prepare_runs in active_engine_module" )
#    command_list = engine_module.prepare_runs ( data_model, project_dir )
#    return run_commands ( command_list )



if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
