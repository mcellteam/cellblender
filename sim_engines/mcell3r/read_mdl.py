from __future__ import print_function
from grammar_definition import *
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import small_structures as st
import pprint
from subprocess import call
from collections import defaultdict
import write_bngxmle
import os


def eprint(*args, **kwargs):
    '''
    stderr printing
    '''
    print(*args, file=sys.stderr, **kwargs)


def process_parameters(statements):
    pstr = StringIO()
    pstr.write('begin parameters\n')
    for parameter in statements:
        if parameter[1][0] != '"':
            temp_str = '\t{0} {1}\n'.format(parameter[0],parameter[1]).replace('/*', '#')
            temp_str.replace('//', '#')
        else:
            continue
        pstr.write(temp_str)
    pstr.write('end parameters\n')

    return pstr.getvalue()


def create_molecule_from_pattern(molecule_pattern, idx):
    tmp_molecule = st.Molecule(molecule_pattern['moleculeName'], idx)
    if 'moleculeCompartment' in molecule_pattern:
        tmp_molecule.compartment = molecule_pattern['moleculeCompartment'][1]
    if 'components' in molecule_pattern.keys():
        for idx2, component in enumerate(molecule_pattern['components']):
            tmp_component = st.Component(component['componentName'],'{0}_{1}'.format(idx,idx2))
            if 'state' in component:
                for state in component['state']:
                    if state != '':
                        tmp_component.addState(state)
            if 'bond' in component.keys():
                for bond in component['bond']:
                    tmp_component.addBond(bond)
            tmp_molecule.addComponent(tmp_component)
    return tmp_molecule


def create_species_from_pattern(speciesPattern):
    tmp_species = st.Species()
    if 'speciesCompartment' in speciesPattern.keys():
        tmp_species.compartment = speciesPattern['speciesCompartment'][1]
    for idx, element in enumerate(speciesPattern['speciesPattern']):
        tmp_species.addMolecule(create_molecule_from_pattern(element, idx))
    return tmp_species


def process_molecules(molecules):
    mstr = StringIO()
    molecule_list = []
    mstr.write('begin molecule types\n')
    for idx, molecule in enumerate(molecules):
        tmp_molecule = create_molecule_from_pattern(molecule[0], idx)
        molecule_list.append((tmp_molecule.name,str(tmp_molecule)))
        mstr.write('\t{0}\n'.format(tmp_molecule.str2()))
    mstr.write('end molecule types\n')
    return mstr.getvalue(), molecule_list


def process_init_compartments(initializations):
    sstr = StringIO()
    cstr = StringIO()
    sstr.write('begin seed species\n')
    cstr.write('begin compartments\n')

    for initialization in initializations:
        #print initialization.keys()
        if 'name' in initialization.keys():
            tmp_species = None
            initialConditions = 0
            for entry in initialization['entries']:
                if entry[0] == 'MOLECULE':
                    pattern = species_definition.parseString(entry[1])
                    tmp_species = create_species_from_pattern(pattern[0])
                elif entry[0] in ['NUMBER_TO_RELEASE', 'CONCENTRATION']:
                    initialConditions = entry[1]
            sstr.write('\t {0} {1}\n'.format(str(tmp_species),initialConditions))
        else:
            optionDict = {'parent': '', 'name': initialization['compartmentName']}
            for option in initialization['compartmentOptions'][0]:
                if len(option) > 0:
                    if option[0] == 'MEMBRANE':

                        tmp = option[1].strip()
                        optionDict['membrane'] = tmp.split(' ')[0]
                    elif option[0] == 'PARENT':
                        tmp = option[1].strip()
                        optionDict['parent'] = tmp
            if 'membrane' in optionDict:
                cstr.write('\t{0} 2 1 {1}\n'.format(optionDict['membrane'], optionDict['parent']))
                cstr.write('\t{0} 3 1 {1}\n'.format(optionDict['name'], optionDict['membrane']))
            else:
                tmp = '{0} 3 1 {1}'.format(optionDict['name'], optionDict['parent'])
                tmp = tmp.strip()
                cstr.write('\t{0}\n'.format(tmp))

    sstr.write('end seed species\n')
    cstr.write('end compartments\n')
    return sstr.getvalue(), cstr.getvalue()


