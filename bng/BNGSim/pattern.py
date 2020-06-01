# All classes that deal with patterns 
class Pattern:
    '''
    A list of molecules
    '''
    def __init__(self, pattern_xml):
        self._bonds = Bonds()
        self._compartment = None
        self._label = None
        self.molecules = []
        # sets self.molecules up 
        self._parse_xml(pattern_xml)

    @property
    def compartment(self):
        return self._compartment 

    @compartment.setter
    def compartment(self, value):
        # TODO: Build in logic to set the 
        # outer compartment
        # print("Warning: Logical checks are not complete")
        self._compartment = value
        # by default, once the outer compartment is set
        # we will set the compartment of each molecule
        # to that new compartment. 
        for molec in self.molecules:
            molec.compartment = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        # TODO: Build in logic to set 
        # the outer label
        # print("Warning: Logical checks are not complete")
        self._label = value

    def __str__(self):
        sstr = ""
        for imol, mol in enumerate(self.molecules):
            if imol == 0 and self.compartment is not None:
                sstr += "@{}:".format(self.compartment)
            if imol == 0 and self.label is not None:
                sstr += "%{}:".format(self.label)
            if imol > 0:
                sstr += "."
            sstr += str(mol)
        return sstr

    def __repr__(self):
        return str(self)

    def __getitem__(self, key):
        return self.molecules[key]

    def __iter__(self):
        return self.molecules.__iter__()

    # TODO: Implement __contains__

    def _parse_xml(self, xml):
        if '@compartment' in xml:
            self.compartment = xml['@compartment']
        if "@label" in xml:
            self.label = xml["@label"]
        if "ListOfBonds" in xml:
            self._bonds.set_xml(xml["ListOfBonds"]["Bond"])
        mols = xml['ListOfMolecules']['Molecule']
        if isinstance(mols, list):
            # list of molecules
            for imol, mol in enumerate(mols):
                mol_obj = self._process_mol(mol)
                self.molecules.append(mol_obj)
        else:
            # a single molecule
            mol_obj = self._process_mol(mols)
            self.molecules.append(mol_obj)

    def _process_mol(self, mol_xml):
        # we are going to store molecules, components
        # and compartments in a separate dictionary 
        # for use later
        mol_obj = Molecule()
        mol_obj.name = mol_xml['@name'] 
        if "@label" in mol_xml:
            mol_obj.label = mol_xml["@label"]
        if "ListOfComponents" in mol_xml:
            # Single molecule can't have bonds
            mol_obj.components = self._process_comp(mol_xml["ListOfComponents"]["Component"])
        if '@compartment' in mol_xml:
            mol_obj.compartment = mol_xml['@compartment']
        return mol_obj

    def _process_comp(self, comp_xml):
        # bonds = compartment id, bond id 
        # comp xml can be a list or a dict
        comp_list = []
        if isinstance(comp_xml, list):
            # we have multiple and this is a list
            for icomp, comp in enumerate(comp_xml):
                comp_obj = Component()
                comp_obj.name = comp['@name']
                if "@label" in comp:
                    comp_obj.label = comp['@label']
                if "@state" in comp:
                    comp_obj.state = comp['@state']
                if comp["@numberOfBonds"] != '0':
                    bond_id = self._bonds.get_bond_id(comp)
                    for bi in bond_id:
                        comp_obj.bonds.append(bi)
                comp_list.append(comp_obj)
        else:
            # single comp, this is a dict
            comp_obj = Component()
            comp_obj.name = comp_xml['@name']
            if "@label" in comp_xml:
                comp_obj.label = comp_xml['@label']
            if "@state" in comp_xml:
                comp_obj.state = comp_xml['@state']
            if comp_xml['@numberOfBonds'] != '0':
                bond_id = self._bonds.get_bond_id(comp_xml)
                for bi in bond_id:
                    comp_obj.bonds.append(bi)
            comp_list.append(comp_obj)
        return comp_list

class Molecule:
    def __init__(self):
        self._name = "0"
        self._components = []
        self._compartment = None
        self._label = None

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.components[key]

    def __iter__(self):
        return self.components.__iter__()

    # TODO: implement __setitem__,  __contains__

    def __str__(self):
        mol_str = self.name
        if self.label is not None:
            mol_str += "%{}".format(self.label)
        if len(self.components) > 0:
            mol_str += "("
            for icomp, comp in enumerate(self.components):
                if icomp > 0:
                    mol_str += ","
                mol_str += str(comp)
            mol_str += ")"
        if self.compartment is not None:
            mol_str += "@{}".format(self.compartment)
        return mol_str
    
    ### PROPERTIES ### 
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        # print("Warning: Logical checks are not complete")
        # TODO: Check for invalid characters
        self._name = value

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, value):
        # print("Warning: Logical checks are not complete")
        self._components = value

    def __repr__(self):
        return str(self)

    @property
    def compartment(self):
        return self._compartment

    @compartment.setter
    def compartment(self, value):
        # print("Warning: Logical checks are not complete")
        self._compartment = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        # print("Warning: Logical checks are not complete")
        self._label = value

    def _add_component(self, name, state=None, states=[]):
        comp_obj = Component()
        comp_obj.name = name
        comp_obj.state = state
        comp_obj.states = states
        self.components.append(comp_obj)

    def add_component(self, name, state=None, states=[]):
        # TODO: Add built-in logic here
        # print("Warning: Logical checks are not complete")
        self._add_component(name, state, states)

