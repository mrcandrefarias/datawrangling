#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sets import Set
import re
def get_db():
    '''
        Conecta-se ao MongoDB.
        Returns:
            Conexão à base de dados bh-osm (MongoClient)
    '''
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db     = client['bh-osm']
    return db

def is_formato_cep_invalido(cep):
    '''
       Verifica se o cep possui formato ivalido.
       Args:
          cep (string): O cep a ser Verificado.
       Returns:
          boolean - Retorna True se invalido e False se invalido
    '''
    cep_regex = re.match(r'^\d{5}-\d{3}$', cep)
    if None == cep_regex:
        print "CEP invalido:" + cep
        return True
    return False


def format_cep_invalido(cep_invalido):
    '''
        Realiza a formatação dos cep inválidos. Elimina caracteres não númericos,
        adiciona o dígito que separa os últimos três números e completa com zero no final, caso
        a string cep possua menos que 8 caracteres.
        Args:
            cep_invalido (string): O cep a ser formatado.
        Returns:
            cep(string): Retorna o cep no novo formato
    '''

    #Retira qualquer caracter da string cep que não seja número.
    cep = re.sub('[^0-9]', '', cep_invalido)
    #Verificando quantos caracteres faltam para completar oito dígitos
    caracteres_faltando = 8 - len(cep)
    cep = '{}{}{}'.format( cep[0:5], '-', cep[5:] + '0' * caracteres_faltando)
    return cep

def verifica_logradouro_invalido(logradouro):
    '''
        Realiza a verificação dos logradouros.
        Args:
            logradouro (string): O logradouro a ser Verificado.
        Returns:
            logradouro(string) ou None: Retorna o logradouro no novo formato, pra ser atualizado,
            None caso o logradouro esteja correto.
    '''
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
            return re.sub(logradouro_regex, logradouro_mapping[nome_inicial], logradouro)
        else
         return None
     else:
         return None

def verificaEnderecos(db):
    '''
        Realiza a verificação da informações dos endereços da região metropolitana de BH,
        armazenadas no MongoDB. As informações com erros, são corrigidas e atualizadas no banco de dados.
        Args:
            db (MongoClient): Conexão à base de dados bh-osm.
        Returns:
             dictionary - contendo um sumário das informações verificadas.
             exemplo: { 'cep_valido': 100, 'cep_invalido': 20}
        '''
    enderecos            = db.bh.find( {'address':{'$exists':1}}, {"address":1, "_id":1} )
    endereco_verificados = { 'cep_valido':0, 'cep_invalido':0, 'logradouro_valido':0, 'logradouro_invalido':0}
    for endereco in enderecos:
        clean = False

        # realiza a limpeza dos cep (postcode). Verifica se existe a chave postcode.
        # Nem todos os endereços foram preenchidos com cep
        if 'postcode' in endereco['address']:
            if is_formato_cep_invalido (endereco['address']['postcode']):
                endereco['address']['postcode'] = format_cep( endereco['address']['postcode'] )
                endereco_verificados['cep_invalido'] += 1
                clean = True
            else:
                endereco_verificados['cep_valido'] += 1

        # realiza a limpeza dos logradouros (street). Verifica se existe a chave street.
        # Nem todos os endereços foram preenchidos com o nome do logradouro
        if 'street' in endereco['street']:
            logradouro_invalido = verifica_logradouro_invalido(endereco['street'])
            if logradouro_invalido is not None:
                endereco['address']['postcode'] = logradouro_invalido
                endereco_verificados['logradouro_invalido'] += 1
                clean = True
            else:
                endereco_verificados['logradouro_valido'] += 1
        '''
            Existindo alguma informação no endereco que deve ser limpa,
            executa a atualização das informações do endereço no banco de dados
        '''
        if(clean):
            print "Limpando endereço:" + endereco
            db.bh.save(endereco)

#db = get_db()
#endereco_verificados = verificaEnderecos(db)
#print endereco_verificados

format_cep_invalido("000000-000")
