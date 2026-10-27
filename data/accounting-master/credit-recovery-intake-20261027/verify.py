from copy import deepcopy
from hashlib import sha256
import json,os,platform,subprocess,sys,time
import intake as m

def main():
    started=time.monotonic();assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    attempt=sys.argv[1];assert attempt in ['01','02','03']
    out=m.H/('attempt-'+attempt);out.mkdir(exist_ok=False)
    checks=[];cases=[];controls=[]
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2)+'\n')
    def ck(name,value):
        checks.append({'name':name,'passed':bool(value)});assert value,name
    protected=m.protected()
    for p in m.H.iterdir():
        if p.is_file():protected[str(p.relative_to(m.R))]=sha256(p.read_bytes()).hexdigest()
    save('source-lock.json',protected)
    try:
        originals=json.loads((m.C/'cases.json').read_text())
        for original in originals:
            claim=original['result'];ident=claim['case_id'];request=m.request(ident);before=deepcopy(request)
            result=m.assess(request)
            ck(ident+':unresolved',result['status']=='unresolved')
            ck(ident+':complete_history',result['historical_claim']==claim)
            ck(ident+':history_identity',result['claim_record_sha256']==original['record_sha256'])
            ck(ident+':unchanged_request',request==before)
            ck(ident+':no_effects',result['financial_effects']==[] and result['posts'] is False and result['mutations']==[])
            for field in ['receipt','allocation','legal_assessment','accounting_proposal','cash_flow_proposal']:
                ck(ident+':unknown:'+field,result[field] is None)
            ck(ident+':admission_flags',all(result[k]==v for k,v in m.FLAGS.items()))
            ck(ident+':missing_evidence_explicit',len(result['missing_evidence'])==5)
            ck(ident+':closure_date',result['closure_date']==claim['timeline'][-1]['date'])
            expected=[x for x in claim['movements'] if x['component'] in ['writeoff','uncollected']]
            ck(ident+':component_count',len(expected)==len(result['historical_components']))
            for component,got in zip(expected,result['historical_components']):
                ck(ident+':component:'+str(component['movement_index']),got=={'movement_index':component['movement_index'],
                   'movement_sha256':m.digest(component),'component':component})
            ck(ident+':saved_validation',m.validate(request,result,m.digest(result))['status']=='verified_unresolved')
            cases.append({'request':request,'result':result,'record_sha256':m.digest(result)})
            # Submit actual historical source IDs only: no invented positive receipt.
            for movement in claim['movements']:
                if movement['component']!='collections':continue
                for field in ['id','sha256']:
                    probe=deepcopy(request);key='historical_source_event_'+field
                    probe['receipt']={key:movement['source_event_'+field]}
                    refusal=m.assess(probe)
                    name=ident+':historical_receipt:'+str(movement['movement_index'])+':'+field
                    ck(name,refusal['status']=='rejected' and refusal['reason']=='receipt_already_in_history')
                    controls.append({'name':name,'request':probe,'verdict':refusal})
        by={x['result']['case_id']:x for x in cases};base=by['partial-early-writeoff']
        def corrupt(name,edit,ident='partial-early-writeoff'):
            row=by[ident];broken=deepcopy(row['result']);edit(broken)
            v=m.validate(row['request'],broken,m.digest(broken));ck(name,v['status']=='rejected')
            controls.append({'name':name,'verdict':v,'fresh_hash':m.digest(broken)})
        corrupt('lost_history_stage',lambda x:x['historical_claim']['timeline'].pop())
        corrupt('erased_zero_component',lambda x:x['historical_components'].pop(0),'zero-rate')
        corrupt('altered_historical_amount',lambda x:x['historical_components'][0]['component'].update(amount='0'))
        corrupt('stale_component_identity',lambda x:x['historical_components'][0].update(movement_sha256='0'*64))
        corrupt('unknown_as_zero',lambda x:x.update(receipt=0))
        corrupt('false_posting',lambda x:x.update(posts=True))
        corrupt('false_receipt_admission',lambda x:x.update(receipt_admission=True))
        corrupt('false_recovery_admission',lambda x:x.update(recovery_admission=True))
        corrupt('false_legal_forgiveness',lambda x:x.update(legal_forgiveness=True))
        corrupt('false_accounting_admission',lambda x:x.update(accounting_admission=True))
        corrupt('missing_gap_reasons',lambda x:x.update(missing_evidence=[]))
        for key in ['claim_record_sha256','native_request_sha256','native_result_sha256','context_sha256']:
            req=deepcopy(base['request']);req[key]='0'*64;v=m.assess(req)
            ck('request:'+key,v['status']=='rejected');controls.append({'name':'stale_'+key,'verdict':v})
        for key in ['allocation','legal_assessment','accounting_proposal','cash_flow_proposal']:
            req=deepcopy(base['request']);req[key]={'status':'admitted'};v=m.assess(req)
            ck('unadmitted:'+key,v['status']=='rejected');controls.append({'name':'unsupported_'+key,'verdict':v})
        req=deepcopy(base['request']);req['receipt']={};v=m.assess(req)
        ck('new_receipt_boundary',v['status']=='rejected' and v['reason']=='new_receipt_outside_unresolved_intake_profile')
        controls.append({'name':'new_receipt_boundary','verdict':v})
        for path,h in protected.items():ck('preserved:'+path,sha256((m.R/path).read_bytes()).hexdigest()==h)
        save('cases.json',cases);save('controls.json',controls)
        save('verification.json',{'status':'PASS_UNRESOLVED_ONLY','cases':len(cases),'assertions':len(checks),
             'controls':len(controls),'protected_files':len(protected),'checks':checks,'readiness':'not_ready'})
    except Exception as exc:
        save('failure.json',{'type':type(exc).__name__,'reason':str(exc),'checks':checks});raise
    finally:
        save('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=m.R,text=True).strip(),
            'command':'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/credit-recovery-intake-20261027/verify.py '+attempt,
            'environment':{'python':platform.python_version(),'executable':sys.executable},
            'cpu_gpu':'CPU; GPU intentionally hidden; no GPU libraries','random_seeds':'N/A deterministic',
            'wall_seconds':round(time.monotonic()-started,3),'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-credit-recovery-intake-20261027.md','result':'data/accounting-master/credit-recovery-intake-20261027/result.md',
            'artifacts':{str(p.relative_to(m.R)):sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    v=json.loads((out/'verification.json').read_text());print(json.dumps({k:x for k,x in v.items() if k!='checks'}))
if __name__=='__main__':main()
