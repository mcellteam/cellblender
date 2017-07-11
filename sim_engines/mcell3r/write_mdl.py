import json
import grammar_definition as gd
import argparse
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def read_bngljson(bngljson):
    with open(bngljson, 'r') as f:
        jsonDict = json.load(f)
    return jsonDict


def write_raw_section(original_mdl, buffer, tab):
    if type(original_mdl) == str:
        buffer.write(tab + original_mdl + '\n')

    elif len(original_mdl) == 0:
        return '{}'
    elif len(original_mdl) == 1:
        write_raw_section(original_mdl[0], buffer, tab)
    elif len(original_mdl) == 2:
        if type(original_mdl[0]) == list:
            for element in original_mdl:
                write_raw_section(element, buffer, tab + '\t')
        elif type(original_mdl[1]) == list:

            buffer.write('{1}{0}{{\n'.format(original_mdl[0], tab))
            write_raw_section(original_mdl[1], buffer, tab + '\t')
            buffer.write('{0}}}\n\n'.format(tab))
        elif type(original_mdl[1]) == str:
            buffer.write(
                '{0}{1} = {2}\n'.format(
                    tab, original_mdl[0], original_mdl[1].strip()))
    else:
        if original_mdl[1] == '@':
            buffer.write(tab + ' '.join(original_mdl) + '\n')
        else:
            for element in original_mdl:
                write_raw_section(element, buffer, tab)
    return buffer.getvalue()


def write_section(original_mdl):
    finalSection = StringIO()
    if original_mdl[0] == 'DEFINE_MOLECULES':
        pass

    else:
        return write_raw_section(original_mdl.asList(), finalSection, '') + '\n'


def read_mdlr(mdlrfile):
    with open(mdlrfile, 'r') as f:
        mdlr = f.read()
    return mdlr


