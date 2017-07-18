#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sets import Set
import re
import string 
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
    
    #cep possui 8 digitos apenas adiciona o '-'
    if caracteres_faltando == 0:
         cep = '{}{}{}'.format( cep[0:5], '-', cep[5:] )
    #cep possui menos que 8 digitos, adiciona o '-' e zeros no final
    if caracteres_faltando > 0:
        cep = '{}{}{}'.format( cep[0:5], '-', cep[5:] + '0' * caracteres_faltando)
    #cep possui mais que 8 digitos, adiciona o '-' e elimina caracteres adicionais
    if caracteres_faltando < 0:
        cep = '{}{}{}'.format( cep[0:5], '-', cep[5:8] )
    
    return cep

def verifica_logradouro_invalido(logradouro):
    if logradouro[0].isupper():
        return
        
    print logradouro
    '''
        Realiza a verificação dos logradouros.
        Args:
            logradouro (string): O logradouro a ser Verificado.
        Returns:
            logradouro(string) ou None: Retorna o logradouro no novo formato, pra ser atualizado,
            None caso o logradouro esteja correto.
    '''
        
    logradouro_mapping = { "Av": "Avenida", "Av.": "Avenida", "R": "Rua", "R.": "Rua", "PR.": u"Praça"}
    
    #Compila a expressão regular "^\S+\.?". Incio da string até algum espaço ou ponto "."
    logradouro_regex = re.compile(r'^\S+\.?',re.IGNORECASE)

    # Faz uma varredura através do string logradouro procurando a primeira parte da string logradouro
    # que bate com o padrão, parte inicial do logradouro até algum espaço ou ponto.
    match  = logradouro_regex.search(logradouro)
    if match:
        nome_inicial = match.group(0)
        nome_inicial = nome_inicial[0].upper() + nome_inicial[1:]
        if nome_inicial in logradouro_mapping.keys():
            print "logradouro invalido:" + logradouro
            return re.sub(logradouro_regex, logradouro_mapping[nome_inicial], logradouro)
        else:
            if not logradouro[0].isupper():
                print "Nome de logradouro iniciado com letra minúscula:" , logradouro
                # Coloca a primeira letra em maisculo, evitando que os nomes dos logradouros iniciem com letra minuscula.
                return logradouro[0].upper() + logradouro[1:]
            else:
                return None
    else:
        print "logradouro invalido fora dos padroes:" + logradouro
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
                endereco['address']['postcode']      = format_cep_invalido( endereco['address']['postcode'] )
                endereco_verificados['cep_invalido'] += 1
                clean                                = True
            else:
                endereco_verificados['cep_valido'] += 1

        # realiza a limpeza dos logradouros (street). Verifica se existe a chave street.
        # Nem todos os endereços foram preenchidos com o nome do logradouro
        if 'street' in endereco['address']:
            logradouro_invalido = verifica_logradouro_invalido(endereco['address']['street'])
            if logradouro_invalido is not None:
                endereco['address']['street']                = logradouro_invalido
                endereco_verificados['logradouro_invalido'] += 1
                clean                                       = True
            else:
                endereco_verificados['logradouro_valido'] += 1
        
        # Caso Exista alguma informação no endereco que deve ser limpa.
        if(clean):
            #print ("Limpando endereço:", endereco)
            #executa a atualização das informações do endereço no banco de dados
            db.bh.save(endereco)
            
    return endereco_verificados

def verifica_nome_belo_horizonte(db):
    '''
        Realiza a verificação do nome da cidade de Belo Horizonte. 
        Existem erros de digitação no nome da cidade e nomeclaturas diferentes para a cidade (bh, Belo Horizonte MG Brazil e etc)
        Args:
            db (MongoClient): Conexão à base de dados bh-osm.
        Returns:
             dictionary - contendo um sumário das informações verificadas.
             exemplo: { 'nome_valido': 100, 'nome_invalido': 20}
    '''
    # nome iniciado com BH
    regx1    = re.compile("^bh", re.IGNORECASE)
    # Nome iniciado com belo
    regx2    = re.compile("^belo", re.IGNORECASE)
    # Procura as incidencias da cidade de Belo Horizonte, baseado nos padrões acima.
    nomes_bh = db.bh.find(  {"$or":[ {"address.city": regx1}, {"address.city": regx2 } ] }, {"address.city":1, "_id":1} )
    retorno  = { 'nome_valido': 0, 'nome_invalido': 0}
    for nome in nomes_bh:
        # Nome da cidade diferente do valor Correto
        if nome['address']['city'] != 'Belo Horizonte':
            nome['address']['city'] = 'Belo Horizonte'
            # Atualiza o nome da cidade
            db.bh.save(nome)
            retorno['nome_invalido'] += 1
        else:
            retorno['nome_valido'] += 1
    return retorno

def exclui_cidades_diferentes(db):
    '''
        Realiza a exclusao das cidades diferentes de Belo Horizonte. 
        Args:
            db (MongoClient): Conexão à base de dados bh-osm.
    '''
   
    nomes_cidades  = db.bh.find(  { "address.city":{"$exists":1} }, {"address.city":1, "_id":1} )
    for nome in nomes_cidades:
        # Cidade diferente de Belo Horizonte
        if nome['address']['city'] != 'Belo Horizonte':
            rs = db.bh.delete_one( { "_id" : nome['_id'] })
            
db = get_db()
endereco_verificados = verificaEnderecos(db)
print endereco_verificados

nomes_bh = verifica_nome_belo_horizonte(db)
print nomes_bh

exclui_cidades_diferentes(db)
