"""Compare independent authoring forms and bind their meaning to checked traces."""
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
from authoring import AuthoringError, lower, rational

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'data/accounting-master/corporate-portable-20261015/portable-exchanges.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def q(value):
    rational(value['n']+'/'+value['d'])
    return Q(int(value['n']),int(value['d']))
def at(value): return datetime.fromisoformat(value.replace('Z','+00:00'))


def validate(body, validator, source):
    if list(validator.iter_errors(body)): return {'status':'invalid','reason':'schema'}
    if body['source']!={'path':str(SOURCE.relative_to(ROOT)),'sha256':sha(SOURCE)}:
        return {'status':'invalid','reason':'source_binding'}
    ref=source['aliases'].get(body['projection']['alias'])
    if not ref or ref['kind']!='Projection' or ref['digest']!=body['projection']['digest']:
        return {'status':'invalid','reason':'projection_binding'}
    projection=source['record_registry'][ref['digest']]['body']
    opening=source['record_registry'][projection['opening_ref']['digest']]['body']
    context=source['record_registry'][opening['context_ref']['digest']]['body']
    if body['context']!={k:context[k] for k in ('entity','book','currency')}:
        return {'status':'invalid','reason':'context'}
    try:
        share=q(body['share']); facility={k:q(body['facility'][k]) for k in ('limit','drawn','reserved')}
        loan={k:q(body['loan'][k]) for k in ('principal','annual_rate','fee')}; tax=q(body['tax']['rate'])
        claims=[(c,q(c['recognised']),q(c['settlement'])) for c in body['claims']]
    except (ValueError,AuthoringError): return {'status':'invalid','reason':'rational'}
    if not 0<=share<=1 or not 0<=tax<=1 or loan['principal']<=0 or loan['annual_rate']<0 or any(v<0 for v in facility.values()):
        return {'status':'invalid','reason':'amount_domain'}
    if loan['fee']!=0: return {'status':'unsupported','reason':'fee_method'}
    if body['loan']['facility_id']!=body['facility']['id'] or loan['principal']>facility['limit']-facility['drawn']-facility['reserved']:
        return {'status':'invalid','reason':'facility_capacity'}
    if len({c['id'] for c,_,_ in claims})!=len(claims) or any(r<0 or s<0 or s>r for _,r,s in claims):
        return {'status':'invalid','reason':'claim_amount_or_id'}
    expected_origins={('receivable','opening'),('receivable','delivery'),('payable','opening'),('payable','purchase')}
    if {(c['ledger'],c['origin']) for c,_,_ in claims}!=expected_origins:
        return {'status':'invalid','reason':'claim_origin_coverage'}
    def amount_of(event,account):
        journal=next(j for j in projection['proposed_journals'] if j['event_kind']==event)
        return sum((q(l['signed_amount']['constant'])+share*q(l['signed_amount']['coefficient_x']) for l in journal['lines'] if l['account']==account),Q(0))
    expected_rec={('receivable','opening'):q(opening['balances']['receivables']),('receivable','delivery'):amount_of('delivery','receivables'),('payable','opening'):-q(opening['balances']['payables']),('payable','purchase'):-amount_of('purchase','payables')}
    for key,value in expected_rec.items():
        if sum((r for c,r,s in claims if (c['ledger'],c['origin'])==key),Q(0))!=value:
            return {'status':'invalid','reason':'claim_control'}
    if sum((s for c,r,s in claims if c['ledger']=='receivable'),Q(0))!=amount_of('collection','cash') or sum((s for c,r,s in claims if c['ledger']=='payable'),Q(0))!=-amount_of('supplier_payment','cash'):
        return {'status':'invalid','reason':'settlement_control'}
    forecast=source['record_registry'][source['aliases']['economic-facts']['digest']]['body']['forecast']
    if tax!=q(forecast['tax_rate']): return {'status':'invalid','reason':'changed_tax_method'}
    names=[e['kind'] for e in body['events']]
    expected={e['event_kind'] for e in projection['event_plan']}|{'facility_draw','facility_interest','facility_repayment'}
    if len(names)!=len(expected) or set(names)!=expected: return {'status':'invalid','reason':'event_coverage'}
    dependencies=[('purchase','delivery'),('purchase','supplier_payment'),('delivery','collection'),('facility_draw','supplier_payment'),('supplier_payment','collection'),('collection','facility_interest'),('facility_interest','facility_repayment'),('facility_draw','facility_interest')]
    dependencies += [(event,'tax') for event in ('delivery','payroll','depreciation','interest','facility_interest')]
    if any(names.index(a)>=names.index(b) for a,b in dependencies) or names[-1]!='close':
        return {'status':'invalid','reason':'event_order'}
    known=[(i,at(e['at'])) for i,e in enumerate(body['events']) if e['at']!='unknown']
    start=at(forecast['start']+'T00:00:00Z'); end=at(forecast['end_exclusive']+'T00:00:00Z')
    if any(not start<=t<end for i,t in known) or any(a[1]>b[1] for a,b in zip(known,known[1:])):
        return {'status':'invalid','reason':'event_dates'}
    if len(known)!=len(names):
        return {'status':'unresolved','reason':'event_time',
                'obligations':['supply_event_instant:'+e['kind'] for e in body['events'] if e['at']=='unknown']}
    times={e['kind']:at(e['at']) for e in body['events']}
    days=(times['facility_repayment'].date()-times['facility_draw'].date()).days
    if times['facility_interest'].date()!=times['facility_repayment'].date():
        return {'status':'unsupported','reason':'separate_interest_payment_date'}
    return {'status':'validated','principal':loan['principal'],'facility_interest':loan['principal']*loan['annual_rate']*Q(days,365),
            'tax_saving':loan['principal']*loan['annual_rate']*Q(days,365)*tax,
            'claim_closing':{c['id']:r-s for c,r,s in claims},'days':days,'event_order':names}


