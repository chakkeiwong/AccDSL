"""Author exact documentary exchanges; never invoke an accounting service."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
from schema_design import schemas, sid, COMPONENTS, EVENTS, ACCOUNTS, ASSETS, LIABILITIES, PROFIT, OCI, CASH
from authored_cases import CASES

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
REG, ALIASES, BLOBS, EX, STEPS = {}, {}, {}, [], []

def enc(v): return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
def q(v):
    f = F(v)
    return {'n': str(f.numerator), 'd': str(f.denominator)}
def num(v): return F(int(v['n']), int(v['d']))
def refs(v):
    if isinstance(v, dict):
        if set(v) == {'kind', 'schema', 'digest'}: yield v
        else:
            for x in v.values(): yield from refs(x)
    elif isinstance(v, list):
        for x in v: yield from refs(x)
def add(kind, key, body):
    assert key not in ALIASES, 'duplicate record identity: ' + key
    deps = {enc(r): r for r in refs(body)}
    r = {'kind': kind, 'schema': sid(kind), 'key': key, 'revision': 0, 'body': body,
         'dependencies': [deps[k] for k in sorted(deps)]}
    d = hashlib.sha256(('accdsl.portable.v1/' + sid(kind)).encode() + b'\0' + enc(r)).hexdigest()
    REG[d] = r
    ALIASES[key] = {'kind': kind, 'schema': sid(kind), 'digest': d}
    return ALIASES[key]
def body(r): return REG[r['digest']]['body']
def blob(p):
    b = p.read_bytes(); d = hashlib.sha256(b).hexdigest()
    BLOBS[d] = {'path': str(p.relative_to(ROOT)), 'byte_length': len(b)}
    return {'kind': 'blob', 'algorithm': 'sha256', 'digest': d, 'byte_length': len(b)}
def typed(s, v):
    if v is None: return None
    if s.get('type') == 'object':
        if set(s['properties']) == {'n', 'd'}: return q(v)
        return {k: typed(z, v[k]) for k, z in s['properties'].items()}
    if s.get('type') == 'array': return [typed(s['items'], z) for z in v]
    if 'anyOf' in s: return typed(s['anyOf'][0], v)
    return v
def closure(roots):
    seen = set()
    def visit(r):
        if r['digest'] in seen: return
        seen.add(r['digest'])
        for dep in REG[r['digest']]['dependencies']: visit(dep)
    for r in roots: visit(r)
    return sorted(seen)
def owner(st):
    c = body(body(st)['context_ref'])
    return '/'.join(c[k] for k in ['entity_id', 'book_id', 'branch_key'])
def head(st): return {'owner_key': owner(st), 'state_ref': st, 'generation': body(st)['sequence']}
def world(st):
    return {'head': head(st), 'event_receipts': {}, 'journals': [], 'deltas': [], 'receipts': [],
            'published_records': closure([st]), 'current_view_ref': body(st)['view_ref'],
            'unaffected_owners': {'Other/Legal': {'generation': 7, 'balance_digest': '0' * 64}}}
def event_key(b): return enc([b['identity'][k] for k in ['entity_id', 'book_id', 'branch_key', 'business_event_id']]).decode()

def main():
    assert len({c['id'] for c in CASES}) == len(CASES), 'duplicate case identity'
    schema = schemas()
    (OUT / 'record-schemas.json').write_text(json.dumps(schema, indent=2) + '\n')
    contract = OUT / 'semantic-contract.md'
    lock = add('SchemaLock', 'lock', {'schema_blob': blob(OUT / 'record-schemas.json'),
        'semantic_contract_blob': blob(contract), 'format': 'jsonschema2020-12'})
    ops = ['accounting.authorize@1', 'accounting.propose@1', 'accounting.commit@1', 'report.build@1']
    profile = add('Profile', 'profile', {'profile_id': 'CorporateComponents/5', 'schema_lock_ref': lock,
        'operations': ops, 'book_mode': 'synthetic', 'execution_mode': 'specification_example',
        'interest_cash_policy': 'historical_IAS7_operating_election'})
    signatures = {op: add('OperationSignature', 'signature.' + op, {'operation': op,
        'profile_ref': profile,
        'arguments_definition': 'Arguments.' + op, 'payload_kinds': {
            'accounting.authorize@1': ['PostingAuthorization'], 'accounting.propose@1': ['JournalProposal', 'EconomicDelta'],
            'accounting.commit@1': ['StateTransitionReceipt'], 'report.build@1': ['Report']}[op],
        'effects': 'accounting_transaction' if op == 'accounting.commit@1' else 'read'}) for op in ops}
    env = add('Environment', 'environment', {'purpose': 'documentary_fixture', 'numerics': 'exact_rational', 'runtime_executed': False})
    decoder = add('Decoder', 'decoder', {'media_type': 'application/json', 'canonical_encoding': 'accdsl.portable.v1'})
    method_texts = {
        'production': ('corporate-cohorts-funding-20261015.tex', ['IAS2.10-16,23-27,34']),
        'inspection': ('corporate-event-repairs-20261015.md', ['IAS16.12-14,43-55']),
        'lease': ('corporate-event-repairs-20261015.md', ['IFRS16.38-50', 'IAS7.31-34']),
        'benefit': ('corporate-event-repairs-20261015.md', ['IAS19.99-112,120-126']),
        'funding': ('corporate-cohorts-funding-20261015.tex', ['IFRIC14.23-24', 'IAS19.120(c)']),
        'restoration': ('corporate-residuals-20261015.md', ['IFRIC1.1-8', 'IAS36.59-64']),
        'impairment': ('impairment-floors-20261014.md', ['IAS36.104-108']),
        'tax': ('impairment-tax-repairs-20261015.md', ['IAS36.60-64', 'IAS12.61A']),
        'advance': (None, ['IFRS15.105-109; local fully-prepaid allocation deduction']),
    }
    method_texts.update({
        'cycle':('customer-contract-extensions-20261014.md',['AASB15.31-45,105-109']),
        'separate':('customer-obligations-20261014.md',['AASB15.18-20,73-86']),
        'rcost':('customer-contract-extensions-20261014.md',['AASB15.B20-B27']),
        'variableD':(None,['AASB15.18-21(a),50-59,73-90(a)']),
        'variableI':(None,['AASB15.18-21(b),35(b),39-45,50-59,73-90(b)']),
        'recovery':(None,['AASB15.35(b),39-45']),
        'ceiling':('corporate-event-repairs-20261015.md',['IAS19.99-103,120-126']),
        'availability':('corporate-cohorts-funding-20261015.tex',['IAS19.64','IFRIC14.7-22']),
        'multiemployer':('corporate-event-repairs-20261015.md',['IAS19.32-41,148','IAS7.14(d),31-34']),
        'uncertaintax':('corporate-residuals-20261015.md',['IFRIC23.6-14','IAS12.46-51','IAS7.35']),
        'acquisitiontax':('impairment-tax-repairs-20261015.md',['IAS12.15(a),66-68','IFRS3.18,24,32','IAS7.39']),
        'investmenttax':('impairment-tax-repairs-20261015.md',['IAS12.39-51,58']),
        'taxorigin':('impairment-tax-repairs-20261015.md',['IAS36.60-64,117-124','IAS12.61A-64','IAS7.35-36']),
        'pillar':('impairment-tax-repairs-20261015.md',['EU2023/2468.Articles1-3','IAS12.4A,88A-88D,98M']),
        'revaluation': ('ppe-operations-20261014.md', ['AASB116.29-55,67-73', 'AASB107.16,43']),
        'corpassets': ('impairment-tax-repairs-20261015.md', ['IAS36.100-108']),
        'ncigoodwill': ('impairment-tax-repairs-20261015.md', ['IAS36.C1-C9,104-108']),
        'reversal': ('impairment-floors-20261014.md', ['IAS36.114-124']),
        'rvrestoration': ('corporate-residuals-20261015.md', ['IFRIC1.6-8']),
        'returns': ('customer-contract-extensions-20261014.md', ['AASB15.47-59,105-109,B20-B27']),
        'assurance': ('corporate-residuals-20261015.md', ['AASB137.14,24,36-62']),
        'service': ('customer-obligations-20261014.md', ['AASB15.22-45,73-86,B28-B33']),
        'distinct': ('customer-obligations-20261014.md', ['AASB15.18-21(a)']),
        'integrated': ('customer-obligations-20261014.md', ['AASB15.18-21(b),35(b),39-45']),
        'mixed': ('corporate-residuals-20261015.md', ['AASB15.18-21(c),39-45,63,73-86']),
        'agency': ('customer-obligations-20261014.md', ['AASB15.B34-B38']),
        'joint': ('corporate-residuals-20261015.md', ['IAS2.14,34']),
        'byproduct': ('corporate-residuals-20261015.md', ['IAS2.14,34']),
        'supplier': ('corporate-residuals-20261015.md', ['IAS2.18', 'IAS7.31-34']),
        'aasb15_support': ('corporate-residuals-20261015.md', ['AASB15.B28-B33']),
        'aasb107_support': ('customer-obligations-20261014.md', ['AASB107.14(a)-(d)']),
    })
    au_families = {'returns', 'assurance', 'service', 'distinct', 'integrated', 'mixed', 'agency', 'aasb15_support', 'aasb107_support', 'revaluation'}
    au_families.update({'cycle','separate','rcost','variableD','variableI','recovery'})
    sources, methods = {}, {}
    for family, (filename, anchors) in method_texts.items():
        mp = ROOT / 'docs/design/proposal/methods' / filename if filename else contract
        pdf = 'docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf'
        lower, upper, available = None, None, None
        if family in au_families:
            pdf = 'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf'
            lower, upper = '2023-01-01', '2026-07-01'
        if family == 'assurance': pdf = 'data/accounting-master/finite-method-decisions-20261015/corporate/sources/aasb137-dec2022.pdf'
        if family == 'aasb107_support':
            pdf = 'docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023.pdf'
            lower, upper = '2024-01-01', '2026-01-01'
        if family == 'revaluation':
            pdf = 'docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb116-compiled-dec2022.pdf'
            lower, upper = '2023-01-01', '2027-01-01'
        if family == 'pillar':
            pdf='data/accounting-master/impairment-tax-repairs-20261015/sources/eu2023-2468.pdf'
            lower,upper,available='2023-01-01',None,'2023-11-10'
        sources[family] = add('SourceSupport', 'source.' + family, {
            'source_pdf': blob(ROOT / pdf),
            'method_text': blob(mp), 'inspection_note': blob(OUT / 'source-reading.md'), 'anchors': anchors,
            'authority_scope': 'historical_not_current_admission', 'family': 'AU_AASB' if family in au_families else 'EU_IFRS',
            'instrument_in_force_on':available,
            'period_start_inclusive': lower, 'period_start_exclusive': upper})
    for method, (tag, _) in EVENTS.items():
        family = method.split('.')[0]
        supporting = [sources['aasb107_support']] if family in au_families else []
        if family == 'assurance': supporting = [sources['aasb15_support'], *supporting]
        if family == 'pillar': supporting=[sources['taxorigin']]
        methods[method] = add('MethodDefinition', 'method.' + method, {'method_id': method, 'component_kind': tag,
            'method_status':'unresolved_settlement_boundary' if method=='rcost.settle' else 'specified_finite',
            'source_ref': sources[family], 'supporting_source_refs': supporting, 'contract_blob': blob(contract), 'profile_ref': profile})
    view = add('View', 'view', {'source_refs': list(sources.values()), 'revision': 0, 'supersedes_ref': None,
                              'information_mode': 'archival_synthetic'})

    def request(key, op, args, st=None, v=view, prof=profile, budget=1000):
        r = add('OperationRequest', 'request.' + key, {'operation': op, 'request_id': key,
            'workspace_key': 'CorporateComponents-specification', 'profile_ref': prof, 'signature_ref': signatures[op],
            'view_ref': v, 'arguments': {'tag': op, 'value': args}, 'execution': {'mode': 'specification_example',
            'budget': {'operation_count': budget, 'elapsed_seconds': 60}, 'environment_ref': env},
            'expected_head': head(st) if st else None})
        p = OUT / 'bytes' / (key + '.json'); p.parent.mkdir(exist_ok=True); p.write_bytes(enc(REG[r['digest']]))
        sub = add('Submission', 'submission.' + key, {'blob_ref': blob(p), 'media_type': 'application/json',
                  'transport': 'authored_fixture', 'decoder_ref': decoder})
        return r, sub

    def response(key, rq, sub, disposition='completed', outputs=(), receipt=None, code=None, valid=True, basis=None):
        domain = add('Domain', 'domain.' + key, {'request_ref': rq, 'meaning': 'singleton_request_decision'}) if valid else None
        region = add('Region', 'region.' + key, {'domain_ref': domain, 'predicate': 'this_request'}) if valid else None
        partial = disposition == 'partial'
        obligations = [add('Obligation', 'obligation.' + key, {'code': code, 'required_input': code, 'basis_ref': basis})] if partial else []
        coverage = None if not valid else {'domain_ref': domain, 'completed': [] if partial or disposition == 'unsupported' else [region],
            'unresolved': [region] if partial else [], 'unsupported': [region] if disposition == 'unsupported' else [],
            'infeasible': [], 'cancelled': [], 'relation': 'disjoint_exhaustive'}
        return add('OperationResult', 'result.' + key, {'submission_ref': sub, 'request_ref': rq if valid else None,
            'operation': body(rq)['operation'] if valid else None, 'input_view_ref': body(rq)['view_ref'] if valid else None,
            'disposition': disposition, 'statuses': {'structural_validity': 'valid' if valid else 'invalid',
                'mathematical_status': 'unresolved' if partial else 'defined',
                'computation_status': 'partial' if partial else 'not_computed' if disposition in ['rejected', 'unsupported'] else 'complete',
                'empirical_justification': 'not_established', 'capability_status': 'specified_only_no_runtime',
                'accounting_validity': 'not_assessed', 'forecast_validity': 'not_assessed',
                'product_readiness': 'not_implemented', 'human_acceptance': 'pending'},
            'payload': None if not valid else {'tag': body(rq)['operation'], 'result_refs': list(outputs),
                'additional_commit': disposition == 'completed' and receipt is not None},
            'diagnostics': [] if not code else [{'code': code, 'stage': 'binding_financial_or_owner_validation',
                'record_ref': None, 'source_locator': None, 'field_path': 'arguments', 'affected_query_branch_ids': [],
                'dependency_path': [], 'observed': code, 'expected_rule': 'CorporateComponents/5',
                'retry_advice': 'repair_named_input_or_resubmit_exact_request', 'blocking_diagnostic_ids': []}],
            'coverage': coverage, 'unresolved': obligations, 'continuation_ref': None,
            'commit_observation': 'committed' if receipt else 'not_committed', 'receipt_ref': receipt,
            'evidence_mode': 'specification_example'})

    def exchange(key, rq, sub, res, before, after):
        EX.append({'id': key, 'request_ref': rq, 'submission_ref': sub, 'response_ref': res,
                   'world_before': deepcopy(before), 'world_after': deepcopy(after)})

    def report_exchange(label, opening_ref, closing_ref, w):
        s0, s1 = body(opening_ref), body(closing_ref)
        v0, v1 = {a:num(v) for a,v in s0['balances'].items()}, {a:num(v) for a,v in s1['balances'].items()}
        report = add('Report', label, {'opening_ref': opening_ref, 'state_ref': closing_ref, 'view_ref': view,
            'values': {'cash':q(v1['cash']), 'assets':q(sum(v1[a] for a in ASSETS)),
                'liabilities':q(-sum(v1[a] for a in LIABILITIES)),
                'equity':q(-sum(v1[a] for a in ['capital','retained',*PROFIT,*OCI])),
                'profit':q(-sum(v1[a]-v0[a] for a in PROFIT)),
                'oci':q(-sum(v1[a]-v0[a] for a in OCI) + num(s1['revaluation_transfers']) - num(s0['revaluation_transfers'])),
                **{k:q(num(s1['cash_movements'][k])-num(s0['cash_movements'][k])) for k in CASH}},
            'income_statement': income_statement(v0,v1),
            'attribution': attribution(s0,s1),
            'oci_components':oci_components(s0,s1),
            'tax_movements':tax_movements(s0,s1),
            'income_taxes_paid':tax_paid(s0,s1),'pillar_disclosures':pillar_disclosures(s0,s1),
            'revaluation_transfer':q(num(s1['revaluation_transfers'])-num(s0['revaluation_transfers'])),
            'tax_status':s1['tax_status'],'complete_company_after_tax':False,
            'cash_classification_complete':num(s1['cash_movements']['unclassified']) == num(s0['cash_movements']['unclassified']),
            'cash_classification_status':s1['cash_classification_status']})
        rq, sub = request(label, 'report.build@1', {'opening_ref':opening_ref,'state_ref':closing_ref,'view_ref':view,'require_current':False})
        rr = response(label,rq,sub,outputs=[report]);exchange(label,rq,sub,rr,w,w)

    def income_statement(v0,v1):
        fields={k:q(-(v1[k]-v0[k])) for k in ['product_revenue','service_revenue','commission_revenue','reimbursement_income']}
        fields['other_gains']=q(-sum(v1[k]-v0[k] for k in ['income','provision_gain']))
        fields.update({k:q(v1[k]-v0[k]) for k in ['cost_of_sales','service_expense','assurance_expense','finance_expense','tax_expense']})
        fields['other_expense']=q(v1['expense']-v0['expense'])
        fields['tax_expense']=q(v1['tax_expense']-v0['tax_expense']+v1['pillar_tax_expense']-v0['pillar_tax_expense'])
        return fields

    def attribution(s0,s1):
        c0,c1 = body(s0['component_ref']),body(s1['component_ref'])
        if c1['tag'] != 'partial_goodwill': return None
        return {dest:q(num(c1['value'][source])-num(c0['value'][source])) for dest,source in
            [('parent_loss','parent_loss'),('nci_loss','nci_loss'),('unrecognized_notional_loss','unrecognized_loss')]}

    def oci_components(s0,s1):
        c0,c1 = body(s0['component_ref']),body(s1['component_ref'])
        restoration = (num(c1['value']['restoration_oci'])-num(c0['value']['restoration_oci'])) if c1['tag']=='restoration_revalued' else F(0)
        revaluation = num(s0['balances']['oci_revaluation'])-num(s1['balances']['oci_revaluation'])
        revaluation += num(s1['revaluation_transfers'])-num(s0['revaluation_transfers'])
        return {'revaluation':q(revaluation-restoration),'restoration_revaluation':q(restoration),
            'pension':q(num(s0['balances']['oci_pension'])-num(s1['balances']['oci_pension']))}

    def tax_movements(s0,s1):
        c0,c1=body(s0['component_ref']),body(s1['component_ref']);tag=c1['tag']
        c0,c1=c0['value'],c1['value']
        d=lambda field:num(c1[field])-num(c0[field])
        result={k:F(0) for k in ['ordinary_current_profit','deferred_profit','deferred_oci','acquisition_deferred','pillar_current_profit']}
        if tag=='uncertain_tax':result.update(ordinary_current_profit=d('current_assessed'),deferred_profit=d('dtl'))
        elif tag=='acquisition_tax':result['acquisition_deferred']=d('dtl')
        elif tag=='investment_tax':result['deferred_profit']=d('dtl')-d('dta')
        elif tag=='tax_revaluation':result.update(deferred_profit=d('tax_profit_to_date'),deferred_oci=d('tax_oci_to_date'))
        elif tag=='tax_origin':result.update(deferred_profit=-d('dta'),deferred_oci=d('dtl'))
        elif tag=='pillar_two':result['pillar_current_profit']=d('current_assessed')
        return {k:q(v) for k,v in result.items()}

    def tax_paid(s0,s1):
        c0,c1=body(s0['component_ref']),body(s1['component_ref'])
        field={'uncertain_tax':'current_paid','pillar_two':'paid'}.get(c1['tag'])
        return q(num(c1['value'][field])-num(c0['value'][field])) if field else q(0)

    def pillar_disclosures(s0,s1):
        c0,c1=body(s0['component_ref']),body(s1['component_ref'])
        if c1['tag']!='pillar_two':return None
        c0,c1=c0['value'],c1['value']
        fields={k:c1[k] for k in ['exception_applied','exception_disclosed','current_separately_disclosed',
            'legislation_effective','exposure_known','exposure_lower','exposure_upper','unavailable_explanation','assessment_progress']}
        fields['current_tax_in_period']=q(num(c1['current_assessed'])-num(c0['current_assessed'])) if c1['legislation_effective'] else None
        return fields

    successes = {}
    for case in CASES:
        name, tag = case['id'], case['tag']
        context = add('Context', name + '.context', {'entity_id': 'ExampleCorp', 'book_id': case.get('book_id','Legal'), 'branch_key': name,
            'currency': 'USD', 'basis': 'historical_AU_AASB_conditional' if case.get('source_family') == 'AU_AASB' else 'historical_EU_IFRS_conditional',
            'issuer_class': 'for_profit', 'calendar': 'relative_synthetic'})
        comp = add('ComponentState', name + '.component.0', {'tag': tag, 'value': typed(COMPONENTS[tag], case['opening_component'])})
        opening = add('CompanyState', name + '.state.0', {'context_ref': context, 'view_ref': view, 'sequence': 0,
            'instant': 0, 'component_ref': comp, 'balances': {a: q(case['opening_balances'].get(a, 0)) for a in ACCOUNTS},
            'cash_movements': {k: q(0) for k in CASH}, 'tax_status': case['tax_status'],
            'revaluation_transfers':q(0),
            'cash_classification_status': 'specified_historical_policy'})
        case_opening = opening
        period_opening = opening
        w = world(opening)
        for i, st in enumerate(case['steps'], 1):
            key = name + '.' + str(i); mid = st['method']; source = body(methods[mid])['source_ref']
            australian = case.get('source_family') == 'AU_AASB'
            dated = australian or case.get('calendar_dates',False)
            date = st.get('event_date'); year = int(date[:4]) if dated else None
            ev = add('EconomicEvent', key + '.event', {'method_id': mid, 'context_ref': context, 'instant': i,
                'event_date': date,
                'reporting_period_start': f'{year}-01-01' if dated else None,
                'reporting_period_end_exclusive': f'{year+1}-01-01' if dated else None,
                'parameters': typed(EVENTS[mid][1], st['parameters'])})
            authority = add('Authority', key + '.authority', {'source_ref': source, 'context_ref': context,
                'supporting_source_refs': body(methods[mid])['supporting_source_refs'],
                'start_inclusive': 0, 'end_exclusive': 20, 'evidence_class': 'synthetic_conditional_admission'})
            basis = add('AccountingEventBasis', key + '.basis', {'identity': {**{k: body(context)[k] for k in
                ['entity_id', 'book_id', 'branch_key']}, 'business_event_id': key}, 'opening_ref': opening,
                'event_ref': ev, 'method_ref': methods[mid], 'authority_ref': authority, 'view_ref': view, 'context_ref': context})
            admission = add('Admission', key + '.admission', {'basis_ref': basis, 'source_ref': source,
                'context_ref': context, 'instant': i, 'status': 'eligible', 'fact_basis': 'authored_synthetic',
                'findings': [{'name': 'declared_finite_method_premises', 'status': 'satisfied', 'support_ref': ev}]})
            auth = add('PostingAuthorization', key + '.authorization', {'basis_ref': basis, 'admission_ref': admission,
                'view_ref': view, 'posting_permitted': True})
            cp = add('ComponentState', key + '.component', {'tag': tag, 'value': typed(COMPONENTS[tag], st['after'])})
            balances = {a: q(num(body(opening)['balances'][a]) + F(st['journal'].get(a, '0'))) for a in ACCOUNTS}
            cash_change = {k: q(st['cash_change'].get(k, '0')) for k in CASH}
            closing = add('CompanyState', key + '.state', {**body(opening), 'component_ref': cp, 'sequence': i, 'instant': i,
                'balances': balances, 'cash_movements': {k: q(num(body(opening)['cash_movements'][k]) + num(cash_change[k])) for k in CASH},
                'revaluation_transfers':q(num(body(opening)['revaluation_transfers']) +
                    (F(st['parameters']['amount']) if mid == 'revaluation.transfer' else 0)),
                'cash_classification_status': st['parameters']['classification_status'] if mid == 'restoration.pay' else body(opening)['cash_classification_status']})
            journal = add('JournalProposal', key + '.journal', {'basis_ref': basis, 'mode': 'monetary' if st['journal'] else 'state_only',
                'currency': 'USD', 'lines': [{'account': a, 'signed_amount': q(v)} for a, v in st['journal'].items() if F(v)]})
            delta = add('EconomicDelta', key + '.delta', {'basis_ref': basis, 'opening_ref': opening, 'closing_ref': closing,
                'cash_change': cash_change})
            args = {'basis_ref': basis, 'authorization_ref': auth, 'journal_ref': journal, 'delta_ref': delta}
            for op, ar, output in [('accounting.authorize@1', {'basis_ref': basis}, [auth]),
                ('accounting.propose@1', {'basis_ref': basis, 'authorization_ref': auth}, [journal, delta])]:
                label = key + '.' + op.split('.')[1].split('@')[0]
                rq, sub = request(label, op, ar)
                rr = response(label, rq, sub, outputs=output)
                exchange(label, rq, sub, rr, w, w)
            rq, sub = request(key, 'accounting.commit@1', args, opening)
            receipt = add('StateTransitionReceipt', key + '.receipt', {'request_ref': rq, **args,
                'opening_ref': opening, 'closing_ref': closing, 'generation': i, 'status': 'committed'})
            after = deepcopy(w); after['head'] = head(closing)
            after['event_receipts'][event_key(body(basis))] = {'request_ref': rq, 'receipt_ref': receipt}
            for dst, rr in [('journals', journal), ('deltas', delta), ('receipts', receipt)]: after[dst].append(rr)
            after['published_records'] = sorted(set(w['published_records']) | set(closure([receipt])))
            rr = response(key, rq, sub, outputs=[receipt], receipt=receipt)
            exchange(key, rq, sub, rr, w, after)
            successes[key] = (args, rq, sub, receipt, deepcopy(w), deepcopy(after))
            STEPS.append({'id': key, 'method': mid, 'opening_ref': opening, 'event_ref': ev,
                          'closing_ref': closing, 'journal_ref': journal, 'delta_ref': delta})
            opening, w = closing, after
            if dated:
                next_date = case['steps'][i].get('event_date') if i < len(case['steps']) else None
                if next_date is None or next_date[:4] != date[:4]:
                    report_exchange(name + '.period-' + date[:4], period_opening, opening, w)
                    period_opening = opening
        b = body(opening); vals = {a: num(v) for a, v in b['balances'].items()}
        start_vals = {a: num(v) for a, v in body(case_opening)['balances'].items()}
        profit = -sum(vals[a] - start_vals[a] for a in PROFIT)
        oci = -sum(vals[a] - start_vals[a] for a in OCI) + num(b['revaluation_transfers']) - num(body(case_opening)['revaluation_transfers'])
        report = add('Report', name + '.report', {'opening_ref': case_opening, 'state_ref': opening, 'view_ref': view, 'values': {
            'cash': q(vals['cash']), 'assets': q(sum(vals[a] for a in ASSETS)),
            'liabilities': q(-sum(vals[a] for a in LIABILITIES)), 'equity': q(-sum(vals[a] for a in ['capital', 'retained', *PROFIT, *OCI])),
            'profit': q(profit), 'oci': q(oci), **b['cash_movements']}, 'income_statement':income_statement(start_vals,vals),
            'attribution':attribution(body(case_opening),b),
            'oci_components':oci_components(body(case_opening),b),
            'tax_movements':tax_movements(body(case_opening),b),
            'income_taxes_paid':tax_paid(body(case_opening),b),'pillar_disclosures':pillar_disclosures(body(case_opening),b),
            'revaluation_transfer':q(num(b['revaluation_transfers'])-num(body(case_opening)['revaluation_transfers'])),
            'tax_status': b['tax_status'],
            'complete_company_after_tax': False, 'cash_classification_complete': num(b['cash_movements']['unclassified']) == 0,
            'cash_classification_status': b['cash_classification_status']})
        label = name + '.report'; rq, sub = request(label, 'report.build@1', {'opening_ref': case_opening,
            'state_ref': opening, 'view_ref': view, 'require_current': False})
        rr = response(label, rq, sub, outputs=[report]); exchange(label, rq, sub, rr, w, w)

    # Full request and store worlds are preserved for replay, conflicts and adverse transitions.
    args, rq, sub, receipt, before, after = successes['production-fifo.2']
    rr = response('exact-replay', rq, sub, 'replayed', [receipt], receipt)
    exchange('exact-replay', rq, sub, rr, after, after)
    observation = add('TransportObservation', 'lost-ack', {'submission_ref': sub, 'request_ref': rq,
        'observation': 'acknowledgement_timeout', 'commit_observation': 'unknown', 'receipt_ref': None,
        'next_action': 'resubmit_exact_original_request'})
    lost = {'observation_ref': observation, 'before_publication': before, 'after_publication': after,
            'retry_before_exchange': 'production-fifo.2', 'retry_after_exchange': 'exact-replay'}
    for label, budget in [('changed-request', 1000), ('changed-budget', 999)]:
        r, su = request(label, 'accounting.commit@1', args, body(args['basis_ref'])['opening_ref'], budget=budget)
        rr = response(label, r, su, 'rejected', code='idempotency_conflict')
        exchange(label, r, su, rr, after, after)

    def mutated(label, original, code, event_changes=None, parameter_changes=None, journal_lines=None,
                authority_changes=None, basis_changes=None, start_after=False, disposition='rejected', consumed=False):
        ar, _, _, _, wb, wa = successes[original]
        ar = deepcopy(ar); old_basis = body(ar['basis_ref']); evbody = deepcopy(body(old_basis['event_ref']))
        if consumed: evbody['instant'] += 1
        if event_changes: evbody.update(event_changes)
        if parameter_changes: evbody['parameters'].update(parameter_changes)
        evr = add('EconomicEvent', label + '.event', evbody)
        au = add('Authority', label + '.authority', {**body(old_basis['authority_ref']), **(authority_changes or {})})
        bb = {**deepcopy(old_basis), 'event_ref': evr, 'authority_ref': au,
              'identity': {**old_basis['identity'], 'business_event_id': label}, **(basis_changes or {})}
        if consumed: bb['opening_ref'] = wa['head']['state_ref']
        br = add('AccountingEventBasis', label + '.basis', bb)
        ad = body(body(ar['authorization_ref'])['admission_ref'])
        adr = add('Admission', label + '.admission', {**ad, 'basis_ref': br, 'instant': evbody['instant'],
            'findings': [{'name': 'declared_finite_method_premises', 'status': 'satisfied', 'support_ref': evr}]})
        ar['basis_ref'] = br
        ar['authorization_ref'] = add('PostingAuthorization', label + '.authorization', {
            **body(ar['authorization_ref']), 'basis_ref': br, 'admission_ref': adr})
        jb = {**body(ar['journal_ref']), 'basis_ref': br}
        if journal_lines is not None: jb['lines'] = [{'account': a, 'signed_amount': q(v)} for a, v in journal_lines.items()]
        ar['journal_ref'] = add('JournalProposal', label + '.journal', jb)
        ar['delta_ref'] = add('EconomicDelta', label + '.delta', {**body(ar['delta_ref']), 'basis_ref': br})
        r, su = request(label, 'accounting.commit@1', ar, bb['opening_ref'])
        rr = response(label, r, su, disposition, code=code, basis=br)
        w = wa if start_after or consumed else wb
        exchange(label, r, su, rr, w, w)

    mutated('balanced-wrong-production', 'production-fifo.2', 'wrong_financial_transition',
        journal_lines={'wip': '-1290', 'finished_goods': '1290'})
    mutated('invalid-unit-balance', 'production-fifo.2', 'physical_units_mismatch', parameter_changes={'closing_units': q(21)})
    mutated('cent-policy-unadmitted', 'production-fifo.2', 'rounding_profile_unsupported', parameter_changes={'rounding': 'cents'}, disposition='unsupported')
    mutated('inspection-old-cost-unknown', 'inspection.1', 'old_component_measurement_unresolved', parameter_changes={'old_allocation_known': False}, disposition='partial')
    mutated('heterogeneous-lease', 'lease.1', 'rights_allocation_unsupported', parameter_changes={'same_remaining_term': False}, disposition='unsupported')
    mutated('benefit-no-discharge', 'benefits.3', 'legal_discharge_failed', parameter_changes={'legal_discharge': False})
    mutated('wrong-tax-origin', 'revalued-tax.1', 'wrong_financial_transition', journal_lines={
        'ppe': '-50', 'expense': '50', 'dtl': '10', 'dta': '5/2', 'tax_expense': '-25/2'})
    mutated('missing-recoverable', 'impairment-floor.1', 'measurement_unresolved', parameter_changes={'unit_recoverable': None}, disposition='partial')
    mutated('wrong-effective-date', 'inspection.1', 'authority_interval_mismatch', authority_changes={'end_exclusive': 1})
    mutated('wrong-source', 'inspection.1', 'source_method_mismatch', authority_changes={'source_ref': sources['tax']})
    mutated('wrong-au-period', 'assurance-population.1', 'source_period_mismatch', event_changes={
        'event_date': '2026-07-02', 'reporting_period_start': '2026-07-01', 'reporting_period_end_exclusive': '2027-07-01'})
    mutated('missing-assurance-classification-source', 'assurance-population.1', 'source_method_mismatch',
        authority_changes={'supporting_source_refs': [sources['aasb107_support']]})
    mutated('netted-reimbursement', 'assurance-population.1', 'wrong_financial_transition', journal_lines={
        'cash': '2000', 'product_revenue': '-2000', 'inventory': '-600', 'cost_of_sales':'600',
        'assurance_expense': '300', 'provision': '-300'})
    mutated('distinct-earlier-revenue-erased', 'distinct-amendment.3', 'wrong_financial_transition', journal_lines={
        'cash': '48', 'contract_liability': '-51', 'product_revenue': '3'})
    mutated('service-progress-unmeasured', 'service-warranty.3', 'progress_measurement_unresolved',
        parameter_changes={'faithful_measure_admitted': False}, disposition='partial')
    mutated('service-released-before-earned', 'service-warranty.3', 'future_service_not_performed',
        event_changes={'event_date':'2024-08-01'})
    mutated('supplier-interest-capitalized', 'supplier-finance.2', 'wrong_financial_transition',
        journal_lines={'inventory': '10', 'payable': '-10'})
    mutated('partial-class-revaluation', 'class-revaluation.2', 'whole_class_required',
        parameter_changes={'values':[{'asset_id':'A','fair_value':q(45)}]})
    mutated('borrow-other-asset-surplus', 'class-revaluation.2', 'wrong_financial_transition',
        journal_lines={'ppe':'-39','oci_revaluation':'39'})
    mutated('surplus-recycled-to-profit', 'class-revaluation.6', 'wrong_financial_transition',
        journal_lines={'oci_revaluation':'15','income':'-15'})
    mutated('wrong-cash-source-period', 'class-revaluation.5', 'source_period_mismatch',
        event_changes={'event_date':'2026-12-31','reporting_period_start':'2026-01-01','reporting_period_end_exclusive':'2027-01-01'})
    mutated('corporate-group-before-leaves', 'corporate-asset-order.3', 'leaf_tests_required',
        basis_changes={'opening_ref':ALIASES['corporate-asset-order.state.0']})
    mutated('corporate-loss-counted-twice', 'corporate-asset-order.3', 'wrong_financial_transition',
        journal_lines={'ppe':'-33','expense':'33'})
    mutated('notional-goodwill-posted', 'partial-goodwill-220.1', 'wrong_financial_transition',
        journal_lines={'goodwill':'-30','expense':'30'})
    mutated('nci-profit-basis-unknown', 'partial-goodwill-larger.1', 'nci_allocation_unresolved',
        parameter_changes={'profit_allocation_matches_ownership':False},disposition='partial')
    mutated('reversal-before-evidence', 'depreciated-reversal.2', 'changed_estimates_required',
        parameter_changes={'changed_estimates_admitted':False},disposition='partial')
    mutated('reversal-erases-all-allowances', 'depreciated-reversal.2', 'wrong_financial_transition',
        journal_lines={'ppe':'30','income':'-30'})
    mutated('restoration-skips-class-review', 'restoration-revalued-increase.1', 'class_revaluation_required',
        parameter_changes={'class_review_supports_unchanged_ppe':False},disposition='partial')
    mutated('restoration-unknown-cost-model', 'restoration-revalued-increase.1', 'cost_model_carrying_unresolved',
        parameter_changes={'new_liability':q(20)},disposition='partial')
    mutated('restoration-wrong-cost-floor', 'restoration-revalued-decrease.1', 'wrong_financial_transition',
        journal_lines={'provision':'50','income':'-40','oci_revaluation':'-10'})
    mutated('exhausted-asset-uses-old-surplus', 'restoration-revalued-exhausted.1', 'wrong_financial_transition',
        journal_lines={'provision':'-5','oci_revaluation':'5'})
    mutated('ceiling-net-gain-misclassified','pension-ceiling-amendment.1','wrong_financial_transition',
        journal_lines={'pension_asset':'5','income':'-5'})
    mutated('availability-sums-exclusive-routes','refund-availability.1','wrong_financial_transition',
        journal_lines={'pension_asset':'5','oci_pension':'-5'})
    mutated('availability-floors-each-period','contribution-availability.1','wrong_financial_transition',
        journal_lines={'pension_asset':'5','oci_pension':'-5'})
    mutated('deficit-omitted-under-dc-fallback','multi-employer-deficit.2','wrong_financial_transition',journal_lines={})
    mutated('uncertain-current-deferred-inconsistent','uncertain-tax-expected-value.1','wrong_financial_transition',
        journal_lines={'current_tax_payable':'-20','tax_expense':'20'})
    mutated('uncertain-resolution-without-evidence','uncertain-tax-expected-value.2','tax_reassessment_facts_unresolved',
        parameter_changes={'new_evidence_admitted':False},disposition='partial')
    mutated('acquisition-recursive-goodwill-tax','acquisition-tax-origin.1','wrong_financial_transition',
        journal_lines={'cash':'-150','ppe':'150','dtl':'-50/3','goodwill':'50/3'})
    mutated('investment-one-condition-exception','investment-tax-liability.1','wrong_financial_transition',journal_lines={})
    mutated('investment-dta-copies-liability-test','investment-tax-deductible-no-reversal.1','wrong_financial_transition',
        journal_lines={'dta':'12','tax_expense':'-12'})
    mutated('tax-rate-origin-sent-to-profit','tax-origin-rate.1','wrong_financial_transition',
        journal_lines={'dtl':'-2','tax_expense':'2'})
    mutated('pillar-deferred-fifteen-percent','pillar-current.1','wrong_financial_transition',
        journal_lines={'pillar_tax_payable':'-7','pillar_tax_expense':'7','dtl':'-6','tax_expense':'6'})
    mutated('pillar-current-unknown','pillar-current.1','pillar_current_tax_unresolved',
        parameter_changes={'current_tax':None},disposition='partial')
    mutated('tax-cash-policy-missing','uncertain-tax-expected-value.3','tax_cash_classification_unresolved',
        parameter_changes={'activity_identification_admitted':False},disposition='partial')
    mutated('pillar-source-before-adoption','pillar-current.1','source_instrument_not_in_force',
        event_changes={'event_date':'2023-11-09','reporting_period_start':'2023-01-01','reporting_period_end_exclusive':'2024-01-01'})
    mutated('pillar-missing-amendment','pillar-current.1','source_method_mismatch',authority_changes={'source_ref':sources['taxorigin']})
    mutated('pillar-missing-exposure-progress','pillar-exposure-unknown.1','pillar_exposure_disclosure_missing',
        parameter_changes={'assessment_progress':None},disposition='partial')
    def mutated_component(label,original,changes,code,disposition='rejected'):
        ar=successes[original][0];st=body(body(ar['basis_ref'])['opening_ref'])
        comp=deepcopy(body(st['component_ref']));comp['value'].update(changes)
        cr=add('ComponentState',label+'.opening-component',comp)
        sr=add('CompanyState',label+'.opening-state',{**st,'component_ref':cr})
        mutated(label,original,code,basis_changes={'opening_ref':sr},disposition=disposition)
    mutated_component('multi-common-control','multi-employer-deficit.1',{'common_control':True},
        'common_control_plan_requires_ias19_41','unsupported')
    mutated_component('multi-information-claim-unsupported','multi-employer-deficit.1',{'information_condition_admitted':False},
        'ias19_34_finding_required','partial')
    mutated_component('tax-examination-discount','uncertain-tax-expected-value.1',{'full_information_examination':False},
        'uncertain_tax_admission','partial')
    mutated_component('tax-probability-mass-wrong','uncertain-tax-expected-value.1',
        {'outcomes':[{'deduction':q(100),'probability':q('1/5')},{'deduction':q(40),'probability':q('3/10')}]},'tax_outcome_mass_invalid')
    mutated_component('investment-control-unknown','investment-tax-exception.1',{'reversal_control':None},
        'investment_exception_unresolved','partial')
    # Customer composition failures retain the entire request and unchanged world.
    mutated('customer-credit-repeated-in-invoice','customer-cycle-performance-first.3','advance_credit_reused',
        parameter_changes={'credits':[{'advance_id':'deposit-30','amount':q(15)},
            {'advance_id':'deposit-30','amount':q(15)}]})
    mutated('customer-credit-reused-across-invoices','customer-cycle-performance-first.6','advance_credit_reused',
        parameter_changes={'credits':[{'advance_id':'deposit-30','amount':q(20)}]})
    mutated('customer-gross-bill-treated-as-new-ar','customer-cycle-performance-first.3','wrong_financial_transition',
        journal_lines={'receivable':'80','contract_asset':'-30','contract_liability':'-50'})
    mutated('customer-advance-premature-revenue','customer-cycle-performance-first.1','wrong_financial_transition',
        journal_lines={'cash':'30','product_revenue':'-30'})
    mutated('customer-wrong-contract','customer-cycle-performance-first.4','customer_contract_mismatch',
        parameter_changes={'contract_id':'other-contract'})
    mutated('customer-wrong-invoice','customer-cycle-performance-first.4','invoice_contract_mismatch',
        parameter_changes={'invoice_id':'other-invoice'})
    mutated('customer-wrong-advance','customer-cycle-performance-first.3','advance_contract_mismatch',
        parameter_changes={'credits':[{'advance_id':'other-advance','amount':q(30)}]})
    mutated('customer-invoice-identity-reused','customer-cycle-performance-first.6','invoice_identity_reused',
        parameter_changes={'invoice_id':'bill-80'})
    mutated('customer-settlement-identity-reused','customer-cycle-performance-first.7','settlement_identity_reused',
        parameter_changes={'settlement_id':'cash-20'})
    mutated('customer-settlement-new-event-duplicate','customer-cycle-performance-first.4','settlement_identity_reused',consumed=True)
    mutated('customer-collection-exceeds-right','customer-cycle-performance-first.4','collection_exceeds_right',
        parameter_changes={'cash':q(51)})
    mutated('customer-performance-not-admitted','customer-cycle-performance-first.2','performance_finding_unresolved',
        parameter_changes={'recognition_admitted':False},disposition='partial')
    mutated('customer-invoice-right-unresolved','customer-cycle-performance-first.3','unconditional_right_unresolved',
        parameter_changes={'unconditional_right_admitted':False},disposition='partial')
    mutated('separate-standalone-price-unknown','separate-contract-addition.3','standalone_price_unresolved',
        parameter_changes={'standalone_price_finding':None},disposition='partial')
    mutated('separate-standalone-price-failed','separate-contract-addition.3','separate_contract_test_failed',
        parameter_changes={'standalone_price_finding':False})
    mutated('separate-contract-id-reused','separate-contract-addition.3','separate_contract_identity_reused',
        parameter_changes={'new_contract_id':'original-10'})
    mutated('separate-allocation-id-reused','separate-contract-addition.3','allocation_identity_reused',
        parameter_changes={'allocation_id':'original-ssp'})
    mutated('separate-cross-contract-funding','separate-contract-addition.3','cross_contract_funding_forbidden',consumed=True,
        event_changes={'method_id':'separate.deliver','parameters':{'contract_id':'new-6','units':q(1),'control_passed':True}},
        basis_changes={'method_ref':methods['separate.deliver']})
    mutated('return-cost-recovery-omitted','return-recovery-nonzero-costs.1','wrong_financial_transition',
        journal_lines={'cash':'1000','product_revenue':'-880','refund_liability':'-120',
            'inventory':'-600','cost_of_sales':'600'})
    mutated('return-cost-refund-and-recovery-netted','return-recovery-nonzero-costs.1','wrong_financial_transition',
        journal_lines={'cash':'1000','product_revenue':'-880','refund_liability':'-66',
            'inventory':'-600','cost_of_sales':'546'})
    for label,parameters,code,disposition in [
        ('return-actual-settlement-missing',{'actual_processing_cost':None,'actual_settlement_cash':None},
            'actual_return_settlement_unresolved','partial'),
        ('return-actual-cost-missing',{'actual_processing_cost':None,'actual_settlement_cash':q(120)},
            'actual_return_settlement_unresolved','partial'),
        ('return-settlement-method-unspecified',{'actual_processing_cost':q(12),'actual_settlement_cash':q(120)},
            'nonzero_cost_settlement_method_not_specified','unsupported')]:
        mutated(label,'return-recovery-nonzero-costs.1',code,consumed=True,disposition=disposition,
            event_changes={'method_id':'rcost.settle','parameters':parameters},
            basis_changes={'method_ref':methods['rcost.settle']})
    mutated('variable-constrained-bonus-recognized','variable-distinct-constrained.2','wrong_financial_transition',
        journal_lines={'contract_liability':'4','product_revenue':'-4'})
    mutated('variable-constraint-unknown','variable-distinct-constrained.2','variable_constraint_unresolved',
        parameter_changes={'constraint_finding':'unknown'},disposition='partial')
    mutated('variable-original-bonus-wrong-pool','variable-distinct-modified.6','original_bonus_allocation_required',
        parameter_changes={'allocation_id':'remaining-fixed-pool'})
    mutated('variable-original-bonus-wrong-promise','variable-distinct-modified.6','bonus_promise_mismatch',
        parameter_changes={'bonus_promise_id':'added-bonus'})
    mutated('variable-original-bonus-evenly-redistributed','variable-distinct-modified.7','wrong_financial_transition',
        journal_lines={'contract_liability':'57','product_revenue':'-57','inventory':'-36','cost_of_sales':'36'})
    mutated('variable-added-goods-receive-original-bonus','variable-distinct-modified.8','wrong_financial_transition',
        journal_lines={'contract_liability':'57','product_revenue':'-57','inventory':'-36','cost_of_sales':'36'})
    mutated('variable-integrated-old-allocation','variable-integrated-modified.6','modified_bonus_allocation_required',
        parameter_changes={'allocation_id':'original-ssp'})
    mutated('variable-integrated-old-promise','variable-integrated-modified.6','modified_bonus_allocation_required',
        parameter_changes={'promise_id':'original-construction'})
    mutated('variable-integrated-old-progress','variable-integrated-modified.6','wrong_financial_transition',
        journal_lines={'contract_liability':'4','service_revenue':'-4'})
    mutated('recovery-missing-progress-replaced-zero','unmeasurable-progress-recovery.2','unmeasurable_progress_is_not_zero',
        parameter_changes={'cumulative_progress':q(0)})
    mutated('recovery-missing-progress-replaced-cost-ratio','unmeasurable-progress-recovery.2','unmeasurable_progress_is_not_zero',
        parameter_changes={'cumulative_progress':q('3/10')})
    mutated('recovery-recoverability-unknown','unmeasurable-progress-recovery.2','recoverability_unresolved',
        parameter_changes={'costs_recoverable':None},disposition='partial')
    mutated('recovery-measured-progress-missing','unmeasurable-progress-recovery.3','faithful_progress_unresolved',
        parameter_changes={'cumulative_progress':None},disposition='partial')
    mutated_component('recovery-costs-capitalized','unmeasurable-progress-recovery.2',{'costs_expensed_admitted':False},
        'cost_capitalization_method_required','unsupported')
    mutated('new-event-stale-head', 'production-fifo.2', 'stale_head', start_after=True)
    mutated('advance-duplicate-economic-effect', 'prepaid-bill.1', 'advance_already_allocated', consumed=True)
    mutated('cross-book-component', 'inspection.1', 'owner_binding_mismatch',
        basis_changes={'context_ref': ALIASES['benefits.context']})
    revised = add('View', 'view.superseding-selection', {**body(view), 'revision': 1, 'supersedes_ref': view})
    revised_world = deepcopy(after); revised_world['current_view_ref'] = revised
    revised_world['published_records'] = sorted(set(revised_world['published_records']) | set(closure([revised])))
    rr = response('replay-after-view-change', rq, sub, 'replayed', [receipt], receipt)
    exchange('replay-after-view-change', rq, sub, rr, revised_world, revised_world)
    for label, current in [('current-report-stale', True), ('frozen-report-after-view-change', False)]:
        state_ref = ALIASES['production-fifo.2.state']
        r, su = request(label, 'report.build@1', {'opening_ref': ALIASES['production-fifo.state.0'],
            'state_ref': state_ref, 'view_ref': view, 'require_current': current})
        rr = response(label, r, su, 'rejected' if current else 'completed',
            outputs=[] if current else [ALIASES['production-fifo.report']], code='stale_dependency_view' if current else None)
        exchange(label, r, su, rr, revised_world, revised_world)
    # The old profile's exact valid request remains an invalid request for this lock.
    legacy_path = ROOT / 'data/accounting-master/corporate-portable-20261015/portable-exchanges.json'
    legacy = json.loads(legacy_path.read_text())
    old_request = next(r for r in legacy['record_registry'].values() if r['kind'] == 'OperationRequest')
    p = OUT / 'bytes/legacy-profile-request.json'; p.write_bytes(enc(old_request))
    old_sub = add('Submission', 'submission.legacy-profile', {'blob_ref': blob(p), 'media_type': 'application/json',
        'transport': 'authored_fixture', 'decoder_ref': decoder})
    old_result = response('legacy-profile', rq, old_sub, 'rejected', code='profile_mismatch', valid=False)
    legacy_rejection = {'id': 'legacy-profile-rejected', 'submission_ref': old_sub, 'response_ref': old_result,
        'source_bundle_blob': blob(legacy_path), 'world_before': before, 'world_after': deepcopy(before)}
    predecessor_path = OUT.parent/'corporate/portable-exchanges.json'
    predecessor=json.loads(predecessor_path.read_text())
    v1_request=next(r for r in predecessor['record_registry'].values() if r['kind']=='OperationRequest')
    p=OUT/'bytes/components-v1-request.json';p.write_bytes(enc(v1_request))
    v1_sub=add('Submission','submission.components-v1',{'blob_ref':blob(p),'media_type':'application/json',
        'transport':'authored_fixture','decoder_ref':decoder})
    v1_result=response('components-v1',rq,v1_sub,'rejected',code='profile_mismatch',valid=False)
    v1_rejection={'id':'components-v1-rejected','submission_ref':v1_sub,'response_ref':v1_result,
        'source_bundle_blob':blob(predecessor_path),'world_before':before,'world_after':deepcopy(before)}
    v2_path=OUT.parent/'corporate-v2/portable-exchanges.json'
    v2_packet=json.loads(v2_path.read_text())
    v2_request=next(r for r in v2_packet['record_registry'].values() if r['kind']=='OperationRequest')
    p=OUT/'bytes/components-v2-request.json';p.write_bytes(enc(v2_request))
    v2_sub=add('Submission','submission.components-v2',{'blob_ref':blob(p),'media_type':'application/json',
        'transport':'authored_fixture','decoder_ref':decoder})
    v2_result=response('components-v2',rq,v2_sub,'rejected',code='profile_mismatch',valid=False)
    v2_rejection={'id':'components-v2-rejected','submission_ref':v2_sub,'response_ref':v2_result,
        'source_bundle_blob':blob(v2_path),'world_before':before,'world_after':deepcopy(before)}
    v3_path=OUT.parent/'corporate-v3/portable-exchanges.json'
    v3_packet=json.loads(v3_path.read_text())
    v3_request=next(r for r in v3_packet['record_registry'].values() if r['kind']=='OperationRequest')
    p=OUT/'bytes/components-v3-request.json';p.write_bytes(enc(v3_request))
    v3_sub=add('Submission','submission.components-v3',{'blob_ref':blob(p),'media_type':'application/json',
        'transport':'authored_fixture','decoder_ref':decoder})
    v3_result=response('components-v3',rq,v3_sub,'rejected',code='profile_mismatch',valid=False)
    v3_rejection={'id':'components-v3-rejected','submission_ref':v3_sub,'response_ref':v3_result,
        'source_bundle_blob':blob(v3_path),'world_before':before,'world_after':deepcopy(before)}
    v4_path=OUT.parent/'corporate-v4/portable-exchanges.json'
    v4_packet=json.loads(v4_path.read_text())
    v4_request=next(r for r in v4_packet['record_registry'].values() if r['kind']=='OperationRequest')
    p=OUT/'bytes/components-v4-request.json';p.write_bytes(enc(v4_request))
    v4_sub=add('Submission','submission.components-v4',{'blob_ref':blob(p),'media_type':'application/json',
        'transport':'authored_fixture','decoder_ref':decoder})
    v4_result=response('components-v4',rq,v4_sub,'rejected',code='profile_mismatch',valid=False)
    v4_rejection={'id':'components-v4-rejected','submission_ref':v4_sub,'response_ref':v4_result,
        'source_bundle_blob':blob(v4_path),'world_before':before,'world_after':deepcopy(before)}
    partial_world = deepcopy(before)
    partial_world['event_receipts'] = deepcopy(after['event_receipts'])
    packet = {'evidence_mode': 'specification_example', 'product_implemented': False,
        'schema_lock_ref': lock, 'profile_ref': profile, 'record_registry': REG, 'aliases': ALIASES,
        'blobs': BLOBS, 'exchanges': EX, 'financial_steps': STEPS, 'lost_acknowledgement': lost,
        'invalid_partial_publication': partial_world, 'unbound_submissions': [legacy_rejection,v1_rejection,v2_rejection,v3_rejection,v4_rejection], 'source_pins': []}
    (OUT / 'portable-exchanges.json').write_text(json.dumps(packet, indent=2) + '\n')
    print(json.dumps({'methods': len(methods), 'financial_steps': len(STEPS), 'records': len(REG), 'exchanges': len(EX), 'blobs': len(BLOBS)}))

if __name__ == '__main__': main()
