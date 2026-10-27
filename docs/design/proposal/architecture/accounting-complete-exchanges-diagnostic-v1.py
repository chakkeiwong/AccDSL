"""Finite proposal-document checks; no product endpoint or accounting engine.

Derive adverse findings from submitted fields. Retained native comparators supply
unchanged treatment facts, not an oracle for the malformed/context predicates.
"""
import copy
import datetime
import hashlib
import importlib.util
import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

START = time.monotonic()
B = Path('docs/design/proposal/architecture')
D = 'accdsl.accounting.integration.v1'
checks, results, used = [], [], {str(Path(__file__))}


def load(path):
    used.add(str(path))
    return json.loads(Path(path).read_text())


def check(label, value):
    checks.append({'id':label,'passed':bool(value)})


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)


def digest(domain, kind, value):
    return hashlib.sha256((domain+'/'+kind+'\0'+canonical(value)).encode('ascii')).hexdigest()


def pins(value):
    if isinstance(value,dict):
        if 'path' in value and 'sha256' in value:
            p=Path(value['path']);used.add(str(p))
            check('file pin '+str(p),p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256'])
        for child in value.values():pins(child)
    elif isinstance(value,list):
        for child in value:pins(child)


f=load(B/'accounting-complete-exchanges-v1.json')
pins(f)
registry={}
for ref in f['imports']:
    for h,row in load(ref['path'])['records'].items():
        domains=[d for d in [D,'accdsl.accounting.records.v1','accdsl.accounting.record.v1'] if digest(d,row['kind'],row['content'])==h]
        check('unambiguous imported digest '+h,len(domains)==1)
        registry[h]={**row,'domain':domains[0]}
registry.update(f['records'])
for h,row in f['records'].items():
    check('new record digest '+h,digest(row['domain'],row['kind'],row['content'])==h)
old=load(B/'accounting-integration-fixtures-v2.json')
I={c['id']:c for c in old['cases']}
sources={c['id']:c for c in load(f['source_packets']['path'])['cases']}
field_path=B/'accounting-integration-c09-c10-conditions-field-diagnostic-v1.py'
used.add(str(field_path))
spec=importlib.util.spec_from_file_location('finite_field_diagnostic',field_path)
field=importlib.util.module_from_spec(spec)
spec.loader.exec_module(field)
ROUTES=['identical_instrument_active_market_quote','technique_only_observable_market_data']


def source(ref):
    return next(c for c in load(ref['file']['path'])['cases'] if c['id']==ref['case_id'])['complete_inputs']


def content(h):
    return registry[h]['content']


def native_branch(c09):
    if not c09['required']:return 'not_applicable'
    a,b=(c09[k] for k in ROUTES)
    if a is True or b is True:return 'B5.1.2A(a)'
    if a is False and b is False:return 'B5.1.2A(b)'
    return 'unknown'


def context_findings(s,q):
    found=[]
    def need(path,ok,code='SOURCE_CONTEXT_MISMATCH'):
        if not ok:found.append({'stage':'bindings','path':path,'code':code})
    values={k:v['value'] for k,v in s.items()}
    ev,ctx,tm=content(q['event']),content(q['context']),content(q['time'])
    el=content(q['eligibility'])
    c1=values['C01'];day=datetime.date.fromisoformat(c1['annual_period_start'])
    need('source/C01/value/annual_period_start',c1['annual_period_start']==ctx['annual_period_start'])
    need('source/C01/value/within_retained_window',c1['within_retained_window']==(datetime.date(2023,1,1)<=day<datetime.date(2026,7,1)))
    need('source/C04/value/recognition_date',values['C04']['recognition_date']==tm['economic_date'])
    need('source/C05/value/category',values['C05']['category']==ev['category'])
    for name in ['price','fair_value']:
        need('source/C06/value/'+name,Fraction(values['C06'][name])==Fraction(ev[name]))
    need('source/C06/value/valuation_date',values['C06']['valuation_date']==tm['economic_date'])
    need('source/C07/value/amount',Fraction(values['C07']['amount'])==Fraction(ev['fee']))
    for name in ['currency','unit','scale']:
        need('source/C08/value/'+name,values['C08'][name]==ctx[name])
    for name in ['entity','book','branch']:
        need('source/C08/value/'+name,values['C08'][name]==el['aliases']['source_labels'][name])
    c9=values['C09'];required=Fraction(values['C06']['price'])!=Fraction(values['C06']['fair_value'])
    need('source/C09/value/required',c9['required'] is required)
    # Branch/OR projection depend on a consistent required controller. This is
    # an explicit guard, not coercion of an invalid controller to false.
    if c9['required'] is required:
        need('source/C09/value/branch',c9['branch']==native_branch(c9))
        if not required:
            for k in ROUTES:need('source/C09/value/'+k,c9[k] is None)
        evidence=content(q['evidence'][0])['observable_valuation']
        if not required or native_branch(c9)=='unknown':
            need('evidence/observable_valuation',evidence['status']=='unknown')
        else:
            need('evidence/observable_valuation',evidence['status']=='known' and evidence['value'] is (native_branch(c9)=='B5.1.2A(a)'))
    for flag in ['unequal_price_a_method_available','unequal_price_b_method_available']:
        need('source/C10/value/'+flag,values['C10'][flag] is False,'METHOD_CAPABILITY_MISMATCH')
    return sorted(found,key=lambda d:(d['path'],d['code']))


def closure(q,label):
    reached=set()
    def walk(value):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value:
                pins(value);return
            for child in value.values():walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
        elif isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value):
            check(label+' reference resolves '+value,value in registry)
            if value in registry and value not in reached:
                reached.add(value);walk(content(value))
    walk(q)
    return sorted(reached)


