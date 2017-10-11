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

plug_code = "CMDLINE"
plug_name = "Command Line"
plug_complete = 0.4


parameter_dictionary = {
  'Print Commands': {'val':False, 'desc':"Print the commands to be executed"},
}


# This runner class will cause this module to be recognized as supporting runner objects
class runner:

    def __init__ ( self, runner_module, engine ):  # Note: couldn't use __module__ to get this information for some reason
        print ( "Module contains " + str(dir(runner_module)) )
        self.name = runner_module.plug_name
        self.engine = engine
        self.par_dict = {}
        self.sp_list = []
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
        if self.par_dict['Print Commands']['val']:
            print ( "Commands for " + plug_name + " runner:" )
            for cmd in commands:
                print ( "  " + str(cmd) )

        self.sp_list = []
        for cmd in commands:
            command_list = []
            if type(cmd) == type('str'):
                # This command is a string, so just append it
                command_list.append ( cmd )
                self.sp_list.append ( subprocess.Popen ( command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) )
            elif type(cmd) == type({'a':1}):
                # This command is a dictionary, so use its keys:
                command_list.append ( cmd['cmd'] )  # The dictionary must contain a 'cmd' key
                if 'args' in cmd:
                    for arg in cmd['args']:
                        # For some reason, the ' ' in the args may be creating a problem for "-seed 1"
                        # This isn't a problem in the Java or OpenGL runners, but it is here.
                        # So ... check for spaces and split into additional arguments
                        if ' ' in arg:
                          for s in arg.split(' '):
                            command_list.append ( s )
                        else:
                          command_list.append ( arg )
                if self.par_dict['Print Commands']['val']:
                    print ( "Popen with: " + str(command_list) )
                if 'wd' in cmd:
                    self.sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE ) )
                else:
                    self.sp_list.append ( subprocess.Popen ( command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) )

        return self.sp_list


def run_commands ( commands ):
    print ( "Running commands inside runner module" )
    if parameter_dictionary['Print Commands']['val']:
        print ( "Commands for " + plug_name + " runner:" )
        for cmd in commands:
            print ( "  " + str(cmd) )

    sp_list = []
    for cmd in commands:
        command_list = []
        if type(cmd) == type('str'):
            # This command is a string, so just append it
            command_list.append ( cmd )
            sp_list.append ( subprocess.Popen ( command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) )
        elif type(cmd) == type({'a':1}):
            # This command is a dictionary, so use its keys:
            command_list.append ( cmd['cmd'] )  # The dictionary must contain a 'cmd' key
            if 'args' in cmd:
                for arg in cmd['args']:
                    # For some reason, the ' ' in the args may be creating a problem for "-seed 1"
                    # This isn't a problem in the Java or OpenGL runners, but it is here.
                    # So ... check for spaces and split into additional arguments
                    if ' ' in arg:
                      for s in arg.split(' '):
                        command_list.append ( s )
                    else:
                      command_list.append ( arg )
            if parameter_dictionary['Print Commands']['val']:
                print ( "Popen with: " + str(command_list) )
            if 'wd' in cmd:
                sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE ) )
            else:
                sp_list.append ( subprocess.Popen ( command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) )

    return sp_list

