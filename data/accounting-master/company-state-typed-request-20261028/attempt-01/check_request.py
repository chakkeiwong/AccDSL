"""Typed request selections agree with native reports and complete histories."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,time
import request as adapter
ROOT=adapter.ROOT;rel=adapter.rel
PLAN='docs/plans/company-state-typed-request-20261028.md'
INPUT='data/accounting-master/company-operation-path-20261023/example.json'
HERE='data/accounting-master/company-state-typed-request-20261028'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    path=json.loads((ROOT/INPUT).read_text());source_path=path['initial_year']['source']['path'];source=(ROOT/source_path).read_bytes()
    queries=[dict(id='annual2025',kind='annual_report',period_start='2025-01-01'),
        dict(id='annual2026',kind='annual_report',period_start='2026-01-01'),
        dict(id='annual2027',kind='annual_report',period_start='2027-01-01'),
        dict(id='first_delivery',kind='event_prefix',year_index=0,operation_id='delivery-1-a'),
        dict(id='next_delivery',kind='event_prefix',year_index=1,operation_id='delivery-1-a'),
        dict(id='opening_claim',kind='claim_history',claim_id='opening-ar'),
        dict(id='created_claim',kind='claim_history',claim_id='sales-ar-2026-a'),
        dict(id='created_asset',kind='asset_history',asset_id='capex-2025-a'),
        dict(id='absent_claim',kind='claim_history',claim_id='not-supplied'),
        dict(id='absent_asset',kind='asset_history',asset_id='not-supplied'),
        dict(id='future_year',kind='annual_report',period_start='2030-01-01'),
        dict(id='foreign_event',kind='event_prefix',year_index=0,operation_id='not-supplied')]
    def req(path):return dict(profile='CompanyStateInspectionRequest/1',owner='CompanyOperationPathDraft/1',
        path_sha256=rel.native.digest(path),source_sha256=sha256(source).hexdigest(),context=deepcopy(path['initial_year']['context']),
        information=dict(use='audit_only',view='archival_exogenous_stress'),joins=[],queries=deepcopy(queries))
    r=req(path);saved=deepcopy((r,path));result=adapter.inspect(r,path,source);checks=[];controls={}
    def check(n,a,b):checks.append(dict(name=n,passed=a==b,actual=a,expected=b))
    check('typed request inspected',result['status'],'inspected')
    check('inputs immutable',(r,path),saved)
    check('all query IDs retained',[x['id'] for x in result['queries']],[x['id'] for x in queries])
    by_id={x['id']:x for x in result['queries']};native=result['admission']['native_result'];pop=result['admission']['population_inspection']
    for year in [2025,2026,2027]:
        row=by_id['annual'+str(year)]
        check('annual native view '+str(year),row['native_view'],rel.native.report_view(path,native,str(year)+'-01-01'))
        check('annual complete '+str(year),row['status'],'complete_conditional')
    for id,yi in [('first_delivery',0),('next_delivery',1)]:
        row=by_id[id];key=rel.event_key(yi,'delivery-1-a')
        expected=next(x['claims'] for x in pop['relationship_result']['prefixes'] if x['event']==key)
        check(id+' full prefix',row['claims'],expected)
        check(id+' year-qualified key',row['event']['id'],key)
    check('reused local event names distinct',by_id['first_delivery']['event']['id']!=by_id['next_delivery']['event']['id'],True)
    check('opening claim lifetime final',by_id['opening_claim']['history'][-1]['state'],dict(ledger='receivable',recognised='35/1',settled='35/1',outstanding='0/1'))
    check('new claim origin year',by_id['created_claim']['origin']['event'],rel.event_key(1,'delivery-1-a'))
    check('asset origin year',by_id['created_asset']['origin']['event'],rel.event_key(0,'plant_addition-1-a'))
    check('asset full final accumulation',by_id['created_asset']['history'][-1]['state']['accumulated'],'2/1')
    for id in ['absent_claim','absent_asset']:
        check(id+' scoped absence',by_id[id]['status'],'not_present_in_executed_prefix')
        check(id+' no actual absence claim',by_id[id]['actual_existence'],'unknown')
    check('future report native invalid',by_id['future_year']['status'],'invalid')
    check('foreign event invalid',by_id['foreign_event']['reason'],'event_not_in_supplied_path')
    mutations=[
      ('wrong owner',lambda r:r.update(owner='InsurancePAADatedBook/1'),'unsupported','native_owner'),
      ('unreviewed join',lambda r:r['joins'].append('InsurancePAADatedBook/1'),'unsupported','cross_profile_join'),
      ('actor request',lambda r:r['information'].update(use='policy',view='manager'),'unsupported','actor_information_request'),
      ('public request',lambda r:r['information'].update(view='public'),'unsupported','actor_information_request'),
      ('wrong entity',lambda r:r['context'].update(entity='Other'),'invalid','context_mismatch'),
      ('wrong book',lambda r:r['context'].update(book='Other'),'invalid','context_mismatch'),
      ('wrong currency',lambda r:r['context'].update(currency='EUR'),'invalid','context_mismatch'),
      ('wrong parent',lambda r:r.update(path_sha256='0'*64),'invalid','path_digest'),
      ('wrong source',lambda r:r.update(source_sha256='0'*64),'invalid','source_digest'),
      ('duplicate query',lambda r:r['queries'].append(deepcopy(r['queries'][0])),'invalid','duplicate_query_id'),
      ('extra field',lambda r:r.update(probability='1/1'),'invalid','request_schema'),
      ('empty queries',lambda r:r.update(queries=[]),'invalid','request_schema'),
      ('malformed date',lambda r:r['queries'][0].update(period_start='2025-13-01'),'invalid','request_schema'),
      ('missing year qualifier',lambda r:r['queries'][3].pop('year_index'),'invalid','request_schema'),
      ('foreign query',lambda r:r['queries'][0].update(kind='posterior'),'invalid','request_schema'),
      ('query extra field',lambda r:r['queries'][0].update(actor='manager'),'invalid','request_schema'),
    ]
    for name,mutate,status,reason in mutations:
        q=deepcopy(r);mutate(q);a=adapter.inspect(q,path,source)
        check(name+' status',a['status'],status);check(name+' reason',a['reason'],reason)
        check(name+' no native evaluation result','admission' in a,False)
        controls[name]=a
    unknown=deepcopy(path);unknown['initial_year']['opening_claims'][0]['amount']='unknown'
    a=adapter.inspect(req(unknown),unknown,source);ab={x['id']:x for x in a['queries']}
    check('unknown opening kept',a['admission']['status'],'opening_not_executable')
    check('unknown claim population unresolved',ab['opening_claim']['status'],'unresolved')
    check('unknown population no history','history' in ab['opening_claim'],False)
    check('unknown population retains obligations',bool(ab['opening_claim']['obligations']),True)
    check('unknown opening first report partial',ab['annual2025']['status'],'partial')
    check('unknown opening future declared report unresolved',ab['annual2026']['status'],'unresolved')
    controls['unknown opening']=a
    partial=deepcopy(path);next(o for o in partial['initial_year']['operations'] if o['kind']=='delivery')['payload']['control_transferred']='unknown'
    a=adapter.inspect(req(partial),partial,source);ab={x['id']:x for x in a['queries']}
    check('refused event not successful snapshot',ab['first_delivery']['status'],'not_executed')
    check('refused event reason',ab['first_delivery']['reason'],'refused')
    check('future event remains unexecuted',ab['next_delivery']['reason'],'unexecuted')
    check('created later claim not fabricated',ab['created_claim']['status'],'not_present_in_executed_prefix')
    check('first partial report preserved',ab['annual2025']['native_view']['report']['status'],'partial')
    controls['partial operation']=a
    for name,a in [('baseline',result),*controls.items()]:
        check(name+' no actual admission',[a['source_admission'],a['actor_information_admission'],a['population_complete'],a['full_company_constructor']],[False]*4)
    files={Path(__file__),Path(adapter.__file__),ROOT/PLAN,ROOT/INPUT,ROOT/source_path}
    for m in list(sys.modules.values())+[rel.native,rel.native.reports,rel.native.annual_path]:
        f=getattr(m,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):files.add(Path(f).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=sys.version,
        cpu_gpu='CPU-only exact typed query validation; no accelerator imports',random_seeds='N/A deterministic',
        data_version='Full original path and existing guarded population/native report interfaces',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
        plan_file=PLAN,result_file=HERE+'/result.md',source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    failed=[c for c in checks if not c['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,queries=len(queries),controls=len(controls))
    for name,x in [('schema',adapter.schema()),('request',r),('result',result),('controls',controls),('checks',checks),('verification',v),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(x,indent=2)+chr(10))
    for f in [Path(__file__),Path(adapter.__file__)]: (out/f.name).write_bytes(f.read_bytes())
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
