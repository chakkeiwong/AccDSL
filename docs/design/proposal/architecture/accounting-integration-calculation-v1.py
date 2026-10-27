"""Finite specification calculation, not a product validator or test suite."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import sys
import platform
import time
started = time.monotonic()
root = Path(__file__).resolve().parents[4]
b = root / 'docs/design/proposal/architecture'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda n: json.loads((b / n).read_text())
f = read('accounting-integration-fixtures-v1.json')
legacy = read('accounting-records-fixtures-v1.json')
records = dict(legacy['records'], **f['records'])
checks = []
def check(label, value): checks.append({'id': label, 'passed': bool(value)})
def canon(x): return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
def dig(kind, content): return hashlib.sha256(('accdsl.accounting.integration.v1/' + kind + '\0' + canon(content)).encode('ascii')).hexdigest()
def get(ref, kind):
    row = records[ref]
    check('typed reference ' + ref, row['kind'] == kind)
    return row['content']
def case(ref):
    p = root / ref['file']['path']
    check('pinned source ' + str(p.relative_to(root)), sha(p) == ref['file']['sha256'])
    return next(c for c in json.loads(p.read_text())['cases'] if c['id'] == ref['case_id'])
for ref, row in f['records'].items():
    check('canonical ' + ref, dig(row['kind'], row['content']) == ref)
    reverse = dict(reversed(list(row['content'].items())))
    check('key-order independent ' + ref, dig(row['kind'], reverse) == ref)
order = [f'C{i:02}' for i in range(1, 11)]
precedence = ['ineligible', 'outside_scope', 'unresolved', 'eligible']
route_fields = ['identical_instrument_active_market_quote', 'technique_only_observable_market_data']
pairs = set()
for ex in f['cases']:
    ident = ex['id']; src = case(ex['source_case'])
    request = get(ex['request'], 'request'); assessment = get(ex['assessment'], 'assessment')
    inp = get(request['eligibility'], 'eligibility_input')
    source = case(inp['source_case'])
    v = {k: x['value'] for k, x in source['complete_inputs'].items()}
    check(ident + ' source equality', source == src)
    check(ident + ' ten ordered references', [x['condition_id'] for x in inp['conditions']] == order)
    for ref in inp['conditions']:
        packet = case(ref['case'])['complete_inputs'][ref['condition_id']]
        check(ident + ' value version ' + ref['condition_id'], packet['version'] == ref['value_version'])
        check(ident + ' retained provenance ' + ref['condition_id'], all(k in packet for k in ['value','unknown_reason','provenance','scope','version']))
    for k, value in inp['bindings'].items(): check(ident + ' equality ' + k, request[k] == value)
    ctx = get(request['context'], 'context'); branch = get(request['branch'], 'branch')
    opening = get(request['opening'], 'state'); event = get(request['event'], 'event')
    tm = get(request['time'], 'time'); chart = get(request['chart'], 'chart'); method = get(request['method'], 'method')
    for k, actual, expected in [('B1',event['branch'],request['branch']),('B2',opening['branch'],request['branch']),('B3',event['time'],request['time']),('B4',opening['chart'],request['chart']),('B5',method['authority'],request['authority'])]: check(ident+' '+k, actual == expected)
    check(ident + ' context closure', all(x['context'] == request['context'] for x in [opening, event, branch, chart]))
    check(ident + ' mapped labels', inp['aliases']['source_labels'] == {k:v['C08'][k] for k in ['entity','book','branch']})
    check(ident + ' identity', request['identity'] == {'entity_id':ctx['entity_id'],'book_id':ctx['book_id'],'branch_id':branch['branch_id'],'business_event_id':event['business_event_id']})
    check(ident + ' annual period', ctx['annual_period_start'] == v['C01']['annual_period_start'])
    check(ident + ' recognition date', tm['economic_date'] == v['C04']['recognition_date'])
    check(ident + ' matching amount facts', [Decimal(event[k]) for k in ['price','fair_value','fee']] == [Decimal(v['C06']['price']),Decimal(v['C06']['fair_value']),Decimal(v['C07']['amount'])])
    for er, ar in zip(request['evidence'],request['admissions']):
        ev=get(er,'evidence'); ad=get(ar,'admission')
        check(ident+' admission', ad['evidence']==er and ad['time']==request['time'] and ad['status']=='synthetic_only' and ad['known_at'] is None and ad['reviewed_at'] is None)
    # Independent derivation for this finite fact set, no imported expected statuses.
    statuses = dict.fromkeys(order, 'satisfied_conditionally')
    if not ('2023-01-01' <= v['C01']['annual_period_start'] < '2026-07-01'): statuses['C01']='outside_scope'
    if v['C03']['party_to_contract'] is False: statuses['C03']='ineligible'
    if not v['C05']['rationale_available']: statuses['C05']='unresolved'
    if v['C07']['incremental'] is None: statuses['C07']='unresolved'
    q,o = [v['C09'][k] for k in route_fields]
    if Decimal(v['C06']['price']) == Decimal(v['C06']['fair_value']):
        valuation='not_applicable'; statuses['C09']='not_applicable'; method_state='conditional'
    else:
        pairs.add((q,o))
        valuation='B5.1.2A(a)' if q is True or o is True else 'B5.1.2A(b)' if q is False and o is False else 'unknown'
        statuses['C09']='unresolved' if valuation=='unknown' else 'satisfied_conditionally'
        statuses['C10']='unresolved' if valuation=='unknown' else 'outside_scope'
        method_state='unresolved' if valuation=='unknown' else 'unavailable'
    summary=next((s for s in precedence if s in statuses.values()),'eligible')
    check(ident+' derived ten statuses', {x['condition']:x['status'] for x in assessment['findings']} == statuses)
    check(ident+' derived summary branch method', [assessment['status'],assessment['valuation_branch'],assessment['method_applicability']] == [summary,valuation,method_state])
    check(ident+' all source findings retained', assessment['findings']==src['condition_findings'])
    check(ident+' complete adverse codes', assessment['reason_codes']==[k+':'+s for k,s in statuses.items() if s in precedence])
    check(ident+' assessment linkage', assessment['request']==ex['request'] and assessment['eligibility']==request['eligibility'] and assessment['authority']==request['authority'] and assessment['method']==request['method'])
    mapping={'satisfied_conditionally':'satisfied','not_applicable':'satisfied','unresolved':'unknown','outside_scope':'failed','ineligible':'failed'}
    check(ident+' coarse projection retains detailed result', assessment['preconditions']==[{'name':x['condition'],'status':mapping[x['status']],'support':x['reason']} for x in assessment['findings']])
    for route, value in zip(assessment['valuation_routes'],[q,o]):
        expected='not_applicable' if valuation=='not_applicable' else 'unknown' if value is None else 'qualifies' if value else 'does_not_qualify'
        check(ident+' individual route '+route['field'], route['value'] is value and route['status']==expected)
    submission=get(ex['submission'],'submission'); response=get(ex['response'],'response')
    check(ident+' retained request bytes', json.loads(submission['raw_text'])==request)
    check(ident+' response links', response['request']==ex['request'] and response['assessment']==ex['assessment'] and response['submission']==ex['submission'])
    check(ident+' no posting permission', assessment['posting_permitted'] is False and request['operation']=='assess_only')
    check(ident+' four domains unchanged', ex['before']==ex['after'] and set(ex['before'])=={'identity_index','committed_journals','selected_state','committed_receipts'})
    check(ident+' no invented commitment', all(response[k] is None for k in ['receipt','diagnostic_journal','diagnostic_delta','observed_state']) and response['commit_status']=='not_committed' and response['additional_commit'] is False)
check('all nine valuation pairs', pairs == {(a,b) for a in [True,False,None] for b in [True,False,None]})
repeat=f['repeat_assessment']; original=next(x for x in f['cases'] if x['id']==repeat['first_case'])
check('same request same diagnostic assessment without committed replay', repeat['same_request']==original['request'] and repeat['same_assessment']==original['assessment'] and repeat['receipt'] is None and repeat['status']=='assessed')
replay=case(f['committed_replay']['case']); first=get(replay['responses'][0],'response'); last=get(replay['responses'][-1],'response')
check('retained replay uses committed matching request', first['request']==last['request'] and first['commit_status']=='unknown' and last['commit_status']=='committed' and last['additional_commit'] is False and get(last['receipt'],'receipt')['request']==last['request'])
control=f['cross_version_control']; check('cross-version digest cannot alias', control['legacy_request'] != control['new_domain_on_same_content'] and not control['alias_allowed'])
# The matched predecessor requests do not carry any condition reference; this is
# an information-preservation comparison, not a competing accounting engine.
old_request=get(control['legacy_request'],'request')
check('predecessor fields retained', set(old_request) <= set(get(f['cases'][0]['request'],'request')))
check('matched information gap', 'eligibility' not in old_request and len(get(get(f['cases'][0]['request'],'request')['eligibility'],'eligibility_input')['conditions'])==10)
for p,h in read('accounting-integration-inputs-v1.json')['predecessor_files'].items(): check('preserved '+p, sha(root/p)==h)
for ref in f['references']+f['imports']: check('file reference '+ref['path'], sha(root/ref['path'])==ref['sha256'])
inputs=[Path(__file__).resolve(),b/'accounting-integration-fixtures-v1.json',b/'accounting-integration-contract-v1.md',b/'accounting-integration-inputs-v1.json',b/'accounting-records-fixtures-v1.json',b/'accounting-eligibility-fixtures-v1.json',b/'accounting-eligibility-decision-fixtures-v1.json']
report={'schema_version':'accdsl.accounting.integration.verification.v1','passed':all(c['passed'] for c in checks),'total':len(checks),'passed_count':sum(c['passed'] for c in checks),'checks':checks,'input_hashes':{str(p.relative_to(root)):sha(p) for p in inputs},'manifest':{'command':['python3',*sys.argv],'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'packages':'standard library only'},'git_commit':'N/A: unusable repository marker; input content hashes retained','device_status':'CPU standard-library calculation; no GPU devices queried or frameworks imported','data_version':'pinned synthetic fixtures','seeds':'N/A: deterministic','wall_seconds':time.monotonic()-started,'plan_file':'data/accounting-master/runs/20261005T150545-71a70996/P16/replan-1/plan-0.response.json','result_file':'data/accounting-master/deliverables/P16/result.md','output_file':sys.argv[1]},'limits':'Finite input-derived document calculations only. No runtime validator, accounting validity, forecast validity, scientific ranking or human acceptance.'}
with Path(sys.argv[1]).open('x') as stream: json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'passed':report['passed'],'total':report['total'],'failures':[c for c in checks if not c['passed']]}))
sys.exit(0 if report['passed'] else 1)
