"""Pure documentary settlement checks; no product endpoint or source mutation."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from jsonschema import Draft202012Validator, FormatChecker

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'data/accounting-master/corporate-portable-20261015/portable-exchanges.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value):
    result = Q(int(value['n']), int(value['d']))
    if (str(result.numerator), str(result.denominator)) != (value['n'], value['d']):
        raise ValueError('Noncanonical rational')
    return result


def at(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def evaluate(body, validator):
    def result(status, reason, **extra):
        return {'status': status, 'reason': reason, **extra}

    if list(validator.iter_errors(body)):
        return result('invalid_input', 'schema')
    opening, claim, funding, decision = (body[k] for k in ('opening', 'claim', 'funding', 'decision'))
    evidence = body['evidence']
    refs = [body['assumption_ref'], opening['source_ref'], claim['source_ref']]
    if funding['tag'] != 'unknown':
        refs.append(funding['source_ref'])
    if decision['policy'] == 'explicit_draw':
        refs.append(decision['authorisation_ref'])
    if any(r not in evidence for r in refs):
        return result('invalid_input', 'reference_closure')
    if evidence[body['assumption_ref']]['kind'] != 'scenario_assumption':
        return result('invalid_input', 'scenario_assumption_required')
    if decision['policy'] == 'explicit_draw' and evidence[decision['authorisation_ref']]['kind'] != 'scenario_assumption':
        return result('invalid_input', 'explicit_draw_authorisation_required')
    if claim['context'] != body['context'] or (funding['tag'] == 'facility' and funding['context'] != body['context']):
        return result('invalid_input', 'context_mismatch')
    instant, payment = at(body['decision_at']), at(body['payment_at'])
    if at(body['information_as_of']) > instant or at(opening['snapshot_at']) != instant or instant > payment or at(claim['due_at']) != payment:
        return result('invalid_input', 'information_or_payment_time')
    try:
        balances = {k: q(opening[k]) for k in ('cash', 'payables', 'other_payables', 'debt')}
        amounts = {k: q(claim[k]) for k in ('recognised', 'adjustments', 'settled', 'outstanding')}
        limits = {k: q(funding[k]) for k in ('limit', 'drawn', 'reserved')} if funding['tag'] == 'facility' else {}
        draw = q(decision['amount']) if decision['policy'] == 'explicit_draw' else Q(0)
    except ValueError:
        return result('invalid_input', 'noncanonical_amount')
    if any(v < 0 for v in balances.values()) or any(amounts[k] < 0 for k in ('recognised', 'settled', 'outstanding')) or any(v < 0 for v in limits.values()) or draw < 0:
        return result('invalid_input', 'negative_amount')
    if amounts['outstanding'] != amounts['recognised'] + amounts['adjustments'] - amounts['settled'] or amounts['outstanding'] <= 0:
        return result('invalid_input', 'claim_rollforward')
    if balances['payables'] != balances['other_payables'] + amounts['outstanding']:
        return result('invalid_input', 'payable_control')
    if limits and (limits['drawn'] + limits['reserved'] > limits['limit'] or limits['drawn'] > balances['debt'] or at(funding['available_from']) >= at(funding['expires_exclusive'])):
        return result('invalid_input', 'inconsistent_facility')
    due = amounts['outstanding']
    if decision['policy'] == 'cash_only':
        if balances['cash'] < due:
            status = 'unresolved_funding' if funding['tag'] == 'unknown' else 'infeasible_under_policy'
            return result(status, 'cash_shortfall', shortfall=due-balances['cash'])
    else:
        settles = at(decision['settles_at'])
        if settles < instant or draw <= 0 or (settles == payment and not decision['draw_before_payment']):
            return result('invalid_input', 'draw_timing_or_amount')
        if settles > payment:
            return result('infeasible_under_policy', 'draw_arrives_after_payment')
        if funding['tag'] == 'unknown':
            return result('unresolved_funding', 'unknown_facility')
        if funding['tag'] == 'known_none':
            return result('infeasible_under_policy', 'no_facility')
        if decision['facility_id'] != funding['id']:
            return result('invalid_input', 'facility_reference')
        if not at(funding['available_from']) <= settles < at(funding['expires_exclusive']):
            return result('infeasible_under_policy', 'draw_window')
        if draw > limits['limit'] - limits['drawn'] - limits['reserved']:
            return result('infeasible_under_policy', 'insufficient_headroom')
        if funding['eligibility'] is False:
            return result('infeasible_under_policy', 'known_ineligible')
        if isinstance(funding['eligibility'], dict):
            return result('unresolved_funding', 'unknown_eligibility')
        if balances['cash'] + draw < due:
            return result('infeasible_under_policy', 'chosen_draw_insufficient')
    journals = []
    if draw:
        journals.append({'event': 'draw_settlement', 'facility_id': funding['id'],
                         'at': decision['settles_at'], 'cash_class': 'financing',
                         'lines': {'cash': draw, 'debt': -draw}})
    journals.append({'event': 'supplier_settlement', 'claim_id': claim['id'],
                     'at': body['payment_at'], 'after': ['draw_settlement'] if draw else [],
                     'cash_class': 'operating', 'lines': {'payables': due, 'cash': -due}})
    return result('proposed', 'conditional_on_successful_settlement', committed=False,
                  journals=journals, conditional_after={
                      'cash': balances['cash'] + draw - due, 'payables': balances['payables'] - due,
                      'debt': balances['debt'] + draw, 'claim_outstanding': Q(0),
                      'claim_settled': amounts['settled'] + due,
                      'facility_drawn': limits['drawn'] + draw if limits else None},
                  flows={'operating': -due, 'financing': draw})


def main():
    started = datetime.now(timezone.utc).isoformat(); timer = time.perf_counter()
    schema = json.loads((OUT/'schema.json').read_text()); Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    packet = json.loads((OUT/'cases.json').read_text()); source_hash = sha(SOURCE)
    source = json.loads(SOURCE.read_text()); records = source['record_registry']
    projection = records[source['aliases']['projection.stress7']['digest']]['body']
    original = records[projection['opening_ref']['digest']]['body']
    purchase = next(j for j in projection['proposed_journals'] if j['event_kind'] == 'purchase')
    purchase_payable = sum((q(l['signed_amount']['constant']) for l in purchase['lines'] if l['account']=='payables'),Q(0))
    base = packet['cases'][0]['body']; checks=[]; outputs={}

    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})

    check('retained_cash_and_payables_bridge', q(base['opening']['cash']) == q(original['balances']['cash']) and q(base['opening']['payables']) == -(q(original['balances']['payables'])+purchase_payable))
    for case in packet['cases']:
        body=case['body']; before=deepcopy(body); output=evaluate(body,validator); outputs[case['id']]=output
        check(case['id']+':status', output['status']==case['expected'])
        check(case['id']+':input_unchanged', body==before)
        if output['status']=='proposed':
            check(case['id']+':balanced_journals', all(sum(j['lines'].values(),Q(0))==0 for j in output['journals']))
            after=output['conditional_after']
            check(case['id']+':cash_bridge', q(body['opening']['cash'])+sum(output['flows'].values(),Q(0))==after['cash'])
            check(case['id']+':claim_and_control', after['claim_outstanding']==0 and after['payables']==q(body['opening']['other_payables']))
            check(case['id']+':not_committed', output['committed'] is False)
    funded=outputs['funded_payment']
    check('exact_funded_consequences', funded['conditional_after']=={'cash':Q(0),'payables':Q(40),'debt':Q(927,5),'claim_outstanding':Q(0),'claim_settled':Q(160),'facility_drawn':Q(427,5)})
    check('cash_flow_classification', funded['flows']=={'operating':Q(-160),'financing':Q(427,5)})
    check('no_whole_payment_revenue_or_profit_post', all(set(j['lines']) <= {'cash','debt','payables'} for j in funded['journals']))
    check('source_evidence_bound', base['evidence']['retained']['sha256']==source_hash)
    check('source_unchanged', sha(SOURCE)==source_hash)
    report={'passed':all(x['passed'] for x in checks),'cases':len(outputs),'checks':checks,'outputs':outputs,
            'scope':'Pure documentary proposal check; no product registration, real lending facts or accounting commit'}
    (OUT/'checks.json').write_text(json.dumps(report,indent=2,default=str)+chr(10))
    manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'command':'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/settlement-decision-20261023/verify.py',
              'environment':{'python':platform.python_version(),'executable':sys.executable,'jsonschema':importlib.metadata.version('jsonschema')},
              'cpu_gpu':'CPU only; GPU intentionally hidden; no ML framework imported','cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),
              'random_seeds':'N/A: deterministic exact checks','data_version':source_hash,'started_utc':started,'wall_seconds':time.perf_counter()-timer,
              'plan_file':'docs/design/proposal/architecture/settlement-decision-draft-20261023.md','result_file':str((OUT/'result.md').relative_to(ROOT)),
              'artifacts':{p.name:sha(p) for p in [OUT/'schema.json',OUT/'cases.json',OUT/'prepare.py',Path(__file__),OUT/'checks.json']}}
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps({'passed':report['passed'],'cases':len(outputs),'checks':len(checks),'failures':[c for c in checks if not c['passed']]}))
    if not report['passed']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
