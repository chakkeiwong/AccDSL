from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json,os,platform,subprocess,sys,time
import classify as m
HERE=m.HERE;ROOT=m.ROOT
def check(v,reason):
    if not v:raise AssertionError(reason)
def request(case,library,mode):
    entry=library.cases[case];retained=library.load(case,entry['sha256']);origins=retained['result']['closing']['unclassified_cash_origins']
    policy={'reference':'conditional-fixture:'+mode,'status':'caller_assumption',
        'context_sha256':m.digest(retained['result']['opening']['context']),
        'rationale':'Synthetic caller-supplied activity labels; no IAS 7 or issuer eligibility assertion.'}
    rows=[]
    for i,origin in enumerate(origins):
        amount=Q(origin['amount']);parts=[]
        if mode=='split' and origin['kind']=='collection':
            pairs=[('first',amount/2,'investing'),('second',amount/2,'operating')]
        else:
            activity='operating' if mode=='all_operating' or origin['kind'] in {'integral_cost','integral_fee'} else 'investing'
            pairs=[('whole',amount,activity)]
        for identity,q,activity in pairs:parts.append({'id':identity,'amount':m.fmt(q),'activity':activity,'policy_reference':policy['reference']})
        rows.append({'origin_index':i,'origin_sha256':m.origin_digest(origin),'status':'declared','components':parts})
    return {'profile':m.PROFILE,'case_id':case,'case_sha256':entry['sha256'],'policy':policy,'classifications':rows}
def oracle(origins,mode):
    totals={a:{'receipts':Q(0),'payments':Q(0),'net':Q(0)} for a in m.ACTIVITIES}
    for origin in origins:
        q=Q(origin['amount'])
        if mode=='split' and origin['kind']=='collection':pairs=[('investing',q/2),('operating',q/2)]
        else:pairs=[('operating' if mode=='all_operating' or origin['kind'] in {'integral_cost','integral_fee'} else 'investing',q)]
        for a,v in pairs:
            totals[a]['net']+=v
            totals[a]['receipts' if v>=0 else 'payments']+=abs(v)
    return {a:{k:m.fmt(v) for k,v in row.items()} for a,row in totals.items()}
