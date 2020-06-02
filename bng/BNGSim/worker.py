import tempfile, os, subprocess
from BNGSim.utils import find_BNG_path
from BNGSim.result import BNGResult

class BNGWorker:
    """
    Takes the parent (for getting the up-to-date model later) and an
    optional path parameter.
    
    If a path isn't given, the simulation will run in a temporary folder
    and the results will be saved in memory. 

    Currently only BNG2.pl simulations can be run but eventually a 
    RoadRunner simulator option will be implemented
    """
    def __init__(self, parent, path=None, bngexec=None):
        # we'll need our parent to get the model
        self.parent = parent
        # this allows us to setup a path
        self.path = path
        self.result = None
        # if we are not given the path to BNG2.pl 
        # try to find it
        if bngexec is None:
            self.BNGPATH, self.bngexec = find_BNG_path()
        else:
            self.bngexec = bngexec
    
    def _setup_working_path(self):
        if self.path is None:
            # work in temp folder
            temp_folder = tempfile.mkdtemp()
            os.chdir(temp_folder)
            return temp_folder
        else:
            if not os.path.isider(self.path):
                print("Given simulation path does not exist or invalid, trying to create")
                try:
                    os.mkdir(path)
                except OSError:
                    print("Failed to create given path")
                    os.exit(1)
            os.chdir(self.path)
            return self.path

    def _get_model(self):
        # this gets us the model object
        model = self.parent.get_model()
        # we are assuming we are in the right
        # folder for what we are doing
        model_name = model.model_name
        self.model_name = model_name
        model_file = model_name + ".bngl"
        with open(model_file, "w") as f:
            f.write(str(model))
        return model_file

    def run(self):
        # setup our path
        sim_path = self._setup_working_path()
        # get our model
        model_file = self._get_model()
        # run 
        rc = subprocess.run(["perl", self.bngexec, model_file])
        print(os.listdir(os.getcwd()))
        if rc.returncode == 0:
            print("Simulation succesful, loading results")
            self.result = BNGResult(bngl=model_file)
            return self.result
        else:
            print("Simulation failed")
            print(rc.stdout)
            print(rc.stderr)
            return None
