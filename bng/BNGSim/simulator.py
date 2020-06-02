import os, sys
sys.setrecursionlimit(2000)
from multiprocessing import Pool
import numpy as np

from BNGSim import BNGWorker
from BNGSim import BNGModel
from BNGSim.utils import find_BNG_path

def _call_into_simulator(simulator):
    res = simulator.run()
    return res

class BNGSimulator:
    """
    A simple front-end for running BNG simulations
    """
    def __init__(self, bngl, path=None, bngexec=None, nsims=1, ncores=1, outname='output.h5', combined=False):
        # find BNG2.pl and path 
        self.BNGPATH, self.bngexec = find_BNG_path(bngexec)
        # Let's load in the model first
        if isinstance(bngl, BNGModel): 
            self.model = bngl
        elif isinstance(bngl, str):
            self.model = BNGModel(bngl)
        # setup our path variable
        # none means we'll run under temp folders
        self.path = path
        # but we want to come back to save output 
        self.cur_dir = os.getcwd()
        # How many cores will we use?
        self.ncores = ncores
        # Initialize results
        self.results = []
        # other misc parameters
        self.nsims = nsims
        self.outname = outname
        self.combined = combined

    def _setup_workers(self):
        '''
        Setting up a list of simulator instances to run. Each instance knows it's own 
        path to run the simulations so the simulators are entirely independent.
        '''
        if self.path is None:
            workers = [BNGWorker(self, self.path) for i in range(self.nsims)]
        return workers 

    def get_model(self):
        return self.model

    def run_simulation(self, nsims=1):
        # let's get our workers ready
        self.workers = self._setup_workers()

        if self.ncores == 1:
            for worker in self.workers:
                result = worker.run()
                if result is not None:
                    result.set_name("simulation_{:08d}".format(len(self.results)))
                    self.results.append(result)
        elif self.ncores > nsims:
            print("running parallel with {} cores".format(self.ncores))
            p = Pool(nsims)
            para_res = p.map(_call_into_simulator, self.workers)
            for res in para_res:
                res.set_name("simulation_{:08d}".format(len(self.results)))
                self.results.append(res)
        else:
            print("running parallel with {} cores".format(self.ncores))
            p = Pool(self.ncores)
            para_res = p.map(_call_into_simulator, self.workers)
            for res in para_res:
                res.set_name("simulation_{:08d}".format(len(self.results)))
                self.results.append(res)
    
    def save_results(self, fname="results.h5", combined=False):
        """
        Saves results in an hdf5 file
        """
        dt = h5py.special_dtype(vlen=str)
        with h5py.File(fname, "w") as h:
            for result in self.results:
                grp = h.create_group(result.name)
                ## Look up how to save strings here
                #grp.create_dataset("bngl_file", data=result.bngl, dtype="S10")
                #if isinstance(result.bngl, dict):
                #    bngl_to_save = result.bngl[result.bngl.keys[0]]
                #    grp.attrs["bngl_file"] = bngl_to_save
                #else:
                #    grp.attrs["bngl_file"] = result.bngl

                #if isinstance(result.net, dict):
                #    net_to_save = result.bngl[result.bngl.keys[0]]
                #    grp.attrs["net_file"] = net_to_save
                #else:
                #    grp.attrs["net_file"] = result.net
                # Let's save cdat/gdats
                if hasattr(result, "gdat"):
                    if isinstance(result.gdat, dict):
                        gdat_grp = grp.create_group("gdat")
                        for key in result.gdat.keys():
                            gdat_grp.create_dataset(key, data=result.gdat[key], dtype=result.gdat[key].dtype)
                    else:
                        gdat_obj = grp.create_dataset("gdat", data=result.gdat, dtype=result.gdat.dtype)
                # now the same for cdat
                if hasattr(result, "cdat"):
                    if isinstance(result.cdat, dict):
                        cdat_grp = grp.create_group("cdat")
                        for key in result.cdat.keys():
                            cdat_grp.create_dataset(key, data=result.cdat[key], dtype=result.cdat[key].dtype)
                    else:
                        cdat_obj = grp.create_dataset("cdat", data=result.cdat, dtype=result.cdat.dtype)
            if combined:
                if self.combined_results is not None:
                    combined_obj = h.create_dataset("combined_results", data=self.combined_results,
                                                   dtype=self.combined_results.dtype)
    
    def combine_results(self):
        """
        Combines all results gdat arrays into a single array. Ensure that the dtype for all
        results is the same! (so the same set of observables but can be different lengths)
        
        TODO: How do we really want to tackle this? Only gdat? Include cdat? Try to combine
        everything? 
        """
        if len(self.results) == 0:
            print("combine_results is called without any results loaded in")
            return None
        
        # We'll use the same dtype and use the maximum length gdat array
        # if all the same, fine, if not the value will be set to NaN
        # The DTYPE has to be the same for all for this to work!
        nres = len(self.results)
        max_len = max([self.results[i].gdat.shape[0] for i in range(nres)])
        self.combined_results = np.empty((nres,max_len), dtype=self.results[0].gdat.dtype)
        self.combined_results[:] = np.nan
        for i, result in enumerate(self.results):
            self.combined_results[i] = result.gdat[:]
        print("Results combined in combined_results attribute")

    def simulate(self, start, end, nsteps, method="ode", nsims=1):
        if hasattr(self.model, "actions"):
            self.model.actions.clear_actions()
        self.model.add_action("generate_network", [("overwrite",1)])
        self.model.add_action("simulate", [("method",method), ("t_start",start), ("t_end",end), ("n_steps", nsteps)])
        self.nsims = nsims
        self.run()

    def run(self):
        '''
        Main way this class is intended to function
        '''
        # run simulations
        self.run_simulation(nsims=self.nsims)
        # Save results
        if self.path is None:
            os.chdir(self.cur_dir)
        # if self.combined:
        #     self.combine_results()
        #     self.save_results(self.outname, combined=True)
        # else:
        #     self.save_results(self.outname)
