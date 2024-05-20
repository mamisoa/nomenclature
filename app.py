import codecs
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree

def read_fees_and_generate_data(input_path, encoding='windows-1252'):
    # Read the original XML for fee details
    tree = ET.parse(codecs.open(input_path, 'r', encoding))
    root = tree.getroot()

    # Dictionary to hold fee data
    nomen_fees = {}
    for elem in root.findall('.//NOMEN_CODE_FEE_LIM'):
        nomen_code = elem.find('nomen_code').text if elem.find('nomen_code') is not None else ''
        fee_code = int(float(elem.find('fee_code').text)) if elem.find('fee_code') is not None else None
        fee = float(elem.find('fee').text) if elem.find('fee') is not None else None

        if nomen_code not in nomen_fees:
            nomen_fees[nomen_code] = {0: None, 1600: None, 1300: None}
        
        if fee_code in nomen_fees[nomen_code]:
            nomen_fees[nomen_code][fee_code] = fee

    return nomen_fees

def read_descriptions(desc_path, encoding='windows-1252'):
    # Read the XML for descriptions
    parser = etree.XMLParser(recover=True, encoding=encoding)
    desc_tree = etree.parse(desc_path, parser=parser)
    desc_root = desc_tree.getroot()

    # Dictionary to hold descriptions
    descriptions = {}
    for elem in desc_root.findall('.//NOMEN_CODE_DESC_HIST'):
        nomen_code = elem.find('nomen_code').text if elem.find('nomen_code') is not None else ''
        language = elem.find('language').text if elem.find('language') is not None else ''
        description = elem.find('nomen_desc').text if elem.find('nomen_desc') is not None else ''
        
        if nomen_code not in descriptions:
            descriptions[nomen_code] = {'F': '', 'N': ''}
        if language == 'F':
            descriptions[nomen_code]['F'] = description
        elif language == 'N':
            descriptions[nomen_code]['N'] = description

    return descriptions

def create_final_xml(fee_data, desc_data, output_path):
    # Create root element for the new XML
    root = ET.Element('nomen_data')
    
    # Merge data and build XML structure
    for code in fee_data:
        entry = ET.SubElement(root, 'nomen_code_entry', attrib={'code': code})
        fees = fee_data[code]
        ET.SubElement(entry, 'cout').text = str([fees[0], fees[1600], fees[1300],0])
        
        if code in desc_data:
            ET.SubElement(entry, 'desc_fr').text = desc_data[code]['F']
            ET.SubElement(entry, 'desc_nl').text = desc_data[code]['N']

    # Pretty print and save to file
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xmlstr)

# File paths
fee_xml_path = './NOMEN_CODE_FEE_LIM.xml'
desc_xml_path = './NOMEN_CODE_DESC_HIST.xml'
output_xml_path = './transformed.xml'

# Process data
fee_data = read_fees_and_generate_data(fee_xml_path)
desc_data = read_descriptions(desc_xml_path)
create_final_xml(fee_data, desc_data, output_xml_path)
