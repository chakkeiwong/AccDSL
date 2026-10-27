from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast
import json
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'authored-event-contract-20261026'))
import contract as c
import method_requirements_v3 as guarded
BOOL=c.core.BOOL
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+chr(10))
def ref(n):return {'op':'ref','id':n}
def known(v):return {'status':'known','value':v}
def rule(name,predicate,deps,false):
    return {'id':name,'guard':{'op':'const','type':BOOL,'value':True},'guard_requires':[],
            'predicate':predicate,'requires':deps,'admission_refs':[],'on_false':false,'on_unknown':'unresolved'}
def main():
    start=time.monotonic();previous=HERE.parent/'event-specialization-audit-20261026'
    path=HERE/'source-lock.json'
    if not path.exists():
        lock=json.loads((previous/'source-lock.json').read_text())
        for p in [previous/'result.md',previous/'request-comparisons.json',ROOT/'scripts/method_requirements_v3.py',ROOT/'scripts/method_requirements_v2.py',ROOT/'scripts/method_requirements_v1.py',ROOT/'scripts/method_collections_v1.py']:
            lock[str(p.relative_to(ROOT))]=sha(p)
        dump(path.name,lock)
    lock=json.loads(path.read_text())
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    manifest={'profile':guarded.PROFILE,'method_id':'audit.flat.collection','version':'1',
              'inputs':{'approved':{'type':BOOL,'role':'assumption','source_ref':'supplied event'},
                        'exists':{'type':BOOL,'role':'state','source_ref':'computed from actual claim map'},
                        'customer':{'type':{'kind':'text','context':{}},'role':'reported_measurement','source_ref':'supplied event'}},
              'requirements':[rule('approval',ref('approved'),['approved'],'unsupported'),
                              rule('claim_exists',ref('exists'),['exists'],'invalid'),
                              rule('customer_known',{'op':'eq','left':ref('customer'),'right':ref('customer')},['customer'],'invalid')],
              'required_known':['customer'],'capabilities':[],'residual_prerequisites':['Deliberately flat audit comparator, not a proposed faithful contract.']}
    guarded.compile_manifest(manifest);mh=c.core.digest(manifest)
    results=[];ordering=[]
    for owner in ('alpha','beta'):
        program=json.loads((HERE.parent/f'authored-event-contract-20261026/examples/{owner}.program.json').read_text())
        original=c.native_body(program);prefix=c.native.run({**deepcopy(original),'commands':deepcopy(original['commands'][:1])})
        book=prefix['current'];assert prefix['status']=='complete_provisional'
        for label,approved,customer,claim,wanted in [
            ('unknown_then_false_and_missing',False,{'status':'unknown','reason':'missing customer'},'absent','unresolved'),
            ('false_then_missing',False,known('Wrong customer'),'absent','unsupported'),
            ('unknown_then_false',False,{'status':'unknown','reason':'missing customer'},next(iter(book['memory']['claims'])),'unresolved')]:
            body=deepcopy(original);event=body['commands'][1]['event'];event['inputs']['approved']['value']=known(approved);event['inputs']['customer']['value']=customer;event['inputs']['claim_id']['value']=known(claim)
            native=c.native.run(body);assert native['stop']['status']==wanted and native['successful_commands']==1
            values={'approved':known(approved),'exists':known(claim in book['memory']['claims']),'customer':customer}
            flat=guarded.assess({mh:manifest},mh,values,[])
            assert flat['status']!=wanted,(label,flat)
            results.append({'company':owner,'case':label,'event':event,'before':book,'manifest':manifest,'values':values,'native_stop':native['stop'],'flat_result':flat,'same_target':False})
        for label,index,mutate,wanted in [
            ('sealed_before_missing',1,lambda ev:(ev.update(date='2027-01-31'),ev['inputs']['claim_id'].update(value=known('absent'))),'assessment_day_sealed'),
            ('cursor_before_window',2,lambda ev:(ev['inputs']['start'].update(value=known('2027-01-02')),ev['inputs']['end_exclusive'].update(value=known('2027-02-02'))),'assessment_cursor')]:
            body=deepcopy(original)
            if label.startswith('sealed'):
                event=deepcopy(body['commands'][1]);event['event']['id']='late.and.missing';mutate(event['event']);body['commands']=body['commands'][:3]+[event];index=3
            else:mutate(body['commands'][index]['event'])
            result=c.native.run(body);assert result['stop']['reason']==wanted and result['successful_commands']==index
            ordering.append({'company':owner,'case':label,'stop':result['stop'],'successful_commands':index})
    source=ROOT/'scripts/declared_receivable_lifecycle_v1.py';tree=ast.parse(source.read_text());anchors={n.name:[n.lineno,n.end_lineno] for n in tree.body if isinstance(n,ast.FunctionDef)}
    mapping=[
      {'stage':1,'rule':'event structure, full input types and provenance','owner':'run','existing':'typed scalar and value validators','needed':'exact closed source declarations; structural errors before all semantic stages'},
      {'stage':2,'rule':'book/event chronology and exact input population','owner':'run','existing':'date lt/le, exact record/type checks','needed':'bind book date and period boundary; preserve native chronology before unknown handling'},
      {'stage':3,'rule':'all supplied full-intent unknowns','owner':'run','existing':'required_known','needed':'ordered early unresolved stage before approval and operation-specific rules'},
      {'stage':4,'rule':'approved must be true','owner':'run','existing':'Boolean predicate on_false unsupported','needed':'ordered early unsupported before claim lookup'},
      {'stage':5,'rule':'sale/collect date at or after assessment cursor','owner':'make_request','existing':'date le','needed':'operation-specific stage selection and exact failure reason'},
      {'stage':6,'rule':'sale due date, claim absence','owner':'make_request','existing':'date le; collection uniqueness/reference machinery','needed':'computed map membership Boolean from actual typed map, not a caller assertion'},
      {'stage':6,'rule':'collection existence then customer equality','owner':'make_request','existing':'text equality after typed lookup','needed':'ordered membership check before row lookup; escaped text key; missing and unknown distinct'},
      {'stage':6,'rule':'assessment cursor then valid nonempty interval and last included date','owner':'make_request','existing':'date eq/lt; no calendar increment in current expression arithmetic','needed':'explicit typed calendar successor/predecessor with overflow handling, not rational subtraction'},
      {'stage':7,'rule':'assessment end within period','owner':'make_request','existing':'date le','needed':'retain after window check'},
      {'stage':8,'rule':'complete method construction then transition predicates','owner':'run','existing':'checked scalar/ordered constructors and transition engines','needed':'reuse those explicit mechanisms after eligibility; do not fold financial predicates into a caller finding'}]
    for item in mapping:item.update(source=str(source.relative_to(ROOT)),source_sha256=sha(source),lines=anchors[item['owner']])
    dump('flat-counterexamples.json',results);dump('ordering-probes.json',ordering);dump('guard-map.json',mapping)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    summary={'passed':True,'flat_conjunction_counterexamples':len(results),'native_order_probes':len(ordering),'mapped_rule_groups':len(mapping),'protected_files':len(lock),'flat_conjunction_faithful':False,'general_eligibility_implemented':False,'accounting_admission':False}
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',{'git_commit':git.stdout.strip() if git.returncode==0 else 'unavailable','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/event-eligibility-audit-20261026/probe.py','environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'data_version':sha(path),'plan_file':'docs/plans/accounting-event-eligibility-audit-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),'artifacts':['guard-map.json','flat-counterexamples.json','ordering-probes.json','checks.json'],'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(summary))
if __name__=='__main__':main()
