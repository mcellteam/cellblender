import argparse


def defineConsole():
    """
    input console options
    """
    parser = argparse.ArgumentParser(description='SBML to BNGL translator')
    parser.add_argument('-i', '--input', type=str, help='input MDLr file', required=True)
    return parser

def extractSeedBNG(xmlname):
    with open(xmlname, 'r') as f:
        bngxml = f.read()

    start = bngxml.find('<ListOfSpecies>')
    end = bngxml.find('</ListOfSpecies>') + len('</ListOfSpecies>')

    seedxml =  '<Model>\n' + bngxml[start:end] + '</Model>\n'
    restxml = bngxml[:start] + '<ListOfSpecies>\n</ListOfSpecies>' + bngxml[end:]

    
    return seedxml, restxml

if __name__ == "__main__":
    parser = defineConsole()
    namespace = parser.parse_args()

    seed, rest = extractSeedBNG(namespace.input)
    with open(namespace.input + '_total.xml','w') as f:
        f.write(rest)