for c in old['cases']:
    q=content(c['request']);s=source(c['source_case'])
    shape=field.derive({k:s[k] for k in ['C09','C10']})
    findings=context_findings(s,q) if not shape else shape
    check(c['id']+' retained control satisfies new predicates',not findings)
    if findings:results.append({'id':c['id'],'derived':findings})

for x in f['exchanges']:
    label=x['id'];base=I[x['control']['case_id']];q=json.loads(x['raw_request'])
    check(label+' request bytes',canonical(q)==x['raw_request'] and digest(D,'request',q)==x['request'])
    check(label+' submitted bytes',content(x['submission'])['raw_text']==x['raw_request'])
    check(label+' exact closure',closure(q,label)==x['required_record_closure'])
    s=source(x['source_case']);before=source(base['source_case']);expected=copy.deepcopy(before)
    for change in x['mutations']:
        parts=change['path'].split('/')[1:];parent=expected
        for p in parts[:-1]:parent=parent[p]
        check(label+' mutation prior '+change['path'],parent[parts[-1]]==change['before'])
        if change['op']=='remove':del parent[parts[-1]]
        else:parent[parts[-1]]=change['after']
    check(label+' isolated source changes',s==expected)
    eligibility=content(q['eligibility'])
    check(label+' full condition order',[c['condition_id'] for c in eligibility['conditions']]==['C%02d'%i for i in range(1,11)])
    check(label+' refreshed source refs',eligibility['source_case']==x['source_case'] and all(c['case']==x['source_case'] for c in eligibility['conditions']))
    findings=[{k:d[k] for k in ['stage','path','code']} for d in field.derive({k:s[k] for k in ['C09','C10'] if k in s})]
    if not findings:
        check(label+' source version bindings',all(c['value_version']==s[c['condition_id']]['version'] for c in eligibility['conditions']))
        findings=context_findings(s,q)
    check(label+' derived findings',findings==x['expected_diagnostics'])
    response=content(x['response'])
    check(label+' committed domains unchanged',x['before']==x['after']==base['before'])
    check(label+' no posting or receipt publication',not response['additional_commit'] and response['commit_status']=='not_committed' and all(response[k] is None for k in ['diagnostic_journal','diagnostic_delta','receipt','observed_state']))
    check(label+' derived validation before lookup',x['lookup']==x['freshness']==x['assess']==(not findings))
    if findings:
        check(label+' invalid request not published',response['request'] is None and response['assessment'] is None and x['assessment'] is None and response['status']=='rejected')
        check(label+' rejection status dimensions',response['statuses']==dict(structural_validity='invalid',mathematical_status='unresolved',computation_status='not_computed',empirical_justification='not_established',capability_status='specified_only_no_runtime',accounting_validity='not_assessed',human_acceptance='pending'))
        check(label+' complete reason codes',response['reason_codes']==list(dict.fromkeys(d['code'] for d in findings)))
    else:
        original=content(base['assessment']);want=copy.deepcopy(original)
        want.update(request=x['request'],eligibility=q['eligibility'],source_assessment=x['source_case'])
        check(label+' complete assessment preservation',content(x['assessment'])==want)
        want_response=copy.deepcopy(content(base['response']));want_response.update(submission=x['submission'],request=x['request'],assessment=x['assessment'])
        check(label+' complete response preservation',response==want_response)
        # Only explanatory reasons may differ in these positive variations.
        original_facts=copy.deepcopy(before);new_facts=copy.deepcopy(s)
        for fact in [original_facts,new_facts]:
            fact['C09'].pop('unknown_reason');fact['C09']['value'].pop('unknown_reason');fact['C10'].pop('unknown_reason')
        check(label+' economic facts unchanged',original_facts==new_facts)
    results.append({'id':label,'derived':findings,'lookup':not findings})

