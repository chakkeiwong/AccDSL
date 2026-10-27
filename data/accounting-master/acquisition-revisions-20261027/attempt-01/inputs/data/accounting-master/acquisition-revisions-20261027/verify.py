"""Whole conditional views, dated revision refusals and full report expectations."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
import json,os,sys,time,platform,resource,subprocess,traceback
import reference as m
H=Path(__file__).resolve().parent;R=H.parents[2]
SAVED=json.loads((m.D/'attempt-01/cases.json').read_text())
def rebind_worksheet(b):
    b['payload']['expected_books_sha256']=m.h.digest(b['payload']['books']);b['expected_payload_sha256']=m.h.digest(b['payload']);return b
def bind(b,requests=True):
    if requests:
        for side in ['original','revised']:rebind_worksheet(b['payload'][side])
        for side in ['original','revised']:b['payload']['revision'][side+'_sha256']=m.h.digest(b['payload'][side])
    b['expected_payload_sha256']=m.h.digest(b['payload']);return b
def fixture(mix='cash',cutoff='2026-03-01T00:00:00Z'):
    original=deepcopy(next(x['request'] for x in SAVED if x['id']=='proportional/'+mix));revised=deepcopy(original)
    rp=revised['payload'];items={x['id']:x for x in rp['acquired_items']};items['equipment']['recognised_balance']='100/1';items['deferred_tax']['recognised_balance']='-15/2';rp['expense_adjustment']='3/1';rp['tax_release']='3/4'
    source='Synthetic later information about the acquisition-date equipment measurement; no actual source truth established.';sid=m.h.source_digest(source)
    old={'equipment':'90/1','deferred_tax':'-5/1','expense_adjustment':'2/1','tax_release':'1/2'};new={'equipment':'100/1','deferred_tax':'-15/2','expense_adjustment':'3/1','tax_release':'3/4'}
    revision=dict(original_sha256='',revised_sha256='',subject=['P','S'],source_sha256=sid,effective_at='2025-07-01T00:00:00Z',discovered_at='2026-01-15T00:00:00Z',period_end_exclusive='2026-07-01T00:00:00Z',provisional=True,disposition='acquisition_date_information',available_at={'manager':'2026-02-01T00:00:00Z'},dependent_adjustments=[dict(field=k,before=old[k],after=new[k],disposition='changed',reason='Stipulated correlated synthetic revision; no tax-policy inference') for k in old],premise='Conditional acquisition-date information on a previously provisional item')
    return bind(dict(profile=m.PROFILE,payload=dict(original=original,revised=revised,revision=revision,sources={sid:source},query=dict(actor='manager',cutoff=cutoff)),expected_payload_sha256=''))
def expected_report(mix):
    cash0,closecash,capital,eqnew,paid,net,assets,equity,owners={
        'cash':('230/1','270/1','-300/1','0/1','120/1','-70/1','6213/16','5779/16','5169/16'),
        'equity':('350/1','390/1','-420/1','120/1','0/1','50/1','8133/16','7699/16','7089/16'),
        'mixed':('300/1','340/1','-370/1','70/1','50/1','0/1','7333/16','6899/16','6289/16')}[mix]
    return dict(net_assets_at_acquisition='245/2',nci_at_acquisition='245/8',goodwill='225/8',acquisition_balances=dict(cash=cash0,equipment='100/1',payable='-20/1',deferred_tax='-15/2',parent_capital=capital,goodwill='225/8',nci='-245/8'),closing_balances=dict(cash=closecash,equipment='90/1',payable='-20/1',deferred_tax='-27/4',parent_capital=capital,goodwill='225/8',nci='-245/8',revenue='-40/1',depreciation='10/1',tax_expense='-3/4'),profit='123/4',owners_profit='369/16',nci_profit='123/16',nci_closing='613/16',owners_equity_closing=owners,assets_closing=assets,liabilities_closing='107/4',equity_closing=equity,cash=dict(opening='300/1',consideration_paid=paid,noncash_equity=eqnew,acquired='50/1',acquisition_net=net,operating='40/1',closing=closecash),parent_equity=dict(opening='300/1',new_equity=eqnew,owners_profit='369/16',closing=owners))
def expected_journals():return [dict(id='acquisition',origin='Conditional supplied item measurements and investment/equity elimination',at='2025-07-01T00:00:00Z',entries={'S.capital':'80/1','S.retained_pre':'20/1','S.equipment':'30/1','group.goodwill':'225/8','group.deferred_tax':'-15/2','P.investment':'-120/1','group.nci':'-245/8'}),dict(id='basis-depreciation',origin='Supplied acquired equipment basis expense',at='2026-01-01T00:00:00Z',entries={'S.equipment':'-3/1','group.depreciation':'3/1'}),dict(id='tax-liability-release',origin='Stipulated tax liability and later release; no tax recognition/rate inference',at='2026-01-01T00:00:00Z',entries={'group.deferred_tax':'3/4','group.tax_expense':'-3/4'})]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(100,100));out=H/sys.argv[1];out.mkdir(exist_ok=False);clock=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];cases=[];controls=[]
    files={H/'reference.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-acquisition-revisions-20261027.md',m.D/'reference.py',m.D/'result.md',m.D/'attempt-01/cases.json',m.D/'attempt-01/source-lock.json'}
    files.update(R/p for p in json.loads((m.D/'attempt-01/source-lock.json').read_text()))
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        dest=out/'inputs'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
    def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n+': '+repr(a)[:170]+' != '+repr(b)[:170]
    def run(name,b,status,selected,mix='cash',reason=None):
        original=deepcopy(b);r=m.view(b);ck(name+'/status',r['status'],status);ck(name+'/selected',r['selected'],selected);ck(name+'/immutable',b,original)
        ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(name+'/submissions',[r['original_submission'],r['revised_submission']],[b['payload']['original'],b['payload']['revised']])
        ck(name+'/query',r['query'],b['payload']['query']);ck(name+'/revision',r['revision'],b['payload']['revision']);ck(name+'/sources',r['sources'],b['payload']['sources'])
        if reason:ck(name+'/reason',r['reason'],reason)
        ck(name+'/alternative_ids',[x['id'] for x in r['alternatives']],['original','revised'] if status in ['conditional_revised_view','unresolved_views'] else ['original'])
        prior=next(x['result'] for x in SAVED if x['id']=='proportional/'+mix)
        for alt in r['alternatives']:
            hr=alt['request']['payload']['symbolic_request']['payload']['scope_request']['history_request']
            ck(name+'/'+alt['id']+'/actor',hr['actor'],b['payload']['query']['actor']);ck(name+'/'+alt['id']+'/cutoff',hr['cutoff'],b['payload']['query']['cutoff'])
            ck(name+'/'+alt['id']+'/full_result',alt['result'],m.w.report(alt['request']))
            if alt['id']=='original':
                for key in ['report','original_books','acquisition_worksheet','closing_worksheet','conditional_measurements','acquired_items']:ck(name+'/original/'+key,alt['result'][key],prior[key])
            else:
                ck(name+'/revised/report',alt['result']['report'],expected_report(mix))
                ck(name+'/revised/legal_books',alt['result']['original_books'],prior['original_books'])
                for stage,key in [('acquisition','acquisition_worksheet'),('closing','closing_worksheet')]:
                    js=expected_journals()[:1] if stage=='acquisition' else expected_journals();ck(name+'/revised/'+stage+'/journals',alt['result'][key]['journals'],js)
                    raw=deepcopy(prior[key]['raw']);ck(name+'/revised/'+stage+'/raw',alt['result'][key]['raw'],raw)
                    adj={k:Fraction(v) for k,v in raw.items()}
                    for journal in js:
                        for account,value in journal['entries'].items():adj[account]=adj.get(account,Fraction())+Fraction(value)
                    ck(name+'/revised/'+stage+'/all_accounts',alt['result'][key]['adjusted'],{k:str(v.numerator)+'/'+str(v.denominator) for k,v in adj.items()})
        cases.append(dict(id=name,request=b,result=r));return r
    def reject(name,b,reason,rehash=True,requests=True):
        if rehash:bind(b,requests)
        before=deepcopy(b);r=m.view(b);ck(name+'/status',r['status'],'invalid');ck(name+'/reason',r['reason'],reason);ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));controls.append(dict(id=name,request=b,result=r))
    try:
        for mix in ['cash','equity','mixed']:
            run(mix+'/before',fixture(mix,'2026-01-20T00:00:00Z'),'original_view','original',mix,'revision_not_yet_available')
            run(mix+'/at',fixture(mix,'2026-02-01T00:00:00Z'),'conditional_revised_view','revised',mix)
            run(mix+'/after',fixture(mix),'conditional_revised_view','revised',mix)
        b=fixture();b['payload']['revision']['available_at']['manager']=None;run('unknown_availability',bind(b),'unresolved_views',None,reason='revision_availability_unknown')
        b=fixture();b['payload']['revision']['disposition']='unresolved';run('unknown_disposition',bind(b),'unresolved_views',None,reason='revision_disposition_unknown')
        for key,value,reason in [('disposition','later_event','later_event_requires_other_method'),('provisional',False,'not_provisional'),('effective_at','2025-07-02T00:00:00Z','different_effective_date'),('period_end_exclusive','2026-01-15T00:00:00Z','outside_measurement_period')]:
            b=fixture();b['payload']['revision'][key]=value;run(key,bind(b),'other_method_required','original',reason=reason)
        b=fixture();b['payload']['query']['cutoff']='2026-03-02T00:00:00Z';reject('stale_envelope',b,'payload_binding',False)
        b=fixture();b['payload']['revision']['original_sha256']='0'*64;reject('original_hash',b,'original_binding',requests=False)
        b=fixture();b['payload']['revision']['revised_sha256']='0'*64;reject('revised_hash',b,'revised_binding',requests=False)
        b=fixture();b['payload']['revision']['subject']=['S','P'];reject('wrong_subject',b,'subject')
        b=fixture();b['payload']['query']['actor']='analyst';reject('wrong_actor',b,'single_actor_profile')
        b=fixture();b['payload']['sources'][next(iter(b['payload']['sources']))]='tampered';reject('source_tamper',b,'source_identity')
        b=fixture();b['payload']['revised']['payload']['consideration']['premise']='changed';reject('unrelated_revision',b,'unsupported_changed_field')
        b=fixture();b['payload']['revision']['period_end_exclusive']='2026-07-01T00:00:00.1Z';reject('over_one_year',b,'measurement_period_limit')
        b=fixture();b['payload']['revision']['discovered_at']='2025-06-30T00:00:00Z';reject('before_acquisition',b,'discovery_before_acquisition')
        b=fixture();b['payload']['revision']['available_at']['manager']='2026-01-14T00:00:00Z';reject('availability_before_discovery',b,'availability_before_discovery')
        b=fixture();b['payload']['revision']['dependent_adjustments'].pop();reject('missing_dependent_adjustment',b,'dependent_adjustments_population')
        b=fixture();b['payload']['revision']['dependent_adjustments'][1]['after']='-5/1';reject('stale_tax_dependency',b,'dependent_amount_binding:deferred_tax')
        b=fixture();b['payload']['revision']['dependent_adjustments'][0]['disposition']='reviewed_unchanged';reject('wrong_change_disposition',b,'dependent_disposition:equipment')
        b=fixture();b['payload']['revision']['dependent_adjustments'][2]['reason']='';reject('missing_adjustment_reason',b,'text_required')
        b=fixture();b['payload']['revision']['provisional']='yes';reject('untyped_provisional',b,'provisional_boolean')
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,obj in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(obj,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic synthetic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-acquisition-revisions-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
