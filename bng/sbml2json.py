# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 11:19:37 2013

@author: Jose Juan Tapia
"""

import platform



try:
    from . import treelib3
    if platform.system() == 'Linux':
        from .libsbml3.linux import libsbml
    elif platform.system() == 'Darwin':
        from .libsbml3.macosx import libsbml
    else:
        libsbml = None
except ImportError:
    treelib3 = None
    libsbml = None

#import treelib3
#from  libsbml3.linux import libsbml
import json
from optparse import OptionParser

def factorial(x):
    temp = x
    acc = 1
    while temp > 0:
        acc *= temp
        temp -= 1
    return acc

def comb(x,y):
    return factorial(x)/(factorial(y) * factorial(x-y))


class SBML2JSON:
        
    def __init__(self, model):
        self.model = model
        self.getUnits()
        self.moleculeData = {}
        self.compartmentMapping = {}
    def getUnits(self):
        self.unitDictionary = {}
        self.mcellUnitDictionary = {}
        
        self.mcellUnitDictionary[libsbml.UNIT_KIND_METER] = [[-6,1]]
        self.mcellUnitDictionary[libsbml.UNIT_KIND_METRE] = [[-6,1]]
        #unitDictionary['substance'] = [libsbml.UNIT_KIND_MOLE,1]
        #unitDictionary['volume'] = [libsbml.UNIT_KIND_LITER,1]
        #unitDictionary['area'] = [libsbml.UNIT_KIND_METER,1]
        #unitDictionary['length'] = [libsbml.UNIT_KIND_METER,1]
        #unitDictionary['time'] = [libsbml.UNIT_KIND_SECOND,1]
        
        '''
        mcell units
        - - lengths: microns
        - - times  : seconds
        - - diffusion coef: cm^2/s
        - - unimol rate constant : 1/s
        - - bimo rate constants:  1/(Mol s)
        -- bimolecular surface 1/(um^2 N s)
        '''

        for unitDefinition in self.model.getListOfUnitDefinitions():
            unitList = []
            for unit in unitDefinition.getListOfUnits():
                        
                unitList.append([unit.getKind(),unit.getScale(),unit.getExponent()])
                
            self.unitDictionary[unitDefinition.getId()] = unitList
        '''
       
        Table 3: SBML's built-in units.
        Name	 Possible Scalable Units	 Default Units	
        substance	 mole, item	 mole	
        volume	 litre, cubic metre	 litre	
        area	 square metre	 square metre	
        length	 metre	 metre	
        time	 second	 second	
        '''

                
    def getParameters(self):
        parameters = []
        prx = [{'name':"Nav",'value':"6.022e8",'unit':"",'type':"Avogadro number for 1 um^3"},
               {'name':"KB",'value':"1.3806488e-19",'unit':"cm^2.kg/K.s^2",'type':"Boltzmann constant"},
               {'name':"gamma",'value':"0.5722",'unit':"",'type':"Euler's constant"},
               {'name':"T",'value':"298.25",'unit':"K",'type':""},
               {'name':"rxn_layer_t",'value':"0.01",'unit':"um",'type':""},
               {'name':"h",'value':"0.01",'unit':"um",'type':""},
               {'name':"Rs",'value':"0.002564",'unit':"um",'type':""},
               {'name':"Rc",'value':"0.0015",'unit':"um",'type':""}
              ]
        parameters.extend(prx)
        
        for compartment in self.model.getListOfCompartments():
            name = compartment.getId()
            parameters.append({'name':"mu_{0}".format(name),'value':"1e-9",'unit':"kg/um.s",'type':"viscosity"})

        for parameter in self.model.getListOfParameters():
            parameterSpecs = {'name':parameter.getId(),'value':parameter.getValue(),
                              'unit':parameter.getUnits(),'type' : ""}
            '''                             
            if parameterSpecs[0] == 'e':
                parameterSpecs = ('are',parameterSpecs[1])
            if parameterSpecs[1] == 0:
                zparam.append(parameterSpecs[0])
            '''
            #transform to standard units
            if parameter.getUnits() in self.unitDictionary:
                for factor in self.unitDictionary[parameter.getUnits()]:
                    parameterSpecs['value'] *= 10 ** (factor[1] * factor[2])
                    parameterSpecs['unit'] = '{0}*1e{1}'.format(parameterSpecs['unit'],factor[1]*factor[2])
                #adjust for mcell units
                if parameter.getUnits() in self.mcellUnitDictionary:
                    mcellfactor = self.mcellUnitDictionary[factor[0]]
                    parameterSpecs['value'] /= 10**(mcellfactor[0]*mcellfactor[1])
                    parameterSpecs['unit'] = '{0}/1e{1}'.format(parameterSpecs['unit'],mcellfactor[0]*mcellfactor[1])
                if 'mole' in parameter.getUnits() and 'per_mole' not in parameter.getUnits():
                    parameterSpecs['value' ] *= float(6.022e8)
                    parameterSpecs['unit'] = '{0}*{1}'.format(parameterSpecs['unit'],'avo.num')
            #if parameter.getUnits() == '':
            #    parameterSpecs['value'] *= float(6.022e8*1000)
            #    parameterSpecs['unit'] = '{0}*{1}'.format(parameterSpecs['unit'],'avo.num*1000')
            
            parameters.append(parameterSpecs)
        prx = {'name':"rxn_layer_t",'value':"0.01",'unit':"um",'type':""}
        ph = {'name':"h",'value':"rxn_layer_t",'unit':"um",'type':""}
        pRs = {'name':"Rs",'value':"0.002564",'unit':"um",'type':""}
        pRc = {'name':"Rc",'value':"0.0015",'unit':"um",'type':""}
        parameters.append(prx)        
        parameters.append(ph)
        parameters.append(pRs)
        parameters.append(pRc)
        #parameterDict = {idx+1:x for idx,x in enumerate(parameters)}
        return parameters
        
    
    def __getRawCompartments(self):
        '''
        extracts information about the compartments in a model
        *returns* name,dimensions,size
        '''
        compartmentList = {}
        for compartment in self.model.getListOfCompartments():
            name = compartment.getId()
            size = compartment.getSize()
            outside = compartment.getOutside()
            dimensions = compartment.getSpatialDimensions()
            compartmentList[name] = [dimensions,self.normalize(size),outside]
        return compartmentList
    
    def getOutsideInsideCompartment(self,compartmentList,compartment):
        inside = []
        outside = compartmentList[compartment][2]
        for comp in compartmentList:
            if compartmentList[comp][2] == compartment:
                return outside, comp
                
        return outside,-1

    def getCompartmentHierarchy(self,compartmentList):
        '''
        constructs a tree structure containing the 
        compartment hierarchy excluding 2D compartments
        @param:compartmentList
        '''
        def removeMembranes(tree,nodeID):
            node = tree.get_node(nodeID)
            if node.data == 2:
                parent = tree.get_node(nodeID).bpointer
                tree.link_past_node(nodeID)
                nodeID = parent
                node = tree.get_node(nodeID)
            for element in node.fpointer:
                removeMembranes(tree,element)
            
        from copy import deepcopy
        tree = treelib3.Tree()
        c2 = deepcopy(compartmentList)
        while len(c2) > 0:
            removeList = []
            for element in c2:
                if c2[element][2] == '':
                    tree.create_node(element,element,data=c2[element][0])
                    removeList.append(element)
                elif tree.contains(c2[element][2]):
                    tree.create_node(element,element,parent=c2[element][2],data=c2[element][0])
                    removeList.append(element)
            for element in removeList:
                c2.pop(element)
        removeMembranes(tree,tree.root)
        return tree
        
    def getMolecules(self):
        '''
        *species* is the element whose SBML information we will extract
        this method gets information directly
        from an SBML related to a particular species.
        It returns id,initialConcentration,(bool)isconstant and isboundary,
        and the compartment
        '''
        
        compartmentList = self.__getRawCompartments()
        tree = self.getCompartmentHierarchy(compartmentList)
        molecules = []
        release = []
        for idx,species in enumerate(self.model.getListOfSpecies()):
            compartment = species.getCompartment()
            outside,inside = self.getOutsideInsideCompartment(compartmentList, compartment)
            if compartmentList[compartment][0] == 3:
                typeD = '3D'
                diffusion = 'KB*T/(6*PI*mu_{0}*Rs)'.format(compartment)
            else:
                typeD = '2D'
                diffusion = 'KB*T*LOG((mu_{0}*h/(SQRT(4)*Rc*(mu_{1}+mu_{2})/2))-gamma)/(4*PI*mu_{0}*h)'.format(compartment,outside,inside)
            self.moleculeData[species.getId()] = [compartmentList[compartment][0]]
            self.compartmentMapping[species.getId()] = compartment
            moleculeSpecs={'name':species.getId(),'type':typeD,'extendedName':species.getName(),'dif':diffusion}
            initialConcentration = species.getInitialConcentration()

            if initialConcentration == 0:
                initialConcentration = species.getInitialAmount()
            if species.getSubstanceUnits() in self.unitDictionary:
                for factor in self.unitDictionary[species.getSubstanceUnits()]:
                    initialConcentration *= 10 ** (factor[1] * factor[2])
                if 'mole' in species.getSubstanceUnits():
                    initialConcentration /= float(6.022e8)
            #if species.getSubstanceUnits() == '':
            #    initialConcentration /= float(6.022e8)
                
            isConstant = species.getConstant()
            #isBoundary = species.getBoundaryCondition()
            if initialConcentration != 0:
                if compartmentList[compartment][0] == 2:
                    objectExpr = '{0}[{1}]'.format(inside.upper(),compartment.upper())
                    #objectExpr = '{0}[ALL]'.format(inside.upper(),compartment.upper())
                else:
                    objectExpr = '{0}[wall]'.format(compartment)                    
                    children = tree.get_node(compartment).fpointer
                    for element in children:
                        objectExpr = '{0} - {1}[wall]'.format(objectExpr,element)
                releaseSpecs = {'name': 'Release_Site_s{0}'.format(idx+1),'molecule':species.getId(),'shape':'OBJECT'
            ,'quantity_type':"NUMBER_TO_RELEASE",'quantity_expr':initialConcentration,'object_expr':objectExpr,'orient':"'"}
                release.append(releaseSpecs)
            #self.speciesDictionary[identifier] = standardizeName(name)
            #returnID = identifier if self.useID else \
            molecules.append(moleculeSpecs)
            
            #self.sp eciesDictionary[identifier]
        #moleculesDict = {idx+1:x for idx,x in enumerate(molecules)}
        #releaseDict = {idx+1:x for idx, x in enumerate(release)}
        return molecules,release
    
    def getPrunnedTree(self,math,remainderPatterns):
        '''
        removes the remainderPatterns leafs from the math tree
        '''
        while (math.getCharacter() == '*' or math.getCharacter() == '/') and len(remainderPatterns) > 0:
            if libsbml.formulaToString(math.getLeftChild()) in remainderPatterns:
                remainderPatterns.remove(libsbml.formulaToString(math.getLeftChild()))
                math = math.getRightChild()
            elif libsbml.formulaToString(math.getRightChild()) in remainderPatterns:
                remainderPatterns.remove(libsbml.formulaToString(math.getRightChild()))
                math = math.getLeftChild()            
            else:
                if(math.getLeftChild().getCharacter()) == '*':
                    math.replaceChild(0, self.getPrunnedTree(math.getLeftChild(), remainderPatterns))
                if(math.getRightChild().getCharacter()) == '*':
                    math.replaceChild(math.getNumChildren() - 1,self.getPrunnedTree(math.getRightChild(), remainderPatterns))
                break
        return math
        
    def getInstanceRate(self,math,compartmentList, reversible,rReactant,rProduct):

        
        #remove compartments from expression
        math = self.getPrunnedTree(math, compartmentList)
        if reversible:
            if math.getCharacter() == '-' and math.getNumChildren() > 1:
                rateL, nl = (self.removeFactorFromMath(
                math.getLeftChild().deepCopy(), rReactant, rProduct))
                rateR, nr = (self.removeFactorFromMath(
                math.getRightChild().deepCopy(), rProduct, rReactant))
            else:
                rateL, nl = self.removeFactorFromMath(math, rReactant,
                                                      rProduct)
                rateL = "if({0} >= 0 ,{0},0)".format(rateL)
                rateR, nr = self.removeFactorFromMath(math, rReactant,
                                                      rProduct)
                rateR = "if({0} < 0 ,-({0}),0)".format(rateR)
                nl, nr = 1,1
        else:
            rateL, nl = (self.removeFactorFromMath(math.deepCopy(),
                                                 rReactant,rProduct))
            rateR, nr = '0', '-1'
        if reversible:
            pass
        return rateL,rateR


    def removeFactorFromMath(self, math, reactants, products):
        remainderPatterns = []
        highStoichoiMetryFactor = 1
        for x in reactants:
            highStoichoiMetryFactor  *= factorial(x[1])
            y = [i[1] for i in products if i[0] == x[0]]
            y = y[0] if len(y) > 0 else 0
            #TODO: check if this actually keeps the correct dynamics
            # this is basically there to address the case where theres more products
            #than reactants (synthesis)
            if x[1] > y:
                highStoichoiMetryFactor /= comb(int(x[1]), int(y))
            for counter in range(0, int(x[1])):
                remainderPatterns.append(x[0])
        #for x in products:
        #    highStoichoiMetryFactor /= math.factorial(x[1])
        #remainderPatterns = [x[0] for x in reactants]
        math = self.getPrunnedTree(math,remainderPatterns)
        rateR = libsbml.formulaToString(math) 
        for element in remainderPatterns:
            rateR = 'if({0} >0,({1})/{0} ,0)'.format(element,rateR)
        if highStoichoiMetryFactor != 1:
            rateR = '{0}*{1}'.format(rateR, int(highStoichoiMetryFactor))

        return rateR,math.getNumChildren()

    def adjustParameters(self,stoichoimetry,rate,parameters):
        for parameter in parameters:
            if parameter['name'] in rate and parameter['unit'] == '':
                if stoichoimetry == 2:
                    parameter['value'] *= float(6.022e8)
                    parameter['unit'] ='Bimolecular * NaV'
                elif stoichoimetry == 0:
                    parameter['value'] /= float(6.022e8)
                    parameter['unit'] ='0-order / NaV'
                elif stoichoimetry == 1:
                    parameter['unit'] ='Unimolecular'
                
    def normalize(self,parameter):
        import math
        if math.isnan(parameter) or parameter == None:
            return 1
        return parameter
        
    def getReactions(self,sparameters):
        def isOutside(compartmentList,inside,outsideCandidate):
            tmp = compartmentList[inside][1]
            while tmp not in  ['',None]:
                tmp = compartmentList[tmp][1]
                if tmp == outsideCandidate:
                    return True
            return False
        def getContained(compartmentList,container):
            for element in compartmentList:
                if compartmentList[element][1] == container:
                    return element
        reactionSpecs = []
        releaseSpecs = []
        from copy import deepcopy
        for index, reaction in enumerate(self.model.getListOfReactions()):
            kineticLaw = reaction.getKineticLaw()
            
            rReactant = [(x.getSpecies(), self.normalize(x.getStoichiometry()),self.compartmentMapping[x.getSpecies()]) for x in reaction.getListOfReactants() if x.getSpecies() != 'EmptySet']
            rProduct = [(x.getSpecies(), self.normalize(x.getStoichiometry()),self.compartmentMapping[x.getSpecies()]) for x in reaction.getListOfProducts() if x.getSpecies() != 'EmptySet']
            reactant = deepcopy(rReactant)
            product = deepcopy(rProduct)
            parameters = [(parameter.getId(), parameter.getValue()) for parameter in kineticLaw.getListOfParameters()]
            math = kineticLaw.getMath()
            reversible = reaction.getReversible()
            compartmentList  = {}
            for compartment in (self.model.getListOfCompartments()):
                compartmentList[compartment.getId()] = (compartment.getSpatialDimensions(),
                                                    compartment.getOutside())
                
            rateL, rateR = self.getInstanceRate(math,compartmentList.keys(),reversible,rReactant,rProduct)
            #finalReactant = [x[0]]    
            #testing whether we have volume-surface interactions
            rcList = []
            prdList = []
            orientationSet = set()
            for element in reactant:
                orientation = "," if len(set(self.moleculeData[x[0]][0] for x in reactant)) \
                > 1 and self.moleculeData[element[0]][0] == 3 else "'"
                rcList.append("{0}{1}".format(element[0],orientation))
                orientationSet.add(self.moleculeData[element[0]][0])
            for element in product:
                orientation = "," if len(set(self.moleculeData[x[0]][0] for x in reactant)) \
                > 1 and self.moleculeData[element[0]][0] == 3 else "'"
                prdList.append("{0}{1}".format(element[0],orientation))
                orientationSet.add(self.moleculeData[element[0]][0])
            #if everything is the same orientation delete orientation
            
            if len(orientationSet) == 1 and 3 in orientationSet:
                for index2,element in enumerate(rcList):
                    rcList[index2] = element[:-1]
                for index2,element in enumerate(prdList):
                    prdList[index2] = element[:-1]
            
            tmpL = {}
            tmpR = {}
            flagL=flagR=False
            if len(reactant) == 1 and len(product) ==1 and reactant[0][2] != product[0][2] \
            and compartmentList[product[0][2]][0] == compartmentList[reactant[0][2]][0]:
                tmpL['rxn_name'] = 'rec_{0}'.format(index+1)
                tmpR['rxn_name'] = 'rec_m{0}'.format(index+1)
                if compartmentList[product[0][2]][0] == 3:
                    object_expr = product[0][2].upper()
                    object_exprm = reactant[0][2].upper()
                else:
                    sourceGeometry = getContained(compartmentList,product[0][2])
                    sourceGeometryM = getContained(compartmentList,reactant[0][2])
                    #if isOutside(compartmentList,reactant[0][2],product[0][2]):
                    #    sourceGeometry = compartmentList[p[0][2]][1]
                    #elif isOutside(compartmentList,product[0][2],reactant[0][2]):
                    #    sourceGeometry = compartmentList[product[0][2]][1]
                    #else:
                    #    sourceGeometry = compartmentList[product[0][2]][1]
                        
                        
                    object_expr = '{0}[{1}]'.format(sourceGeometry,product[0][2])
                    object_exprm = '{0}[{1}]'.format(sourceGeometryM,reactant[0][2])

                releaseSpecs.append({'name': 'Release_Site_pattern_s{0}'.format(index+1),
                'molecule':product[0][0],'shape':'OBJECT',
                'orient':"'",'quantity_type':'NUMBER_TO_RELEASE',
                'release_pattern':'rec_{0}'.format(index+1),
                'quantity_expr':"1",'object_expr':object_expr
                })
                flagL= True
                
                if rateR != '0':
                    releaseSpecs.append({'name': 'Release_Site_pattern_sm{0}'.format(index+1),
                    'molecule':reactant[0][0],'shape':'OBJECT',
                    'orient':"'",'quantity_type':'NUMBER_TO_RELEASE',                    
                    'release_pattern':'rec_m{0}'.format(index+1),
                    'quantity_expr':"1",'object_expr':object_exprm
                    })
                    flagR = True
                    
                
            if rateL != '0':
                
                tmpL['reactants'] = ' + '.join(rcList)
                if flagL:
                    tmpL['products'] = 'NULL'
                else:
                    tmpL['products'] = ' + '.join(prdList)
                tmpL['fwd_rate'] = rateL
                reactionSpecs.append(tmpL)
            if rateR != '0':
                tmpR['reactants'] = ' + '.join(prdList)
                if flagR:
                    tmpR['products'] = 'NULL'
                else:                    
                    tmpR['products'] = ' + '.join(rcList)
                tmpR['fwd_rate'] = rateR
                reactionSpecs.append(tmpR)
            self.adjustParameters(len(reactant),rateL,sparameters)
            self.adjustParameters(len(product),rateR,sparameters)
        #reactionDict = {idx+1:x for idx,x in enumerate(reactionSpecs)}
        return reactionSpecs,releaseSpecs
            #SBML USE INSTANCE RATE 
            #HOW TO GET THE DIFFUSION CONSTANT

def transform(filePath):
    if libsbml == None:
        return False
        
    reader = libsbml.SBMLReader()

    print(filePath)
    document = reader.readSBMLFromFile(filePath)
    if document.getModel() == None:
        return False
    parser = SBML2JSON(document.getModel())
    parameters =  parser.getParameters()
    molecules,release = parser.getMolecules()      
    reactions,release2 =  parser.getReactions(parameters)
    release.extend(release2)
    definition = {}
    definition['par_list'] = parameters
    definition['mol_list'] = molecules
    definition['rxn_list'] = reactions
    definition['rel_list'] = release
    with open(filePath + '.json','w') as f:
        json.dump(definition,f,sort_keys=True,indent=1, separators=(',', ': '))
    return True
    

def main():
	
    parser = OptionParser()
    parser.add_option("-i","--input",dest="input",
		default='/home/proto/workspace/bionetgen/bng2/Validate/comp/Motivating_example_cBNGL_13_sbml.xml',type="string",
		#default='/home/proto/Downloads/cell1test3.xml',type="string",
        help="The input SBML file in xml format. Default = 'input.xml'",metavar="FILE")
    parser.add_option("-o","--output",dest="output",
		type="string",
		help="the output JSON file. Default = <input>.py",metavar="FILE")
    (options, args) = parser.parse_args()
    reader = libsbml.SBMLReader()
    nameStr = options.input
    if options.output == None:
        outputFile = nameStr + '.json'
    else:
        outputFile = options.output
    print(outputFile)
    document = reader.readSBMLFromFile(nameStr)
    if document.getModel() == None:
        return
    parser = SBML2JSON(document.getModel())
    parameters =  parser.getParameters()
    molecules,release = parser.getMolecules()
    reactions,release2 =  parser.getReactions(parameters)
    release.extend(release2)
    #release.extend(release2)
    definition = {}
    definition['par_list'] = parameters
    definition['mol_list'] = molecules
    definition['rxn_list'] = reactions
    definition['rel_list'] = release
    with open(outputFile,'w') as f:
        json.dump(definition,f,sort_keys=True,indent=1, separators=(',', ': '))
        

if __name__ == "__main__":
	main()