def construct_mcell(xmlStructs, mdlrPath, outputFileName, nautyDict):
    '''
    uses information from the bngxml and the original mdl to create a plain mdl
    file. this is mainly important to assign the right surface/volume
    compartment to the seed species.
    '''
    # load up data structures
    mdlr = read_mdlr(mdlrPath)
    section_mdlr = gd.nonhashedgrammar.parseString(mdlr)
    statement_mdlr = gd.statementGrammar.parseString(mdlr)
    hashed_mdlr = gd.grammar.parseString(mdlr)

    # create output buffers
    final_mdl = StringIO()
    molecule_mdl = StringIO()
    reaction_mdl = StringIO()
    output_mdl = StringIO()
    seed_mdl = StringIO()
    mod_surf_reg__mdl = StringIO()
    surface_classes__mdl = StringIO()

    # output statements as is
    for element in statement_mdlr:
        final_mdl.write('{0} = {1}\n'.format(element[0], element[1]))

    final_mdl.write('\n')
    final_mdl.write('INCLUDE_FILE = "{0}.molecules.mdl"\n'.format(outputFileName))
    final_mdl.write('INCLUDE_FILE = "{0}.reactions.mdl"\n'.format(outputFileName))
    final_mdl.write('INCLUDE_FILE = "{0}.seed.mdl"\n\n'.format(outputFileName))
    final_mdl.write('INCLUDE_FILE = "{0}.surface_classes.mdl"\n\n'.format(outputFileName))
    final_mdl.write('INCLUDE_FILE = "{0}.mod_surf_reg.mdl"\n\n'.format(outputFileName))

    # output sections using json information
    sectionOrder = {'DEFINE_SURFACE_CLASSES': surface_classes__mdl,
                    'MODIFY_SURFACE_REGIONS': mod_surf_reg__mdl,
                    'DEFINE_MOLECULES': molecule_mdl,
                    'DEFINE_REACTIONS': reaction_mdl,
                    'REACTION_DATA_OUTPUT': output_mdl,
                    'INSTANTIATE': seed_mdl}
    for element in section_mdlr:
        if element[0] not in sectionOrder:
            final_mdl.write(write_section(element))

    dimensionalityDict = {}
    bngLabel = {}
    # molecules
    molecule_mdl.write('DEFINE_MOLECULES\n{\n')
    if 'DEFINE_MOLECULES' in section_mdlr.keys():
        for element in section_mdlr['DEFINE_MOLECULES']:
            write_raw_section(element, molecule_mdl, '\t')

    dimensionalityDict['volume_proxy'] = '3D'
    molecule_mdl.write('\t{0} //{1}\n\t{{ \n'.format('volume_proxy', 'proxy molecule type. the instance contains the actual information'))
    molecule_mdl.write('\t\tDIFFUSION_CONSTANT_{0}D = {1}\n'.format(3, 1))
    molecule_mdl.write('\t\tEXTERN\n')
    molecule_mdl.write('\t}\n')

    dimensionalityDict['surface_proxy'] = '2D'
    molecule_mdl.write('\t{0} //{1}\n\t{{ \n'.format('surface_proxy', 'proxy surface type. the instance contains the actual information'))
    molecule_mdl.write('\t\tDIFFUSION_CONSTANT_{0}D = {1}\n'.format(2, 1))
    molecule_mdl.write('\t\tEXTERN\n')
    molecule_mdl.write('\t}\n')
    molecule_mdl.write('}\n')

    # extract bng name
    # for molecule in jsonDict['mol_list']:
    #     dimensionalityDict[molecule['name']] = molecule['type']
    #     bngLabel[molecule['name']] = molecule['extendedName']

    compartmentDict = {}

    for molecule in xmlStructs['molecules']:
        bngLabel[molecule.name] = molecule.str2()

    for compartment in xmlStructs['compartments']:
        compartmentDict[compartment['identifier']] = compartment

    # reactions
    reaction_mdl.write('DEFINE_REACTIONS\n{\n')
    if 'DEFINE_REACTIONS' in section_mdlr.keys():
        for element in section_mdlr['DEFINE_REACTIONS']:
            write_raw_section(element, reaction_mdl, '\t')

    artificialRate = '1e-15'
    reaction_mdl.write('\t{0} -> {1} [{2}]\n'.format('volume_proxy', 'volume_proxy', artificialRate))
    reaction_mdl.write('\t{0} + {0} -> {0} + {0} [{1}]\n'.format('volume_proxy', artificialRate))
    reaction_mdl.write('\t{0}; + {1}; -> {0}; [{2}]\n'.format('volume_proxy', 'surface_proxy', artificialRate))
    reaction_mdl.write('\t{1}; + {1}; -> {1}; [{2}]\n'.format('volume_proxy', 'surface_proxy', artificialRate))
    reaction_mdl.write('\t{1}; -> {1}; [{2}]\n'.format('volume_proxy', 'surface_proxy', artificialRate))

    reaction_mdl.write('}\n')

    if 'MODIFY_SURFACE_REGIONS' in section_mdlr.keys():
        mod_surf_reg__mdl.write('MODIFY_SURFACE_REGIONS {\n')
        for element in section_mdlr['MODIFY_SURFACE_REGIONS']:
            if type(element) is str:
                mod_surf_reg__mdl.write("  {0} {{\n".format(element))
            else:
                mod_surf_reg__mdl.write("    {0} = {1}\n  }}\n".format(element[0][0], element[0][1]))
        mod_surf_reg__mdl.write('}\n')

    if 'DEFINE_SURFACE_CLASSES' in section_mdlr.keys():
        surface_classes__mdl.write('DEFINE_SURFACE_CLASSES {\n')
        for element in section_mdlr['DEFINE_SURFACE_CLASSES']:
            surface_classes__mdl.write("  {0} {{\n    {1} = {2}\n  }}\n".format(element[0], element[1][0][0], element[1][0][1]))
        surface_classes__mdl.write('}\n')

    # seed species
    seed_mdl.write('INSTANTIATE Scene OBJECT\n{\n')
    if 'INSTANTIATE' in section_mdlr.keys():
        for element in section_mdlr['INSTANTIATE'][-1].asList():
            seed_mdl.write('\t' + ' '.join(element[:-1]))
            seed_mdl.write(write_raw_section(element[-1], seed_mdl, '') + '\n')

    # include geometry information related to this scene
    mdlrseeds = []
    for entries in hashed_mdlr['initialization']['entries']:
        if entries[1] != 'RELEASE_SITE':
            seed_mdl.write('\t{0} OBJECT {1} {{}}\n'.format(entries[0], entries[1]))
        else:
            mdlrseeds.append(entries)

    for bngseed, mdlrseed in zip(xmlStructs['seedspecies'], mdlrseeds):

        seed_mdl.write('\t{0} {1} //{2}\n'.format(mdlrseed[0], mdlrseed[1], str(bngseed['structure'])))
        seed_mdl.write('\t{\n')
        # print the shape option first
        for element in mdlrseed[2]:
            if element[0] == 'SHAPE':
                seed_mdl.write('\t\t{0} = {1}\n'.format(element[0].strip(), element[1].strip()))
        if compartmentDict[bngseed['structure'].compartment]['dimensions'] in ['3', 3]:
            seed_mdl.write('\t\tMOLECULE = {0}\n'.format('volume_proxy'))
        else:
            seed_mdl.write('\t\tMOLECULE = {0}{1}\n'.format('surface_proxy', "'"))

        for element in mdlrseed[2]:
            if element[0] not in ['SHAPE', 'MOLECULE']:
                seed_mdl.write('\t\t{0} = {1}\n'.format(element[0].strip(), element[1].strip()))
            else:
                pass
        seed_mdl.write('\t\tGRAPH_PATTERN = "{0}"\n'.format(nautyDict[bngseed['structure'].trueName]))

        seed_mdl.write('\t}\n')
    seed_mdl.write('}\n')

    output_mdl.write('REACTION_DATA_OUTPUT\n{\n')

    if 'REACTION_DATA_OUTPUT' in section_mdlr.keys():
        for element in section_mdlr['REACTION_DATA_OUTPUT']:
            write_raw_section(element, output_mdl, '\t')

    for element in hashed_mdlr['observables']:
        if type(element[0]) == str:
            output_mdl.write('\t{0} = {1}\n'.format(element[0], element[1]))

    output_mdl.write('}\n')

    return {'main': final_mdl,
            'molecules': molecule_mdl,
            'reactions': reaction_mdl,
            'mod_surf_reg': mod_surf_reg__mdl,
            'surface_classes': surface_classes__mdl,
            'rxnOutput': output_mdl,
            'seeding': seed_mdl}