def main():
    started=time.monotonic();check(os.environ.get('CUDA_VISIBLE_DEVICES')=='-1','CPU hiding required');library=m.Library()
    out=HERE/'cases';out.mkdir(exist_ok=True);rows=[];host_checks=0;observations=0;nonrational=0
    for case in library.cases:
        for mode in ['all_operating','mixed','split']:
            req=request(case,library,mode);before=deepcopy(req);retained=library.load(case,req['case_sha256']);native_before=m.digest(retained)
            result=m.assess(req,library);check(result['status']=='classified_under_supplied_premise',str(result)[:300])
            check(req==before and m.digest(retained)==native_before,'mutation')
            check(result['mutations']==[] and not any(result[k] for k in ['posts','source_admission','accounting_admission','fiscal_complete','notes_complete']),'admission')
            original=retained['result'];origins=original['closing']['unclassified_cash_origins']
            for actual,native in zip(result['observations'],original['observations']):
                observations+=1;prefix=actual['origin_prefix'];expected=oracle(origins[:prefix],mode)
                check(actual['known_activity_totals']==expected,'independent activity oracle')
                check(actual['native_report']==native['report'] and actual['state_sha256']==native['state_sha256'],'native evidence lost')
                check(Q(actual['native_cash_change'])==sum((Q(x['amount']) for x in origins[:prefix]),Q(0)),'cash prefix')
                check(sum((Q(v['net']) for v in expected.values()),Q(0))==Q(actual['native_cash_change']),'activity net')
                check(actual['unclassified_net']=='0/1' and actual['totals_scope']=='complete_retained_cash_origins','partial labelled complete')
                host=actual['host_report']
                if host:
                    host_checks+=1;check(set(host['reconciliations'].values())=={'0/1'},'host statements do not tie')
                    check(host['cash_flows']['gross_origins']==actual['gross_flows'],'gross origins lost')
                    check(host['equity']['profit']==host['income']['profit'],'equity profit')
                else:nonrational+=1;check(actual['host_comparison_status']=='nonrational_financial_state_not_rounded','nonrational hidden')
            path=out/(case+'.'+mode+'.json');path.write_text(json.dumps({'request':req,'result':result},indent=2)+chr(10))
            rows.append({'case':case,'mode':mode,'observations':len(result['observations']),'path':str(path.relative_to(ROOT)),'sha256':sha256(path.read_bytes()).hexdigest()})
    # Missing zero-valued origins still make classification incomplete.
    base=request('partial-early-writeoff.named.plain',library,'mixed');positive=m.assess(base,library)
    missing=deepcopy(base);missing['classifications'].pop(2);result=m.assess(missing,library)
    check(result['status']=='unresolved' and result['observations'][-1]['unclassified_net']=='0/1','missing zero origin hidden')
    check(all(r['host_report'] is None for r in result['observations']),'partial host report admitted')
    unknown=deepcopy(base);unknown['classifications'][-1]={'origin_index':4,'origin_sha256':base['classifications'][-1]['origin_sha256'],'status':'unknown','reason':'contractual classification undecided'}
    result=m.assess(unknown,library);check(result['observations'][0]['status']=='classified_under_supplied_premise' and result['observations'][-1]['status']=='unresolved','future unknown contaminated earlier prefix')
    check(result['origins'][-1]['classification']['reason']=='contractual classification undecided','unknown reason lost')
    # Exercise the third permitted activity as a deliberately labelled test
    # premise. This does not propose financing classification for a real loan.
    financing=deepcopy(base)
    for row in financing['classifications']:
        for part in row['components']:part['activity']='financing'
    financed=m.assess(financing,library);check(financed['status']=='classified_under_supplied_premise','financing branch')
    check(financed['observations'][-1]['known_activity_totals']['financing']=={'receipts':'99/1','payments':'100/1','net':'-1/1'},'financing gross totals')
    check(all(o['native_report']==p['native_report'] for o,p in zip(financed['observations'],positive['observations'])),'classification changed financial state')
    (HERE/'supplemental-cases.json').write_text(json.dumps({'missing_zero_origin':m.assess(missing,library),
        'future_unknown':result,'financing_branch':financed},indent=2)+chr(10))
    negatives=[]
    def run(name,edit):
        req=deepcopy(base);edit(req);outcome=m.assess(req,library);check(outcome['status']=='invalid',name+' accepted');negatives.append({'case':name,'reason':outcome['reason']})
    run('stale_case',lambda r:r.update(case_sha256='0'*64))
    run('wrong_origin',lambda r:r['classifications'][0].update(origin_sha256='0'*64))
    run('duplicate_origin',lambda r:r['classifications'].__setitem__(1,deepcopy(r['classifications'][0])))
    run('bad_sum',lambda r:r['classifications'][0]['components'][0].update(amount='-97/1'))
    run('opposite_sign',lambda r:r['classifications'][0]['components'][0].update(amount='98/1'))
    run('unknown_activity',lambda r:r['classifications'][0]['components'][0].update(activity='other'))
    run('noncanonical_rational',lambda r:r['classifications'][0]['components'][0].update(amount='-196/2'))
    run('wrong_policy',lambda r:r['classifications'][0]['components'][0].update(policy_reference='unrelated'))
    run('wrong_context',lambda r:r['policy'].update(context_sha256='0'*64))
    run('invented_admission',lambda r:r['policy'].update(status='accounting_approved'))
    run('unknown_field',lambda r:r.update(round_balances=True))
    def hidden_net(r):
        a=r['classifications'][0]['components'][0];r['classifications'][0]['components']=[dict(a,amount='-100/1'),dict(a,id='offset',amount='2/1')]
    run('hidden_netting',hidden_net)
    # An independent hand calculation for the price/cost/receipt example.
    final=positive['observations'][-1]['known_activity_totals']
    check(final['investing']=={'receipts':'99/1','payments':'98/1','net':'1/1'},'hand investing amounts')
    check(final['operating']=={'receipts':'0/1','payments':'2/1','net':'-2/1'},'hand operating amounts')
    check(positive['observations'][-1]['native_cash_change']=='-1/1','hand cash change')
    for path,h in library.lock['files'].items():check(sha256((ROOT/path).read_bytes()).hexdigest()==h,'source changed')
    checks={'status':'passed_conditional_classification','retained_projections':36,'native_schedules':9,'classification_cases':len(rows),
        'observations':observations,'unchanged_host_reports':host_checks,'nonrational_observations_preserved':nonrational,
        'negative_cases':negatives,'unknown_and_missing_cases':2,'financing_branch_checked':True,'cases':rows,'source_files_preserved':len(library.lock['files']),
        'accounting_admission':False,'readiness':'not_ready'}
    (HERE/'checks.json').write_text(json.dumps(checks,indent=2)+chr(10))
    files=[p for p in HERE.iterdir() if p.is_file() and p.name!='run-manifest.json']
    manifest={'git_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/credit-cash-classification-20261026/verify.py',
        'environment':{'python':platform.python_version(),'executable':sys.executable,'libraries':'standard library and pinned local helpers'},
        'cpu_gpu':'CPU only; GPU intentionally hidden; no GPU libraries imported','random_seeds':'N/A: deterministic',
        'wall_seconds':round(time.monotonic()-started,3),'data_version':'source-lock.json','plan':library.lock['plan'],
        'result':'data/accounting-master/credit-cash-classification-20261026/result.md',
        'artifacts':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}}
    (HERE/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps({k:v for k,v in checks.items() if k not in ['cases','negative_cases']}|{'negative_cases':len(negatives)}))
if __name__=='__main__':main()
