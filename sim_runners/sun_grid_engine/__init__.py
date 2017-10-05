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


# Description of files created in blend_file_name_files/mcell directory for a run with 2 seeds and 3 parameter settings:

# master_job_list.sh contains the list of qsub commands:
#
# echo "Start of master job list"
# cd /home/.../blend_file_files/mcell/output_data
# qsub -o /home/.../blend_file_files/mcell/log_0.txt -e /home/.../blend_file_files/mcell/error_0.txt -l mt=2G -m e -M user@addr.com /home/.../blend_file_files/mcell/job_0.sh
# qsub -o /home/.../blend_file_files/mcell/log_1.txt -e /home/.../blend_file_files/mcell/error_1.txt -l mt=2G -m e -M user@addr.com /home/.../blend_file_files/mcell/job_1.sh
# qsub -o /home/.../blend_file_files/mcell/log_2.txt -e /home/.../blend_file_files/mcell/error_2.txt -l mt=2G -m e -M user@addr.com /home/.../blend_file_files/mcell/job_2.sh
# qsub -o /home/.../blend_file_files/mcell/log_3.txt -e /home/.../blend_file_files/mcell/error_3.txt -l mt=2G -m e -M user@addr.com /home/.../blend_file_files/mcell/job_3.sh
# qsub -o /home/.../blend_file_files/mcell/log_4.txt -e /home/.../blend_file_files/mcell/error_4.txt -l mt=2G -m e -M user@addr.com /home/.../blend_file_files/mcell/job_4.sh
# qsub -o /home/.../blend_file_files/mcell/log_5.txt -e /home/.../blend_file_files/mcell/error_5.txt -l mt=2G -m e -M user@addr.com /home/.../blend_file_files/mcell/job_5.sh
# echo "End of master job list"

# Each job file (job_#.sh) will contain a "cd" command and an mcell command:
#
# cd /home/.../blend_file_files/mcell/output_data/dc_index_0
# /home/.../build/mcell -seed 1 Scene.main.mdl

# <pep8 compliant>

import os
import subprocess
import sys
import time

import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, PointerProperty, StringProperty, BoolVectorProperty

plug_code = "SGE_HOST_SEL"
plug_name = "SGE Host Select"
plug_complete = 0.4
# plug_active = False

def term_all():
    print ( "Terminating all jobs ..." )

def info():
    print ( "Print SGE Information" )

def fetch():
    # Move files as required by parameters
    submit_host = parameter_dictionary['Submit Host']['val']
    project_dir = parameter_dictionary['project_dir']['val']
    remote_path = parameter_dictionary['Remote Path']['val']
    remote_user = parameter_dictionary['Remote User']['val']
    remote_path = os.path.join(remote_path, os.path.split(project_dir)[-1])
    if len(remote_path) > 0:
        print ( "Local Blend_files Directory = " + project_dir )
        print ( "Moving files from remote path: \"" + remote_path + "\"" )
        rsync_command = []
        if len(remote_user) > 0:
            rsync_command = [ "rsync", "-avz", "%s@%s:%s" % (remote_user, submit_host, remote_path), os.path.split(project_dir)[0] ]
        else:
            rsync_command = [ "rsync", "-avz", "%s:%s" % (submit_host, remote_path), os.path.split(project_dir)[0] ]
        print ( "rsync command = " + str(rsync_command) )
        subprocess.Popen ( rsync_command, stdout=None, stderr=None )


parameter_dictionary = {
  'Notice': {'val':"Notice: File transfer functionality is under development.", 'icon':"ERROR"},
  'Submit Host': {'val': "", 'desc':"Host for SGE Job Submission"},
  'Email': {'val': "", 'desc':"Email address for notification"},
  'Remote User': {'val':"", 'desc':"User name on remote system"},
  'Remote Path': {'val':"", 'desc':"Path to files on remote system (blank for shared files)"},
  'Required Memory (G)': {'val': 2, 'desc':"Required Memory for Host Selection"},
  'Best Nodes': {'val': "", 'desc':"List of best nodes to use"},
  'Fetch': {'val': fetch, 'desc':"Get data back from remote host"},
  'Terminate All': {'val': term_all, 'desc':"Terminate All Jobs"},
  'Information': {'val': info, 'desc':"Print Information"},

  'project_dir': {'val': "", 'desc':"INTERNAL: project directory storage"}
}

