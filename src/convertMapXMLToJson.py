#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

def parser_subtag(element, node):
    address = {}
    for subtag in element:
        if subtag.tag == 'tag': 
            if subtag.get('k').startswith('addr:'):
                address[subtag.get('k')[5:]] = subtag.get('v')
            else:
                node[subtag.get('k')] = subtag.get('v') 
        
    if len(address) > 0:
        node['address'] = address
        print address
        
    return node
    
def parser_element(element):
    node = {}
    
    if element.tag == "node" or element.tag == "way" :
        for e in element.attrib.keys():    
            node[e]      = element.get(e)
            node['type'] = element.tag
            
        return parser_subtag(element, node)
    else:
        return None

def xml_to_json(arquivo_entrada, arquivo_saida):
    
    with codecs.open(arquivo_saida, "w") as saida:
        saida.write("[");
        start = True
        for _, element in ET.iterparse(arquivo_entrada):
            el = parser_element(element)
            if el:
                if start == False:
                     saida.write( ",\n" )
                     
                saida.write(json.dumps(el))
                start = False
                
        saida.write("]");
    
def process(file):   
    data = []
    for _, element in ET.iterparse(file):
        el = parser_element(element)
        if el:
            data.append(el)
         
    return data
    

file_path  = "../data/bhmicro"
data = xml_to_json( file_path + ".osm", file_path + ".json")
#print data