from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json,os,platform,subprocess,sys,time
import stage as m
def main():
    start=time.monotonic();assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    attempt=sys.argv[1];assert attempt in ['01','02','03']
    out=m.H/('attempt-'+attempt);out.mkdir(exist_ok=False)
    checks=[];cases=[];controls=[]
    def save(n,v):(out/n).write_text(json.dumps(v,indent=2)+'\n')
    def ck(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
    lock=m.protected()
    lock.update({str(p.relative_to(m.R)):sha256(p.read_bytes()).hexdigest() for p in m.H.iterdir() if p.is_file()})
    save('source-lock.json',lock)
    try:
        authored=json.loads((m.H/'authored.json').read_text());accounts=authored['accounts']
        sys.path.insert(0,str(m.R/'scripts'));import insurance_loss_book_v1 as native
        for ident,expected in authored['cases'].items():
            req=m.request(ident);before=deepcopy(req);row=m.retained(ident);result=m.assess(req)
            ck(ident+':accepted',result['status']=='checked_stage_only')
            ck(ident+':native_replay',native.native_result(row['request'])==row['result']==result['native_result'])
            ck(ident+':input_preserved',req==before)
            ck(ident+':flags',all(result[k]==v for k,v in m.FLAGS.items()))
            ck(ident+':stage_count',len(result['stages'])==4)
            ck(ident+':journal_count',len(result['journals'])==3)
            ck(ident+':memory_count',len(result['memory_origins'])==4)
            ck(ident+':cash_count',len(result['cash_origins'])==2)
            ck(ident+':zero_loss_not_account','issued_loss' not in accounts and 'held_loss_recovery' not in accounts)
            for i,(actual,target) in enumerate(zip(result['stages'],expected)):
                values=dict(zip(accounts,target['balances']))
                ck(ident+':complete_balance:'+str(i),actual['balances']==values)
                for k in ['stage','memory','issued_profit','held_profit','cash_change','equity']:
                    ck(ident+':authored:'+str(i)+':'+k,actual[k]==target[k])
                ck(ident+':unknowns:'+str(i),all(actual[k] is None for k in ['date','issued_group_id','held_group_id']))
                ck(ident+':no_equity_plug:'+str(i),actual['balances']['opening_equity']=='-34')
                if i:
                    previous=dict(zip(accounts,expected[i-1]['balances']));journal=result['journals'][i-1]
                    aggregate={a:Q(0) for a in accounts}
                    for p in journal['postings']:aggregate[p['account']]+=Q(p['debit_change'])
                    ck(ident+':independent_journal:'+str(i),aggregate=={a:Q(values[a])-Q(previous[a]) for a in accounts})
                    origins=[o for o in result['memory_origins'] if o['stage']==target['stage']]
                    changed=['issued_loss','held_loss_recovery'] if i==1 else ['issued_loss'] if i==2 else ['held_loss_recovery']
                    oracle=[{'stage':target['stage'],'component':k,'before':expected[i-1]['memory'][k],
                        'delta':str(Q(target['memory'][k])-Q(expected[i-1]['memory'][k])),
                        'after':target['memory'][k],'native_source':['report/change','report/issued_service','report/held_service'][i-1]} for k in changed]
                    ck(ident+':complete_memory_origin:'+str(i),origins==oracle)
            # Independent source example is pre-existing, not generated here.
            treaty=json.loads((m.H.parent/'insurance-treaty-changes-20261015/cases.json').read_text())
            old=next(c for c in treaty['cases'] if c['id']=='covered-contracts-and-estimate-change')
            if ident=='recovery-change-once':
                rename={'issued-liability':'issued_liability','issued-loss':'issued_loss_reversal','held-fcf':'held_fcf',
                        'held-expense':'held_change_expense','cash':'cash'}
                event=next(e for e in old['events'] if e['id']=='covered-claims-revised')
                source={rename[k]:str(Q(v)) for k,v in event['debits_positive'].items()}
                ck('historical_change_journal',source=={p['account']:p['debit_change'] for p in result['journals'][0]['postings']})
            ck(ident+':saved_validation',m.validate(req,result,m.digest(result))['status']=='verified_stage_only')
            cases.append({'request':req,'result':result,'record_sha256':m.digest(result)})
        def corrupt(name,edit,case=0):
            base=cases[case];broken=deepcopy(base['result']);edit(broken)
            v=m.validate(base['request'],broken,m.digest(broken));ck('control:'+name,v['status']=='rejected')
            controls.append({'name':name,'fresh_hash':m.digest(broken),'verdict':v})
        corrupt('lost_origin',lambda x:x['memory_origins'].pop())
        corrupt('duplicate_origin',lambda x:x['memory_origins'].append(deepcopy(x['memory_origins'][0])))
        corrupt('lost_zero_origin',lambda x:x['memory_origins'].pop(),1)
        corrupt('wrong_origin_component',lambda x:x['memory_origins'][0].update(component='held_loss_recovery'))
        corrupt('invented_date',lambda x:x['stages'][0].update(date='2025-01-01'))
        corrupt('invented_group',lambda x:x['stages'][0].update(held_group_id='G2'))
        corrupt('false_fiscal',lambda x:x.update(fiscal_admission=True))
        corrupt('false_group_admission',lambda x:x.update(separate_group_identity_admission=True))
        corrupt('false_accounting',lambda x:x.update(accounting_admission=True))
        corrupt('false_posting',lambda x:x.update(posts=True))
        corrupt('false_cash_classification',lambda x:x.update(cash_classification_admission=True))
        corrupt('hidden_group_netting',lambda x:x['stages'][1].update(issued_profit='2',held_profit='0'))
        corrupt('double_estimate_expense',lambda x:x['journals'][0]['postings'].append({'account':'held_component_expense','debit_change':'2'}))
        corrupt('omit_later_component_expense',lambda x:x['journals'][2]['postings'].__setitem__(3,{'account':'held_component_expense','debit_change':'0'}))
        corrupt('net_cash_only',lambda x:x.update(cash_origins=[{'stage':'held_service','kind':'net','amount':'-92'}]))
        corrupt('changed_native',lambda x:x['native_result']['report']['change'].update(additional_component_expense='2'))
        corrupt('changed_context',lambda x:x['native_context'].update(group='another'))
        corrupt('equity_plug',lambda x:x['stages'][1]['balances'].update(opening_equity='-36'))
        corrupt('lost_journal',lambda x:x['journals'].pop())
        corrupt('changed_stage_order',lambda x:x['stages'].reverse())
        for key in ['native_request_sha256','native_result_sha256']:
            req=deepcopy(cases[0]['request']);req[key]='0'*64;v=m.assess(req)
            ck('stale:'+key,v['status']=='rejected');controls.append({'name':key,'verdict':v})
        for p,h in lock.items():ck('source:'+p,sha256((m.R/p).read_bytes()).hexdigest()==h)
        save('cases.json',cases);save('controls.json',controls)
        save('verification.json',{'status':'PASS_STAGE_ONLY','cases':len(cases),'stages':8,'assertions':len(checks),
             'controls':len(controls),'protected_files':len(lock),'checks':checks,'fiscal_admission':False,'readiness':'not_ready'})
    except Exception as exc:save('failure.json',{'reason':str(exc),'type':type(exc).__name__,'checks':checks});raise
    finally:
        save('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=m.R,text=True).strip(),
             'command':'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/insurance-recovery-stage-book-20261027/verify.py '+attempt,
             'environment':{'python':platform.python_version(),'executable':sys.executable},
             'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':round(time.monotonic()-start,3),
             'data_version':'source-lock.json','plan':'docs/plans/accounting-insurance-recovery-stage-book-20261027.md',
             'result':'data/accounting-master/insurance-recovery-stage-book-20261027/result.md',
             'artifacts':{p.name:sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    print(json.dumps({k:v for k,v in json.loads((out/'verification.json').read_text()).items() if k!='checks'}))
if __name__=='__main__':main()
