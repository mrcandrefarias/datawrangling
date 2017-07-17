#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

def parser_subtag(element, documento):
    address = {}
    for subtag in element:
        if subtag.tag == 'tag': 
            if subtag.get('k').startswith('addr:'):
                address[subtag.get('k')[5:]] = subtag.get('v')
            else:
                documento[subtag.get('k')] = subtag.get('v') 
        
    if len(address) > 0:
        documento['address'] = address
        print address
        
    return documento
    
def parser_element(element):
    documento = {}
    if element.tag == "node" or element.tag == "way" :
        for e in element.attrib.keys():    
            documento[e]      = element.get(e)
            documento['type'] = element.tag
         
        return parser_subtag(element, documento)
    else:
        return None

def xml_to_json(arquivo_entrada, arquivo_saida):
    with codecs.open(arquivo_saida, "w") as saida:
        for _, element in ET.iterparse(arquivo_entrada):
            el = parser_element(element)
            if el:     
                saida.write( json.dumps(el) + "\n")
                

file_path  = "../data/bh"
xml_to_json( file_path + ".osm", file_path + ".json")