def process_observables(observables):
    ostr = StringIO()
    ostr.write('begin observables\n')
    for observable in observables:
        if 'patterns' in observable.keys() and 'outputfile' in observable.keys():
            tmpObservable = '\tMolecules '
            tmpObservable += '{0} '.format(observable['outputfile'].split('/')[-1].split('.')[0])
            patternList = []
            for pattern in observable['patterns']:
                patternList.append(str(create_species_from_pattern(pattern['speciesPattern'])))
            tmpObservable +=  ', '.join(patternList)
            ostr.write(tmpObservable + '\n')
        elif 'obskey' in observable.keys():
            tmpObservable = '\t{0} '.format(observable['obskey'])
            tmpObservable += '{0} '.format(observable['obsname'])
            patternList = []
            for pattern in observable['obspatterns']:
                patternList.append(str(create_species_from_pattern(pattern)))
            tmpObservable +=  ', '.join(patternList)
            ostr.write(tmpObservable + '\n')

    ostr.write('end observables\n')
    return ostr.getvalue()


def process_mtobservables(moleculeTypes):
    '''
    creates a list of observables from just molecule types
    '''
    ostr = StringIO()
    raise Exception

    ostr.write('begin observables\n')
    for moleculeType in moleculeTypes:
        ostr.write('\t Species {0} {1}\n'.format(moleculeType[0], moleculeType[1]))
    ostr.write('end observables\n')


    return ostr.getvalue()


def process_reaction_rules(rules):
    rStr = StringIO()
    rStr.write('begin reaction rules\n')
    for rule in rules:
        tmp_rule = st.Rule()
        for pattern in rule['reactants']:
            tmp_rule.addReactant(create_species_from_pattern(pattern))
        for pattern in rule['products']:
            tmp_rule.addProduct(create_species_from_pattern(pattern))
        for rate in rule['rate']:
            tmp_rule.addRate(rate)
        rStr.write('\t{0}\n'.format(str(tmp_rule)))

    rStr.write('end reaction rules\n')
    return rStr.getvalue()


def process_diffussion_elements(parameters, extendedData):
    '''
    extract the list of properties associated to molecule types and compartment
    objects. right now this information will be encoded into the bng-exml spec.
    It also extracts some predetermined model properties.
    '''
    modelProperties = {}
    moleculeProperties = defaultdict(list)
    compartmentProperties = defaultdict(list)

    #for parameter in parameters:
    #    if parameter[0] in ['TEMPERATURE']:
    #        modelProperties[parameter[0]] = parameter[1]

    for parameter in extendedData['system']:
        modelProperties[parameter[0].strip()] = parameter[1].strip()

    for molecule in extendedData['molecules']:
        if 'moleculeParameters' in molecule[1]:
            for propertyValue in molecule[1]['moleculeParameters']:
                data = {'name':propertyValue[1].strip(), 'parameters': []}
                moleculeProperties[molecule[0][0]].append((propertyValue[0], data))
        if 'diffusionFunction' in molecule[1]:
            if 'function' in molecule[1]['diffusionFunction'].keys():
                parameters = molecule[1]['diffusionFunction'][1]['parameters']
                data = {'name': '"{0}"'.format(molecule[1]['diffusionFunction'][1]['functionName']),
                'parameters':[(x['key'], x['value']) for x in parameters]}
            else:
                data = {'name':molecule[1]['diffusionFunction'][1].strip(), 'parameters': []}
            #moleculeProperties[molecule[0][0]].append((molecule[1]['diffusionFunction'][0], data))
            if '3D' in molecule[1]['diffusionFunction'].keys():
                dimensionality = {'name':'3','parameters':[]}
            if '2D' in molecule[1]['diffusionFunction'].keys():
                dimensionality = {'name':'2','parameters':[]}

            moleculeProperties[molecule[0][0]].append(('diffusion_function', data))
            moleculeProperties[molecule[0][0]].append(('dimensionality', dimensionality))

    for seed in extendedData['initialization']:
        if 'compartmentName' in seed.keys():
            membrane = ''
            membrane_properties = []
            for element in seed['compartmentOptions'][0]:
                # skip stuff already covered by normal cbng
                if element[0] in ['PARENT']:
                    continue
                if element[0] == 'MEMBRANE':
                    membrane = element[1].strip().split(' ')[0]
                elif element[0].startswith('MEMBRANE'):
                    membrane_properties.append((element[0].split('_')[1], element[1].strip()))

                else:
                    compartmentProperties[seed['compartmentName']].append((element[0], element[1]))
            if membrane != '' and len(membrane_properties) > 0:
                compartmentProperties[membrane] = membrane_properties

    return {'modelProperties':modelProperties, 'moleculeProperties': moleculeProperties,
            'compartmentProperties': compartmentProperties}


