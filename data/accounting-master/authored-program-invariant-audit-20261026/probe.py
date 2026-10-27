from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,sys,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
PROGRAM=HERE.parent/'authored-program-composition-20261026'
sys.path.insert(0,str(PROGRAM));import runner
spec=importlib.util.spec_from_file_location('program_invariant_fixtures',PROGRAM/'verify.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+NL)
def main():
    start=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True)
    lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        lock=json.loads((PROGRAM/'source-lock.json').read_text())
        for p in [PROGRAM/'runner.py',PROGRAM/'verify.py',PROGRAM/'checks.json',PROGRAM/'result.md']:
            lock[str(p.relative_to(ROOT))]=sha(p)
        dump(lock_path,lock)
    lock=json.loads(lock_path.read_text())
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    rows=[]
    for owner in ['alpha','beta']:
        body,native,source,mapping,_=helper.build(owner)
        book=deepcopy(native['trace'][0]['result']['after']);claim='invoice/a~1'
        helper.life.control(book,source['roles']);runner.typed.typed_book(book,body['memory_definition'],body['schemas'])
        mutations=[
            ('claim-total',lambda b:b['memory']['claims'][claim].update(remaining='31/1'),'claim_receivable_sum'),
            ('missing-sale-event',lambda b:b['memory']['claims'][claim].update(sale_event='unseen-event'),'claim_sale_event'),
            ('due-before-issued',lambda b:b['memory']['claims'][claim].update(due='2027-01-01'),'claim_dates'),
            ('future-issue',lambda b:b['memory']['claims'][claim].update(issued='2027-01-03'),'claim_dates'),
            ('negative-assessment',lambda b:b['memory']['claims'][claim].update(assessed_remaining='-1/1'),'negative_assessment'),
            ('unassessed-nonzero-overdue',lambda b:b['memory']['claims'][claim].update(overdue='1/1'),'unassessed_placeholder'),
            ('future-assessment',lambda b:b['memory']['claims'][claim].update(assessed=True,assessment_date='2027-01-03'),'assessment_chronology'),
            ('wrong-overdue-snapshot',lambda b:b['memory']['claims'][claim].update(assessed=True,overdue='1/1'),'overdue_snapshot'),
            ('empty-customer',lambda b:b['memory']['claims'][claim].update(customer=''),'customer'),
        ]
        for name,change,reason in mutations:
            bad=deepcopy(book);change(bad)
            try:helper.life.control(bad,source['roles'])
            except (ValueError,KeyError,TypeError) as exc:native_reason=str(exc)
            else:raise AssertionError('native accepted '+name)
            assert reason in native_reason,(name,native_reason)
            try:runner.typed.typed_book(bad,body['memory_definition'],body['schemas'])
            except ValueError as exc:
                assert name=='empty-customer',(name,str(exc))
                rows.append({'company':owner,'case':name,'native_control':'refused','native_reason':native_reason,
                    'typed_book':'refused','typed_reason':str(exc),'authored_report':'not_attempted','gap_confirmed':False})
                continue
            # Keep the genuine period opening. Author the one changed claim field
            # in the sale method, then ask for the report after that sale.
            program=deepcopy(body);program['commands']=program['commands'][:1]
            old_key=program['commands'][0]['registry_sha256'];registry=deepcopy(program['registries'][old_key])
            entry=registry['entries']['sale'];method=entry['method']
            changed_fields={k:v for k,v in bad['memory']['claims'][claim].items() if v!=book['memory']['claims'][claim][k]}
            operation=next(x for x in method['memory']['definition']['operations'] if x['op']=='insert')
            for key,value in changed_fields.items():operation['value']['fields'][key]={'kind':'literal','value':value}
            q=deepcopy(native['trace'][0]['request']);q['method']=deepcopy(method);q['event']=deepcopy(program['commands'][0]['event'])
            text=runner.methods.frontend.render(method,q['profile'],helper.helpers.environment(program['opening'],q))
            entry.update(method_sha256=runner.digest(method),source=text,source_sha256=sha256(text.encode()).hexdigest())
            key=runner.digest(registry);program['registries'][key]=registry;program['commands'][0]['registry_sha256']=key
            program['commands'].append({'kind':'report','id':'audit.report','cutoff':bad['date'],'equity_movements':[],'notes':[]})
            result=runner.run(program)
            stop=result.get('stop') or {};assert result['status']=='complete_provisional',(name,result['status'],stop.get('reason',result.get('reason')))
            assert result['current']==bad,(name,'changed state mismatch')
            row={'company':owner,'case':name,'native_control':'refused','native_reason':native_reason,
                 'typed_book':'accepted','authored_report':result['status'],'gap_confirmed':True}
            rows.append(row);dump(out/(owner+'.'+name+'.json'),{'changed_book':bad,'comparison':row,'program':program,'program_result':result})
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    gaps=[row for row in rows if row['gap_confirmed']]
    checks={'passed':True,'derived_cases':len(rows),'derived_counterexamples':len(gaps),
        'native_outer_guard_gaps':len({row['case'] for row in gaps}),'already_typed_refusals':len(rows)-len(gaps),'companies':2,
        'protected_files':len(lock),'successful_baselines_remain_valid':True,'whole_lifecycle_equivalence':False}
    dump(HERE/'checks.json',checks);dump(HERE/'comparisons.json',rows)
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/authored-program-invariant-audit-20261026/probe.py',
        'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
        'wall_seconds':time.monotonic()-start,'data_version':sha(lock_path),
        'plan_file':'docs/plans/accounting-authored-program-invariant-audit-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),
        'artifact_paths':['checks.json','comparisons.json','examples/'],'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(checks))
if __name__=='__main__':main()