def construct_mdl(jsonPath, mdlrPath, outputFileName):
    """
    Create an _mdl readable by standard mcell.

    Keyword arguments:
    jsonPath -- A json dictionary containing structures and parameters extracted from the mdlr input
    mdlrPath -- An mdlr file. In this method we will be mainly extracting the non RBM sections

    Returns:
    A dictionary containing the different _mdl sections
    """

    # load up data structures
    jsonDict = read_bngljson(jsonPath)
    mdlr = read_mdlr(mdlrPath)
    # print mdlr
    section_mdlr = gd.nonhashedgrammar.parseString(mdlr)
    statement_mdlr = gd.statementGrammar.parseString(mdlr)

    # create output buffers
    final_mdl = StringIO()
    molecule_mdl = StringIO()
    reaction_mdl = StringIO()
    output_mdl = StringIO()
    seed_mdl = StringIO()

    # output statements as is
    for element in statement_mdlr:
        final_mdl.write('{0} = {1}\n'.format(element[0], element[1]))

    final_mdl.write('\n')
    final_mdl.write('INCLUDE_FILE = "{0}.molecules.mdl"\n'.format(outputFileName))
    final_mdl.write('INCLUDE_FILE = "{0}.reactions.mdl"\n'.format(outputFileName))
    final_mdl.write('INCLUDE_FILE = "{0}.seed.mdl"\n\n'.format(outputFileName))

    # output sections using json information
    sectionOrder = {'DEFINE_MOLECULES': molecule_mdl, 'DEFINE_REACTIONS': reaction_mdl, 'REACTION_DATA_OUTPUT': output_mdl, 'INSTANTIATE': seed_mdl}
    for element in section_mdlr:
        if element[0] not in sectionOrder:
            final_mdl.write(write_section(element))

    final_mdl.write('INCLUDE_FILE = "{0}.output.mdl"\n'.format(outputFileName))

    dimensionalityDict = {}
    # molecules
    molecule_mdl.write('DEFINE_MOLECULES\n{\n')
    if 'DEFINE_MOLECULES' in section_mdlr.keys():
        for element in section_mdlr['DEFINE_MOLECULES']:
            write_raw_section(element, molecule_mdl, '\t')

    for molecule in jsonDict['mol_list']:
        dimensionalityDict[molecule['name']] = molecule['type']
        molecule_mdl.write('\t{0} //{1}\n\t{{ \n'.format(molecule['name'], molecule['extendedName']))
        molecule_mdl.write('\t\tDIFFUSION_CONSTANT_{0} = {1}\n'.format(molecule['type'], molecule['dif']))
        molecule_mdl.write('\t}\n')
    molecule_mdl.write('}\n')

    # reactions
    reaction_mdl.write('DEFINE_REACTIONS\n{\n')
    if 'DEFINE_REACTIONS' in section_mdlr.keys():
        for element in section_mdlr['DEFINE_REACTIONS']:
            write_raw_section(element, reaction_mdl, '\t')

    for reaction in jsonDict['rxn_list']:
        reaction_mdl.write('\t{0} -> {1} [{2}]\n'.format(reaction['reactants'], reaction['products'], reaction['fwd_rate']))
    reaction_mdl.write('}\n')

    # seed species
    seed_mdl.write('INSTANTIATE Scene OBJECT\n{\n')
    if 'INSTANTIATE' in section_mdlr.keys():
        for element in section_mdlr['INSTANTIATE'][-1].asList():
            seed_mdl.write('\t' + ' '.join(element[:-1]))
            seed_mdl.write(write_raw_section(element[-1], seed_mdl, '') + '\n')
            #
    for seed in jsonDict['rel_list']:
        seed_mdl.write('\t{0} RELEASE_SITE\n\t{{\n'.format(seed['name']))
        seed_mdl.write('\t\tSHAPE = Scene.{0}\n'.format(seed['object_expr']))
        orientation = seed['orient'] if dimensionalityDict[seed['molecule']] == '2D' else ''
        seed_mdl.write('\t\tMOLECULE = {0}{1}\n'.format(seed['molecule'], orientation))
        if seed['quantity_type'] == 'DENSITY':
            quantity_type = 'DENSITY' if dimensionalityDict[seed['molecule']] == '2D' else 'CONCENTRATION'
        else:
            quantity_type = seed['quantity_type']
        seed_mdl.write('\t\t{0} = {1}\n'.format(quantity_type, seed['quantity_expr']))
        seed_mdl.write('\t\tRELEASE_PROBABILITY = 1\n'.format(seed['molecule']))
        seed_mdl.write('\t}\n')

    seed_mdl.write('}\n')

    # rxn_output
    output_mdl.write('REACTION_DATA_OUTPUT\n{\n')

    if 'REACTION_DATA_OUTPUT' in section_mdlr.keys():
        for element in section_mdlr['REACTION_DATA_OUTPUT']:
            write_raw_section(element, output_mdl, '\t')

    for obs in jsonDict['obs_list']:
        if any([x != ['0'] for x in obs['value']]):
            output_mdl.write('\t{')

            output_mdl.write(' + '.join(['COUNT[{0},WORLD]'.format(x[0]) for x in obs['value'] if x != ['0']]) + '}')

            output_mdl.write(' => "./react_data/{0}.dat"\n'.format(obs['name']))
    output_mdl.write('}\n')

    return {'main': final_mdl, 'molecules': molecule_mdl, 'reactions': reaction_mdl, 'rxnOutput': output_mdl, 'seeding': seed_mdl}


