"""Exact amendment paths and content-bound reuse of original literature cases."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip,json,platform,subprocess,sys,time,traceback
import fixture as f
import measure

H=Path(__file__).resolve().parent;ROOT=f.ROOT;OUT=H/sys.argv[1]
OUT.mkdir(exist_ok=False);started=time.monotonic()
checks=[];native=[];controls=[];measures=[];reused=[];sources=set()
def dump(name,x):(OUT/name).write_text(json.dumps(x,indent=2)+chr(10))
def ck(name,a,b):checks.append(dict(name=name,actual=a,expected=b,passed=a==b))
def read(path):
    p=ROOT/'data/accounting-master'/path;sources.add(p)
    return json.loads(p.read_text())
def run(name,b,scoped=True):
    before=deepcopy(b);r=f.run(b) if scoped else f.program.run(b)
    ck(name+'/input unchanged',b,before);ck(name+'/replay',f.program.verify(b,r),True)
    native.append(dict(id=name,input=b,result=r));return r
def refused(name,fn,reason):
    try:fn();actual='accepted'
    except ValueError as exc:actual=str(exc)
    controls.append(dict(id=name,reason=actual));ck(name,actual,reason)
def reuse(directory,names):
    rows=read(directory+'/checks.json');lookup={x.get('name',x.get('id')):x for x in rows}
    for name in names:
        x=lookup[name];ck('reused/'+name,x['actual'],x['expected']);ck('saved pass/'+name,x['passed'],True)
    folder=ROOT/'data/accounting-master'/directory
    files=sorted(p for p in folder.iterdir() if p.is_file());sources.update(files)
    for filename in ['source-hashes.json','run-manifest.json']:
        p=folder/filename
        if not p.exists():continue
        content=json.loads(p.read_text());hashes=content if filename=='source-hashes.json' else content.get('source_hashes',{})
        for path,expected in hashes.items():
            source=ROOT/path;sources.add(source);ck('retained source/'+path,sha256(source.read_bytes()).hexdigest(),expected)
    reused.append(dict(directory=directory,selected_checks=names,files={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}))

def main():
    complete={}
    for owner in ['alpha','beta']:
        for amend in [False,True]:
            name=owner+('/amended' if amend else '/unchanged');b,m=f.make(owner,amend);r=run(name,b)
            ck(name+'/status',r['status'],'complete_provisional')
            if r['status']!='complete_provisional':continue
            complete[name]=r;opening=b['opening'];second=7 if amend else 5
            for year,index,coupon,total in [(1,0,5,5),(2,4 if amend else 3,second,5+second)]:
                t=r['trace'][index]['result']['transition'];balances=deepcopy(opening['balances'])
                balances.update({m['cash']:f.h.fmt(20-total),m['interest']:f.h.fmt(coupon),m['retained']:f.h.fmt(0 if year==1 else 5)})
                memory=deepcopy(opening['memory']);memory['terms']['stage']='1/1'
                if year==2 and amend:memory['terms'].update(coupon='7/1',revision='1/1')
                journal={a:'0/1' for a in balances};journal.update({m['cash']:f.h.fmt(-coupon),m['interest']:f.h.fmt(coupon)})
                ck(name+f'/year{year}/all balances',t['after']['balances'],balances)
                ck(name+f'/year{year}/all memory',t['after']['memory'],memory)
                ck(name+f'/year{year}/all journal',t['journal'],journal)
                ck(name+f'/year{year}/flows',[x['amount'] for x in t['flows']],[f.h.fmt(-coupon)])
                report=r['trace'][index+1]['result']
                ck(name+f'/year{year}/BS',report['balance_sheet'],dict(total_assets=f.h.fmt(120-total),total_liabilities='100/1',equity_including_profit=f.h.fmt(20-total)))
                ck(name+f'/year{year}/income',report['income'],dict(income='0/1',expenses=f.h.fmt(coupon),profit=f.h.fmt(-coupon)))
                ck(name+f'/year{year}/cash bridge',[report['cash_flows'][k] for k in ['opening_cash','closing_cash','net_movement']],[f.h.fmt(20 if year==1 else 15),f.h.fmt(20-total),f.h.fmt(-coupon)])
                ck(name+f'/year{year}/equity bridge',[report['equity'][k] for k in ['opening','direct_movements','profit','closing']],[f.h.fmt(20 if year==1 else 15),'0/1',f.h.fmt(-coupon),f.h.fmt(20-total)])
                ck(name+f'/year{year}/reconciliation',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(name+f'/year{year}/no admission',[report['source_admission'],report['accounting_admission']],[False,False])
            carry=r['trace'][2]['result'];expected=deepcopy(opening['balances'])
            expected.update({m['cash']:'15/1',m['retained']:'5/1'})
            ck(name+'/carry all balances',carry['next_opening']['balances'],expected)
            ck(name+'/carry all memory',carry['next_opening']['memory'],opening['memory'])
            ck(name+'/archive identity',r['archives'][0]['archive'],carry['archive'])
            ck(name+'/period',carry['next_opening']['period'],dict(start='2028-01-01',end_exclusive='2029-01-01'))
            if amend:
                a=r['trace'][3]['result']['transition'];mem=deepcopy(opening['memory']);mem['terms'].update(coupon='7/1',revision='1/1')
                ck(name+'/amendment full memory',a['after']['memory'],mem)
                ck(name+'/amendment no balance change',a['after']['balances'],expected)
                ck(name+'/amendment zero journal',a['journal'],{k:'0/1' for k in expected})
                ck(name+'/amendment no flows',a['flows'],[])
        ck(owner+'/prior report unchanged',complete[owner+'/amended']['trace'][1]['result'],complete[owner+'/unchanged']['trace'][1]['result'])
        ck(owner+'/prior archive unchanged',complete[owner+'/amended']['archives'],complete[owner+'/unchanged']['archives'])
    for name in ['false_approval','unknown_approval','wrong_date','wrong_new_coupon','duplicate_id','duplicate_revision','bad_revision','wrong_old_coupon','pre_effective_revision']:
        b,m=f.make();e=b['commands'][3]['event'];expected_status='invalid';prefix=3
        if name=='false_approval':e['inputs']['approved']['value']=f.program.engine.known(False);expected_status='unsupported'
        if name=='unknown_approval':e['inputs']['approved']['value']=dict(status='unknown',reason='Approval unavailable');expected_status='unresolved'
        if name=='wrong_date':e['date']='2028-01-02'
        if name=='wrong_new_coupon':e['inputs']['new_coupon']['value']=f.program.engine.known('8/1')
        if name.startswith('duplicate'):
            b['commands'].insert(4,deepcopy(b['commands'][3]));prefix=4
            if name=='duplicate_revision':b['commands'][4]['event']['id']='amend.again'
        if name=='bad_revision':b['opening']['memory']['terms']['revision']='2/1';prefix=0
        if name=='wrong_old_coupon':b['opening']['memory']['terms']['coupon']='4/1';prefix=0
        if name=='pre_effective_revision':b['opening']['memory']['terms'].update(revision='1/1',coupon='7/1');prefix=0
        r=run(name,b);ck(name+'/stopped',r['status'],'stopped_provisional')
        ck(name+'/stop status',r['stop']['status'],expected_status);ck(name+'/accepted prefix',len(r['trace']),prefix)
        ck(name+'/remaining retained',r['remaining_commands'],b['commands'][prefix:])
        ck(name+'/atomic',f.program.digest(r['current']),r['trace'][-1]['after_sha256'] if r['trace'] else f.program.digest(b['opening']))
        controls.append(dict(id=name,status=r['stop']['status'],reason=r['stop']['reason']))
    # Generic carry permits explicit resets. Demonstrate its limit and reject at the scoped boundary.
    forged,m=f.make(amend=False)
    for key,value in [('coupon','7/1'),('revision','1/1')]:
        forged['commands'][2]['memory_policies']['/terms/'+key]=dict(kind='reset',type=forged['opening']['memory_types']['/terms/'+key],value=value,provenance='Deliberately forged no-event change')
    r=run('generic forged carry limitation',forged,False)
    ck('generic forged carry accepted',r['status'],'complete_provisional')
    ck('generic forged carry cash',r['current']['balances'][m['cash']],'8/1')
    refused('scoped forged carry',lambda:f.run(forged),'term_change_without_event:/terms/coupon')
    b,m=f.make();b['commands'][2]['memory_policies']['/terms/face']=dict(kind='reset',type=b['opening']['memory_types']['/terms/face'],value='101/1',provenance='Wrong principal')
    refused('principal mutation',lambda:f.run(b),'term_change_without_event:/terms/face')
    reuse('company-state-original-debt-failures-20261028/attempt-03',['fixed historical and stress family feasible','floating historical and stress family feasible','interior historical and stress family feasible','original marginal combination rejected','joint identity no below violation within declared family','joint identity no above violation within declared family'])
    witnesses=read('company-state-original-debt-failures-20261028/attempt-03/witnesses.json')
    ck('same observed debt and interest',[(x['principal'],x['historical_interest'],x['probability']) for x in witnesses],[('100','5',None)]*3)
    ck('different supported futures',[(x['stress_interest'],x['closing_cash']) for x in witnesses],[('5','90'),('7','88'),('6','89')])
    reuse('company-state-persistent-rate-failures-20261028/attempt-01',[owner+'/'+kind+'/carry full memory' for owner in ['alpha','beta'] for kind in ['fixed','floating']])
    reuse('company-state-model-scope-20261028/attempt-01',['duplicate_preserves_full_observations','original.mean','split_duplicate.mean','equal_encoding_weights.mean','equal_weights_change_law','relation_support_preserved'])
    paths={x['id']:x for x in read('company-state-model-scope-20261028/attempt-01/paths.json')}
    histories={x['history'][-1]['current_output']['cash']:x['history'] for x in paths['original']['original']['paths']}
    supports={};base_measure=None
    for name,weights in [('original',{'high':'1/2','low':'1/2'}),('split_duplicate',{'high':'1/4','high.copy':'1/4','low':'1/2'}),('equal_encoding_weights',{'high':'1/3','high.copy':'1/3','low':'1/3'})]:
        support=[dict(id=k,history=deepcopy(histories[60 if k=='low' else 100])) for k in weights]
        premise=dict(profile='AuthoredHistoryMeasure/1',support_sha256=measure.digest(support),weights=weights,provenance=dict(origin='Explicit synthetic teaching hypothesis',meaning='Equal economic-state mass' if name!='equal_encoding_weights' else 'Equal syntax-record mass, a different measure',source='Saved company-state-model-scope-20261028/attempt-01 plus this declared binding'))
        before=deepcopy(support);r=measure.evaluate(support,premise);ck(name+'/support not mutated',support,before)
        ck(name+'/complete saved law',r['probability_law'],sorted(paths[name]['original']['paths'],key=lambda x:json.dumps(x['history'],sort_keys=True,separators=(',',':'))))
        ck(name+'/provenance retained',r['provenance'],premise['provenance'])
        ck(name+'/no justified issuer prior',r['issuer_prior_justified'],False)
        ck(name+'/no invented probability',measure.evaluate(support)['probability_law'],None)
        measures.append(dict(id=name,support=support,measure=premise,result=r));supports[name]=support
        if name=='original':base_measure=premise
    s=supports['original']
    for name,reason in [('missing_provenance','explicit_provenance_required'),('stale_support','stale_support'),('missing_weight','weight_support_mismatch'),('unnormalized','mass_not_one'),('negative','negative_mass'),('float','exact_rational_required'),('zero_denominator','exact_rational_required')]:
        p=deepcopy(base_measure)
        if name=='missing_provenance':p['provenance']={}
        if name=='stale_support':p['support_sha256']='0'*64
        if name=='missing_weight':del p['weights']['low']
        if name=='unnormalized':p['weights']['high']='1/3'
        if name=='negative':p['weights'].update(high='-1/2',low='3/2')
        if name=='float':p['weights']['high']=0.5
        if name=='zero_denominator':p['weights']['high']='1/0'
        refused(name,lambda:measure.evaluate(s,p),reason)
    reuse('company-state-quiet-rights-scope-20261028/attempt-01',['equal immediate marginal/next','equal immediate marginal/observation','equal immediate marginal/output','signal retained/x/status','signal retained/y/status','equal-law duplicate full path/full path equality'])
    expectations=read('company-state-quiet-rights-scope-20261028/attempt-01/signal-expectations.json')
    ck('joint signals affect chosen policy',[expectations[k] for k in ['x/lend/wait','y/lend/wait']],['7/10','-1/2'])
    rows=read('unified-program-20261028/failure-map.json')['rows']
    original=[r['original_row'] for r in rows if r['original_row']['id'] in ['LIT-F001','LIT-F002','LIT-F003','LIT-F005']]
    ck('original rows retained',len(original),4);dump('original-rows.json',original)
    return dict(passed=all(c['passed'] for c in checks),checks=len(checks),native_programs=len(native),refusal_controls=len(controls),separate_measures=len(measures),reused_units=len(reused),failed=[c['name'] for c in checks if not c['passed']],original_rows=[r['id'] for r in original])

try:
    summary=main();dump('verification.json',summary)
except Exception:
    dump('failure.json',dict(error=traceback.format_exc(),checks_passed=sum(c['passed'] for c in checks)));raise
finally:
    dump('checks.json',checks);dump('controls.json',controls);dump('measures.json',measures);dump('reused-evidence.json',reused)
    (OUT/'native-results.json.gz').write_bytes(gzip.compress(json.dumps(native).encode()))
    for name in ['check.py','fixture.py','measure.py']:(OUT/name).write_bytes((H/name).read_bytes());sources.add(H/name)
    sources.add(ROOT/'docs/plans'/('company-state-literature-history-20261028.md'))
    sources.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump('source-hashes.json',{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)})
    dump('manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU only; no accelerator imports',random_seeds='N/A deterministic exact examples',data_version='Supplied amendment and content-bound retained results',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-started,plan='docs/plans/company-state-literature-history-20261028.md',result=str(H.relative_to(ROOT)/'result.md'),artifacts=str(OUT.relative_to(ROOT))))
print(json.dumps(summary));raise SystemExit(not summary['passed'])
