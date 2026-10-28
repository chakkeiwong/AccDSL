"""Explicit synthetic gross-equity histories using unchanged declared execution."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'data/accounting-master/literature-closure-20261026/runtime-integration.py'
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('retained_equity_factory', SOURCE)
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
program, h, native = base.program, base.h, base.native
fmt, ref, binary, constant = h.fmt, h.ref, h.binary, h.constant


def make(history, owner='alpha'):
    if history not in ['issue_only', 'issue_and_retire']:
        raise ValueError('explicit original history required')
    body, mapping = base.make('floating', owner)
    book = body['opening']
    book['balances'] = {account: '0/1' for account in book['balances']}
    book['balances'].update({mapping['cash']: '10/1', mapping['capital']: '-10/1'})
    book['memory']['terms'].update(face='0/1', old_shares='100/1', new_shares='0/1',
                                  coupon='0/1', covenant_cash='0/1', stage='3/1')
    entries = {'equity_issue': deepcopy(body['registry']['entries']['equity_issue'])}
    # New immutable method data, not an existing repurchase library operation.
    retire = deepcopy(entries['equity_issue']); method = retire['method']
    identity = 'gross-equity.synthetic.retire-new-ordinary'
    method['id'] = identity
    for key in ['preconditions', 'postconditions']:
        method[key]['manifest']['method_id'] = identity
    money = program.engine.money_type(book)
    shares = retire['event_inputs']['shares']
    unit = book['memory_types']['/terms/stage']
    for key, stage in [('preconditions', 4), ('postconditions', 5)]:
        for row in method[key]['manifest']['requirements']:
            if row['id'] in ['correct_stage', 'stage_advanced']:
                row['predicate'] = binary('eq', ref('stage'), constant(unit, fmt(stage)))
    pre = method['preconditions']
    pre['manifest']['inputs']['existing_new'] = h.declaration(shares, 'existing_new')
    pre['bindings']['existing_new'] = h.memory('/terms/new_shares')
    pre['manifest']['requirements'].append(dict(id='available_new_shares',
        guard=constant(program.core.BOOL, True), guard_requires=[],
        predicate=binary('le', ref('shares'), ref('existing_new')),
        requires=['shares', 'existing_new'], admission_refs=[],
        on_false='invalid', on_unknown='unresolved'))
    monetary = method['monetary']['definition']; monetary['method_id'] = identity
    amount = binary('mul', ref('shares'), ref('price'))
    negative = binary('sub', constant(money, '0/1'), deepcopy(amount))
    for row in monetary['postings']:
        row['expression'] = deepcopy(negative if row['account'] == 'cash' else amount)
    for row in monetary['flows']:
        row['expression'] = deepcopy(negative); row['origin'] = 'equity_retire'
    monetary['calculations'][0]['expression'] = binary('sub', ref('existing_new'), ref('shares'))
    for row in method['memory']['definition']['operations']:
        if row['id'] == 'advance': row['value']['value'] = '5/1'
    method['residual_prerequisites'] = [
        'Authored retirement of newly issued homogeneous ordinary shares only.',
        'Repurchase cost reduces the one synthetic equity account; no par/treasury/retained-earnings allocation.',
        'No fees, tax, voting/ownership rights, source, legal authority or accounting-treatment admission.']
    retire['method_sha256'] = program.digest(method)
    entries['equity_retire'] = retire
    body['registry']['entries'] = entries
    body['name'] = 'original-SIM-F006-' + history + '-' + owner
    transactions = [('equity_issue', '2027-01-05', 20, 3)] if history == 'issue_only' else [
        ('equity_issue', '2027-01-05', 30, 4), ('equity_retire', '2027-01-06', 10, 6)]
    commands, movements = [], []
    for kind, day, count, price in transactions:
        inputs = {key: dict(type=deepcopy(entries[kind]['event_inputs'][key]),
            value=program.engine.known(fmt(value)), provenance='Original synthetic SIM-F006 terms')
            for key, value in [('shares', count), ('price', price)]}
        commands.append(dict(kind='event', method_key=kind,
                             event=dict(id=kind, date=day, inputs=inputs)))
        movement = count*price*(1 if kind == 'equity_issue' else -1)
        movements.append(dict(id='movement.'+kind,event_id=kind,date=day,
            account=mapping['capital'],amount=fmt(movement),description='Synthetic gross ordinary equity cash'))
    commands.append(dict(kind='report',id='closing',cutoff='2027-01-07',equity_movements=movements,
        notes=[dict(id='authority',label='Synthetic share retirement',status='unresolved',
                    reason='Rights, legal authority and accounting treatment require separate admission')]))
    body['commands'] = commands
    return body, mapping


def select_histories(rows, note=None, cutoff=None):
    """Finite exact hard-evidence diagnostic; not a filing extractor or probability model."""
    if note is None:
        return dict(status='conditional_family', ids=list(rows), applied=False)
    required = {'gross_issue_cash', 'retirement_cash', 'available_at'}
    if set(note) != required:
        return dict(status='invalid', ids=[], applied=False)
    if note['available_at'] is None or cutoff is None:
        return dict(status='unresolved_availability', ids=list(rows), applied=False)
    if type(note['available_at']) is not int or type(cutoff) is not int:
        return dict(status='invalid', ids=[], applied=False)
    if note['available_at'] > cutoff:
        return dict(status='conditional_family', ids=list(rows), applied=False)
    if note['gross_issue_cash'] is None or note['retirement_cash'] is None:
        return dict(status='unresolved_amount', ids=list(rows), applied=False)
    try:
        quantities = []
        for key in ['gross_issue_cash', 'retirement_cash']:
            if isinstance(note[key], (float, bool)): raise ValueError('exact input required')
            value = Q(note[key])
            if value < 0: raise ValueError('gross positive magnitudes required')
            quantities.append(value)
    except (ValueError, TypeError, ZeroDivisionError):
        return dict(status='invalid', ids=[], applied=False)
    ids = [key for key, row in rows.items() if [Q(row['gross_issue_cash']), Q(row['retirement_cash'])] == quantities]
    return dict(status='conditional_family' if ids else 'conflict', ids=ids, applied=True)

