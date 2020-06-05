import os, sys, subprocess, pickle
from multiprocessing import Pool
from shutil import copyfile

import numpy as np

class BNGResult:
    def __init__(self, bngl=None):
        self.name = "BNGResult"
        if bngl is not None:
            self.bngl = self.load_bngl(bngl)
        # find and set existing files, load if it's a dat file
        self._find_existing_files()
    
    def set_name(self, name):
        self.name = name
        
    def load_bngl(self, bngl):
        if os.path.isfile(bngl):
            f = open(bngl)
            l = f.readlines()
            f.close()
            return np.string_("".join(l))
        else:
            return np.string_("")
    
    def _find_existing_files(self, extensions=["gdat", "cdat", "net"]):
        '''
        Searches through the extensions we want and loads them in 
        
        If a loader is set in _load_file front end then the file will be loaded
        accordingly (currently only gdat/cdat is supported), if only the file path
        will be set as an attribute
        '''
        print("Searching for existing files")
        # Magical trick to pull a particular extension file from the current path
        for ext in extensions:
            print("Finding and loading .{} file".format(ext))
            dat_files = list(filter(lambda x: x.endswith("." + ext), os.listdir(os.getcwd())))
            if len(dat_files) == 0:
                print("Can't find any .{} files".format(ext))
            elif len(dat_files) == 1:
                setattr(self, ext, self._load_file(dat_files[0], ext=ext))
            else:
                print("There are multiple .{} files, loading all".format(ext))
                attr = {}
                for dat_file in dat_files:
                    attr[dat_file] = self._load_file(dat_file, ext=ext)
                setattr(self, ext, attr)
        print("Loaded results files")

    def _load_file(self, file_path, ext=""):
        '''
        File loader front end. 
        
        If you want to write a loader for a file format check the extensions here
        and pass to your loader
        '''
        if ext == "":
            # Let's try to divine the extension from the file path
            ext = file_path.split(".")[-1]
            
        if "dat" in ext:
            return self._load_into_struct_array(file_path)
        elif "net" in ext:
            return self.load_bngl(file_path)
        else: 
            return file_path          
                        
    def _load_into_struct_array(self, path, dformat="f8"):
        '''
        This function takes a path to a gdat/cdat file as a string and loads that 
        file into a numpy structured array, including the correct header info.
        TODO: Add link
    
        Optional argument allows you to set the data type for every column. See
        numpy dtype/data type strings for what's allowed. TODO: Add link
        '''
        # First step is to read the header, 
        # we gotta open the file and pull that line in
        f = open(path)
        header = f.readline()
        f.close()
        # Ensure the header info is actually there
        assert header.startswith("#"), "No header line that starts with #"
        # Now turn it into a list of names for our struct array
        header = header.replace("#","")
        headers = header.split()
        # For a magical reason this is how numpy.loadtxt wants it, 
        # in tuples passed as a dictionary with names/formats as keys
        names = tuple(headers)
        formats = tuple([dformat for i in range(len(headers))])
        # return the loadtxt result as a record array
        # which is similar to pandas data format without the helper functions
        return np.rec.array(np.loadtxt(path, dtype={'names': names, 'formats': formats}))
