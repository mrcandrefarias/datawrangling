#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import codecs
import json

def parser_subtag(element, documento):
    '''
        Realiza o parseamento das subtags dentro do elemento xml  
        Args:
            element (xml.etree.ElementTree.Element): Objeto XML.
            documento (dictionary): Documento contendo informações do mapa, previamente parseados. 
        Returns:
             dictionary - Documento contendo as informações do mapa, enriquecido com informações de endereco e outros recursos do mapa
             exemplo: {'changeset': '46708443', 'amenity': 'restaurant', 'uid': '2336678', 'source': 'survey', 
             'timestamp': '2017-03-09T12:38:53Z', 'lon': '-43.9570401', 'phone': '+55 31 3441-4455', 'version': '2', 
             'user': 'Gilmar Ferreira', 'address': {'street': u'Rua Professor J\xe9rson Martins', 'housenumber': '146'}, 
             'lat': '-19.8557650', 'type': 'node', 'id': '2311902994', 'name': 'La Palma'}
    '''
    address = {}
    for subtag in element:
        if subtag.tag == 'tag': 
            if subtag.get('k').startswith('addr:'):
                address[subtag.get('k')[5:]] = subtag.get('v')
            else:
                documento[subtag.get('k')] = subtag.get('v') 
                
    #verifica se o dictionary adress não está vazio 
    if len(address) > 0:
        documento['address'] = address
                
    return documento
    
def parser_element(element):
    '''
        Realiza o parseamento do elemento xml  
        Args:
            element (xml.etree.ElementTree.Element): Objeto XML.
        Returns:
             dictionary - Documento contendo as informações do mapa.
             exemplo: {'changeset': '2196289', 'uid': '72239', 'timestamp': '2009-08-19T01:51:35Z', 'lon': '-44.0454339', 
             'version': '1', 'user': 'Samuel Vale', 'lat': '-19.9276840', 'type': 'node', 'id': '470748241'
    '''
    documento = {}
    if element.tag == "node" or element.tag == "way" :
        for e in element.attrib.keys():    
            documento[e]      = element.get(e)
            documento['type'] = element.tag
         
        return parser_subtag(element, documento)
    else:
        return None

def xml_to_json(arquivo_entrada, arquivo_saida):
    '''
        Converte o arquivo_entrada com os dados do OpenStreetMap no formato xml 
        para json e gera o arquivo_saida com os dados do OpenStreetMap nesse novo formato. 
        Args:
            arquivo_entrada (string): O caminho do arquivo de entrada, com os dados do OpenStreetMap no formato xml.
            arquivo_saida (string): O caminho do arquivo de saida, que receberá os dados no formato json.
    '''
    with codecs.open(arquivo_saida, "w") as saida:
        for _, element in ET.iterparse(arquivo_entrada):
            element_json = parser_element(element)
            if element_json:
                # Escreve os dados no arquivo de saida      
                saida.write( json.dumps(element_json) + "\n")
                
file_path  = "../data/bh"
xml_to_json( file_path + ".osm", file_path + ".json")