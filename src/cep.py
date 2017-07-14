#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sets import Set
import re
def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db     = client['bh-osm']
    return db

db           = get_db()
enderecos    = db.bh.find( {'address':{'$exists':1}}, {"address":1, "_id":1} )
nomes_cidade = Set()

def is_formato_cep_invalido(cep):
    cep_regex = re.match(r'^\d{5}-\d{3}$', cep)
    if None == cep_regex:
        return True
    return False
        
for endereco in enderecos:
    if 'postcode' in endereco['address']:
        if( is_formato_cep_invalido (endereco['address']['postcode']) ) :
            print endereco['address']['postcode']
        else:
            print endereco['address']['postcode'] + ":"
        
        #db.bh.save(endereco)
    #print address
    
#print nomes_cidade