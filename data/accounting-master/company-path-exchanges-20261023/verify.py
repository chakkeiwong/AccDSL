"""Deterministic exchange conformance; read-only unless --record is explicit."""
from copy import deepcopy
from datetime import datetime,timezone
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from exchanges import schemas,canonical,digest
from admission import blobs
from support import HERE,ROOT,BASE,context


def conformance():
    previous,engine,validate=context()
    packet=json.loads((HERE/'packet.json').read_text())
    raw=previous.load_blob_files(packet);saved=deepcopy(packet)
    checks=[];witnesses={}
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    accepted=validate(packet,raw);bound=validate(packet,raw,False)
    witnesses['accepted']=accepted;witnesses['bindings_only']=bound
    check('trusted_replay_accepts',accepted['status']=='validated_synthetic_exchange')
    check('explicit_replay_level',accepted.get('verification_level')=='trusted_local_semantic_replay')
    check('binding_check_is_not_replay',bound.get('verification_level')=='content_binding_only' and bound.get('replayed_paths')==0)
    for k,v in [('path_count',5),('revision_count',5),('year_outcomes',13),('partial_paths',2),('replayed_paths',5)]:
        check('count:'+k,accepted.get(k)==v)
    check('validation_is_pure',packet==saved)
    check('saved_schema_matches',schemas()==json.loads((HERE/'extension-schemas.json').read_text()))
    registry=packet['record_registry'];root=registry[packet['root_ref']['digest']]['body']
    base=json.loads((BASE/'packet.json').read_text())
    check('all_original_records_preserved',all(registry.get(h)==v for h,v in base['record_registry'].items()))
    check('all_original_blob_metadata_preserved',all(packet['blobs'].get(h)==v for h,v in base['blobs'].items()))
    cases={registry[r['digest']]['body']['name']:registry[r['digest']]['body'] for r in root['path_refs']}
    get=lambda ref:json.loads(raw[ref['digest']])
    runs={name:get(body['result_blob']) for name,body in cases.items()}
    for name,body in cases.items():
        run=runs[name]
        check('chain:'+name,engine.verify_chain(get(body['path_blob']),run))
        for i,ref in enumerate(body['year_refs']):
            year=registry[ref['digest']]['body'];y=run['years'][i]
            check(name+':year_bytes:'+str(i),get(year['year_blob'])==y)
            check(name+':memory_presence:'+str(i),(year['closing_memory_blob'] is not None)==(y['run']['status']=='complete_conditional'))
            check(name+':not_historical:'+str(i),year['historical_admission'] is False)
    for name,status in [('unknown_middle_payroll','unresolved'),('middle_supplier_failure','funding_failure')]:
        run=runs[name];y=run['years'][1]
        check(name+':distinct_stop_status',y['run']['status']==status)
        check(name+':third_year_unexecuted',run['unexecuted']==[{'index':2,'period':{'start':'2027-01-01','end_exclusive':'2028-01-01'},'status':'unresolved','reason':'predecessor_incomplete'}])
        opening_fields={'opening_cash','opening_equity'}
        check(name+':no_annual_totals',y['report']['annual_complete'] is False and all(v['status']=='unresolved' for k,v in y['report']['lines'].items() if k not in opening_fields))
        check(name+':known_opening_preserved',all(y['report']['lines'][k]==runs['baseline']['years'][1]['report']['lines'][k] for k in opening_fields))
        check(name+':first_year_unchanged',run['years'][0]==runs['baseline']['years'][0])
    check('unresolved_payroll_retains_eleven_operations',len(runs['unknown_middle_payroll']['years'][1]['run']['applied'])==11)
    check('second_year_revision_preserves_first_result',runs['second_year_price_revision']['years'][0]==runs['baseline']['years'][0])
    check('second_year_revision_recomputes_suffix',all(runs['second_year_price_revision']['years'][i]['result_sha256']!=runs['baseline']['years'][i]['result_sha256'] for i in [1,2]))
    check('first_year_revision_recomputes_all_years',all(a['result_sha256']!=b['result_sha256'] for a,b in zip(runs['first_year_price_revision']['years'],runs['baseline']['years'])))
    repair=registry[root['revision_refs'][-1]['digest']]['body']
    check('repair_parent_is_partial',registry[repair['parent_ref']['digest']]['body']['status']=='partial')
    check('repair_child_restores_complete_path',registry[repair['child_ref']['digest']]['body']==cases['baseline'])
    check('repair_not_committed_or_restatement',repair['committed'] is False and repair['historical_restatement'] is False)

    def rec(p,kind,name=None):
        return next(r for r in p['record_registry'].values() if r['kind']==kind and (name is None or r['body'].get('name')==name))['body']
    def year(p,name,index):
        return p['record_registry'][rec(p,'PathOutcome',name)['year_refs'][index]['digest']]['body']
    def blob(p,b,value):
        data=canonical(value);h=hashlib.sha256(data).hexdigest();b[h]=data
        p['blobs'][h]={'path':'adverse-in-memory.json','byte_length':len(data),'label':'in-memory adverse fixture'}
        return {'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(data)}
    def normalize(p):
        previous.rekey(p)
        used={x['digest'] for entry in p['record_registry'].values() for x in blobs(entry)}
        p['blobs']={h:m for h,m in p['blobs'].items() if h in used}
    def invalid(name,mutate,rehash=True,detail=None,replay=False):
        p=deepcopy(packet);b=dict(raw);mutate(p,b)
        if rehash:normalize(p)
        result=validate(p,b,replay);witnesses[name]=result
        check(name,result['status']=='invalid')
        if detail:check(name+':reason',detail in result.get('detail',''))
    invalid('changed_record_bytes',lambda p,b:rec(p,'PathOutcome','baseline').update(status='partial'),False)
    invalid('missing_blob',lambda p,b:b.pop(cases['baseline']['result_blob']['digest']),False)
    invalid('duplicate_path_ref',lambda p,b:rec(p,'PathExchange')['path_refs'].append(rec(p,'PathExchange')['path_refs'][0]),detail='duplicate exchange reference')
    invalid('duplicate_revision_ref',lambda p,b:rec(p,'PathExchange')['revision_refs'].append(rec(p,'PathExchange')['revision_refs'][0]),detail='duplicate exchange reference')
    invalid('partial_supplied_complete_memory',lambda p,b:year(p,'unknown_middle_payroll',1).update(closing_memory_blob=year(p,'baseline',1)['closing_memory_blob']),detail='partial year has closing memory')
    invalid('complete_memory_missing',lambda p,b:year(p,'baseline',1).update(closing_memory_blob=None),detail='complete memory')
    invalid('partial_relabelled_complete',lambda p,b:year(p,'unknown_middle_payroll',1).update(outcome='complete_conditional'),detail='year outcome tag')
    invalid('unexecuted_year_discarded',lambda p,b:rec(p,'PathOutcome','unknown_middle_payroll').update(unexecuted=[]),detail='case outcome binding')
    invalid('wrong_predecessor',lambda p,b:year(p,'baseline',1).update(predecessor_ref=None),detail='year predecessor')
    invalid('wrong_year_index',lambda p,b:year(p,'baseline',1).update(index=2),detail='year identity')
    invalid('false_historical_admission',lambda p,b:year(p,'baseline',0).update(historical_admission=True))
    invalid('stale_year_blob',lambda p,b:year(p,'second_year_price_revision',1).update(year_blob=year(p,'baseline',1)['year_blob']),detail='year bytes binding')
    invalid('changed_revision_index',lambda p,b:rec(p,'PathRevision').update(changed_year_index=2),detail='undeclared revision changes')
    invalid('changed_revision_parent_identity',lambda p,b:rec(p,'PathRevision').update(parent_input_sha256='0'*64),detail='revision input identities')
    invalid('empty_revision_reason',lambda p,b:rec(p,'PathRevision').update(reason='   '),detail='empty revision')
    invalid('revision_claims_historical_restatement',lambda p,b:rec(p,'PathRevision').update(historical_restatement=True))
    invalid('revision_claims_committed',lambda p,b:rec(p,'PathRevision').update(committed=True))
    invalid('exchange_claims_transactional_storage',lambda p,b:rec(p,'PathExchange').update(transactional_storage=True))
    def wrong_replacement(p,b):
        replacement=deepcopy(get(cases['baseline']['path_blob'])['continuations'][0])
        rec(p,'PathRevision')['replacement_blob']=blob(p,b,replacement)
    invalid('replacement_does_not_explain_child',wrong_replacement,detail='undeclared revision changes')
    def changed_opening(p,b):
        body=rec(p,'PathOutcome','first_year_price_revision');path=json.loads(b[body['path_blob']['digest']])
        path['initial_year']['context']['entity']='Another company';body['path_blob']=blob(p,b,path)
    invalid('changed_opening_rehashed',changed_opening,detail='case opening changed')
    def stale_suffix(p,b):
        body=rec(p,'PathOutcome','second_year_price_revision');run=json.loads(b[body['result_blob']['digest']])
        run['years'][2]=deepcopy(runs['baseline']['years'][2]);body['result_blob']=blob(p,b,run)
    invalid('stale_suffix_rehashed',stale_suffix,detail='case result chain')
    def extra_year_change(p,b):
        body=rec(p,'PathOutcome','second_year_price_revision')
        path=json.loads(b[body['path_blob']['digest']])
        path['continuations'][1]['name']='Undeclared renamed third year'
        export=rec(p,'PathExport');source=b[export['source_bundle_blob']['digest']]
        run=engine.wire(engine.execute(path,source))
        body.update(path_blob=blob(p,b,path),result_blob=blob(p,b,run),branch_sha256=digest(path))
        for i,y in enumerate(run['years']):
            yr=year(p,'second_year_price_revision',i)
            yr.update(year_result_sha256=y['result_sha256'],path_input_sha256=digest(path),
                      year_blob=blob(p,b,y),closing_memory_blob=blob(p,b,y['closing_memory']))
        rec(p,'PathRevision')['child_input_sha256']=digest(path)
    invalid('undeclared_additional_year_change',extra_year_change,detail='undeclared revision changes',replay=True)
    base_path=get(cases['baseline']['path_blob'])
    source=raw[registry[root['baseline_export_ref']['digest']]['body']['source_bundle_blob']['digest']]
    for index in [0,1]:
        replacement=deepcopy(base_path['initial_year'] if index==0 else base_path['continuations'][0])
        replacement['period']['end_exclusive']='2028-01-01'
        result=engine.revise(base_path,source,index,replacement,'Adverse period change')
        witnesses['period_change:'+str(index)]=result
        check('revision_period_change_refused:'+str(index),result.get('reason')=='revision_changes_opening_or_period')
    def forged_report(p,b):
        # Keep every hash and exported year binding internally consistent.
        body=rec(p,'PathOutcome','second_year_price_revision');run=json.loads(b[body['result_blob']['digest']])
        y=run['years'][-1];y['report']['lines']['cash']['value']='999/1'
        y['result_sha256']=digest({k:v for k,v in y.items() if k!='result_sha256'})
        yr=year(p,'second_year_price_revision',2)
        yr['year_result_sha256']=y['result_sha256'];yr['year_blob']=blob(p,b,y)
        body['result_blob']=blob(p,b,run)
    p=deepcopy(packet);b=dict(raw);forged_report(p,b);normalize(p)
    witnesses['forged_report_bindings_only']=validate(p,b,False)
    check('hashes_do_not_prove_report_arithmetic',witnesses['forged_report_bindings_only']['status']=='validated_synthetic_exchange')
    invalid('forged_report_semantic_replay',forged_report,detail='local replay mismatch',replay=True)
    for name,path in [('relative','../outside-project'),('absolute','/etc/passwd')]:
        p=deepcopy(packet);p['blobs'][next(iter(p['blobs']))]['path']=path
        try:previous.load_blob_files(p);rejected=False
        except ValueError:rejected=True
        check('blob_path_refused:'+name,rejected)
    protected=json.loads((HERE/'baseline.json').read_text())
    check('protected_evidence_unchanged',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()))
    return {'checks':checks,'passed':all(x['passed'] for x in checks),'witnesses':witnesses}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    start=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();evidence=conformance();target=HERE/'checks.json'
    if args.record:
        if target.exists():raise RuntimeError('Evidence exists; use read-only replay')
        target.write_text(json.dumps(evidence,indent=2)+'\n')
        manifest={'started_utc':start,'wall_seconds':time.perf_counter()-clock,
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-path-exchanges-20261023/verify.py --record',
            'environment':'system Python '+platform.python_version()+'; jsonschema; trusted local replay',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
            'data_version':json.loads((HERE/'baseline.json').read_text()),'random_seeds':'N/A: deterministic',
            'plan':'docs/plans/accounting-company-path-exchanges-20261023.md',
            'result':'data/accounting-master/company-path-exchanges-20261023/result.md',
            'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif target.exists() and evidence!=json.loads(target.read_text()):raise AssertionError('Evidence replay mismatch')
    failed=[x['name'] for x in evidence['checks'] if not x['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'recorded':args.record}))
    return bool(failed)


if __name__=='__main__':raise SystemExit(main())
