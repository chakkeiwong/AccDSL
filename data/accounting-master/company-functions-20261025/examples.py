"""Authored functions matching the frozen collection-policy illustration."""
from copy import deepcopy

SCALAR = {'kind':'number','dimensions':{},'context':None}
BOOL = {'kind':'boolean'}

def literal(ident, value, typ=SCALAR):
    return {'id':ident,'op':'literal','type':deepcopy(typ),'value':value}

def node(ident, op, *args): return {'id':ident,'op':op,'args':list(args)}
def param(ident, target): return {'id':ident,'op':'param','target':target}
def call(ident, function, *args):
    return {'id':ident,'op':'call','function':function,'args':list(args)}

def function(name, parameters, nodes, output, return_type=SCALAR):
    return {'name':name,'parameters':[{'name':k,'type':deepcopy(t)} for k,t in parameters],
            'return_type':deepcopy(return_type),'nodes':nodes,'output':output}

def program(nodes, functions=None, inputs=None, outputs=None):
    return {'profile':'CompanyFunctions/1','name':'Authored policy example',
            'inputs':inputs or {},'functions':functions or [],'nodes':nodes,
            'outputs':outputs or {'result':'r'}}

def identity(typ=SCALAR):
    return function('identity',[('x',typ)],[param('r','x')],'r',typ)

def policy_program():
    complement = function('complement',[('discount',SCALAR)],
        [param('d','discount'),literal('one','1/1'),node('r','sub','one','d')],'r')
    choose = function('choose',[('guard',BOOL),('ordinary',SCALAR),('stress',SCALAR)],
        [param('g','guard'),param('a','ordinary'),param('b','stress'),node('r','if','g','a','b')],'r')
    half = function('half',[],[literal('one','1/1'),literal('two','2/1'),node('r','div','one','two')],'r')
    return program([
        {'id':'ordinary','op':'input','target':'ordinary'},
        {'id':'discount','op':'input','target':'discount'},literal('stress','4/5'),
        call('regular','complement','discount'),call('fraction','choose','ordinary','regular','stress'),
        call('half','half')], [complement,choose,half],
        {'ordinary':{'type':deepcopy(BOOL),'value':True},'discount':{'type':deepcopy(SCALAR),'value':'1/10'}},
        {'fraction':'fraction','first_share':'half','second_share':'half'})

def call_chain(length):
    functions = [identity()]
    previous = 'identity'
    for i in range(1,length):
        ident = 'f'+str(i)
        functions.append(function(ident,[('x',SCALAR)],
                         [param('x','x'),call('r',previous,'x')],'r'))
        previous = ident
    return program([literal('a','3/7'),call('r',previous,'a')],functions)
