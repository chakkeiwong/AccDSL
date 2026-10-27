"""Finite document construction and Decimal verification, not a runtime engine.
Run from repository root. Exclusive outputs preserve previous evidence.
"""
import copy
import hashlib
import json
import platform
import sys
import time
from decimal import Decimal as D
from pathlib import Path

ROOT = Path.cwd()
OUT = Path('docs/design/proposal/architecture')
START = time.monotonic()

def encoded(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')

def digest(kind, content):
    return hashlib.sha256(('accdsl.accounting.records.v1/' + kind).encode() + b'\0' + encoded(content)).hexdigest()

def key(identity):
    return hashlib.sha256(b'accdsl.replay.v1/key\0' + encoded(identity)).hexdigest()

def file_ref(path):
    return {'path': str(path), 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}

def save(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, indent=2, ensure_ascii=True, allow_nan=False)
        f.write('\n')

records = {}
def add(record_kind, **content):
    ref = digest(record_kind, content)
    records[ref] = {'kind': record_kind, 'content': content}
    return ref

def get(ref):
    return records[ref]['content']

source = file_ref('docs/design/proposal/methods/standards-fixtures-v1.json')
legacy_paths = [OUT / n for n in ['accounting-contract-v1.md', 'accounting-fixtures-v1.json', 'accounting-replay-contract-v1.md', 'accounting-replay-fixtures-v1.json', 'accounting-replay-calculation-v1.py', 'accounting-replay-verification-v1.json']]
legacy = [file_ref(p) for p in legacy_paths]
ctx = add('context', entity_id='example-company', book_id='illustrative-book', currency='CU', unit='units', scale=0, basis='synthetic-A01-FVTPL', annual_period_start='2024-01-01', schema_version=1)
branch = add('branch', context=ctx, branch_id='A', family_id='synthetic-family-1', version=1, admissibility='stipulated')
tm = add('time', economic_date='2024-01-02', reporting_start='2024-01-01', reporting_end='2024-12-31', source_cutoff='2026-10-05T00:00:00Z', review_cutoff='2026-10-05T00:00:00Z', view='restated', basis='synthetic_scenario')
auth = add('authority', version=1, source={'file':file_ref('docs/design/research/p08-v1/aasb9.pdf'), 'locator':'AASB 9 compilation 5, paragraphs 5.1.1 and B5.1.2A; retained example scope'}, paragraphs=['5.1.1','B5.1.2A'], application_scope='For-profit annual period beginning 2024-01-01; applicability stipulated, no new source interpretation', applicability='stipulated')
method = add('method', version=1, name='synthetic-A01-acquisition', authority=auth, rounding='exact_two_decimal_reject_extra_precision', formula='asset=price=fair_value; expense=fee; cash=-(price+fee); equity=0', scope='A01 only; A03 requires resolution of valuation evidence before measurement')
assumptions = add('assumptions', version=1, eligibility='stipulated', cash_settlement=True, no_other_flows=True, branch_admissibility='stipulated', balance_sign='debit_positive')
accounts = [{'account_id':n,'concept_id':'synthetic.'+n,'normal_side':('credit' if n=='equity' else 'debit'),'dimensions':{}} for n in ['cash','asset','expense','equity']]
chart = add('chart', context=ctx, version=1, accounts=accounts)
opening = add('state', context=ctx, branch=branch, chart=chart, sequence=0, balances={'cash':'1000.00','asset':'0.00','expense':'0.00','equity':'-1000.00'})
closing = add('state', context=ctx, branch=branch, chart=chart, sequence=1, balances={'cash':'898.00','asset':'100.00','expense':'2.00','equity':'-1000.00'})
base_world = {'identity_index':{}, 'committed_journals':[], 'selected_state':opening, 'committed_receipts':[]}

def request(case_id, source_case='A01'):
    ev = add('evidence', version=1, source={'file':source,'locator':'acquisitions[id='+source_case+']'}, source_case=source_case, nature='synthetic', observable_valuation=({'status':'unknown','reason':'Retained A03 has no observable valuation evidence'} if source_case=='A03' else {'status':'known','value':True}))
    admission = add('admission', evidence=ev, time=tm, status='synthetic_only', known_at=None, reviewed_at=None, reason='Scenario input, not a historically available company fact')
    ar = assumptions if source_case=='A01' else add('assumptions', **{**get(assumptions),'eligibility':'unresolved'})
    event = add('event', business_event_id=case_id, version=1, kind='cash_acquisition', context=ctx, branch=branch, time=tm, price='100.00', fair_value=('105.00' if source_case=='A03' else '100.00'), fee='2.00', category='FVTPL')
    return add('request', schema_version=1, identity={'entity_id':'example-company','book_id':'illustrative-book','branch_id':'A','business_event_id':case_id}, event=event, opening=opening, context=ctx, branch=branch, time=tm, chart=chart, authority=auth, method=method, evidence=[ev], admissions=[admission], assumptions=ar, lineage=[{'file':source,'locator':'acquisitions[id='+source_case+']'}])

def assessment(req, unresolved=False):
    return add('assessment', request=req, status=('unresolved' if unresolved else 'eligible'), reason_codes=(['TREATMENT_UNRESOLVED'] if unresolved else []), preconditions=[{'name':'classification_and_applicability','status':'satisfied','support':'Stipulated source-scoped synthetic context; not established accounting validity'}, {'name':'valuation_condition','status':('unknown' if unresolved else 'satisfied'),'support':('A03 evidence unknown; measurement not selected' if unresolved else 'A01 price equals fair value; treatment stipulated')}], authority=auth, method=method)

def candidates(req, assess, mismatch=False):
    journal=add('journal', request=req, assessment=assess, context=ctx, branch=branch, chart=chart, purpose='candidate', lines=[{'account_id':n,'concept_id':'synthetic.'+n,'dimensions':{},'debit':de,'credit':cr} for n,de,cr in [('asset','99.00' if mismatch else '100.00','0.00'),('expense','3.00' if mismatch else '2.00','0.00'),('cash','0.00','102.00')]])
    delta=add('delta', request=req, context=ctx, branch=branch, chart=chart, changes={'asset':'100.00','expense':'2.00','cash':'-102.00','equity':'0.00'}, derivation='independent_event_formula')
    return journal,delta

def receipt(req, ass, journal, delta):
    return add('receipt', request=req, assessment=ass, journal=journal, delta=delta, opening=opening, closing=closing, identity_key=key(get(req)['identity']), status='committed', commit=True, sequence=1, encoding_version='accdsl.accounting.records.v1')

def world(rec):
    r=get(rec)
    return {'identity_index':{r['identity_key']:rec},'committed_journals':[r['journal']],'selected_state':r['closing'],'committed_receipts':[rec]}

def status(struct='valid', math='satisfied', comp='specified_exact'):
    return dict(structural_validity=struct, mathematical_status=math, computation_status=comp, empirical_justification='not_established',capability_status='specified_only_no_runtime',accounting_validity='not_assessed',human_acceptance='pending')

def response(sub, req, state, outcome, reason, ass=None, journal=None, delta=None, rec=None, commit='not_committed', extra=False, statuses=None, operation='submit'):
    return add('response', submission=sub, request=req, status=outcome, reason_codes=reason, assessment=ass, diagnostic_journal=journal, diagnostic_delta=delta, receipt=rec, observed_state=state, commit_status=commit, additional_commit=extra, statuses=statuses or status(), metadata={'response_id':outcome+'-'+sub[:12]+'-'+operation,'operation':operation})

def submission(req):
    return add('submission', wire_format='ASCII_JSON',raw_text=encoded(get(req)).decode())

cases=[]
req=request('records-acq-001');sub=submission(req);ass=assessment(req);j,d=candidates(req,ass);rec=receipt(req,ass,j,d)
success=response(sub,req,closing,'committed',[],ass,j,d,rec,'committed',True)
cases.append(dict(id='R01_success',input_submission=sub,commit_signal='acknowledged',before=base_world,after=world(rec),responses=[success],audit_writes=[]))
raw=copy.deepcopy(get(req));del raw['event']
sub_bad=add('submission',wire_format='ASCII_JSON',raw_text=encoded(raw).decode())
bad=response(sub_bad,None,opening,'rejected',['MALFORMED_REQUIRED_FIELD'],statuses=status('invalid','unresolved','not_computed'))
cases.append(dict(id='R02_missing_event',input_submission=sub_bad,commit_signal='not_attempted',before=base_world,after=base_world,responses=[bad],audit_writes=[]))
ru=request('records-acq-003','A03');su=submission(ru);au=assessment(ru,True)
unresolved=response(su,ru,opening,'rejected',['TREATMENT_UNRESOLVED'],au,statuses=status('valid','unresolved','not_computed'))
cases.append(dict(id='R03_unresolved_A03',input_submission=su,commit_signal='not_attempted',before=base_world,after=base_world,responses=[unresolved],audit_writes=[]))
rm=request('records-acq-004');sm=submission(rm);am=assessment(rm);jm,dm=candidates(rm,am,True)
mismatch=response(sm,rm,opening,'rejected',['DELTA_MISMATCH'],am,jm,dm,statuses=status('valid','failed','specified_exact'))
cases.append(dict(id='R04_delta_mismatch',input_submission=sm,commit_signal='not_attempted',before=base_world,after=base_world,responses=[mismatch],audit_writes=[]))
ra=request('records-acq-005');sa=submission(ra);aa=assessment(ra);ja,da=candidates(ra,aa)
aborted=response(sa,ra,opening,'aborted',['COMMIT_ABORT_CONFIRMED'],aa,ja,da)
cases.append(dict(id='R05_confirmed_abort',input_submission=sa,commit_signal='abort_confirmed_no_publication',before=base_world,after=base_world,responses=[aborted],audit_writes=[]))
unknown=response(sub,req,None,'commit_unknown',['ACKNOWLEDGEMENT_LOST'],ass,j,d,None,'unknown',None)
lookup=response(sub,req,closing,'replayed',[],ass,None,None,rec,'committed',False,operation='lookup')
cases.append(dict(id='R06_lost_ack_then_lookup',input_submission=sub,commit_signal='committed_ack_lost',before=base_world,after=world(rec),responses=[unknown,lookup],lookup={'identity':get(req)['identity'],'expected_request':req},after_lookup=world(rec),audit_writes=[]))
fixture={'schema_version':'accdsl.accounting.records.fixtures.v1','scope':'Six finite synthetic specified exchanges, no runtime execution','source_bindings':[source,file_ref('docs/design/proposal/methods/standards-source-register-v1.json')], 'preserved_legacy_files':legacy,'records':records,'cases':cases,'replay_examples':{'file':file_ref(OUT/'accounting-replay-fixtures-v1.json'),'case_ids':['AR01_control','AR02_exact_retry','AR03_changed_payload','AR04_new_stale','AR05_other_branch']},'supersedes':['accounting-fixtures-v1.json:AC01_A01_eligible_fvtpl (complete exchange only)','accounting-fixtures-v1.json:AC03_A03_missing_valuation_evidence (complete exchange only)'],'limits':['Eligibility and branch admissibility stipulated; A03 unresolved','No historical evidence admission, runtime atomicity, accounting validity, forecasting or human acceptance']}
fixture_path=OUT/'accounting-records-fixtures-v1.json'
save(fixture_path,fixture)
# Reload saved bytes: verification concerns the document actually saved.
fixture=json.loads(fixture_path.read_text());records=fixture['records'];checks=[]
def check(name,condition):
    checks.append({'id':name,'passed':bool(condition)})
# Typed reference closure, plus every nested file binding.
refs={'branch':{'context':'context'},'chart':{'context':'context'},'method':{'authority':'authority'},'admission':{'evidence':'evidence','time':'time'},'state':{'context':'context','branch':'branch','chart':'chart'},'event':{'context':'context','branch':'branch','time':'time'},'request':{'event':'event','opening':'state','context':'context','branch':'branch','time':'time','chart':'chart','authority':'authority','method':'method','assumptions':'assumptions'},'assessment':{'request':'request','authority':'authority','method':'method'},'journal':{'request':'request','assessment':'assessment','context':'context','branch':'branch','chart':'chart'},'delta':{'request':'request','context':'context','branch':'branch','chart':'chart'},'receipt':{'request':'request','assessment':'assessment','journal':'journal','delta':'delta','opening':'state','closing':'state'},'response':{'submission':'submission','request':'request','assessment':'assessment','diagnostic_journal':'journal','diagnostic_delta':'delta','receipt':'receipt','observed_state':'state'}}
def files(x):
    if isinstance(x,dict):
        if 'path' in x and 'sha256' in x:check('file '+x['path'],file_ref(x['path'])['sha256']==x['sha256'])
        for v in x.values():files(v)
    elif isinstance(x,list):
        for v in x:files(v)
files(fixture)
for h,r in records.items():
    c=r['content'];k=r['kind'];check('digest '+h,digest(k,c)==h)
    for f,t in refs.get(k,{}).items():
        v=c[f];check('typed '+h+':'+f,v is None and k=='response' or v in records and records[v]['kind']==t)
    if k=='request':
        for f,t in [('evidence','evidence'),('admissions','admission')]:
            check('array '+h+f,bool(c[f]) and all(v in records and records[v]['kind']==t for v in c[f]))
        e=get(c['event']);b=get(c['branch']);cx=get(c['context']);check('identity '+h,c['identity']==dict(entity_id=cx['entity_id'],book_id=cx['book_id'],branch_id=b['branch_id'],business_event_id=e['business_event_id']))
        check('context '+h,all(get(c[x])['context']==c['context'] for x in ['event','opening','branch','chart']))
        check('admission '+h,len(c['evidence'])==len(c['admissions']) and all(get(a)['evidence']==ev and get(a)['time']==c['time'] for a,ev in zip(c['admissions'],c['evidence'])))
    if k=='state':check('trial balance '+h,sum(map(D,c['balances'].values()))==0)
    if k=='receipt':
        rq=get(c['request']);check('receipt identity '+h,c['identity_key']==key(rq['identity']) and c['opening']==rq['opening'])
        check('receipt dependencies '+h,all(get(c[n])['request']==c['request'] for n in ['assessment','journal','delta']))
        op=get(c['opening']);cl=get(c['closing']);delta=get(c['delta'])['changes']
        check('rollforward '+h,cl['sequence']==op['sequence']+1 and all(D(cl['balances'][n])==D(op['balances'][n])+D(delta[n]) for n in delta))
        check('immutable receipt '+h,c['status']=='committed' and c['commit'] is True)
    if k=='response':check('status vocabulary '+h,c['statuses']['mathematical_status'] in ['satisfied','failed','undefined','unresolved'] and c['statuses']['computation_status'] in ['specified_exact','specified_partial','symbolic','not_computed'])
for case in fixture['cases']:
    ident=case['id'];resp=get(case['responses'][0]);raw=json.loads(get(case['input_submission'])['raw_text'])
    if 'event' not in raw:
        expected='rejected';reason=['MALFORMED_REQUIRED_FIELD'];check(ident+' no canonical request',resp['request'] is None)
    else:
        rq=resp['request'];check(ident+' wire fingerprint',digest('request',raw)==rq)
        event=get(raw['event']);ev=get(raw['evidence'][0]);unknown_fact=ev['observable_valuation']['status']=='unknown'
        if unknown_fact:
            expected='rejected';reason=['TREATMENT_UNRESOLVED'];check(ident+' no candidate',resp['diagnostic_journal'] is None and resp['diagnostic_delta'] is None)
        else:
            expected_delta={'asset':D(event['price']),'expense':D(event['fee']),'cash':-D(event['price'])-D(event['fee']),'equity':D(0)}
            jrn=get(resp['diagnostic_journal']);posted=dict.fromkeys(expected_delta,D(0))
            for line in jrn['lines']:
                posted[line['account_id']]+=D(line['debit'])-D(line['credit'])
                check(ident+' line '+line['account_id'],line['concept_id']=='synthetic.'+line['account_id'] and line['dimensions']=={} and ((D(line['debit'])>0 and D(line['credit'])==0) or (D(line['credit'])>0 and D(line['debit'])==0)))
            check(ident+' balanced',sum(posted.values())==0)
            check(ident+' independent delta',{n:D(v) for n,v in get(resp['diagnostic_delta'])['changes'].items()}==expected_delta)
            if posted!=expected_delta:expected='rejected';reason=['DELTA_MISMATCH']
            elif case['commit_signal']=='abort_confirmed_no_publication':expected='aborted';reason=['COMMIT_ABORT_CONFIRMED']
            elif case['commit_signal']=='committed_ack_lost':expected='commit_unknown';reason=['ACKNOWLEDGEMENT_LOST']
            else:expected='committed';reason=[]
    check(ident+' derived response',resp['status']==expected and resp['reason_codes']==reason)
    if expected in ['rejected','aborted']:
        check(ident+' four parts unchanged',case['before']==case['after'] and resp['receipt'] is None and resp['commit_status']=='not_committed' and resp['additional_commit'] is False)
    else:
        rr=resp['receipt'] if expected=='committed' else get(case['responses'][1])['receipt']
        check(ident+' complete publication',case['after']==world(rr) and case['before']==base_world)
        if expected=='commit_unknown':
            replay=get(case['responses'][1]);check(ident+' honest uncertainty',resp['receipt'] is None and resp['observed_state'] is None and resp['commit_status']=='unknown' and resp['additional_commit'] is None)
            check(ident+' lookup resolves without write',replay['status']=='replayed' and replay['additional_commit'] is False and case['after_lookup']==case['after'] and replay['receipt']==rec and get(replay['receipt'])['request']==case['lookup']['expected_request'])
    check(ident+' audit separate',case['audit_writes']==[])
# Matched balance-only counterexamples: neither zero sum resolves missing facts nor wrong allocations.
check('A03 price and FV retained',get(get(ru)['event'])['fair_value']=='105.00' and get(get(ru)['evidence'][0])['observable_valuation']['status']=='unknown')
check('A03 balanced comparator insufficient',D('100')+D('2')-D('102')==0 and get(au)['status']=='unresolved')
check('R04 balanced comparator insufficient',D('99')+D('3')-D('102')==0 and D('99')!=D('100'))
report={'schema_version':'accdsl.accounting.records.verification.v1','passed':all(x['passed'] for x in checks),'tests':len(checks),'checks':checks,'fixture':file_ref(fixture_path),'preserved_legacy_files':legacy,'manifest':{'git_commit':'N/A: project .git marker is unusable; no initialization authorized','command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/accounting-records-calculation-v1.py','environment':platform.python_version()+' standard library','cpu_gpu':'CPU-only Decimal/JSON; no accelerator framework imported or device detection','data_version':source,'random_seeds':'N/A deterministic','wall_seconds':round(time.monotonic()-START,6),'plan':'data/accounting-master/runs/20261005T133743-c8a796f3/P16/approved-plan.json','result':'data/accounting-master/deliverables/P16/result.md','outputs':[str(fixture_path),str(OUT/'accounting-records-verification-v1.json')]},'limits':['Finite calculations verify these saved records and traces only','No runtime crash/recovery execution or accounting eligibility validation']}
save(OUT/'accounting-records-verification-v1.json',report)
print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[c['id'] for c in checks if not c['passed']],'records':len(records),'cases':len(cases)}))
sys.exit(0 if report['passed'] else 1)
