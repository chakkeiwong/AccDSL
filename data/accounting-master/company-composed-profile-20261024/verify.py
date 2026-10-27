"""Check explicit composition routes against the retained native reference."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
from hashlib import sha256
import json,os,sys,time,platform,subprocess,traceback
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
from company_program import fixture,execute,verify_result,schema,canon,digest,EXEC,FILES
from company_program_text import render,lower

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def conformance():
    body,*_=fixture();checks=[];adverse={}
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    text=render(body);restored=lower(text);result=execute(body);expected=json.loads((EXEC/'trace.json').read_text())
    check('typed_text_exact_identity',canon(body)==canon(restored))
    check('canonical_text_roundtrip',render(restored)==text)
    check('complete_conditional',result['status']=='complete_conditional')
    check('complete_13_proposals',len(result['proposals'])==13)
    check('all_proposals_match_predecessor',result['proposals']==[r['proposal'] for r in expected['trace']])
    check('whole_annual_report_matches',result['annual_report']==expected['annual'])
    check('whole_next_opening_matches',result['next_opening']==expected['next_opening'])
    check('text_typed_execution_identity',execute(restored)==result)
    check('trusted_result_replay',verify_result(body,result))
    check('admission_and_durability_not_inferred',result['source_admission'] is False and result['durable_commit'] is False)
    def trial(name,edit,status='invalid',stopped=None):
        b=deepcopy(body);edit(b);before=canon(b);r=execute(b);adverse[name]=r if r['status']=='invalid' else {k:r[k] for k in ['status','stopped_status','stopped_index','reason','unexecuted','complete_annual_opening']}
        check(name,r['status']==status and (stopped is None or r.get('stopped_status')==stopped))
        check(name+'_input_unchanged',canon(b)==before);return r
    trial('wrong_profile',lambda b:b.__setitem__('profile','CompanyOperationPathDraft/1'))
    trial('extra_wallet',lambda b:b.__setitem__('wallet','100/1'))
    trial('missing_opening',lambda b:b['source'].pop('opening_sha256'))
    trial('changed_owner',lambda b:b['context'].__setitem__('entity','Northstar'))
    trial('changed_currency',lambda b:b['context'].__setitem__('currency','EUR'))
    trial('changed_packet',lambda b:b['source'].__setitem__('packet_sha256','0'*64))
    trial('changed_component',lambda b:b.__setitem__('return_module_sha256','0'*64))
    trial('changed_event_pointer',lambda b:b['events'][0].__setitem__('source_pointer','/elsewhere'))
    trial('changed_event_digest',lambda b:b['events'][0].__setitem__('event_sha256','0'*64))
    trial('duplicate_event',lambda b:b['events'].append(deepcopy(b['events'][0])))
    trial('omitted_event',lambda b:b['events'].pop(1))
    trial('reordered_events',lambda b:b['events'].reverse())
    trial('swapped_native_route',lambda b:b['events'][1].__setitem__('capability','retained-corporate'))
    trial('swapped_tax_route',lambda b:b['events'][7].__setitem__('capability','native-return'))
    trial('arbitrary_import',lambda b:b['capabilities'][0].__setitem__('id','os.system'))
    trial('changed_method_bytes',lambda b:b['capabilities'][0].__setitem__('implementation_sha256','0'*64))
    trial('wrong_report_route',lambda b:b['report'].__setitem__('capability','native-tax'))
    trial('wrong_carry_route',lambda b:b['carry'].__setitem__('capability','native-tax'))
    trial('different_next_year',lambda b:b['carry'].__setitem__('next_end_exclusive','2028-01-01'))
    trial('extra_review',lambda b:b['events'][1]['review_findings'].__setitem__('invented',True))
    trial('integer_review',lambda b:b['events'][1]['review_findings'].__setitem__('all_rights_closed',1))
    trial('multiline_metadata',lambda b:b.__setitem__('name','P\nCompany'))
    partial=trial('unknown_tax_review',lambda b:b['events'][7]['review_findings'].__setitem__('rate_enacted','unknown'),'partial','unresolved')
    check('unknown_tax_preserves_seven_events',len(partial['proposals'])==7 and partial['state']==expected['trace'][6]['proposal']['after'])
    check('unknown_tax_has_no_report_or_opening','annual_report' not in partial and 'next_opening' not in partial and partial['complete_annual_opening'] is False)
    check('unknown_tax_lists_six_unexecuted',len(partial['unexecuted'])==6)
    unknown_body=deepcopy(body);unknown_body['events'][7]['review_findings']['rate_enacted']='unknown'
    check('unknown_review_text_identity',canon(lower(render(unknown_body)))==canon(unknown_body))
    check('partial_result_replays',verify_result(unknown_body,partial))
    forged_partial=deepcopy(partial);forged_partial['unexecuted']=[]
    check('partial_unexecuted_schedule_binding',not verify_result(unknown_body,forged_partial))
    check('caller_review_does_not_rewrite_source',partial['source']==result['source'] and partial['program_sha256']!=result['program_sha256'])
    trial('false_return_review',lambda b:b['events'][1]['review_findings'].__setitem__('all_rights_closed',False),'partial','unsupported')
    unknown_return=trial('unknown_return_review',lambda b:b['events'][1]['review_findings'].__setitem__('all_rights_closed','unknown'),'partial','unresolved')
    check('unknown_return_preserves_redemption',len(unknown_return['proposals'])==1 and unknown_return['state']==expected['trace'][0]['proposal']['after'])
    trial('false_review_precedes_unknown',lambda b:b['events'][7]['review_findings'].update(rate_enacted='unknown',recovery_supported=False),'partial','unsupported')
    for cap,index in [('native-return',1),('native-tax',7),('retained-corporate',0),('legal-annual',13),('annual-carry',13)]:
        r=execute(body,set(FILES)-{cap})
        check('missing_capability_'+cap,r['status']=='partial' and r['stopped_status']=='unsupported' and r['stopped_index']==index and len(r['proposals'])==index)
        check('missing_capability_'+cap+'_no_carry','next_opening' not in r and r['complete_annual_opening'] is False)
        if cap=='annual-carry':check('report_survives_missing_carry_capability',r['annual_report']==expected['annual'])
    forged=deepcopy(result);forged['annual_report']['closing_cash']='999/1'
    check('forged_report_refused',not verify_result(body,forged))
    forged=deepcopy(result);forged['next_opening']['seen']=[]
    check('forged_lifetime_history_refused',not verify_result(body,forged))
    label=deepcopy(body);label['name']='P "quoted"; café'
    check('quoted_name_roundtrip',canon(lower(render(label)))==canon(label))
    check('name_metadata_preserves_financial_result',execute(label)['annual_report']==result['annual_report'])
    malformed=[text.replace('end_program;',''),text+'source invalid;',text.replace('return_component','exec_code',1),
        text.replace(' true;',' 1;',1),text.replace('end_program;','review absent finding true;\nend_program;')]
    for i,value in enumerate(malformed):
        try:lower(value);bad=False
        except Exception:bad=True
        check('malformed_text_'+str(i),bad)
    m=json.loads((EXEC/'manifest.json').read_text());locks={}
    for group in ['inputs','implementation','outputs']:locks.update(m[group])
    for p in [EXEC/'manifest.json',ROOT/'docs/plans/accounting-company-composed-profile-20261024.md']:
        locks[str(p.relative_to(ROOT))]=sha(p)
    for n,h in locks.items():check('protected_'+n,sha(ROOT/n)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'adverse':adverse},body,text,result,locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for n,h in m[group].items():assert sha(ROOT/n)==h,n
    result,body,text,run,locks=conformance();obs={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
        'failed':[c['name'] for c in result['checks'] if not c['passed']],'protected_files':len(locks),'wall_seconds':time.monotonic()-clock}
    if not result['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for n,v in [('checks.json',result),('fixture.json',body),('schema.json',schema()),('execution.json',run),('source-lock.json',locks)]:dump(HERE/n,v)
        (HERE/'example.accdsl').write_text(text)
        outputs={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','fixture.json','schema.json','execution.json','source-lock.json','example.accdsl']}
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':obs['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; exact composed reference','cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1',
            'random_seeds':'N/A: deterministic','inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':outputs,'plan':'docs/plans/accounting-company-composed-profile-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':
        assert canon(result)==canon(json.loads((HERE/'checks.json').read_text()))
        assert canon(body)==canon(json.loads((HERE/'fixture.json').read_text()))
        assert canon(run)==canon(json.loads((HERE/'execution.json').read_text()))
        assert text==(HERE/'example.accdsl').read_text()
    print(json.dumps(obs));return 0 if result['passed'] else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        p=HERE/('failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc())
        print(json.dumps({'status':'failed','error':type(exc).__name__+': '+str(exc)[:350],'diagnostic':str(p.relative_to(ROOT))}));sys.exit(1)
