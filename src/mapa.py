#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


def getAdress(subtag, address_type):
    if address_type == 'street':
        logradouro = subtag.get('v')
        logradouro_mapping = { "Av":"Avenida", "Av.":"Avenida", "R":"Rua", "R.":"Rua",  "rua":"Rua",
                           "r.":"Rua", "r":"Rua", "Pr.":u"Praça", "PR.":u"Praça"}
                           
        #Compila a expressão regular "^\S+\.?". Incio da string até algum espaço ou ponto "."
        logradouro_regex = re.compile(r'^\S+\.?',re.IGNORECASE)
    
        # Faz uma varredura através do string logradouro procurando a primeira parte da string logradouro 
        # que bate com o padrão, parte inicial do logradouro até algum espaço ou ponto.
        match  = logradouro_regex.search(logradouro)
        if match:
            nome_inicial = match.group(0)
            if nome_inicial in logradouro_mapping.keys():
                logradouro = re.sub(logradouro_regex, logradouro_mapping[nome_inicial], logradouro)
          
        return logradouro
    else:
        return subtag.get('v')
        
def parser_subtag(element, node):
    address = {}
    for subtag in element:
        if subtag.tag == 'tag': 
            if subtag.get('k').startswith('addr:'):
                address_type = subtag.get('k')[5:]
                address[address_type] = getAdress( subtag, address_type )
            else:
                node[subtag.get('k')] = subtag.get('v') 
        
    if len(address) > 0:
        node['address'] = address
        
    return node
    
def shape_element(element):
    node = {}
    
    if element.tag == "node" or element.tag == "way" :
        for e in element.attrib.keys():    
            node[e]      = element.get(e)
            node['type'] = element.tag
            
        return parser_subtag(element, node)
    else:
        return None

def process(file):   
    data = []
    for _, element in ET.iterparse(file):
            el = shape_element(element)
            if el:
                data.append(el)
                
    return data
    

file_path  = "../data/bhmicro"
data = process( file_path + ".osm")
print data