"""Supplied synthetic measurement and cash-category discriminators; no tax law."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
SOURCE = ROOT / 'data/accounting-master/declared-financing-clock-20261025/examples.py'
spec = importlib.util.spec_from_file_location('measurement_financing_fixture', SOURCE)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
program, f = ex.program, ex.financing
engine, core = f.engine, f.core
ref, binary, constant = f.ref, f.binary, f.constant
fmt = f.fmt


def report(ident='measurement.report', day='2027-12-31'):
    return dict(kind='report', id=ident, cutoff=day, equity_movements=[], notes=[
        dict(id='measurement.premise', label='Supplied synthetic measurement',
             status='unresolved', reason='No source, recognition, tax-law or valuation admission')])


def make(owner='alpha', target='4/1', expected='10/1', carry=False):
    body, _, _, mapping = ex.fixture(owner)
    book = body['opening']
    for name, classification in [('dta', 'asset'), ('dtl', 'liability'), ('deferred_tax', 'expense')]:
        mapping[name] = name if owner == 'alpha' else 'measurement_' + name
        book['accounts'][mapping[name]] = dict(classification=classification)
        body['mapping']['lines'].append(dict(id=name, label=name,
            classification=classification, accounts=[mapping[name]]))
    book['balances'] = {key: '0/1' for key in book['accounts']}
    book['balances'].update({mapping['cash']: '20/1', mapping['dta']: '10/1',
                             mapping['dtl']: '-4/1', mapping['capital']: '-26/1'})
    shape = deepcopy(body['schemas'][book['memory_schema']])
    shape['properties']['tax_rights'] = f.record({'legal_loss': f.scalar('rational'),
                                                  'authority': f.scalar('text')})
    shape['required'].append('tax_rights')
    book['memory_schema'] = program.digest(shape)
    book['memory']['tax_rights'] = dict(legal_loss='40/1', authority='synthetic-right-premise')
    money = engine.money_type(book)
    book['memory_types']['/tax_rights/legal_loss'] = deepcopy(money)
    book['memory_types']['/tax_rights/authority'] = dict(kind='text', context={})
    schemas = {program.digest(shape): shape}
    identity = 'synthetic.dta.remeasurement'
    zero = constant(money, '0/1')
    pre_types = dict(approved=core.BOOL, dta=money, expected=money, target=money)
    pre_bindings = dict(approved=f.event('approved'), dta=f.account('dta'),
                        expected=f.event('expected'), target=f.event('target'))
    pre_rows = [
        ('applicable', ref('approved'), ['approved'], 'unsupported'),
        ('opening_measurement', binary('eq', ref('dta'), ref('expected')), ['dta', 'expected'], 'invalid'),
        ('nonnegative_target', binary('le', deepcopy(zero), ref('target')), ['target'], 'invalid'),
        ('reduction_scope', binary('le', ref('target'), ref('dta')), ['target', 'dta'], 'unsupported')]
    post_types = dict(dta=money, target=money, legal_loss=money)
    post_bindings = dict(dta=f.account('dta'), target=f.event('target'),
                         legal_loss=f.memory('/tax_rights/legal_loss'))
    post_rows = [
        ('measured_asset', binary('eq', ref('dta'), ref('target')), ['dta', 'target'], 'invalid'),
        ('legal_right_unchanged', binary('eq', ref('legal_loss'), constant(money, '40/1')), ['legal_loss'], 'invalid')]
    empty = f.record({})
    schemas[program.digest(empty)] = empty
    delta = binary('sub', ref('old'), ref('target'))
    roles = ['cash', 'dta', 'deferred_tax']
    monetary = dict(profile=engine.monetary.PROFILE, method_id=identity, version='1',
        inputs={k: f.declaration(money, k) for k in ['old', 'target']}, calculations=[],
        accounts={k: deepcopy(money) for k in roles}, cash_account='cash',
        postings=[dict(id='remeasure', account='dta', expression=binary('sub', deepcopy(zero), deepcopy(delta)), requires=['old', 'target']),
                  dict(id='expense', account='deferred_tax', expression=deepcopy(delta), requires=['old', 'target'])], flows=[])
    method = dict(profile=engine.METHOD, id=identity, version='1', context=deepcopy(book['context']),
        account_map={k: mapping[k] for k in roles},
        preconditions=dict(manifest=f.conditions(identity, pre_types, pre_rows), bindings=pre_bindings),
        postconditions=dict(manifest=f.conditions(identity, post_types, post_rows), bindings=post_bindings),
        monetary=dict(definition=monetary, bindings=dict(old=f.account('dta'), target=f.event('target'))),
        memory=dict(definition=dict(profile=engine.memory.PROFILE, state_schema=book['memory_schema'],
                                    input_schema=program.digest(empty), operations=[]), input_bindings={}),
        residual_prerequisites=['Supplied synthetic expense treatment and revised measurement; no legal tax rights change or settlement'])
    entry = dict(method_sha256=program.digest(method), method=method, schemas=deepcopy(schemas),
        account_classes=dict(cash='asset', dta='asset', deferred_tax='expense'),
        event_inputs=dict(approved=deepcopy(core.BOOL), expected=deepcopy(money), target=deepcopy(money)),
        metadata_bindings={}, clock=dict(kind='direct_event_date'))
    body['schemas'] = schemas
    body['registry']['entries'] = {'remeasure': entry}
    body['name'] = 'measurement-cash-' + owner
    body['commands'] = [ex.event(body, 'remeasure', 'remeasure.1', '2027-12-31',
                                  dict(expected=expected, target=target)), report()]
    if carry:
        close = {**report('close.2027'), 'kind': 'carry', 'retained_account': mapping['retained'],
                 'next_end_exclusive': '2029-01-01', 'memory_policies': {
                     key: dict(kind='preserve', provenance='Remeasurement changes no legal right or other memory')
                     for key in book['memory_types']}}
        body['commands'] += [close, report('opening.2028', '2028-01-01')]
    return body, mapping


def rehash(body):
    for entry in body['registry']['entries'].values():
        entry['method_sha256'] = program.digest(entry['method'])


def false_cash(body):
    method = body['registry']['entries']['remeasure']['method']
    monetary = method['monetary']['definition']
    debit = monetary['postings'][1]
    debit['account'] = 'cash'
    monetary['flows'] = [dict(id='invented.receipt', activity='operating', origin='remeasurement',
                              expression=deepcopy(debit['expression']), requires=deepcopy(debit['requires']))]
    rehash(body)


def false_right(body, weaken=False):
    method = body['registry']['entries']['remeasure']['method']
    method['memory']['definition']['operations'] = [dict(id='wrong.right', op='replace',
        path=['tax_rights', 'legal_loss'], value=dict(kind='literal', value='0/1'))]
    if weaken:
        row = method['postconditions']['manifest']['requirements'][1]
        row['predicate'] = binary('le', constant(engine.money_type(body['opening']), '0/1'), ref('legal_loss'))
    rehash(body)


def financing(owner='alpha', wrong_category=False):
    body, _, _, mapping = ex.fixture(owner)
    book = body['opening']
    book['balances'] = {key: '0/1' for key in book['balances']}
    book['balances'][mapping['cash']] = '20/1'
    book['balances'][mapping['capital']] = '-20/1'
    body['registry']['entries'] = {k: v for k, v in body['registry']['entries'].items()
                                   if k in ['debt_issue', 'debt_redeem']}
    if wrong_category:
        for entry in body['registry']['entries'].values():
            entry['method']['monetary']['definition']['flows'][0]['activity'] = 'operating'
        rehash(body)
    body['commands'] = [ex.event(body, 'debt_issue', 'borrow', '2027-01-01', dict(amount='100/1')),
                        ex.event(body, 'debt_redeem', 'repay', '2027-01-01', dict(amount='40/1')),
                        report('finance.report')]
    return body, mapping
