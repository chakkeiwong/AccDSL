"""Check complete independent PAA expectations and native refusal behavior."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--smoke',action='store_true');args=parser.parse_args()
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];out=args.output.resolve()
assert out.is_relative_to(ROOT) and out!=ROOT
out.mkdir(exist_ok=False);os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic()
read=lambda p:json.loads(p.read_text());digest=lambda p:sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load('paa_bridge',HERE/'bridge.py');f=load('paa_authored',HERE/'authored.py')
lock=read(HERE/'source-lock.json');checks=[];cases=[];controls=[];current=None
def dump(name,value):
    with (out/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
def ck(name,actual,expected=True):
    passed=actual==expected;checks.append(dict(name=name,passed=passed))
    if not passed:
        dump('difference.json',dict(name=name,actual=actual,expected=expected));raise AssertionError(name)
def financial(body,result,expected):
    compiled=result['compiled'];execution=result['execution'];events=[r for r in execution['trace'] if r['command']['kind']=='event']
    reports=[r['result'] for r in execution['trace'] if r['command']['kind']=='report']
    ck('eight events',len(events),8);ck('one interim report',len(reports),1);ck('no stop',execution['stop'],None)
    ck('complete opening',compiled['opening']['balances'],expected['opening'])
    ck('complete final balances',execution['current']['balances'],expected['closing'])
    ck('complete groups',result['groups'],body['payload']['groups'])
    for observed,authored in zip(events,expected['stages']):
        transition=observed['result']['transition'];after=transition['after'];key=authored['id']
        ck(key+'/identity',observed['command']['event']['id'],key)
        ck(key+'/date',after['date'],authored['date'])
        journal={p['account']:p['amount'] for p in transition['journal']}
        ck(key+'/complete journal',journal,authored['postings'])
        ck(key+'/balanced journal',sum(Q(v) for v in journal.values()),Q(0))
        ck(key+'/complete balances',after['balances'],authored['balances'])
        mem=deepcopy(compiled['opening']['memory']);mem['step']=authored['step']
        ck(key+'/complete memory',after['memory'],mem)
        ck(key+'/no negative cash',Q(after['balances'][expected['roles']['cash']])>=0)
    report=reports[0]
    for key,value in expected['financial'].items():ck('report/'+key,report[key],value)
    for key,value in expected['cash'].items():ck('cash/'+key,report['cash_flows'][key],value)
    for key in ['entity','book','currency']:
        ck('report/context/'+key,report['context'][key],compiled['opening']['context'][key])
    ck('period',report['period'],body['payload']['calendar']['coverage']);ck('as_of',report['as_of'],body['payload']['calendar']['cutoff'])
    ck('notes',report['notes'],f.NOTES)
    flows=[{k:row[k] for k in ['event_id','date','amount','activity','origin']} for row in report['cash_flows']['gross_origins']]
    ck('complete gross cash origins',flows,expected['flows'])
    ck('still provisional',[report['fiscal_complete'],report['notes_complete']],[False,False])
    ck('all adapter admissions false',{k:result[k] for k in m.FLAGS},m.FLAGS)
    # Complete native report comparison adds record identity/status fields to
    # the independent financial expectations, using only declared metadata.
    native_request=execution['trace'][-1]['request']
    full=dict(profile=m.program.reports.PROFILE,**m.program.reports.FLAGS,status='reported',scope='recorded_period_only',
        context=deepcopy(compiled['opening']['context']),period=deepcopy(body['payload']['calendar']['coverage']),
        as_of=body['payload']['calendar']['cutoff'],**deepcopy(expected['financial']),
        cash_flows={**deepcopy(expected['cash']),'gross_origins':deepcopy(execution['current']['flows'])},notes=deepcopy(f.NOTES),
        unresolved=['Event-population completeness','Source and accounting admission','Complete note package','Indirect operating cash-flow bridge'],
        request_sha256=f.digest(native_request),opening_sha256=f.digest(native_request['opening']),
        closing_sha256=f.digest(native_request['closing']),mapping_sha256=f.digest(compiled['mapping']),
        implementation_sha256=digest(ROOT/'scripts/company_book_reports_v1.py'),
        book_sha256=digest(ROOT/'scripts/company_book_transition_v1.py'))
    ck('complete report record',report,full)
    return report

passed=False
try:
    for p,h in lock.items():ck('before/'+p,digest(ROOT/p),h)
    baseline=read(HERE/'authored-expectations.json')
    population=[('base','named',False)] if args.smoke else [(case,chart,False) for case in f.CASES for chart in ['named','renamed']]+[('base','named',True)]
    for case,chart,complement in population:
        identifier=case+'/'+chart+('/complement' if complement else '')
        body=f.fixture(case,chart,complement);before=deepcopy(body);current=m.propose(body)
        ck(identifier+'/status',current['status'],'proposed_conditional');ck(identifier+'/immutable',body,before)
        expected=baseline[identifier];ck(identifier+'/independent expected frozen',f.expected(case,chart,complement),expected)
        report=financial(body,current,expected)
        cases.append(dict(id=identifier,request=body,result=current,report=report))
    if not args.smoke:
        def control(name,change,status,reason,rehash=True):
            body=f.fixture();change(body)
            if rehash:f.bind(body)
            before=deepcopy(body);result=m.propose(body)
            ck(name+'/status',result['status'],status);ck(name+'/reason',result['reason'],reason)
            ck(name+'/immutable',body,before);ck(name+'/no execution','execution' not in result)
            controls.append(dict(id=name,request=body,result=result))
        control('stale_payload',lambda b:b['payload']['amounts'].update(premium='121/1'),'invalid','payload_binding',False)
        control('same_group',lambda b:b['payload']['groups']['held'].update(id='PAA.ISSUED.2024'),'invalid','distinct_groups')
        control('wrong_underlying',lambda b:b['payload']['groups']['held'].update(underlying_group='other'),'invalid','underlying_group_link')
        control('owner',lambda b:b['payload']['groups']['held'].update(owner='J'),'invalid','group_owner_or_role')
        control('held_calendar',lambda b:b['payload']['groups']['held'].update(recognition='2023-12-31'),'invalid','group_calendar')
        control('approximate_half',lambda b:b['payload']['calendar'].update(cutoff='2024-06-30'),'unsupported','selected_synthetic_calendar')
        control('nonuniform',lambda b:b['payload']['findings'].update(uniform_service_and_risk_release=False),'unsupported','outside_uniform_service_and_risk_release')
        control('unknown_transferred_risk',lambda b:b['payload']['amounts'].update(transferred_risk=None),'unresolved','unknown_transferred_risk')
        control('unknown_nonperformance',lambda b:b['payload']['amounts'].update(nonperformance=None),'unresolved','unknown_nonperformance')
        control('unsupported_long_claims',lambda b:b['payload']['findings'].update(claims_settle_within_one_year=False),'unsupported','outside_claims_settle_within_one_year')
        control('unknown_held_eligibility',lambda b:b['payload']['findings'].update(one_year_each_held_contract=None),'unresolved','unknown_one_year_each_held_contract')
        control('actual_scope',lambda b:b['payload'].update(assumption_scope='actual accounting approved'),'invalid','assumption_scope')
        control('cash_policy',lambda b:b['payload']['cash_policy'].update(activity='financing'),'unsupported','cash_activity')
        control('source_edition',lambda b:b['payload'].update(source_edition='current all jurisdictions'),'unsupported','source_edition')
        control('gross_claims_changed',lambda b:b['payload']['amounts'].update(incurred_claims='41/1'),'unsupported','outside_selected_amounts')
        control('risk_wrong_case',lambda b:b['payload']['amounts'].update(transferred_risk='3/2'),'unsupported','case_measurements')
        compiled=cases[0]['result']['compiled']
        def native_control(name,change):
            body=deepcopy(compiled);change(body);result=m.program.run(body)
            ck(name+'/stopped',result['status']!='complete_provisional')
            ck(name+'/no final report',not any(r['command']['kind']=='report' for r in result.get('trace',[])))
            controls.append(dict(id=name,compiled=body,result=result))
        native_control('reordered_premiums',lambda b:b['commands'].__setitem__(slice(0,2),list(reversed(b['commands'][:2]))))
        native_control('duplicate_premium',lambda b:b['commands'].insert(1,deepcopy(b['commands'][0])))
        native_control('wrong_event_date',lambda b:b['commands'][2]['event'].update(date='2024-06-30'))
        native_control('wrong_event_group',lambda b:b['commands'][2]['event']['inputs']['group_id']['value'].update(value='PAA.HELD.2024'))
        native_control('omitted_claim_payment',lambda b:b['commands'].pop(5))
    for p,h in lock.items():ck('after/'+p,digest(ROOT/p),h)
    passed=True
except Exception:
    dump('failure.json',dict(error=traceback.format_exc(),completed_cases=len(cases)))
    if current is not None:dump('current-result.json',current)
finally:
    dump('cases.json',cases);dump('controls.json',controls);dump('checks.json',checks)
    result=dict(passed=passed,cases=len(cases),controls=len(controls),checks=len(checks),smoke_only=args.smoke,
                source_admission=False,accounting_admission=False,full_requirement_closed=False)
    dump('verification.json',result)
    dump('run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),command=[sys.executable,'-I','-B',*sys.argv],
        git_commit='N/A: exact per-file source lock used',environment=sys.version,cpu_gpu='CPU only; GPUs intentionally hidden',
        random_seeds='N/A exact deterministic arithmetic',data_version=digest(HERE/'source-lock.json'),wall_seconds=time.monotonic()-start,
        plan='docs/plans/accounting-insurance-paa-dated-book-20261027.md',result='data/accounting-master/insurance-paa-dated-book-20261027/result.md',
        outputs=str(out),passed=passed,scope='Native-engine conformance; no OS/file-access isolation claim'))
print(json.dumps(result))
if not passed:raise SystemExit(1)
