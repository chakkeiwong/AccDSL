"""Bind an existing policy's exact allocations to complete claim histories."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import subprocess
import sys
import time
import relationships as rel

ROOT = rel.ROOT
HERE = 'data/accounting-master/company-state-relationship-dependencies-20261028'
PLAN = 'docs/plans/company-state-claim-policy-connection-20261028.md'
PACKET = 'data/accounting-master/company-path-exchanges-20261023/packet.json'
POLICY = 'data/accounting-master/company-policy-20261023/policy.json'
spec = importlib.util.spec_from_file_location('existing_claim_policy',ROOT/'data/accounting-master/company-policy-20261023/policy.py')
policy_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy_module)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    packet=json.loads((ROOT/PACKET).read_text())
    records=packet['record_registry']
    root=records[packet['root_ref']['digest']]['body']
    selected=[records[r['digest']]['body'] for r in root['path_refs']
              if records[r['digest']]['body']['name']=='second_year_price_revision']
    if len(selected)!=1:raise ValueError('exact policy parent missing or ambiguous')
    paths_read=[]
    def blob(ref):
        entry=packet['blobs'][ref['digest']]
        p=ROOT/entry['path'];raw=p.read_bytes();paths_read.append(p)
        if sha256(raw).hexdigest()!=ref['digest'] or len(raw)!=ref['byte_length']:
            raise ValueError('exchange blob identity')
        return raw
    path=json.loads(blob(selected[0]['path_blob']))
    retained_result=json.loads(blob(selected[0]['result_blob']))
    policy=json.loads((ROOT/POLICY).read_text())
    source_path=path['initial_year']['source']['path']
    source=(ROOT/source_path).read_bytes()
    saved=deepcopy((path,policy))
    base=rel.inspect(path,source,rel.native.digest(path))
    checks,results,controls=[],{},{}
    def check(name,actual,expected):
        checks.append(dict(name=name,passed=actual==expected,actual=rel.wire(actual),expected=rel.wire(expected)))
    check('exact saved parent identity',rel.native.digest(path),policy['parent_path_sha256'])
    check('full saved price-revision replay',base['native_result'],retained_result)
    for fraction,expected_status in [('9/10','complete_conditional'),('4/5','complete_conditional'),('1/1','partial')]:
        p=deepcopy(policy)
        p['fraction']=fraction
        generated=policy_module.generate(path,p)
        check(fraction+' materialized',generated['status'],'materialized_conditional_path')
        if generated['status']!='materialized_conditional_path':
            raise ValueError('unexpected policy refusal: '+json.dumps(generated))
        check(fraction+' exact verification',policy_module.verify_materialization(path,p,generated)['status'],'verified_materialization')
        inspection=rel.inspect(generated['path'],source,generated['child_path_sha256'])
        native=inspection['native_result']
        check(fraction+' full path status',native['status'],expected_status)
        check(fraction+' earlier year unchanged',native['years'][0],base['native_result']['years'][0])
        check(fraction+' all events retained',len(inspection['event_nodes']),63)
        check(fraction+' source unchanged',inspection['source_sha256'],base['source_sha256'])
        check(fraction+' actor admission unresolved',generated['information_admission'],
              dict(status='unresolved',reason='policy_information_not_admitted'))
        check(fraction+' no behavioral evidence',generated['real_behavior_evidence'],False)
        check(fraction+' no forecast admission',generated['forecast_admission'],False)
        original=[path['initial_year'],*path['continuations']][p['year_index']]
        edited=[generated['path']['initial_year'],*generated['path']['continuations']][p['year_index']]
        target={(c,cid) for c in p['collection_operations'] for cid in p['claim_ids']}
        restored=deepcopy(generated['path'])
        restore_year=[restored['initial_year'],*restored['continuations']][p['year_index']]
        originals={o['id']:o for o in original['operations']}
        for op in restore_year['operations']:
            if op['id'] in p['collection_operations']:
                old={a['claim_id']:a for a in originals[op['id']]['payload']['allocations']}
                for a in op['payload']['allocations']:
                    if (op['id'],a['claim_id']) in target:a['amount']=old[a['claim_id']]['amount']
        check(fraction+' only target values changed',restored,path)
        edges={(e['event'],e['claim_id']):e for e in inspection['relation_edges'] if e['kind']=='settles_claim'}
        check(fraction+' full policy trace population',len(generated['allocation_trace']),4)
        for trace in generated['allocation_trace']:
            key=(rel.event_key(p['year_index'],trace['operation_id']),trace['claim_id'])
            check(fraction+' trace endpoint '+str(key),key in edges,True)
            check(fraction+' trace amount '+str(key),edges[key]['amount'],trace['generated_amount'])
            expected=Q(16)*Q(12)*Q(fraction)*Q(1,2)
            check(fraction+' independent invoice fraction share '+str(key),Q(edges[key]['amount']),expected)
        if fraction=='9/10':
            check('retained policy exact generated installment',generated['allocation_trace'][0]['generated_amount'],'432/5')
            check('retained policy exact prior installment',generated['allocation_trace'][0]['prior_amount'],'396/5')
            cash_change=Q(native['years'][1]['run']['closing_balances']['cash'])-Q(base['native_result']['years'][1]['run']['closing_balances']['cash'])
            check('retained policy exact cash change',cash_change,Q(144,5))
            for cid in policy['claim_ids']:
                check('retained policy carried residual '+cid,inspection['year_ends'][-1]['claims'][cid]['outstanding'],'8/5')
        if fraction=='4/5':
            last=inspection['year_ends'][-1]['claims']
            for cid in policy['claim_ids']:
                check('reduced collections retained '+cid,last[cid]['outstanding'],'104/5')
        if fraction=='1/1':
            check('full collection first later refusal year',native['stopped_index'],2)
            check('full collection refusal reason',native['years'][-1]['run']['reason'],'over_settlement')
            check('full collection refuses later collection',native['years'][-1]['run']['event'],'collection-1-a')
            for cid in policy['claim_ids']:
                check('fully settled claim persists '+cid,inspection['year_ends'][1]['claims'][cid]['outstanding'],'0/1')
            check('refused event posts no settlement relations',
                any(e['event']==rel.event_key(2,'collection-1-a') for e in inspection['relation_edges']),False)
        results[fraction]=dict(materialization=generated,inspection=inspection)
    mutations=[
        ('stale parent',lambda p:p.update(parent_path_sha256='0'*64),'invalid','parent_path_identity'),
        ('wrong year',lambda p:p.update(year_index=2),'invalid','claim_binding'),
        ('duplicate claim',lambda p:p['claim_ids'].append(p['claim_ids'][0]),'invalid','duplicate_claim_target'),
        ('unknown fraction',lambda p:p.update(fraction='unknown'),'unresolved','policy_fraction_or_share_unknown'),
        ('invalid shares',lambda p:p.update(installment_shares=['1/2','1/3']),'invalid','fraction_domain'),
        ('over fraction',lambda p:p.update(fraction='11/10'),'invalid','fraction_domain'),
        ('missing claim coverage',lambda p:p.update(claim_ids=p['claim_ids'][:1]),'invalid','claim_binding'),
        ('wrong collection endpoint',lambda p:p.update(collection_operations=['supplier_payment-1-a','collection-1-b']),'invalid','collection_binding'),
    ]
    for name,mutate,status,reason in mutations:
        p=deepcopy(policy);mutate(p)
        r=policy_module.generate(path,p)
        check(name+' status',r['status'],status)
        check(name+' reason',r['reason'],reason)
        check(name+' creates no path','path' in r,False)
        controls[name]=r
    generated=deepcopy(results['9/10']['materialization'])
    generated['allocation_trace'][0]['generated_amount']='1/1'
    rejected=policy_module.verify_materialization(path,policy,generated)
    check('tampered policy trace rejected',rejected,dict(status='invalid',reason='policy_materialization_mismatch'))
    controls['tampered_trace']=rejected
    check('inputs immutable',(path,policy),saved)
    failed=[c for c in checks if not c['passed']]
    paths={Path(__file__),Path(rel.__file__),Path(policy_module.__file__),ROOT/PLAN,ROOT/PACKET,ROOT/POLICY,ROOT/source_path,*paths_read,
           ROOT/'data/accounting-master/company-operation-path-20261023/schema.json'}
    for module in list(sys.modules.values())+[rel.native,rel.native.reports,rel.native.annual_path]:
        f=getattr(module,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):paths.add(Path(f).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=sys.version,
        cpu_gpu='CPU-only exact arithmetic; no accelerator imports',random_seeds='N/A deterministic',
        data_version='Retained complete 3-year authored path and named SettlementPolicyDraft/1',
        utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
        plan_file=PLAN,result_file=HERE+'/policy-result.md',
        source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,
                      exact_policy_cases=len(results),adverse_controls=len(controls))
    for name,data in [('results',results),('controls',controls),('checks',checks),('run-manifest',manifest),('verification',verification)]:
        (out/(name+'.json')).write_text(json.dumps(rel.wire(data),indent=2)+chr(10))
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print(json.dumps(verification))
    return bool(failed)


if __name__=='__main__':
    raise SystemExit(main())
