# All classes that deal with patterns 
class Pattern:
    '''
    A list of molecules
    '''
    def __init__(self, pattern_xml):
        self._bonds = Bonds()
        self.molecules = []
        # sets self.molecules up 
        self.parse_xml(pattern_xml)

    def __str__(self):
        sstr = ""
        for imol, mol in enumerate(self.molecules):
            if imol == 0 and self.outer_comp is not None:
                sstr += "@{}:".format(self.outer_comp)
            if imol == 0 and self.outer_label is not None:
                sstr += "%{}:".format(self.outer_label)
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

    def parse_xml(self, xml):
        if '@compartment' in xml:
            self.outer_comp = xml['@compartment']
        else:
            self.outer_comp = None
        if "@label" in xml:
            self.outer_label = xml["@label"]
        else: 
            self.outer_label = None
        if "ListOfBonds" in xml:
            self._bonds.set_xml(xml["ListOfBonds"]["Bond"])
        mols = xml['ListOfMolecules']['Molecule']
        if isinstance(mols, list):
            # list of molecules
            for imol, mol in enumerate(mols):
                mol_obj = self.process_mol(mol)
                self.molecules.append(self.process_mol(mol))
        else:
            # a single molecule
            mol_obj = self.process_mol(mols)
            self.molecules.append(mol_obj)

    def process_mol(self, mol_xml):
        # we are going to store molecules, components
        # and compartments in a separate dictionary 
        # for use later
        name = mol_xml['@name'] 
        if "@label" in mol_xml:
            label = mol_xml["@label"]
        else:
            label = None
        # molecule dictionary
        mol_dict = {"name": name, "components": [], "compartment": None, "label": label} 
        if "ListOfComponents" in mol_xml:
            # Single molecule can't have bonds
            mol_dict['components'] = self.process_comp(mol_xml["ListOfComponents"]["Component"])
        if '@compartment' in mol_xml:
            mol_dict['compartment'] = mol_xml['@compartment']
        mol_obj = Molecule(mol_dict)
        return mol_obj

    def process_comp(self, comp_xml):
        # bonds = compartment id, bond id 
        # comp xml can be a list or a dict
        comp_list = []
        if isinstance(comp_xml, list):
            # we have multiple and this is a list
            for icomp, comp in enumerate(comp_xml):
                comp_dict = {}
                comp_dict['name'] = comp['@name']
                if "@label" in comp:
                    comp_dict['label'] = comp['@label']
                if "@state" in comp:
                    comp_dict['state'] = comp['@state']
                if comp["@numberOfBonds"] != '0':
                    comp_dict['bonds'] = []
                    bond_id = self._bonds.get_bond_id(comp)
                    for bi in bond_id:
                        comp_dict['bonds'].append(bi)
                comp_list.append(comp_dict)
        else:
            # single comp, this is a dict
            comp_dict = {}
            comp_dict['name'] = comp_xml['@name']
            if "@label" in comp_xml:
                comp_dict['label'] = comp_xml['@label']
            if "@state" in comp_xml:
                comp_dict['state'] = comp_xml['@state']
            if comp_xml['@numberOfBonds'] != '0':
                comp_dict['bonds'] = []
                bond_id = self._bonds.get_bond_id(comp_xml)
                for bi in bond_id:
                    comp_dict['bonds'].append(bi)
            comp_list.append(comp_dict)
        return comp_list

class Molecule:
    def __init__(self,  mol_dict=None):
        if mol_dict is not None:
            self.mol_dict = mol_dict
            self.__dict__.update(mol_dict)
        else:
            self.mol_dict = {"name": "0", 
                    "components": [], 
                    "compartment": None,
                    "label": None} 

    def __repr__(self):
        return str(self)

    def __str__(self):
        mol = self.mol_dict
        mol_str = mol["name"]
        if mol["label"] is not None:
            mol_str += "%{}".format(mol["label"])
        if len(mol["components"]) > 0:
            mol_str += "("
            for icomp, comp in enumerate(mol["components"]):
                if icomp > 0:
                    mol_str += ","
                comp_str = comp["name"]
                # only for moltypes
                if "states" in comp:
                    for istate, state in enumerate(comp["states"]):
                        comp_str += "~{}".format(state)
                # for any other pattern
                if "state" in comp:
                    comp_str += "~{}".format(comp["state"])
                if "label" in comp:
                    comp_str += "%{}".format(comp["label"])
                if "bonds" in comp:
                    for bond in comp["bonds"]:
                        comp_str += "!{}".format(bond)
                mol_str += comp_str 
            mol_str += ")"
        if mol["compartment"] is not None:
            mol_str += "@{}".format(mol["compartment"])
        return mol_str

    def add_component(self, name, state=None, states=None):
        comp_dict = {"name": name}
        if state is not None:
            comp_dict["state"] = state
        if states is not None:
            comp_dict["states"] = states
        self.mol_dict['components'].append(comp_dict)

    def set_compartment(self, compt):
        self.mol_dict['compartment'] = compt
    
    def set_label(self, label):
        self.mol_dict['label'] = label

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
