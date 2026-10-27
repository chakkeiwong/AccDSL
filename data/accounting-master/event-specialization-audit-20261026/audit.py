"""Recompute saved full requests and inventory native specialization ownership."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast
import json
import os
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PREVIOUS=HERE.parent/'authored-event-contract-20261026'
sys.path.insert(0,str(PREVIOUS))
import contract as c
import contract_runner as runner
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')

def main():
    start=time.monotonic()
    path=HERE/'source-lock.json'
    if not path.exists():
        lock=json.loads((PREVIOUS/'source-lock.json').read_text())
        for n in ['contract.py','contract_runner.py','verify.py','result.md','checks.json','native-refusals.json','comparisons.json','examples/alpha.program.json','examples/alpha.result.json','examples/beta.program.json','examples/beta.result.json']:
            p=PREVIOUS/n;lock[str(p.relative_to(ROOT))]=sha(p)
        for p in [HERE.parent/'complete-method-authoring-20261026/frontend.py',HERE.parent/'authored-method-registry-20261026/registry.py',HERE.parent/'invariant-source-authoring-20261026/design.md']:
            lock[str(p.relative_to(ROOT))]=sha(p)
        dump(path.name,lock)
    lock=json.loads(path.read_text())
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    comparisons=[];requests=[];refusals=[]
    for owner in ['alpha','beta']:
        body=json.loads((PREVIOUS/('examples/'+owner+'.program.json')).read_text())
        saved=json.loads((PREVIOUS/('examples/'+owner+'.result.json')).read_text())
        actual=runner.run(body)
        assert c.core.canonical(actual)==c.core.canonical(saved),owner
        nativebody=c.native_body(body)
        book=deepcopy(body['opening'])
        for i,row in enumerate(saved['trace']):
            assert c.digest(book)==row['before_sha256']
            command=row['command'];kind=command['kind']
            if kind=='event':
                full=deepcopy(command);full.pop('registry_sha256');full['event']=deepcopy(body['event_contract']['intents'][command['event']['id']])
                expected=c.native.make_request(book,nativebody,full)
                assert c.core.canonical(expected)==c.core.canonical(row['event_contract']['native_request'])
                requests.append({'company':owner,'index':i,'method':command['method_key'],'before':deepcopy(book),'body_parameters':{k:deepcopy(nativebody[k]) for k in ['schemas','roles','unit_cost_pointer','memory_definition','policy']},'full_command':full,'request':expected})
                book=deepcopy(row['result']['transition']['after'])
            elif kind=='report':book['date']=command['cutoff']
            else:book=deepcopy(row['result']['next_opening'])
            assert c.digest(book)==row['after_sha256']
        assert book==saved['current']
        comparisons.append({'company':owner,'commands':len(saved['trace']),'complete_saved_result_equal':True,'recomputed_full_requests':sum(r['company']==owner for r in requests)})
        mutations=[('wrong-customer',1,'customer',c.base.known('Different customer'),'invalid','claim_customer_mismatch'),
          ('missing-claim',1,'claim_id',c.base.known('absent'),'invalid','unknown_claim'),
          ('unknown-customer',1,'customer',{'status':'unknown','reason':'unobserved'},'unresolved','unknown_event_inputs'),
          ('false-approval',1,'approved',c.base.known(False),'unsupported','applicability_not_selected'),
          ('assessment-start',2,'start',c.base.known('2027-01-02'),'invalid','assessment_cursor'),
          ('assessment-end',2,'end_exclusive',c.base.known('2027-02-02'),'invalid','assessment_window'),
          ('due-before-sale',0,'due',c.base.known('2027-01-01'),'invalid','due_before_sale')]
        for name,index,key,value,status,reason in mutations:
            changed=deepcopy(nativebody);changed['commands'][index]['event']['inputs'][key]['value']=value
            result=c.native.run(changed)
            assert result['stop']['status']==status and result['stop']['reason']==reason
            assert result['successful_commands']==index
            expected=body['opening'] if index==0 else requests[next(j for j,r in enumerate(requests) if r['company']==owner and r['index']==index)]['before']
            assert result['current']==expected
            refusals.append({'company':owner,'case':name,'status':status,'reason':reason,'successful_prefix':index,'current':result['current']})
        for name,index,source_index,event_id,date,reason in [('sealed-window',3,1,'late.same.day','2027-01-31','assessment_day_sealed'),('duplicate-claim',1,0,'sale.duplicate','2027-01-03','duplicate_claim')]:
            changed=deepcopy(nativebody);event=deepcopy(changed['commands'][source_index]);event['event'].update(id=event_id,date=date)
            changed['commands']=changed['commands'][:index]+[event]
            result=c.native.run(changed)
            assert result['stop']['status']=='invalid' and result['stop']['reason']==reason and result['successful_commands']==index
            previous=saved['trace'][index-1];expected=previous['result']['transition']['after']
            assert result['current']==expected
            refusals.append({'company':owner,'case':name,'status':'invalid','reason':reason,'successful_prefix':index,'current':result['current']})
    source=ROOT/'scripts/declared_receivable_lifecycle_v1.py'
    tree=ast.parse(source.read_text())
    anchors={n.name:{'start':n.lineno,'end':n.end_lineno} for n in tree.body if isinstance(n,ast.FunctionDef)}
    operations=[
     ('input_shape','event_types','Complete event input types vary by operation; the existing method body sees only the projected subset.','Explicit typed full-intent declaration and knownness/applicability requirements.'),
     ('input_admission','run','Chronology, exact input population, types, provenance, unknown and false approval are checked before specialization.','Keep this boundary and failure status before template evaluation.'),
     ('opening_contract','validate','Empty opening claim map, map capacity, typed memory, role mapping and explicit policy are baseline scope.','Do not silently generalize opening population or accounting authority.'),
     ('sale_construction','make_request','Claim id/customer/due and event id/date specialize insertion path and row constants; duplicate and due-date eligibility precede construction.','Typed metadata/value binding, explicit guarded declarations and dynamic path segments.'),
     ('collection_construction','make_request','Selected claim lookup checks ownership, constructs an escaped remaining pointer, then extends preconditions, monetary calculation and write.','Typed map lookup with exact failure, safe pointer construction and complete explicit method template.'),
     ('assessment_construction','make_request','Date-window/cursor checks construct a state-only method, then one set of writes per current claim with overdue selection and sequential operation ids.','Bounded declared map iteration, explicit ordering, date relations and exact guarded template values.'),
     ('schema_construction','make_request','The memory-input schema derives from the exact emitted input types and its digest enters the method.','Reuse the pinned schema compiler after data construction; do not expose arbitrary callbacks.'),
     ('request_binding','make_request','Final request binds actual current book, full event, full method, schema population and memory definition.','Recompute digests from complete objects; refuse stale state or contract.'),
     ('state_control','control','Claim sums, dates, sale references and assessment snapshots constrain accepted states.','Already authored through explicit invariant source; retain without rebuilding.'),
     ('runtime_accounting','run','Original transition, report and carry evaluators compute actual results.','Reuse them as explicit baseline evaluators; a template is not accounting admission.')]
    inventory=[]
    for ident,func,meaning,need in operations:
        inventory.append({'id':ident,'source':str(source.relative_to(ROOT)),'sha256':sha(source),'function':func,'lines':anchors[func],'native_behavior':meaning,'declarative_requirement':need})
    dump('operation-map.json',inventory);dump('request-comparisons.json',requests);dump('program-comparisons.json',comparisons);dump('refusal-comparisons.json',refusals)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    summary={'passed':True,'complete_programs':len(comparisons),'complete_commands':sum(x['commands'] for x in comparisons),'full_requests':len(requests),'native_refusals':len(refusals),'operation_groups':len(inventory),'protected_files':len(lock),'portable_specialization_implemented':False,'accounting_admission':False,'production_ready':False}
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',{'git_commit':git.stdout.strip() if git.returncode==0 else 'unavailable','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/event-specialization-audit-20261026/audit.py','environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'data_version':sha(path),'plan_file':'docs/plans/accounting-event-specialization-audit-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),'artifacts':['operation-map.json','request-comparisons.json','program-comparisons.json','refusal-comparisons.json','checks.json'],'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(summary))
if __name__=='__main__':main()
