from lxml import etree


def create_property_node(parentNode, key, value):
    if value.startswith('"'):
        propertyNode = etree.SubElement(parentNode, "Property", id=key, value=value.strip('"'), type="str")
    else:
        propertyNode = etree.SubElement(parentNode, "Property", id=key, value=value, type="num")
    return propertyNode


def write2bngxmle(properties_dict, model_name):
    '''
    creates a bng-xml v1.1 spec from model properties
    '''
    #xmlns="bngexperimental"
    root = etree.Element("bngexperimental", version="1.1", name=model_name)
    #mainNode = etree.SubElement(root, "model", id=model_name)
    if len(properties_dict['modelProperties']) > 0:
        listOfModelProperties = etree.SubElement(root, "ListOfProperties")
        for element in properties_dict['modelProperties']:
            #etree.SubElement(listOfModelProperties, "Property", id=element.strip().lower(), value=properties_dict['modelProperties'][element].strip())
            create_property_node(listOfModelProperties, element.strip().lower(), properties_dict['modelProperties'][element].strip())

    listOfCompartments = etree.SubElement(root, "ListOfCompartments")

    for element in properties_dict['compartmentProperties']:
        compartmentNode = etree.SubElement(listOfCompartments,"Compartment", id=element)
        listOfCompartmentProperties = etree.SubElement(compartmentNode,"ListOfProperties")
        for propertyEntry in properties_dict['compartmentProperties'][element]:
            #etree.SubElement(listOfCompartmentProperties, "Property", id=propertyEntry[0].strip().lower(), value=propertyEntry[1].strip())
            create_property_node(listOfCompartmentProperties, propertyEntry[0].strip().lower(), propertyEntry[1].strip())

    listOfMoleculeTypes = etree.SubElement(root, "ListOfMoleculeTypes")

    for element in properties_dict['moleculeProperties']:
        moleculeNode = etree.SubElement(listOfMoleculeTypes,"MoleculeType", id=element)
        listOfMoleculeProperties = etree.SubElement(moleculeNode,"ListOfProperties")
        for propertyEntry in properties_dict['moleculeProperties'][element]:
            propertyNode = create_property_node(listOfMoleculeProperties, propertyEntry[0].strip().lower(), propertyEntry[1]['name'].strip())
            if len(propertyEntry[1]['parameters']) > 0:
                sublistOfMoleculeProperties = etree.SubElement(propertyNode,"ListOfProperties")
                #propertyNode = etree.SubElement(listOfMoleculeProperties, "Property", id=propertyEntry[0].strip().lower(), value=propertyEntry[1]['name'].strip())
                for parameter in propertyEntry[1]['parameters']:
                    etree.SubElement(sublistOfMoleculeProperties, "Property",id=parameter[0],value=parameter[1])

    return etree.tostring(root, pretty_print=True)


def merge_bxbxe(base_bngxml, extended_bngxml):
    '''
    temporary method to concatenate a bng-xml 1.0 and bng-xml 1.1 definition
    '''
    basedoc = etree.parse(base_bngxml).getroot()
    edoc = etree.parse(extended_bngxml).getroot()
    basedoc.append(edoc)
    return etree.tostring(basedoc, encoding='unicode', pretty_print=True)
