from ctypes import *


class NFSim:
    def __init__(self, libPath):
        self.lib = cdll.LoadLibrary(libPath)
        self.lib.setupNFSim_c.argtypes = [c_char_p, c_int]
        self.lib.initSystemXML_c.argtypes = [c_char_p]
        self.lib.querySystemStatus_c.argtypes = [c_char_p, c_void_p]
        self.lib.mapvector_create.restype = c_void_p
        self.lib.map_get.restype = c_char_p
        self.lib.mapvector_size.argtypes = [c_void_p]
        self.lib.mapvector_get.argtypes = [c_void_p, c_int]
        self.lib.mapvector_get.restype = c_void_p
        self.lib.map_get.argtypes = [c_void_p, c_char_p]
        self.lib.map_get.restype = c_char_p
        self.lib.mapvector_delete.argtypes = [c_void_p]


    def init_nfsim(self, fileName, verbose):
        """
        inits an nfsim object with a given xml file and a verbosity setting
        """
        c_fileName = c_char_p(bytes(fileName,'ASCII'))
        self.lib.setupNFSim_c(c_fileName, verbose)


    def reset_system(self):
        """
        Resets an nfsim system to having no seeds species
        """
        return self.lib.resetSystem_c()


    def init_system_nauty(self, initDict):
        """
        Initializes an nfsim simulation with a given nfsim dictionary with the species in nauty format
        """
        species = [x for x in initDict]
        seeds = [initDict[x] for x in initDict]

        CArray = c_char_p * len(initDict)
        speciesCArray = CArray(*species)
        seedCArray = CArray(*seeds)
        return self.lib.initSystemNauty_c(speciesCArray, seedCArray, len(initDict))


    def init_system_xml(self, initXML):
        """
        Initializes an nfsim simulation with a given seed species XML string
        """
        c_initXML = c_char_p(bytes(initXML,'ASCII'))
        return self.lib.initSystemXML_c(c_initXML)


    def querySystemStatus(self, option):
        """
        returns all species that participate in active reactions with numReactants reactants
        """

        mem = self.lib.mapvector_create()

        key = c_char_p(bytes(option,'ASCII'))
        self.lib.querySystemStatus_c(key,mem)
        results = []
        n = self.lib.mapvector_size(mem)
        for idx in range(0, n):
            #XXX:ideally i would like to returns all key values but that will require a lil more work on the wrapper side
            partialResults = self.lib.mapvector_get(mem, idx)
            retval = self.lib.map_get(partialResults,b"label")
            results.append(retval.decode('ASCII'))
        self.lib.mapvector_delete(mem)
        return sorted(results, key=len)



if __name__ == "__main__":
    nfsim = NFSim('./debug/libnfsim_c.so')

    nfsim.init_nfsim("cbngl_test_empty.xml", 0)
    nfsim.reset_system()
    #nfsim.init_system_nauty({"c:a~NO_STATE!4!2,c:l~NO_STATE!3,c:l~NO_STATE!3!0,m:Lig!2!1,m:Rec!0":1})
    #nfsim.init_system_nauty({"c:a~NO_STATE!4!2,c:l~NO_STATE!3,c:l~NO_STATE!3!0,m:Lig!1!2,m:Rec!0,":1})
    #print '---', nfsim.querySystemStatus("observables")
    nfsim.init_system_nauty({"c:l~NO_STATE!3!1,c:r~NO_STATE!2!0,m:L@EC!1,m:R@PM!0,":1})
    print('----', nfsim.querySystemStatus(b"complex"))


    """
    nfsim.initSystemXML('''<Model><ListOfSpecies><Species id="S1"  concentration="1" name="@PM::Lig(l!1,l).Rec(a!1)" compartment="PM">
        <ListOfMolecules>
          <Molecule id="S1_M1" name="Lig" compartment="PM">
            <ListOfComponents>
              <Component id="S1_M1_C1" name="l" numberOfBonds="0"/>
              <Component id="S1_M1_C2" name="l" numberOfBonds="1"/>
            </ListOfComponents>
          </Molecule>
          <Molecule id="S1_M2" name="Rec" compartment="PM">
            <ListOfComponents>
              <Component id="S1_M2_C1" name="a" numberOfBonds="1"/>
            </ListOfComponents>
          </Molecule>
        </ListOfMolecules>
        <ListOfBonds>
          <Bond id="S1_B1" site1="S1_M1_C1" site2="S1_M2_C1"/>
        </ListOfBonds>
      </Species></ListOfSpecies></Model>''')
    """
