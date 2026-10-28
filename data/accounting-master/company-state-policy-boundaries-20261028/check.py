"""Deterministic finite policy discriminators with preserved complete results."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import json,platform,subprocess,sys,time,traceback
import methods as m

H=Path(__file__).resolve().parent;ROOT=H.parents[2];OUT=H/sys.argv[1]
OUT.mkdir(exist_ok=False);start=time.monotonic();checks=[];results=[];controls=[]
def dump(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+chr(10))
def ck(name,actual,expected):checks.append(dict(name=name,actual=actual,expected=expected,passed=actual==expected))
def refuse(name,fn,reason):
    try:fn();actual='accepted'
    except ValueError as exc:actual=str(exc)
    controls.append(dict(name=name,reason=actual));ck(name,actual,reason)
def keep(name,inputs,result):results.append(dict(name=name,inputs=inputs,result=result));return result

def main():
    discrete=[m.issue(a) for a in ['0','1']]
    keep('original discrete regimes',dict(actions=['0','1'],lot='100',obligation='50'),discrete)
    ck('discrete full results',discrete,[dict(action='0',proceeds='0',payment='0',closing_cash='0',unpaid='50',default=True,cost='2'),dict(action='1',proceeds='100',payment='50',closing_cash='50',unpaid='0',default=False,cost='1')])
    half=Q(1,2);relaxed=dict(action=str(half),proceeds=str(100*half),unpaid='0',closing_cash='0',cost=str(half))
    keep('continuous relaxation is changed problem',dict(action='1/2'),relaxed)
    ck('fractional relaxation apparent lower cost',Q(relaxed['cost'])<min(Q(x['cost']) for x in discrete),True)
    refuse('fractional action',lambda:m.issue('1/2'),'indivisible_action')
    refuse('negative issue',lambda:m.issue('-1'),'indivisible_action')
    refuse('float action',lambda:m.issue(0.5),'exact_rational_required')
    for action in ['0','1']:
        rows=[dict(id=t,observation='cash0',lifted_action=action) for t in ['fixed','floating']]
        r=keep('explicit lift'+action,rows,m.lift(rows));ck('lift feasible'+action,r['cash0'],m.issue(action))
    refuse('hidden type dependent lift',lambda:m.lift([dict(observation='cash0',lifted_action='0'),dict(observation='cash0',lifted_action='1')]),'lift_uses_hidden_history')
    basis=dict(x_currency='USD',y_currency='USD',x_date='2028-12-31',y_date='2028-12-31')
    for denominator in [10,100,10000]:
        e=Q(1,denominator);rows=[dict(id='near',x=str(-e),y=str(e),mass='1')]
        r=keep('small cash/unit default error'+str(denominator),dict(rows=rows,threshold='0',delta=str(e),context=basis),m.boundary(rows,'0',str(e),basis))
        ck('unit probability error'+str(denominator),r['probability_error'],'1')
        ck('small cash error'+str(denominator),r['mean_absolute_error'],str(2*e))
    # The exact pointwise implication supplies the set inclusion used by the proof.
    values=['-2','-1/100','0','1/100','2']
    for x,y,delta in product(values,values,['1/200','1/10','1']):
        mismatch=(Q(x)<0)!=(Q(y)<0);near=abs(Q(x))<=Q(delta);large=abs(Q(x)-Q(y))>=Q(delta)
        ck('indicator inclusion/'+x+'/'+y+'/'+delta,(not mismatch) or near or large,True)
    rows=[dict(id=str(i),x=x,y=y,mass='1/4') for i,(x,y) in enumerate([('-2','-2'),('-1/10','1/10'),('1/10','1/5'),('2','2')])]
    for delta in ['1/20','1/5','1']:
        r=keep('finite boundary coupling'+delta,dict(rows=rows,threshold='0',delta=delta,context=basis),m.boundary(rows,'0',delta,basis))
        ck('finite probability error'+delta,r['probability_error'],'1/4')
        ck('finite mean distance'+delta,r['mean_absolute_error'],'3/40')
        ck('boundary inequality'+delta,Q(r['probability_error'])<=Q(r['probability_bound']),True)
    unweighted=[{k:v for k,v in r.items() if k!='mass'} for r in rows]
    r=keep('unweighted boundary',dict(rows=unweighted,threshold='0',delta='1/5',context=basis),m.boundary(unweighted,'0','1/5',basis))
    ck('unweighted no probability',r['probability_bound'],None);ck('boundary alternatives',r['uncertain_ids'],['1','2'])
    atom=[dict(id='at',x='0',y='-1/100',mass='1')]
    r=keep('strict threshold atom',dict(rows=atom,threshold='0',delta='1/10',context=basis),m.boundary(atom,'0','1/10',basis))
    ck('strict zero is not default',[r['exact_default'],r['approx_default'],r['boundary_mass']],['0','1','1'])
    same=[dict(id='same',x='0',y='0',mass='1')];r=m.boundary(same,'0','1/10',basis)
    ck('zero distance zero probability error',[r['mean_absolute_error'],r['probability_error']],['0','0'])
    for name,change,reason in [('currency',dict(y_currency='EUR'),'cash_basis_mismatch'),('date',dict(y_date='2029-12-31'),'cash_basis_mismatch')]:
        refuse(name,lambda:m.boundary(rows,'0','1/5',{**basis,**change}),reason)
    refuse('zero delta',lambda:m.boundary(rows,'0','0',basis),'positive_delta_required')
    bad=deepcopy(rows);bad[0]['mass']='-1/4';refuse('negative coupling mass',lambda:m.boundary(bad,'0','1/5',basis),'negative_mass')
    bad=deepcopy(rows);bad[0]['mass']='1/2';refuse('unnormalized coupling',lambda:m.boundary(bad,'0','1/5',basis),'mass_not_one')
    bad=deepcopy(rows);del bad[0]['mass'];refuse('partial coupling measure',lambda:m.boundary(bad,'0','1/5',basis),'partial_measure')
    exact={'wait':'0','issue':'100'};approx={'wait':'100','issue':'0'}
    r=keep('same minima wrong policy',dict(exact=exact,approx=approx,selected='issue',epsilon='100',eta='0'),m.regret(exact,approx,'issue','100','0'))
    ck('equal optimized values',r['optimized_value_gap'],'0');ck('wrong chosen policy regret',r['selected_regret'],'100')
    refuse('minima do not establish uniform bound',lambda:m.regret(exact,approx,'issue','0','0'),'uniform_bound_violated')
    exact={'wait':'0','issue':'1/5'};approx={'wait':'1/10','issue':'9/100'}
    r=keep('uniform common policy bound',dict(exact=exact,approx=approx,selected='issue',epsilon='11/100',eta='0'),m.regret(exact,approx,'issue','11/100','0'))
    ck('actual finite regret',r['selected_regret'],'1/5');ck('uniform bound',r['bound'],'11/50')
    # Exhaustively compare all two-policy exact/approximate costs on a small grid.
    grid=['0','1/10','1/5'];table=[]
    for a,b,c,d in product(grid,repeat=4):
        x={'a':a,'b':b};y={'a':c,'b':d};e=max(abs(Q(a)-Q(c)),abs(Q(b)-Q(d)))
        for selected in ['a','b']:
            eta=Q(y[selected])-min(map(Q,y.values()));r=m.regret(x,y,selected,str(e),str(eta))
            ck('common class bound/'+','.join([a,b,c,d,selected]),Q(r['selected_regret'])<=Q(r['bound']),True)
            table.append(dict(exact=x,approx=y,selected=selected,epsilon=str(e),eta=str(eta),result=r))
    keep('exhaustive two-policy costs',dict(grid=grid),table)
    refuse('different feasible class',lambda:m.regret({'a':'0'},{'b':'0'},'a','0','0'),'common_policy_class_required')
    refuse('missing chosen action',lambda:m.regret(exact,approx,'fractional','1','0'),'selected_policy_missing')
    refuse('eta condition violated',lambda:m.regret(exact,approx,'wait','11/100','0'),'eta_optimality_violated')
    # Local finite illustration of the sampled-first-value identifier mechanism.
    empirical=[dict(id='left',x1='-1/100',x2='99/100',mass='1/2'),dict(id='right',x1='1/100',x2='-99/100',mass='1/2')]
    individual={'left':'-1/100','right':'1/100'};pooled={k:'near_zero' for k in individual}
    for name,obs,expected,count in [('individual',individual,'-1/2',5),('pooled',pooled,'0',3)]:
        r=keep('empirical stopping/'+name,dict(rows=empirical,observations=obs),m.stopping(empirical,obs))
        ck(name+'/optimum',r['optimal_cost'],expected);ck(name+'/complete policy count',len(r['policies']),count)
    sample_policy={'left':'stop','right':'continue'}
    ck('sample-specific actions measurable individually',m.validate_path_actions(empirical,individual,sample_policy),{'-1/100':'stop','1/100':'continue'})
    refuse('same observed history future choice',lambda:m.validate_path_actions(empirical,pooled,sample_policy),'future_information_leak')
    true=[];obs={}
    for first,shock in product([Q(-1,100),Q(1,100)],[-1,1]):
        ident=str(first)+'/'+str(shock);true.append(dict(id=ident,x1=str(first),x2=str(first+shock),mass='1/4'));obs[ident]=str(first)
    r=keep('declared independent-increment comparison',dict(rows=true,observations=obs),m.stopping(true,obs))
    ck('all feasible true policy costs',[p['cost'] for p in r['policies']],['0']*5)
    selected=next(p for p in r['policies'] if p['policy']=={'-1/100':'stop','1/100':'continue'})
    ck('empirical selected policy true cost',selected['cost'],'0')
    future_actions={r['id']:'stop' if Q(r['x1'])<Q(r['x2']) else 'continue' for r in true}
    refuse('true future sign inaccessible',lambda:m.validate_path_actions(true,obs,future_actions),'future_information_leak')
    original=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
    ids=['LIT-F006','LIT-F007','LIT-F008','LIT-F009'];rows=[r['original_row'] for r in original['rows'] if r['original_row']['id'] in ids]
    ck('all original rows preserved',len(rows),4);dump('original-rows.json',rows)
    return dict(passed=all(c['passed'] for c in checks),checks=len(checks),result_groups=len(results),refusal_controls=len(controls),finite_policy_comparisons=len(table),failed=[c['name'] for c in checks if not c['passed']],original_rows=ids)

try:
    summary=main();dump('verification.json',summary)
except Exception:
    dump('failure.json',dict(error=traceback.format_exc(),checks_passed=sum(c['passed'] for c in checks)));raise
finally:
    dump('checks.json',checks);dump('results.json',results);dump('controls.json',controls)
    sources=[H/'methods.py',H/'check.py',ROOT/'docs/plans/company-state-policy-boundaries-20261028.md',ROOT/'data/accounting-master/unified-program-20261028/failure-map.json']
    sources+=[ROOT/'data/accounting-master/literature-closure-20261026'/name for name in ['exact_cases.py','exact-results.json','finite-compression.py','finite-compression-results.json','source-reading.md','source-support.json','text/pflug.txt','text/adapted-estimation.txt']]
    sources+=[ROOT/'docs/papers'/name for name in ['A Distance for Multistage Stochastic Optimization Models Pflug (2012).pdf','Estimating processes in adapted Wasserstein distance Backhoff (2022).pdf']]
    sources.append(ROOT/'docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/lit-09-approximation-4.tex')
    for name in ['check.py','methods.py']:(OUT/name).write_bytes((H/name).read_bytes())
    dump('source-hashes.json',{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources})
    dump('manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU only; standard-library rational arithmetic; no accelerator imports',random_seeds='N/A deterministic finite enumeration',data_version='Explicit teaching laws/actions, local derivations and retained technical sources',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan='docs/plans/company-state-policy-boundaries-20261028.md',result=str(H.relative_to(ROOT)/'result.md'),artifacts=str(OUT.relative_to(ROOT))))
print(json.dumps(summary));raise SystemExit(not summary['passed'])