parameter_layout = [
  ['Notice'],
  ['Submit Host', 'Email'],
  ['Remote User', 'Remote Path'],
  ['Required Memory (G)', 'Best Nodes'],
  ['Fetch', 'Terminate All', 'Information']
]



def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def run_engine ( engine_module, data_model, project_dir ):
    command_list = None
    dm = None
    print ( "Calling prepare_runs... in engine_module" )
    if 'prepare_runs_no_data_model' in dir(engine_module):
        command_list = engine_module.prepare_runs_no_data_model ( project_dir )
    elif 'prepare_runs_data_model_no_geom' in dir(engine_module):
        command_list = engine_module.prepare_runs_data_model_no_geom ( data_model, project_dir )
    elif 'prepare_runs_data_model_full' in dir(engine_module):
        command_list = engine_module.prepare_runs_data_model_full ( data_model, project_dir )

    return run_commands ( command_list )


def run_commands ( commands ):
    sp_list = []

    print ( "run_commands" )
    for cmd in commands:
      print ( "  CMD: " + str(cmd['cmd']) + " " + str(cmd['args']) )
      """
      CMD: {
        'args': ['print_detail=20',
                 'proj_path=/.../intro/2017/2017_07/2017_07_11/queue_runner_tests_files/mcell',
                 'seed=1',
                 'data_model=dm.json'],
        'cmd': '/.../blender/2.78/scripts/addons/cellblender/sim_engines/limited_cpp/mcell_main',
        'wd':  '/.../intro/2017/2017_07/2017_07_11/queue_runner_tests_files/mcell',
        'stdout': '',
        'stderr': ''
      }
      """

    # Convert parameter_dictionary entries to convenient local variables
    submit_host = parameter_dictionary['Submit Host']['val']
    email = parameter_dictionary['Email']['val']
    remote_user = parameter_dictionary['Remote User']['val']
    remote_path = parameter_dictionary['Remote Path']['val']

    best_nodes = None
    if len ( parameter_dictionary['Best Nodes']['val'] ) > 0:
        best_nodes = parameter_dictionary['Best Nodes']['val']

    min_memory = parameter_dictionary['Required Memory (G)']['val']



    # Figure out a "project_dir" from the common path of the working directories
    project_dir = ""
    paths_list = []
    for cmd in commands:
        if type(cmd) != type({'a':1}):
            print ( "Error: SGE Runner requires engines that produce dictionary commands containing a working directory ('wd') entry" )
            return sp_list
        elif not 'wd' in cmd:
            print ( "Error: SGE Runner requires engines that produce dictionary commands containing a working directory ('wd') entry" )
            return sp_list
        else:
            paths_list.append ( cmd['wd'] )
    project_dir = os.path.commonpath ( paths_list )
    if os.path.split(project_dir)[-1] == 'output_data':
        # Remove the last "output_data" which should be at the end of the path
        project_dir = os.path.sep.join ( os.path.split(project_dir)[0:-1] )
    if os.path.split(project_dir)[-1] == 'mcell':
        # Remove the last "mcell" which should be at the end of the path
        project_dir = os.path.sep.join ( os.path.split(project_dir)[0:-1] )
    print ( "Project Directory = " + project_dir )

    parameter_dictionary['project_dir']['val'] = project_dir


    # Move files as required by parameters
    if len(remote_path) > 0:
        print ( "Local Blend_files Directory = " + project_dir )
        print ( "Moving files to remote path: \"" + remote_path + "\"" )
        rsync_command = []
        if len(remote_user) > 0:
            rsync_command = [ "rsync", "-avz", project_dir, "%s@%s:%s" % (remote_user, submit_host, remote_path) ]
        else:
            rsync_command = [ "rsync", "-avz", project_dir, "%s:%s" % (submit_host, remote_path) ]
        print ( "rsync command = " + str(rsync_command) )
        subprocess.Popen ( rsync_command, stdout=None, stderr=None )



    # Build 1 master qsub file and a job file for each MCell run

    master_job_list_name = os.path.join ( project_dir, "master_job_list.sh" )
    master_job_list = open ( master_job_list_name, "w" )
    master_job_list.write ( 'echo "Start of master job list"\n' )
    master_job_list.write ( "cd %s\n" % os.path.join(project_dir,"mcell","output_data") )
    job_index = 0
    for run_cmd in commands:

        job_filename = "job_%d.sh" % (job_index)
        job_filepath = os.path.join(project_dir, job_filename)

        log_filename = "log_%d.txt" % (job_index)
        log_filepath = os.path.join(project_dir, log_filename)

        error_filename = "error_%d.txt" % (job_index)
        error_filepath = os.path.join(project_dir, error_filename)

        job_file = open(job_filepath,"w")
        if len(remote_path) > 0:
          wd_list = run_cmd['wd'].split(os.sep)
          pd_list = project_dir.split(os.sep)
          remote_wd = os.sep.join(wd_list[len(pd_list)-1:])
          remote_wd = os.path.join(remote_path,remote_wd)
          job_file.write ( "cd %s\n" % remote_wd )
        else:
          job_file.write ( "cd %s\n" % run_cmd['wd'] )
        full_cmd = run_cmd['cmd']
        if len(run_cmd['args']) > 0:
          full_cmd = full_cmd + " " + " ".join(run_cmd['args'])
        job_file.write ( full_cmd + "\n" )
        job_file.close()

        qsub_command = "qsub"
        # qsub_command += " -wd " + subprocess_cwd
        qsub_command += " -o " + log_filepath
        qsub_command += " -e " + error_filepath
        resource_list = []
        if best_nodes != None:
            resource_list.append ( "h=" + best_nodes[job_index%len(best_nodes)][0] )
        if min_memory > 0:
            resource_list.append ( "mt=" + str(min_memory) + "G" )
        if len(resource_list) > 0:
            qsub_command += " -l " + ",".join(resource_list)
        if len(email) > 0:
            qsub_command += " -m e"
            qsub_command += " -M " + email
        qsub_command += " " + job_filepath

        master_job_list.write ( qsub_command + "\n" )

        job_index += 1


    master_job_list.write ( 'echo "End of master job list"\n' )
    master_job_list.close()
    os.chmod ( master_job_list_name, 0o740 )  # Must make executable

    args = ['ssh', submit_host, master_job_list_name ]
    print ( "Args for Popen: " + str(args) )
    p = subprocess.Popen ( args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

    pi = p.stdin
    po = p.stdout
    pe = p.stderr

    print ( "Waiting for something from subprocess ..." )
    count = 0
    while len(po.peek()) == 0:
        # Wait for something
        time.sleep ( 0.01 )
        count = count + 1
        if count > 100:
            break

    print ( "Waiting for pause from subprocess..." )
    count = 0
    while (len(po.peek()) > 0) and (count < 1000):
        # Wait for nothing
        # time.sleep ( 0.01 )
        if b'\n' in po.peek():
            line = str(po.readline())
            print ( "J: " + str(line) )
            count = 0
        count = count + 1
        # print ( "Count = " + str(count) )
        #if b"nothing" in po.peek():
        #  break
    #print ( "Terminating subprocess..." )
    #p.kill()

    return sp_list.append ( p )




class sge_interface:

    def read_a_line ( self, process_output, wait_count, sleep_time ):
        count = 0
        while (len(process_output.peek()) > 0) and (count < wait_count):
            # Keep checking for a full line
            if b'\n' in process_output.peek():
                line = str(process_output.readline())
                if line != None:
                    return line
            else:
                # Not a full line yet, so kill some time
                time.sleep ( sleep_time )
            count = count + 1
        # Try to read the line anyway ... this seems to be needed in some cases
        line = str(process_output.readline())
        if line != None:
            return line
        return None


    def wait_for_anything (self, pipe_in, sleep_time, max_count):
        count = 0
        while len(pipe_in.peek()) == 0:
            # Wait for something
            time.sleep ( sleep_time )
            count = count + 1
            if count > max_count:
                # That's enough waiting
                break

    def wait_for_line_start (self, pipe_in, line_start, max_wait_count, line_wait_count, line_sleep_time):
        num_wait = 0
        while True:
            line = self.read_a_line ( pipe_in, 100, 0.001 )
            num_wait += 1
            if num_wait > 1000:
                break
            if line == None:
                break
            if line.startswith("b'----------"):
                break

    def kill_all_users_jobs (self, host_name, user_name):
        num_wait = 0

        args = ['ssh', host_name, 'qdel', '-u', user_name]

        p = subprocess.Popen ( args, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        pi = p.stdin
        po = p.stdout
        pe = p.stderr

        # Read lines until done

        num_wait = 0
        while True:
            line = self.read_a_line ( po, 100, 0.001 )
            if line == None:
                break
            elif len(line.strip()) == 0:
                break
            elif str(line) == "b''":
                break
            else:
                num_wait = 0
                print ( line )
            num_wait += 1
            if num_wait > 1000:
                print ( "Submit Host " + engine_props.sge_host_name + " seems unresponsive. List may not be complete." )
                break
        p.kill()


    def get_hosts_information (self, host_name):
        # Build generic Python structures to use for filling Blender properties later
        name_list = []
        comp_dict = {}


        # First pass - Use qhost to build the basic structure (additional passes will add to it)
        args = ['ssh', host_name, 'qhost']

        p = subprocess.Popen ( args, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        pi = p.stdin
        po = p.stdout
        pe = p.stderr

        # Start by waiting for any kind of response

        self.wait_for_anything (po, 0.01, 100)

        # Read lines until the header line has been found

        self.wait_for_line_start (po, "b'----------", 1000, 100, 0.001)

        # Read lines until done

        num_wait = 0
        while True:
            line = self.read_a_line ( po, 100, 0.001 )
            if line == None:
                break
            elif len(line.strip()) == 0:
                break
            elif str(line) == "b''":
                break
            else:
                num_wait = 0
                print ( " Pass 1 SGE: " + str(line) )
                try:
                    comp = {}
                    fields = line[2:len(line)-3].split()
                    comp['comp_props'] = ','.join(fields[1:])
                    comp['name']  = fields[0].strip()
                    comp['mem']   = fields[4].strip()
                    comp['cores_in_use'] = 0
                    comp['cores_total'] = 0
                    name_list.append ( comp['name'] )
                    comp_dict[comp['name']] = comp
                except Exception as err:
                    # This line didn't contain proper fields, so don't add it to the list
                    print ( "This line didn't contain proper fields, so don't add it to the list" + line )
                    pass
            num_wait += 1
            if num_wait > 1000:
                print ( "Submit Host " + engine_props.sge_host_name + " seems unresponsive. List may not be complete." )
                break
        p.kill()


        # Second pass - Use qhost -q to add the number of cores in use and available
        args = ['ssh', host_name, 'qhost', '-q']

        p = subprocess.Popen ( args, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        pi = p.stdin
        po = p.stdout
        pe = p.stderr

        # Start by waiting for any kind of response

        self.wait_for_anything (po, 0.01, 100)

        # Read lines until the header line has been found

        self.wait_for_line_start (po, "b'----------", 1000, 100, 0.001)

        # Read lines until done

        num_wait = 0
        most_recent_host = "";
        while True:
            line = self.read_a_line ( po, 100, 0.001 )
            if line == None:
                most_recent_host = "";
                break
            elif len(line.strip()) == 0:
                most_recent_host = "";
                break
            elif str(line) == "b''":
                most_recent_host = "";
                break
            else:
                num_wait = 0
                print ( " Pass 2 SGE: " + str(line) )
                try:
                    fields = line[2:len(line)-3].split()
                    if fields[0].strip() in comp_dict:
                        # The returned name matches a known host, so store the name in preparation for a subsequent line
                        most_recent_host = fields[0].strip()
                    else:
                        if len(most_recent_host) > 0:
                            # The previous line should have been a valid host, and this line should contain: queue BIPC cores_in_use/cores_available
                            if fields[1].strip() == "BIPC":
                                core_info = [ int(f.strip()) for f in fields[2].strip().split('/') ]
                                comp = comp_dict[most_recent_host]
                                comp['cores_in_use'] = core_info[0]
                                comp['cores_total'] = core_info[1]
                                print ( "Cores for " + most_recent_host + " " + core_info[0] + "/" + core_info[1] )
                except Exception as err:
                    most_recent_host = "";
                    # This line didn't contain proper fields, so don't add it to the list
                    print ( "This line didn't contain proper fields, so don't add it to the list" + line )
                    pass
            num_wait += 1
            if num_wait > 1000:
                print ( "Submit Host " + engine_props.sge_host_name + " seems unresponsive. List may not be complete." )
                break
        p.kill()
        return ( name_list, comp_dict )




class MCellComputerProperty(bpy.types.PropertyGroup):
    comp_name = StringProperty ( default="", description="Computer name" )
    comp_mem = FloatProperty ( default=0, description="Total Memory" )
    cores_in_use = IntProperty ( default=0, description="Cores in use" )
    cores_total = IntProperty ( default=0, description="Cores total" )
    comp_props = StringProperty ( default="", description="Computer properties" )
    selected = BoolProperty ( default=False, description="Select for running" )

class MCell_UL_computer_item ( bpy.types.UIList ):
    def draw_item (self, context, layout, data, item, icon, active_data, active_propname, index):
      col = layout.column()
      col.label ( item.comp_name + "  " + str(int(item.comp_mem)) + "G " + str(item.cores_in_use) + "/" + str(item.cores_total) )
      col = layout.column()
      if item.selected:
          col.prop ( item, "selected", text="", icon="POSE_DATA" )
      else:
          col.prop ( item, "selected", text="" )

class EnginePropertyGroup(bpy.types.PropertyGroup):
    enable_python_scripting = BoolProperty ( name='Enable Python Scripting', default=False )  # Intentionally not in the data model
    sge_host_name = StringProperty ( default="", description="Name of Grid Engine Scheduler" )
    sge_email_addr = StringProperty ( default="", description="Email address for notifications" )
    computer_list = CollectionProperty(type=MCellComputerProperty, name="Computer List")
    required_memory_gig = FloatProperty(default=2.0, description="Minimum memory per job - used for selecting hosts")
    required_free_slots = IntProperty(default=1, description="Minimum free slots for selecting hosts")
    active_comp_index = IntProperty(name="Active Computer Index", default=0)

    show_sge_control_panel = BoolProperty ( name="Host Selection Details", default=False, description="Show or hide the Grid Engine host selection controls" )
    manual_sge_host = BoolProperty ( name="Select execution hosts manually", default=False, description="Select execution hosts from a capabilities list" )


    def draw_layout(self, context, layout):
        mcell = context.scene.mcell
        run_sim = mcell.run_simulation
        engine_props = context.scene.mcell_engine_props
        ps = mcell.parameter_system

        row = layout.row()
        run_sim.start_seed.draw(layout,ps)
        run_sim.end_seed.draw(layout,ps)
        run_sim.run_limit.draw(layout,ps)

        row = layout.row()
        row.prop(run_sim, "mcell_processes")
        #row = layout.row()
        #row.prop(run_sim, "log_file")
        #row = layout.row()
        #row.prop(run_sim, "error_file")
        row = layout.row()
        row.prop(mcell.export_project, "export_format")


        row = layout.row()
        row.prop(run_sim, "remove_append", expand=True)
        
        """

        if cellblender_sim.global_scripting_enabled_once:
            helptext = "Allow Running of Python Code in Scripting Panel - \n" + \
                       " \n" + \
                       "The Scripting Interface can run Python code contained\n" + \
                       "in text files (text blocks) within Blender.\n" + \
                       "\n" + \
                       "Running scripts from unknown sources is a security risk.\n" + \
                       "Only enable this option if you are confident that all of\n" + \
                       "the scripts contained in this .blend file are safe to run."
            ps.draw_prop_with_help ( layout, "Enable Python Scripting", run_sim,
                       "enable_python_scripting", "python_scripting_show_help",
                       run_sim.python_scripting_show_help, helptext )
        else:
            helptext = "Initialize Python Code Scripting for this Session\n" + \
                       "This must be done each time CellBlender is restarted."
            ps.draw_operator_with_help ( layout, "Enable Python Scripting", run_sim,
                       "mcell.initialize_scripting", "python_initialize_show_help",
                       run_sim.python_initialize_show_help, helptext )

        """

        row = layout.row()
        col = row.column()
        col.prop(mcell.cellblender_preferences, "decouple_export_run")


        box = layout.box()


        # box = layout.box()
        row = layout.row()
        subbox = row.box()
        row = subbox.row()
        col = row.column()
        col.prop ( self, "sge_host_name", text="Submit Host" )
        col = row.column()
        col.prop ( self, "sge_email_addr", text="Email" )

        row = subbox.row()
        row.alignment = 'LEFT'
        if not self.show_sge_control_panel:
            col = row.column()
            col.alignment = 'LEFT'
            col.prop ( self, "show_sge_control_panel", icon='TRIA_RIGHT', emboss=False )
            col = row.column()
            col.prop ( self, "manual_sge_host" )

        else:
            col = row.column()
            col.alignment = 'LEFT'
            col.prop ( self, "show_sge_control_panel", icon='TRIA_DOWN', emboss=False )
            col = row.column()
            col.prop ( self, "manual_sge_host" )

            if not self.manual_sge_host:
                row = subbox.row()
                col = row.column()
                col.prop ( self, "required_memory_gig", text="Memory(G)" )
                col = row.column()
                col.operator ( "sge.kill_all_users_jobs" )
            else:
                row = subbox.row()
                col = row.column()
                col.operator( "sge.refresh_sge_list", icon='FILE_REFRESH' )
                row = subbox.row()
                row.template_list("MCell_UL_computer_item", "computer_item",
                                  self, "computer_list", self, "active_comp_index", rows=4 )
                row = subbox.row()
                col = row.column()
                col.prop ( self, "required_memory_gig", text="Memory(G)" )
                col = row.column()
                col.prop ( self, "required_free_slots", text="Free Slots" )
                col = row.column()
                col.operator( "sge.select_with_required" )

                row = subbox.row()
                col = row.column()
                col.operator ( "sge.select_all_computers" )
                col = row.column()
                col.operator ( "sge.deselect_all_computers" )
                col = row.column()
                col.operator ( "sge.kill_all_users_jobs" )





class SGE_OT_refresh_sge_list(bpy.types.Operator):
    bl_idname = "sge.refresh_sge_list"
    bl_label = "Refresh the Execution Host list"
    bl_description = ("Refresh the list of execution hosts in the Sun Grid Engine list.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Refreshing the SGE execution host list" )
        engine_props = context.scene.mcell_engine_props
        if len(engine_props.sge_host_name) <= 0:
            print ( "Error: SGE Submit Host name is empty" )
        else:
            engine_props.computer_list.clear()
            engine_props.active_comp_index = 0

            # Get the host information as a name list and a dictionary of capabilities for each computer

            sge = sge_interface()
            ( name_list, comp_dict ) = sge.get_hosts_information ( engine_props.sge_host_name )

            # Build the Blender properties from the list

            for name in name_list:
                if comp_dict[name]['mem'] != '-':   # Filter out the "global" node which has "-" for all fields
                    print ( "Adding to computer_list: " + name )
                    engine_props.computer_list.add()
                    engine_props.active_comp_index = len(engine_props.computer_list) - 1
                    new_comp = engine_props.computer_list[engine_props.active_comp_index]
                    new_comp.comp_name = comp_dict[name]['name']
                    new_comp.comp_props = comp_dict[name]['comp_props']
                    new_comp.cores_in_use = comp_dict[name]['cores_in_use']
                    new_comp.cores_total = comp_dict[name]['cores_total']
                    try:
                        # Parse the memory specification (#M,#G,#T)
                        new_comp.comp_mem = float(comp_dict[name]['mem'][:-1])
                        if comp_dict[name]['mem'][-1] == 'G':
                            # No change ... report everything in G for CellBlender interface
                            pass
                        elif comp_dict[name]['mem'][-1] == 'M':
                            new_comp.comp_mem *= 1.0/1024
                        elif comp_dict[name]['mem'][-1] == 'T':
                            new_comp.comp_mem *= 1024
                        elif comp_dict[name]['mem'][-1] == 'P':
                            new_comp.comp_mem *= 1024 * 1024
                        elif comp_dict[name]['mem'][-1] == 'E':
                            new_comp.comp_mem *= 1024 * 1024 * 1024
                        elif comp_dict[name]['mem'][-1] == 'K':
                            new_comp.comp_mem *= 1.0/(1024 * 1024)
                        else:
                            print ( "Unidentified memory units used in: \"" + comp_dict[name]['mem'] + "\"" )
                            new_comp.comp_mem = 0
                    except Exception as err:
                        print ( "Exception translating memory specification: \"" +  comp_dict[name]['mem'] + "\", exception = " + str(err) )
                        pass

            engine_props.active_comp_index = 0

        return {'FINISHED'}


class SGE_OT_select_all_computers(bpy.types.Operator):
    bl_idname = "sge.select_all_computers"
    bl_label = "Select All"
    bl_description = ("Select all computers.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        engine_props = context.scene.mcell_engine_props
        computer_list = engine_props.computer_list
        for computer in computer_list:
            computer.selected = True
        return {'FINISHED'}

class SGE_OT_deselect_all_computers(bpy.types.Operator):
    bl_idname = "sge.deselect_all_computers"
    bl_label = "Select None"
    bl_description = ("Select no computers.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        engine_props = context.scene.mcell_engine_props
        computer_list = engine_props.computer_list
        for computer in computer_list:
            computer.selected = False
        return {'FINISHED'}


class SGE_OT_kill_all_users_jobs(bpy.types.Operator):
    bl_idname = "sge.kill_all_users_jobs"
    bl_label = "Terminate All"
    bl_description = ("Kill all jobs run by the current user name.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        engine_props = context.scene.mcell_engine_props
        sge = sge_interface()
        sge.kill_all_users_jobs ( engine_props.sge_host_name, os.getlogin() );
        return {'FINISHED'}


class SGE_OT_select_with_required(bpy.types.Operator):
    bl_idname = "sge.select_with_required"
    bl_label = "Select"
    bl_description = ("Select computers meeting requirements.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Selecting" )
        engine_props = context.scene.mcell_engine_props
        computer_list = engine_props.computer_list
        for computer in computer_list:
            #print ( "Computer " + str(computer.comp_name.split()[0]) + " selection = " + str(computer.selected) )
            #print ( "Is \"" + str(computer.comp_mem) + "\" > " + str(engine_props.required_memory_gig) + " ?" )
            if (computer.comp_mem >= engine_props.required_memory_gig) and ((computer.cores_total - computer.cores_in_use) >= engine_props.required_free_slots):
                print ( "  Selected to run on " + str(computer.comp_name) )
                computer.selected = True
            else:
                computer.selected = False
        return {'FINISHED'}




def draw_layout ( self, context, layout ):
    engine_props = context.scene.mcell_engine_props
    if 'mcell_engine_props' in context.scene:
        engine_props.draw_layout ( context, layout )




def register_blender_classes():
    print ( "Registering Sun Grid Engine classes" )
    bpy.utils.register_class(MCellComputerProperty)
    bpy.utils.register_class(MCell_UL_computer_item)
    bpy.utils.register_class(EnginePropertyGroup)
    bpy.types.Scene.mcell_engine_props = bpy.props.PointerProperty(type=EnginePropertyGroup)
    bpy.utils.register_class(SGE_OT_refresh_sge_list)
    bpy.utils.register_class(SGE_OT_select_all_computers)
    bpy.utils.register_class(SGE_OT_deselect_all_computers)
    bpy.utils.register_class(SGE_OT_kill_all_users_jobs)
    bpy.utils.register_class(SGE_OT_select_with_required)
    print ( "Done Registering" )


def unregister_this_class(this_class):
    try:
      bpy.utils.unregister_class(this_class)
    except Exception as ex:
      pass

def unregister_blender_classes():
    print ( "UnRegistering Sun Grid Engine classes" )
    unregister_this_class(MCellComputerProperty)
    unregister_this_class(MCell_UL_computer_item)
    unregister_this_class(EnginePropertyGroup)
    unregister_this_class(SGE_OT_refresh_sge_list)
    unregister_this_class(SGE_OT_select_all_computers)
    unregister_this_class(SGE_OT_deselect_all_computers)
    unregister_this_class(SGE_OT_kill_all_users_jobs)
    unregister_this_class(SGE_OT_select_with_required)
    print ( "Done Unregistering" )



if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