def define_console():
    parser = argparse.ArgumentParser(description='SBML to BNGL translator')
    parser.add_argument(
        '-ij',
        '--input_json',
        type=str,
        help='input SBML-JSON file',
        required=True)
    parser.add_argument(
        '-im',
        '--input_mdl',
        type=str,
        help='input SBML-JSON file',
        required=True)
    parser.add_argument('-o', '--output', type=str, help='output _mdl file')
    return parser


def write_mdl(mdl_dict, outputFileName):
    with open('{0}.main.mdl'.format(outputFileName), 'w') as f:
        f.write(mdl_dict['main'].getvalue())
    with open('{0}.molecules.mdl'.format(outputFileName), 'w') as f:
        f.write(mdl_dict['molecules'].getvalue())
    with open('{0}.reactions.mdl'.format(outputFileName), 'w') as f:
        f.write(mdl_dict['reactions'].getvalue())
    with open('{0}.surface_classes.mdl'.format(outputFileName), 'w') as f:
        f.write(mdl_dict['surface_classes'].getvalue())
    with open('{0}.mod_surf_reg.mdl'.format(outputFileName), 'w') as f:
        f.write(mdl_dict['mod_surf_reg'].getvalue())
    with open('{0}.seed.mdl'.format(outputFileName), 'w') as f:
        f.write(mdl_dict['seeding'].getvalue())
    with open('{0}.output.mdl'.format(outputFileName), 'w') as f:
        f.write(mdl_dict['rxnOutput'].getvalue())


if __name__ == "__main__":
    parser = define_console()
    namespace = parser.parse_args()

    finalName = namespace.output if namespace.output else 'example_expanded'
    mdl_dict = construct_mdl(
        namespace.input_json, namespace.input_mdl, finalName)
    write_mdl(mdl_dict)
