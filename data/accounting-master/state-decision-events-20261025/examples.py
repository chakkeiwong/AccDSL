"""Authored stock/reserve policy; not estimated demand or historical evidence."""
from copy import deepcopy
from functools import lru_cache
from fractions import Fraction
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'scripts'))
import state_decision_events_v1 as decision

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

native = load('state_decision_inventory_examples', ROOT/'data/accounting-master/annual-inventory-composition-20261025/examples.py')
expressions = load('state_decision_function_examples', ROOT/'data/accounting-master/company-functions-20261025/examples.py')

@lru_cache(maxsize=1)
def saved_start(): return native.start()

def start(): return deepcopy(saved_start())

def policy(state):
    e = expressions; t = decision.types(state); quantity = t['units']; money = t['cash']
    price = {'kind': 'number', 'dimensions': {state['after']['context']['currency']: 1, 'unit': -1}, 'context': quantity['context']}
    minimum = e.function('minimum', [('left', quantity), ('right', quantity)],
        [e.param('a','left'), e.param('b','right'), e.node('choose','le','a','b'), e.node('r','if','choose','a','b')], 'r', quantity)
    inputs = {key: {'type': deepcopy(typ), 'value': 'unknown'} for key, typ in
              [('stock',quantity),('reserve',quantity),('demand',quantity),('price',price),('enabled',t['boolean'])]}
    nodes = [{'id': key, 'op': 'input', 'target': key} for key in inputs]
    nodes += [e.literal('zero','0/1',quantity), e.node('surplus','sub','stock','reserve'),
              e.node('has_surplus','lt','zero','surplus'), e.node('capacity','if','has_surplus','surplus','zero'),
              e.call('units','minimum','capacity','demand'), e.node('positive','lt','zero','units'),
              e.literal('disabled',False,e.BOOL), e.node('act','if','enabled','positive','disabled'),
              e.node('proceeds','mul','units','price')]
    return e.program(nodes, [minimum], inputs, {'execute':'act','sold_units':'units','proceeds':'proceeds'})

def request(state, ident='decision-1', date='2027-01-02', demand='3/2', reserve='1/2', price='15/1', enabled=True):
    for name, value in [('demand',demand),('reserve',reserve),('price',price)]:
        if value != 'unknown' and Fraction(value) < 0:
            raise ValueError('negative_example_assumption:' + name)
    program = policy(state)
    values = {'reserve':reserve,'demand':demand,'price':price,'enabled':enabled}
    bindings = {'stock':{'kind':'state_lot_units','lot_id':'recovered'}}
    for name, value in values.items():
        bindings[name] = {'kind':'scenario','type':deepcopy(program['inputs'][name]['type']),
                          'value':value,'available_on':'2027-01-01',
                          'provenance':'Explicit synthetic decision assumption; no fitted or historical claim'}
    sale = native.sale(ident+'-sale', day=date)['event']
    event = {k:deepcopy(sale[k]) for k in ['id','date','method','lot_id','findings']}
    return {'profile':decision.PROFILE,'id':ident,'expected_state_sha256':decision.digest(state),
            'context':deepcopy(state['after']['context']),'decision_date':date,
            'scenario':{'kind':'authored_closed_path','premise':'Only the supplied dated decisions occur after this snapshot; no omitted intervening event.'},
            'model':{'program':program,'available_on':'2027-01-01','provenance':'Authored stock/reserve example; nonnegative demand, reserve and price premises'},
            'bindings':bindings,'output_map':{'execute':'execute','sold_units':'sold_units','proceeds':'proceeds'},'event':event}

def repeated():
    state = start()
    first = request(state, demand='1/1')
    one = decision.apply(state, first, decision.propose(state, first))
    assert one['status'] == 'applied_provisional', one
    second = request(one['after'], 'decision-2', '2027-01-03', demand='1/1')
    two = decision.apply(one['after'], second, decision.propose(one['after'], second))
    assert two['status'] == 'applied_provisional', two
    third = request(two['after'], 'decision-3', '2027-01-04', demand='1/1')
    return [first,second,third]