class Component:
    def __init__(self):
        self._name = ""
        self._label = None
        self._state = None
        self._states = []
        self._bonds = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        comp_str = self.name
        # only for moltypes
        if len(self.states) > 0:
            for istate, state in enumerate(self.states):
                comp_str += "~{}".format(state)
        # for any other pattern
        if self.state is not None:
            comp_str += "~{}".format(self.state)
        if self.label is not None:
            comp_str += "%{}".format(self.label)
        if len(self.bonds) > 0:
            for bond in self.bonds:
                comp_str += "!{}".format(bond)
        return comp_str

    ### PROPERTIES ### 
    @property
    def name(self):
        return self._name
   
    @name.setter
    def name(self, value):
        # TODO: Add built-in logic here
        # print("Warning: Logical checks are not complete")
        self._name = value

    @property
    def label(self):
        return self._label
   
    @label.setter
    def label(self, value):
        # TODO: Add built-in logic here
        # print("Warning: Logical checks are not complete")
        self._label = value

    @property
    def state(self):
        return self._state
   
    @state.setter
    def state(self, value):
        # TODO: Add built-in logic here
        # print("Warning: Logical checks are not complete")
        self._state = value

    @property
    def states(self):
        return self._states
   
    @states.setter
    def states(self, value):
        # TODO: Add built-in logic here
        # print("Warning: Logical checks are not complete")
        self._states = value

    @property
    def bonds(self):
        return self._bonds
   
    @bonds.setter
    def bonds(self, value):
        # TODO: Add built-in logic here
        # print("Warning: Logical checks are not complete")
        self._bonds = value

    def _add_state(self):
        raise NotImplemented

    def add_state(self):
        self._add_state()

    def _add_bond(self):
        raise NotImplemented

    def add_bond(self):
        self._add_bond()

###### BONDS #####
class Bonds:
    def __init__(self, bonds_xml=None):
        self.bonds_dict = {}
        if bonds_xml is not None:
            self.resolve_xml(bonds_xml)

    def set_xml(self, bonds_xml):
        self.resolve_xml(bonds_xml)

    def get_bond_id(self, comp):
        # Get the ID of the bond from an XML id something 
        # belongs to, e.g. O1_P1_M1_C2 
        num_bonds = comp["@numberOfBonds"]
        comp_id = comp["@id"]
        try: 
            num_bond = int(num_bonds)
        except: 
            # This means we have something like +/?
            return num_bonds
        # use the comp_id to find the bond index from 
        # self.bonds_dict 
        comp_key = self.get_tpl_from_id(comp_id)
        bond_id = self.bonds_dict[comp_key]
        return bond_id
        
    def get_tpl_from_id(self, id_str):
        # ID str is looking like O1_P1_M2_C3
        # we are going to assume a 4-tuple per key
        id_list = id_str.split("_")
        id_tpl = tuple(id_list)
        return id_tpl

    def tpls_from_bond(self, bond):
        s1 = bond["@site1"] 
        s2 = bond["@site2"]
        id_list_1 = s1.split("_")
        s1_tpl = tuple(id_list_1)
        id_list_2 = s2.split("_")
        s2_tpl = tuple(id_list_2)
        return (s1_tpl, s2_tpl) 

    def resolve_xml(self, bonds_xml):
        # self.bonds_dict is a dictionary you can key
        # with the tuple taken from the ID and then 
        # get a bond ID cleanly
        if isinstance(bonds_xml, list):
            for ibond, bond in enumerate(bonds_xml): 
                bond_partner_1, bond_partner_2 = self.tpls_from_bond(bond)
                if bond_partner_1 not in self.bonds_dict:
                    self.bonds_dict[bond_partner_1] = [ibond+1]
                else:
                    self.bonds_dict[bond_partner_1].append([ibond+1])
                if bond_partner_2 not in self.bonds_dict:
                    self.bonds_dict[bond_partner_2] = [ibond+1]
                else:
                    self.bonds_dict[bond_partner_2].append(ibond+1)
        else:
            bond_partner_1, bond_partner_2 = self.tpls_from_bond(bonds_xml)
            self.bonds_dict[bond_partner_1] = [1]
            self.bonds_dict[bond_partner_2] = [1]
###### BONDS #####
