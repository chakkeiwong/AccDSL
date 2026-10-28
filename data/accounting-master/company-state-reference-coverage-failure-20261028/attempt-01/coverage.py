"""Fixture-specific coverage guard; no automatic source or covenant admission."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
BASELINE_SHA = '498d83f53560bb470408f52d932ccd4b804b0c82329bd797442e8ae92b2fb42c'
BASE = json.loads((H / 'fixture-baseline.json').read_text())
REF = 'synthetic.note.covenant'
PROFILE = 'SyntheticReferenceCoverage/1'
p = ROOT / 'data/accounting-master/company-state-borrowing-recognition-failure-20261028/fixture.py'
s = importlib.util.spec_from_file_location('reference_borrowing_fixture', p)
f = importlib.util.module_from_spec(s)
s.loader.exec_module(f)
program, financing = f.program, f.financing

def need(value, reason):
    if not value: raise ValueError(reason)

def closed(value, keys, reason):
    need(type(value) is dict and set(value) == set(keys), reason)

def protect():
    need(sha256((H / 'fixture-baseline.json').read_bytes()).hexdigest() == BASELINE_SHA, 'baseline_identity')
    for name, value in BASE['files'].items():
        need(sha256((H / 'sources' / name).read_bytes()).hexdigest() == value, 'source_identity:' + name)

def make_program(owner, amounts, include_covenant=True):
    need(owner in ['alpha', 'beta'], 'owner')
    need(type(amounts) is list and 1 <= len(amounts) <= 4, 'bounded_amounts')
    need(all(type(x) is str and f.fmt(Q(x)) == x and Q(x) >= 0 for x in amounts), 'canonical_amounts')
    body, mapping = f.make(owner)
    body['registry']['entries'] = {'debt_issue': body['registry']['entries']['debt_issue']}
    entry = body['registry']['entries']['debt_issue']
    if include_covenant:
        pre = entry['method']['preconditions']['manifest']
        money = program.engine.money_type(body['opening'])
        # Debt is stored as a credit-negative balance. Amount - debt is total principal after issue.
        predicate = financing.binary('le', financing.binary('sub', financing.ref('amount'), financing.ref('debt')),
                                     financing.constant(money, BASE['interpretation']['total_principal_after_borrowing_max']))
        pre['requirements'].append(dict(id='incorporated_principal_ceiling',
            guard=financing.constant(financing.core.BOOL, True), guard_requires=[],
            predicate=predicate, requires=['amount', 'debt'], admission_refs=[],
            on_false='invalid', on_unknown='unresolved'))
        entry['method']['residual_prerequisites'].append('Authored synthetic scanned covenant only; no actual contract admission.')
        entry['method_sha256'] = program.digest(entry['method'])
    body['commands'] = [f.ex.event(body, 'debt_issue', 'borrow.' + str(i+1), '2027-01-01', {'amount': amount})
                        for i, amount in enumerate(amounts)]
    body['commands'].append(dict(kind='report', id='after.borrow', cutoff='2027-01-01', equity_movements=[],
        notes=[dict(id='synthetic_note', label='Synthetic incorporated covenant', status='unresolved',
                    reason='Bound fixture only; actual source/legal/accounting admission remains absent')]))
    return body, mapping

def request(owner='alpha', amounts=None, stage='modeled'):
    amounts = ['100/1'] if amounts is None else amounts
    body, _ = make_program(owner, amounts)
    record = dict(retrieval=None, parsing=None, modeling=None)
    if stage in ['retrieved', 'parsed', 'modeled']:
        record['retrieval'] = dict(path='sources/covenant-scan.pdf', sha256=BASE['files']['covenant-scan.pdf'])
    if stage in ['parsed', 'modeled']:
        record['parsing'] = dict(method='author_visual_transcription',
            text=(H / 'sources/transcription.txt').read_text(), sha256=BASE['files']['transcription.txt'])
    if stage == 'modeled':
        record['modeling'] = dict(interpretation=deepcopy(BASE['interpretation']),
            method_sha256=body['registry']['entries']['debt_issue']['method_sha256'])
    return dict(profile=PROFILE, owner=owner, amounts=deepcopy(amounts), synthetic=True,
        parent_sha256=BASE['files']['parent.txt'], required_documents={REF: record}, native_program=body,
        source_admission=False, complete_company_population=False)

def assess(body):
    boundary = dict(profile=PROFILE, synthetic=True, source_admission=False, accounting_admission=False,
                    complete_company_population=False, required_document_ids=[REF])
    try:
        protect()
        closed(body, ['profile','owner','amounts','synthetic','parent_sha256','required_documents','native_program',
                      'source_admission','complete_company_population'], 'request_schema')
        need(body['profile'] == PROFILE and body['synthetic'] is True, 'profile')
        need(body['source_admission'] is False and body['complete_company_population'] is False, 'false_admission')
        need(body['parent_sha256'] == BASE['files']['parent.txt'], 'parent_binding')
        closed(body['required_documents'], [REF], 'required_document_population')
        row = body['required_documents'][REF]
        closed(row, ['retrieval','parsing','modeling'], 'coverage_schema')
        canonical = request(body['owner'], body['amounts'])
        expected = canonical['required_documents'][REF]
        missing = None
        for key in ['retrieval','parsing','modeling']:
            value = row[key]
            if value is None:
                if missing is None: missing = key
            else:
                need(missing is None, 'coverage_order')
                need(value == expected[key], key + '_binding')
        need(body['native_program'] == canonical['native_program'], 'native_method_binding')
        if missing:
            return dict(**boundary, status='unresolved', missing_stage=missing,
                required_documents=deepcopy(body['required_documents']), native_result=None,
                financial_execution=False, current=deepcopy(body['native_program']['opening']))
        result = program.run(body['native_program'])
        return dict(**boundary, status='native_result', required_documents=deepcopy(body['required_documents']),
                    financial_execution=True, native_result=result)
    except (ValueError, TypeError, KeyError, OSError, ZeroDivisionError) as exc:
        return dict(**boundary, status='invalid', reason=str(exc), native_result=None, financial_execution=False)