def process_functions(rawFunctions):
    ofun = StringIO()
    ofun.write('begin functions\n')
    for function in rawFunctions:

        ofun.write('{0}() ={1}\n'.format(function['functionName'][0], function['functionBody'][0]))
    ofun.write('end functions\n')

    return ofun.getvalue()


def write_default_functions():
    defaultFunctions = StringIO()

    defaultFunctions.write('begin functions\n')
    defaultFunctions.write('\teinstein_stokes(p_kb, p_t, p_rs, p_mu)= p_kb*p_t/(6*3.141592*p_mu*p_rs)\n')
    defaultFunctions.write('\tsaffman_delbruck(p_kb, p_t, p_rc, p_mu, p_mu_ex, p_gamma, p_h) = p_kb*p_t*log((p_mu*p_h/(p_rc*p_mu_ex)-p_gamma))/(4*3.141592*p_mu*p_h)\n')
    defaultFunctions.write('end functions\n')

    return defaultFunctions.getvalue()


def construct_bng_from_mdlr(mdlrPath,nfsimFlag=False, separate_spatial=True):
    '''
    initializes a bngl file and an extended-bng-xml file with a MDLr file description
    '''
    with open(mdlrPath, 'r') as f:
        mdlr = f.read()

    statements = statementGrammar.parseString(mdlr)

    sections = grammar.parseString(mdlr)
    final_bngl_str = StringIO()
    final_bngl_str.write('begin model\n')
    parameterStr = process_parameters(statements)
    try:
        moleculeStr, molecule_list = process_molecules(sections['molecules'])
    except 'KeyError':
        eprint('There is an issue with the molecules section in the mdlr file')
    try:
        seedspecies, compartments = process_init_compartments(sections['initialization']['entries'])
    except KeyError:
        eprint('There is an issue with the initialization section in the mdlr file')
    if 'math_functions' in sections:
        functions = process_functions(sections['math_functions'])
    else:
        functions = ''

    if not nfsimFlag:
        observables = process_observables(sections['observables'])
    else:
        try:
            observables = process_observables(sections['observables'])
        except KeyError:
            eprint('There is an issue with the observables section in the mdlr file')
        #observables = process_mtobservables(molecule_list)
    reactions = process_reaction_rules(sections['reactions'])

    #functions = write_default_functions()

    final_bngl_str.write(parameterStr)
    final_bngl_str.write(moleculeStr)
    final_bngl_str.write(compartments)
    final_bngl_str.write(seedspecies)
    final_bngl_str.write(observables)
    final_bngl_str.write(functions)
    #final_bngl_str.write('begin observables\nend observables\n')
    final_bngl_str.write(reactions)
    final_bngl_str.write('end model\n')

    #add processing actions
    if not nfsimFlag:
        final_bngl_str.write('generate_network({overwrite=>1})\n')
        final_bngl_str.write('writeSBML()\n')

    '''
    eventually this stuff should be integrated into bionetgen proper
    '''
    if separate_spatial:

        extended_data = {}
        if 'systemConstants' in sections.keys():
            extended_data['system'] = sections['systemConstants']
        else:
            extended_data['system'] = []
        extended_data['molecules'] = sections['molecules']
        extended_data['initialization'] = sections['initialization']['entries']
        propertiesDict = process_diffussion_elements(statements, extended_data)
        bngxmle = write_bngxmle.write2bngxmle(propertiesDict, mdlrPath.split(os.sep)[-1])

    return {'bnglstr':final_bngl_str.getvalue(), 'bngxmlestr':bngxmle}


def bngl2json(bnglFile):
    call(['bngdev',bnglFile])
    sbmlName = '.'.join(bnglFile.split('.')[:-1]) + '_sbml.xml'
    print(sbmlName)
    call(['./sbml2json','-i', sbmlName])


def output_bngl(bngl_str, bnglPath):
    with open(bnglPath, 'w') as f:
        f.write(bngl_str)


if __name__ == "__main__":

    bngl_str = construct_bng_from_mdlr('example.mdlr')
    bnglPath = 'output.bngl'
    output_bngl(bngl_str, bnglPath)

    bngl2json(bnglFile)