# The V records were already materialized. Inspect their actual candidate data,
# without using their IDs, mutation paths, declared stages or expected findings
# to select a predicate.
v=load(f['retained_adverse_outputs']['path'])


def adverse_outcome(reg,q,output_digest):
    def rec(h):return reg[h]['content']
    if reg[q['eligibility']]['kind']!='eligibility_input':return 'dependencies','INVALID_REFERENCE_KIND'
    e=rec(q['eligibility'])
    if q['operation']!='assess_only' or e['profile']!='acquisition-conditions-v1':return 'shape','UNSUPPORTED_PROFILE_OPERATION'
    if type(e['schema_version']) is not int:return 'shape','INVALID_RECORD_VERSION_TYPE'
    if e['aliases']['scope']!='synthetic_only':return 'shape','INVALID_ALIAS_SCOPE'
    if [c['condition_id'] for c in e['conditions']]!=['C%02d'%i for i in range(1,11)]:return 'shape','INVALID_CONDITION_ORDER'
    if not {'context','branch','time','chart','authority','method','assumptions','evidence','admissions'}.issubset(e['bindings']):return 'shape','MISSING_FIELD'
    if any(e['aliases']['identity'][k]!=q['identity'][k] for k in ['entity_id','book_id','branch_id']):return 'bindings','ELIGIBILITY_BINDING_MISMATCH'
    s=source(e['source_case'])
    if any(e['aliases']['source_labels'][k]!=s['C08']['value'][k] for k in ['entity','book','branch']):return 'bindings','ELIGIBILITY_BINDING_MISMATCH'
    if any(c['case']!=e['source_case'] for c in e['conditions']):return 'bindings','CONDITION_CASE_MISMATCH'
    if output_digest is None:return None
    r=reg[output_digest]
    if r['kind']=='response':
        z=r['content']
        if z['additional_commit'] or z['commit_status']!='not_committed':return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
        a=rec(z['assessment'])
    else:a=r['content']
    if a['posting_permitted']:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
    ids=[x['condition'] for x in a['findings']]
    if ids!=['C%02d'%i for i in range(1,11)]:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
    statuses={x['status'] for x in a['findings']}
    summary=next((k for k in ['ineligible','outside_scope','unresolved'] if k in statuses),'eligible')
    if a['status']!=summary:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
    for route in a['valuation_routes']:
        value=s['C09']['value'][route['field']]
        if route['value'] is not value:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
    if a['diagnostic_example'] is not None and summary!='eligible':return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
    return None


for x in v['cases']:
    reg={**registry,**x['candidate_records']};q=json.loads(x['raw_request'])
    actual=adverse_outcome(reg,q,x.get('candidate_output_digest'))
    wanted=(x['expected']['stage'],x['expected']['code'])
    check(x['id']+' candidate-derived disposition',actual==wanted)
    check(x['id']+' unchanged four domains',x['expected']['before']==x['expected']['after'])
    results.append({'id':x['id'],'derived':actual})

out=Path(sys.argv[1]);failures=[c for c in checks if not c['passed']]
report={'passed':not failures,'checks':checks,'failures':failures,'derived_results':results,
        'input_hashes':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(used)},
        'manifest':{'command':'python3 '+str(Path(__file__))+' '+str(out),
                    'environment':platform.python_version()+' standard library','cpu_gpu':'CPU only; no accelerator framework imported',
                    'git_commit':'N/A: existing unusable repository marker','random_seeds':'N/A deterministic examples',
                    'wall_seconds':round(time.monotonic()-START,4),'plan':'docs/plans/accounting-p16-direct-execution-20261006.md','result':str(out)},
        'scope':'27 complete new exchanges, 17 retained controls, 16 independently classified V outcomes; finite document checks only. No arbitrary validator, runtime, accounting-authority or phase acceptance.'}
with out.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'passed':not failures,'checks':len(checks),'failures':failures,'result':str(out)}))
sys.exit(1 if failures else 0)
