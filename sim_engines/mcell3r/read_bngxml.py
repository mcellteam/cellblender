# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 14:28:16 2012

@author: proto
"""
from lxml import etree
import small_structures as st
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
# http://igraph.sourceforge.net/documentation.html
# ----------------------------------------------------------------------


def findBond(bondDefinitions, component):
    '''
    Returns an appropiate bond number when veryfying how
    to molecules connect in a species
    '''
    for idx, bond in enumerate(bondDefinitions.getchildren()):
        if component in [bond.get('site1'), bond.get('site2')]:
            return str(idx+1)


def createMolecule(molecule, bonds):
    nameDict = {}
    mol = st.Molecule(molecule.get('name'), molecule.get('id'))
    if molecule.get('compartment') not in ['', None]:
        mol.setCompartment(molecule.get('compartment'))
    nameDict[molecule.get('id')] = molecule.get('name')
    listOfComponents = molecule.find('.//{http://www.sbml.org/sbml/level3}ListOfComponents')
    if listOfComponents is not None:
        for element in listOfComponents:
            component = st.Component(element.get('name'), element.get('id'))
            nameDict[element.get('id')] = element.get('name')
            if element.get('numberOfBonds') in ['+', '?']:
                component.addBond(element.get('numberOfBonds'))
            elif element.get('numberOfBonds') != '0':
                component.addBond(findBond(bonds, element.get('id')))
            state = element.get('state') if element.get('state') != None else ''
            component.states.append(state)
            component.activeState = state
            mol.addComponent(component)
    return mol, nameDict


def createSpecies(pattern):
    tmpDict = {}
    species = st.Species()
    species.idx = pattern.get('id')
    species.trueName = pattern.get('name')
    compartment = pattern.get('compartment')
    if compartment != None:
        species.compartment = compartment
    mol = pattern.find('.//{http://www.sbml.org/sbml/level3}ListOfMolecules')
    bonds = pattern.find('.//{http://www.sbml.org/sbml/level3}ListOfBonds')
    for molecule in mol.getchildren():
        molecule, nameDict = createMolecule(molecule, bonds)
        tmpDict.update(nameDict)
        species.addMolecule(molecule)
        if bonds != None:
            species.bonds = [(bond.get('site1'), bond.get('site2')) for bond in bonds]
        tmpDict.update(nameDict)
    return species, tmpDict


def parseRule(rule, parameterDict):
    '''
    Parses a rule XML section
    Returns: a list of the reactants and products used, followed by the mapping
    between the two and the list of operations that were performed
    '''
    rp = rule.find('.//{http://www.sbml.org/sbml/level3}ListOfReactantPatterns')
    pp = rule.find('.//{http://www.sbml.org/sbml/level3}ListOfProductPatterns')
    mp = rule.find('.//{http://www.sbml.org/sbml/level3}Map')
    op = rule.find('.//{http://www.sbml.org/sbml/level3}ListOfOperations')
    rt = rule.find('.//{http://www.sbml.org/sbml/level3}RateLaw')
    nameDict = {}
    reactants = []
    products = []
    actions = []
    mappings = []

    if len(rp) == 0:
        sp = st.Species()
        ml = st.Molecule('0', '')
        sp.addMolecule(ml)
        reactants.append(sp)
    if len(pp) == 0:
        sp = st.Species()
        ml = st.Molecule('0', '')
        sp.addMolecule(ml)
        products.append(sp)
    for pattern in rp:
        elm, tmpDict = createSpecies(pattern)
        reactants.append(elm)
        nameDict.update(tmpDict)
    for pattern in pp:
        elm, tmpDict = createSpecies(pattern)
        products.append(elm)
        nameDict.update(tmpDict)
    for operation in op:
        action = st.Action()
        tag = operation.tag
        tag = tag.replace('{http://www.sbml.org/sbml/level3}', '')
        if operation.get('site1') != None:
            action.setAction(tag, operation.get('site1'), operation.get('site2'))
        else:
            action.setAction(tag, operation.get('site'), None)
        actions.append(action)
    for mapping in mp:
        tmpMap = (mapping.get('sourceID'), mapping.get('targetID'))
        mappings.append(tmpMap)
    rateConstants = rt.find('.//{http://www.sbml.org/sbml/level3}ListOfRateConstants')
    if rateConstants == None:
        rateConstants = rt.get('name')
    else:
        for constant in rateConstants:
            tmp = constant.get('value')
        rateConstants = tmp
    rateConstantsValue = parameterDict[rateConstants] if rateConstants in parameterDict else rateConstants
    #rule = st.Rule()
    label = rule.get('name')
    label = label.replace('(', '_').replace(')', '_')
    rule = st.Rule(label)
    rule.addReactantList(reactants)
    rule.addProductList(products)
    rule.addActionList(actions)
    rule.addMappingList(mappings)
    rule.addRate(rateConstants)

    # return reactants, products, actions, mappings, nameDict,rateConstantsValue,rateConstants
    return rule, nameDict, rateConstantsValue, rateConstants


def parseMolecules(molecules):
    '''
    Parses an XML molecule section
    Returns: a molecule structure
    '''

    mol = st.Molecule(molecules.get('id'), molecules.get('id'))
    components = \
        molecules.find('.//{http://www.sbml.org/sbml/level3}ListOfComponentTypes')
    if components != None:
        for component in components.getchildren():
            comp = parseComponent(component)
            mol.addComponent(comp)
    return mol


def parseComponent(component):
    '''
    parses  a bngxml molecule types section
    '''
    comp = st.Component(component.get('id'), component.get('id'))
    states = component.find('.//{http://www.sbml.org/sbml/level3}ListOfAllowedStates')
    if states != None:
        for state in states.getchildren():
            comp.addState(state.get('id'))
    return comp


def parseObservable(observable):
    nameDict = {}
    name = observable.get('name')
    otype = observable.get('type')
    rp = observable.find('.//{http://www.sbml.org/sbml/level3}ListOfPatterns')

    patternList = []
    for pattern in rp:
        elm, tmpDict = createSpecies(pattern)
        patternList.append(elm)

    return name, otype, patternList


def parseObservables(observables):
    observableDescription = []

    for observable in observables:
        observableDescription.append(parseObservable(observable))
    return observableDescription


def parseFunction(function):
    referenceList = []
    name = function.get('id')
    #expression = function.find('.//{http://www.sbml.org/sbml/level3}Expression')
    expression = function.findtext('.//{http://www.sbml.org/sbml/level3}Expression')

    references = function.find('.//{http://www.sbml.org/sbml/level3}ListOfReferences')
    for reference in references:
        referenceList.append([reference.get('name'), reference.get('type')])

    return name, expression, referenceList


def parseFunctions(functions):

    functionDescription = []

    for function in functions:
        functionDescription.append(parseFunction(function))
    return functionDescription


def parseFullXML(xmlFile):
    doc = etree.parse(xmlFile)
    molecules = doc.findall('.//{http://www.sbml.org/sbml/level3}MoleculeType')
    seedspecies = doc.findall('.//{http://www.sbml.org/sbml/level3}Species')
    rules = doc.findall('.//{http://www.sbml.org/sbml/level3}ReactionRule')
    functions = doc.findall('.//{http://www.sbml.org/sbml/level3}Function')

    structureDefinitions = {}
    ruleDescription = []
    moleculeList = []
    seedSpeciesList = []
    compartmentList = []
    observables = doc.findall('.//{http://www.sbml.org/sbml/level3}Observable')
    parameters = doc.findall('.//{http://www.sbml.org/sbml/level3}Parameter')
    compartments = doc.findall('.//{http://www.sbml.org/sbml/level3}compartment')

    parameterDict = {}
    for parameter in parameters:
        parameterDict[parameter.get('id')] = parameter.get('value')

    structureDefinitions['parameters'] = parameterDict

    for compartment in compartments:
        compartmentDict = {}
        compartmentDict['identifier'] = compartment.get('id')
        compartmentDict['dimensions'] = compartment.get('spatialDimensions')
        compartmentDict['size'] = compartment.get('size')
        compartmentDict['outside'] = compartment.get('outside')
        compartmentList.append(compartmentDict)

    structureDefinitions['compartments'] = compartmentList

    for molecule in molecules:
        moleculeList.append(parseMolecules(molecule))

    structureDefinitions['molecules'] = moleculeList

    for species in seedspecies:
        concentration = species.get('concentration')
        compartment = species.get('compartment')
        seedSpeciesList.append({'concentration': concentration, 'structure': createSpecies(species)[0],
                                'compartment': compartment})

    structureDefinitions['seedspecies'] = seedSpeciesList

    for rule in rules:
        # description = parseRule(rule, parameterDict)
        # if 'reverse' in description[0].label:
        #    ruleDescription[-1][0].bidirectional= True
        #    ruleDescription[-1][0].rates.append(description[0].rates[0])
        # else:
        ruleDescription.append(parseRule(rule, parameterDict))

    structureDefinitions['rules'] = ruleDescription
    structureDefinitions['functions'] = parseFunctions(functions)
    structureDefinitions['observables'] = parseObservables(observables)

    return structureDefinitions


def parseXMLStruct(doc):
    molecules = doc.findall('.//{http://www.sbml.org/sbml/level3}MoleculeType')
    rules = doc.findall('.//{http://www.sbml.org/sbml/level3}ReactionRule')
    ruleDescription = []
    moleculeList = []

    parameters = doc.findall('.//{http://www.sbml.org/sbml/level3}Parameter')
    parameterDict = {}
    for parameter in parameters:
        parameterDict[parameter.get('id')] = parameter.get('value')

    for molecule in molecules:
        moleculeList.append(parseMolecules(molecule))

    for rule in rules:
        description = parseRule(rule, parameterDict)
        # if 'reverse' in description[0].label:
        #    ruleDescription[-1][0].bidirectional= True
        #    ruleDescription[-1][0].rates.append(description[0].rates[0])
        # else:
        ruleDescription.append(parseRule(rule, parameterDict))
    return moleculeList, ruleDescription, parameterDict


def parseXMLFromString(xmlString):
    doc = etree.fromstring(xmlString)
    return parseXMLStruct(doc)



def parseXML(xmlFile):
    doc = etree.parse(xmlFile)
    return parseXMLStruct(doc)

def getNumObservablesXML(xmlFile):
    doc = etree.parse(xmlFile)
    observables = doc.findall('.//{http://www.sbml.org/sbml/level3}Observable')
    return len(observables)


def createBNGLFromDescription(namespace):
    """creates a bngl file from a dictionary description containing molecules, species, etc."""

    bnglString = StringIO()

    bnglString.write('begin model\n')
    # parameters
    bnglString.write('begin parameters\n')
    for parameterName in namespace['parameters']:
        bnglString.write('\t{0} {1}\n'.format(parameterName, namespace['parameters'][parameterName]))
    bnglString.write('end parameters\n')

    # molecule types
    bnglString.write('begin molecule types\n')
    for molecule in namespace['molecules']:
        bnglString.write('\t' + molecule.str2() + '\n')
    bnglString.write('end molecule types\n')

    # compartments
    bnglString.write('begin compartments\n')
    for compartment in namespace['compartments']:
        bnglString.write('\t{0} {1} {2}'.format(compartment['identifier'], compartment['dimensions'], compartment['size']))
        if compartment['outside']:
            bnglString.write('\t {0}\n'.format(compartment['outside']))
        else:
            bnglString.write('\n')
    bnglString.write('end compartments\n')

    # seed species
    bnglString.write('begin seed species\n')
    for seedspecies in namespace['seedspecies']:
        if seedspecies['concentration'] not in [0, '0','0.0']:
            bnglString.write('\t{0} {1}\n'.format(seedspecies['structure'], seedspecies['concentration']))
    bnglString.write('end seed species\n')

    # observables
    bnglString.write('begin observables\n')
    for observables in namespace['observables']:
        bnglString.write('\t{0} {1} {2}\n'.format(observables[1], observables[0], ', '.join([str(x) for x in observables[2]])))
    bnglString.write('end observables\n')

    # functions
    bnglString.write('begin functions\n')
    for functions in namespace['functions']:
        bnglString.write('\t{0}() = {1}\n'.format(functions[0], functions[1]))
    bnglString.write('end functions\n')

    # rules
    bnglString.write('begin reaction rules\n')
    for rule in namespace['rules']:
        bnglString.write('\t{0}\n'.format(rule[0]))
    bnglString.write('end reaction rules\n')

    bnglString.write('end model\n')

    return bnglString.getvalue()

if __name__ == "__main__":
    #mol,rule,par = parseXML("output19.xml")
    # print [str(x) for x in mol]
    with open('output19.xml','r') as f:
        s = f.read()
    print(parseXMLFromString(s))
    #print getNumObservablesXML('output19.xml')

