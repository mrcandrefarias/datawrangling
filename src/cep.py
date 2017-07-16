#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sets import Set
import re
def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db     = client['bh-osm']
    return db

def is_formato_cep_invalido(cep):
    cep_regex = re.match(r'^\d{5}-\d{3}$', cep)
    if None == cep_regex:
        return True
    return False

def format_cep(cep):
    '''
        Retira qualquer caracter da string cep que não seja número.
        Apenas os números são mantidos na nova string cep, que é formada.
    '''
    cep = re.sub('[^0-9]', '', cep)
    #Verificando quantos caracteres faltam para completar oito dígitos
    caracteres_faltando = 8 - len(cep)
    cep = '{}{}{}'.format(cep[0:5],'-', cep[5:] + '0' * caracteres_faltando)
    print cep

def verificaEnderecos():
    db           = get_db()
    enderecos    = db.bh.find( {'address':{'$exists':1}}, {"address":1, "_id":1} )
    for endereco in enderecos:
        clean = False
        if 'postcode' in endereco['address']:
            if( is_formato_cep_invalido (endereco['address']['postcode']) ) :
                print "CEP invalido:" + endereco['address']['postcode']
                endereco['address']['postcode'] = format_cep( endereco['address']['postcode'] )
                clean = True
        if(clean)
            print "Limpando endereço:" + endereco
            db.bh.save(endereco)
    #print address