def main():
    start=datetime.now(timezone.utc).isoformat(); timer=time.perf_counter()
    schema=json.loads((OUT/'schema.json').read_text()); Draft202012Validator.check_schema(schema)
    validator=Draft202012Validator(schema,format_checker=FormatChecker())
    source=json.loads(SOURCE.read_text()); source_hash=sha(SOURCE)
    typed=json.loads((OUT/'example.json').read_text()); text=(OUT/'example.accdsl').read_text()
    lowered=lower(text); checks=[]
    def check(name,passed): checks.append({'name':name,'passed':bool(passed)})
    check('text_typed_identical',lowered==typed)
    result=validate(lowered,validator,source); check('semantic_validation',result['status']=='validated')
    retained=json.loads((ROOT/'data/accounting-master/funded-year-20261023/checks.json').read_text())
    trace=next(r for r in retained['runs'] if r['name']=='stress7:share=1/2:facility_rate=1/20')
    check('principal_interest_match_trace',result['principal']==Q(trace['contract']['principal']) and result['facility_interest']==Q(trace['contract']['interest']))
    check('event_order_matches_trace',result['event_order']==[j['event'] for j in trace['journals']])
    check('event_dates_match_trace',[e['at'][:10] for e in typed['events']]==[j['date'] for j in trace['journals']])
    check('claim_closing_expected',result['claim_closing']=={'opening-ar':Q(25),'sales-ar':Q(30),'opening-ap':Q(30),'purchase-ap':Q(10)})
    bad_texts={'missing_loan':chr(10).join(l for l in text.splitlines() if not l.startswith('loan ')),
               'duplicate_share':text+'share 1/2;'+chr(10),
               'noncanonical_number':text.replace('427/5','854/10'),
               'missing_semicolon':text.replace('share 1/2;','share 1/2'),
               'unknown_keyword':text+'infer_facility yes;'+chr(10)}
    for name,bad in bad_texts.items():
        try: observed=validate(lower(bad),validator,source)['status']
        except AuthoringError: observed='invalid'
        check(name,observed=='invalid')
    variants=[]
    def variant(name,path,value,expected='invalid'):
        b=deepcopy(typed); node=b
        for k in path[:-1]: node=node[k]
        node[path[-1]]=value; variants.append((name,b,expected))
    variant('duplicate_claim_id',['claims',1,'id'],'opening-ar')
    variant('wrong_projection',['projection','digest'],'0'*64)
    variant('wrong_currency',['context','currency'],'EUR')
    variant('invalid_calendar_date',['events',0,'at'],'2025-02-30T09:00:00Z')
    variant('unknown_collection',['events',4,'at'],'unknown','unresolved')
    variant('out_of_horizon',['events',13,'at'],'2026-01-01T00:00:00Z')
    variant('claim_overpayment',['claims',3,'settlement'],{'n':'171','d':'1'})
    variant('new_fee_not_implemented',['loan','fee'],{'n':'1','d':'1'},'unsupported')
    variant('insufficient_headroom',['facility','reserved'],{'n':'20','d':'1'})
    b=deepcopy(typed); b['events'][2],b['events'][3]=b['events'][3],b['events'][2]; variants.append(('payment_before_draw',b,'invalid'))
    b=deepcopy(typed); b['events'][10],b['events'][11]=b['events'][11],b['events'][10]; variants.append(('tax_before_interest',b,'invalid'))
    for name,b,expected in variants:
        before=deepcopy(b); check(name,validate(b,validator,source)['status']==expected and b==before)
    unknown=next(b for name,b,expected in variants if name=='unknown_collection')
    check('named_unknown_time_obligation',validate(unknown,validator,source)['obligations']==['supply_event_instant:collection'])
    check('source_unchanged',sha(SOURCE)==source_hash)
    report={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'lowered':lowered,'semantic_result':result,
            'scope':'Bounded documentary authoring and trace conformance; product grammar unchanged'}
    (OUT/'checks.json').write_text(json.dumps(report,indent=2,default=str)+chr(10))
    manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'command':'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/funded-authoring-20261023/verify.py',
              'environment':{'executable':sys.executable,'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema')},
              'cpu_gpu':'CPU only; GPU intentionally hidden','cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),
              'random_seeds':'N/A: deterministic conformance','data_version':source_hash,'started_utc':start,'wall_seconds':time.perf_counter()-timer,
              'plan_file':'docs/plans/accounting-funded-year-design-20261023.md','result_file':str((OUT/'result.md').relative_to(ROOT)),
              'artifacts':{p.name:sha(p) for p in [OUT/n for n in ['schema.json','example.json','example.accdsl','grammar.md','authoring.py','prepare.py','verify.py','checks.json']]}}
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps({'passed':report['passed'],'checks':len(checks),'failures':[c for c in checks if not c['passed']]}))
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__': main()
