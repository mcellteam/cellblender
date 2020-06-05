import re, functools, subprocess, os, BNGSim.xmltodict, sys, shutil, tempfile
import BNGSim.xmltodict as xmltodict
from BNGSim.utils import find_BNG_path
from BNGSim.structs import Parameters, Species, MoleculeTypes, Observables, Functions, Compartments, Rules, Actions

###### CORE OBJECT AND PARSING FRONT-END ######
class BNGModel:
    '''
    The full model
    '''
    def __init__(self, bngl_model, BNGPATH=None):
        self.active_blocks = []
        # We want blocks to be printed in the same order
        # every time
        self._action_list = ["generate_network(", "generate_hybrid_model(","simulate(", "simulate_ode(", "simulate_ssa(", "simulate_pla(", "simulate_nf(", "parameter_scan(", "bifurcate(", "readFile(", "writeFile(", "writeModel(", "writeNetwork(", "writeXML(", "writeSBML(", "writeMfile(", "writeMexfile(", "writeMDL(", "visualize(", "setConcentration(", "addConcentration(", "saveConcentration(", "resetConcentrations(", "setParameter(", "saveParameters(", "resetParameters(", "quit(", "setModelName(", "substanceUnits(", "version(", "setOption("]
        self.block_order = ["parameters", "compartments", "moltypes", 
                            "species", "observables", "functions", 
                            "rules", "actions"]
        BNGPATH, bngexec = find_BNG_path(BNGPATH)
        self.BNGPATH = BNGPATH
        self.bngexec = bngexec 
        self.model_name = ""
        self.parse_model(bngl_model)

    def __str__(self):
        '''
        write the model to str
        '''
        model_str = "begin model\n"
        for block in self.block_order:
            if block in self.active_blocks:
                if block != "actions":
                    model_str += str(getattr(self, block))
        model_str += "\nend model\n"
        if "actions" in self.active_blocks:
            model_str += str(self.actions)
        return model_str

    def __repr__(self):
        return self.model_name

    def __iter__(self):
        active_ordered_blocks = [getattr(self,i) for i in self.block_order if i in self.active_blocks]
        return active_ordered_blocks.__iter__()

    def parse_model(self, model_file):
        # this route runs BNG2.pl on the bngl and parses
        # the XML instead
        if model_file.endswith(".bngl"):
            # TODO: Strip actions into a temp file
            # then run the gen xml 
            print("Attempting to generate XML")
            model_file = self.generate_xml(model_file)
            if model_file is not None:
                print("Parsing XML")
                self.parse_xml(model_file)
            else:
                print("XML file doesn't exist")
        elif model_file.endswith(".xml"):
            self.parse_xml(model_file)
        else:
            print("The extension of {} is not supported".format(model_file))
            raise NotImplemented

    def generate_xml(self, model_file):
        cur_dir = os.getcwd()
        # temporary folder to work in
        temp_folder = tempfile.mkdtemp()
        # make a stripped copy without actions in the folder
        stripped_bngl = self.strip_actions(model_file, temp_folder)
        # run with --xml 
        os.chdir(temp_folder)
        # TODO: Make output supression an option somewhere
        rc = subprocess.run(["perl",self.bngexec, "--xml", stripped_bngl])
        if rc.returncode == 1:
            print("XML generation failed")
            # go back to our original location
            os.chdir(cur_dir)
            return None
        else:
            # we should now have the XML file 
            path, model_name = os.path.split(stripped_bngl)
            model_name = model_name.replace(".bngl", "")
            xml_file = model_name + ".xml"
            # go back to our original location
            os.chdir(cur_dir)
            return os.path.join(path, xml_file)

    def strip_actions(self, model_path, folder):
        '''
        Strips actions from a BNGL folder and makes a copy
        into the given folder
        '''
        # Get model name and setup path stuff
        path, model_file = os.path.split(model_path)
        # open model and strip actions
        with open(model_path, 'r') as mf:
            # read and strip actions
            mlines = mf.readlines()
            stripped_lines = filter(lambda x: self._not_action(x), mlines)
        # open new file and write just the model
        stripped_model = os.path.join(folder, model_file)
        with open(stripped_model, 'w') as sf:
            sf.writelines(stripped_lines)
        return stripped_model 

    def _not_action(self, line):
        for action in self._action_list:
            if action in line:
                return False
        return True

    def parse_xml(self, model_file):
        with open(model_file, "r") as f:
            xml_str = "".join(f.readlines())
        xml_dict = xmltodict.parse(xml_str)
        self.xml_dict = xml_dict
        xml_model = xml_dict['sbml']['model']
        self.model_name = xml_model['@id']
        for listkey in xml_model.keys():
            if listkey == "ListOfParameters":
                param_list = xml_model[listkey]
                if param_list is not None:
                    params = param_list['Parameter']
                    self.parameters = Parameters()
                    self.parameters.parse_xml_block(params)
                    self.active_blocks.append("parameters")
            elif listkey == "ListOfObservables":
                obs_list = xml_model[listkey]
                if obs_list is not None:
                    obs = obs_list['Observable']
                    self.observables = Observables()
                    self.observables.parse_xml_block(obs)
                    self.active_blocks.append("observables")
            elif listkey == "ListOfCompartments":
                comp_list = xml_model[listkey]
                if comp_list is not None:
                    self.compartments = Compartments()
                    comps = comp_list['compartment']
                    self.compartments.parse_xml_block(comps)
                    self.active_blocks.append("compartments")
            elif listkey == "ListOfMoleculeTypes":
                mtypes_list = xml_model[listkey]
                if mtypes_list is not None:
                    mtypes = mtypes_list["MoleculeType"]
                    self.moltypes = MoleculeTypes()
                    self.moltypes.parse_xml_block(mtypes)
                    self.active_blocks.append("moltypes")
            elif listkey == "ListOfSpecies":
                species_list = xml_model[listkey]
                if species_list is not None:
                    species = species_list["Species"]
                    self.species = Species()
                    self.species.parse_xml_block(species)
                    self.active_blocks.append("species")
            elif listkey == "ListOfReactionRules":
                rrules_list = xml_model[listkey]
                if rrules_list is not None:
                    rrules = rrules_list["ReactionRule"]
                    self.rules = Rules()
                    self.rules.parse_xml_block(rrules)
                    self.active_blocks.append("rules")
            elif listkey == "ListOfFunctions":
                # TODO: Optional expression parsing?
                # TODO: Add arguments correctly
                func_list = xml_model[listkey]
                if func_list is not None:
                    self.functions = Functions()
                    funcs = func_list['Function']
                    self.functions.parse_xml_block(funcs)
                    self.active_blocks.append("functions")
        # And that's the end of parsing
        print("XML parsed")

    def add_action(self, action_type, action_args):
        # add actions block and to active list
        if not hasattr(self, "actions"):
            self.actions = Actions()
            self.active_blocks.append("actions")
        self.actions.add_action(action_type, action_args)

    def write_model(self, file_name):
        '''
        write the model to file 
        '''
        model_str = ""
        for block in self.active_blocks:
            model_str += str(getattr(self, block))
        with open(file_name, 'w') as f:
            f.write(model_str)

    def write_xml(self, file_name):
        '''
        write new XML to file by calling BNG2.pl again
        '''
        cur_dir = os.getcwd()
        # temporary folder to work in
        temp_folder = tempfile.mkdtemp()
        # write the current model to temp folder
        os.chdir(temp_folder)
        with open("temp.bngl", "w") as f:
            f.write(str(self))
        # run with --xml 
        # TODO: Make output supression an option somewhere
        rc = subprocess.run(["perl",self.bngexec, "--xml", "temp.bngl"])
        if rc.returncode == 1:
            print("XML generation failed")
            # go back to our original location
            os.chdir(cur_dir)
        else:
            # we should now have the XML file 
            fpath = os.path.join(cur_dir, file_name)
            shutil.copy("temp.xml", fpath)
            os.chdir(cur_dir)
###### CORE OBJECT AND PARSING FRONT-END ######

if __name__ == "__main__":
    # model = BNGModel("test.bngl")
    # import IPython
    # IPython.embed()
    # with open("test.bngl", 'w') as f:
    #     f.write(str(model))
    os.chdir("validation")
    bngl_list = os.listdir(os.getcwd())
    bngl_list = filter(lambda x: x.endswith(".bngl"), bngl_list)
    for bngl in bngl_list:
        m = BNGModel(bngl)
        with open('test.bngl', 'w') as f:
            f.write(str(m))
        rc = subprocess.run([m.bngexec, 'test.bngl'])
        if rc.returncode == 1:
            print("issues with the written bngl")
            sys.exit()
    # with open("test_res.txt", "w") as f:
    #     for bngl in bngl_list:
    #         print("Working on {}".format(bngl))
    #         try:
    #             m = BNGModel(bngl)
    #         except:
    #             f.write(("Failed at {}\n".format(bngl)))
    #             # IPython.embed()
