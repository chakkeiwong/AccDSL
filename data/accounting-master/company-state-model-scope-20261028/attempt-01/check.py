"""Finite scope and duplicate-measure discriminators; no population inference."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json, platform, subprocess, sys, time, traceback
import cases
import scope as scoped
from quotient import Refusal,check,digest,key,reuse
from paths import PolicyRefusal,enumerate_paths,supply_policy

H=Path(__file__).resolve().parent;ROOT=cases.ROOT;OUT=H/sys.argv[1]
OUT.mkdir(exist_ok=False);started=time.monotonic();checks=[];models=[];runs=[];controls=[]
def dump(name,x):(OUT/name).write_text(json.dumps(x,indent=2)+chr(10))
def ck(name,a,b):
    checks.append(dict(id=name,actual=a,expected=b,passed=a==b))
    if a!=b:raise AssertionError((name,a,b))
def refuse(name,fn,expected):
    try:fn()
    except (Refusal,PolicyRefusal) as e:
        reason=e.code if isinstance(e,Refusal) else str(e)
        controls.append(dict(id=name,reason=reason));ck(name,reason,expected)
    else:ck(name,'unexpected_acceptance',expected)
def declared(model,represented,excluded=None,unresolved=None):
    return dict(profile='AuthoredFiniteScope/1',model_sha256=digest(model),represented=represented,
                excluded=excluded or [],unresolved_candidates=unresolved or [],
                source_premise='Supplied teaching alternatives, not discovered or verified company contracts')
def run_paths(name,m,p,chooser):
    cert=check(m,p);ck(name+'.certificate',cert['status'],'accepted')
    scenarios=['base']*m['horizon'];policy=supply_policy(m,scenarios,chooser)
    full=enumerate_paths(m,scenarios,policy);reduced=enumerate_paths(reuse(cert,m,p),scenarios,policy)
    ck(name+'.full_exact',full['status'],'exact');ck(name+'.reduced_exact',reduced['status'],'exact')
    ck(name+'.all_paths',full['paths'],reduced['paths'])
    models.append(dict(id=name,model=m,partition=p,certificate=cert))
    runs.append(dict(id=name,policy=policy,original=full,reduced=reduced))
    return cert,policy,full

def main():
    base=cases.mechanisms(['clear']);bpart=cases.identity(base)
    _,bp,bpaths=run_paths('clear_only',base,bpart,cases.choose)
    bs=declared(base,['clear'],['guarantee','private_covenant','withdrawal'])
    original=scoped.evaluate(base,bpart,bp,['base']*3,bs)
    ck('restricted_cash',original['finite_cash_range'],['10','10'])
    ck('restricted_unpaid',original['finite_unpaid_range'],['0','0'])
    expanded=cases.mechanisms(cases.TYPES);epart=cases.identity(expanded)
    cert,ep,epaths=run_paths('expanded',expanded,epart,cases.choose)
    es=declared(expanded,cases.TYPES,['other_contracts_or_behaviors'],['source meaning of an additional guarantee'])
    result=scoped.evaluate(expanded,epart,ep,['base']*3,es)
    runs.append(dict(id='scoped_original',result=original));runs.append(dict(id='scoped_expanded',result=result))
    ck('expanded_cash',result['finite_cash_range'],['0','10'])
    ck('expanded_unpaid',result['finite_unpaid_range'],['0','15'])
    ck('observable_expanded_paths',len(epaths['paths']),3)
    outcomes={h['history'][2]['observation']:h['history'] for h in epaths['paths']}
    expected={'stable':([30,30,30,10],[0,0,-20],0),
              'guarantee_call':([30,30,10,0],[0,-20,-10],10),
              'customer_withdrawal':([30,30,5,0],[0,-25,-5],15)}
    for kind,(cash,flows,unpaid) in expected.items():
        hist=outcomes[kind]
        ck(kind+'.all_cash',[h['current_output']['cash'] for h in hist],cash)
        ck(kind+'.all_flows',[h['output']['cash_flow'] for h in hist[1:]],flows)
        ck(kind+'.unpaid',hist[-1]['output']['unpaid'],unpaid)
        ck(kind+'.cash_conservation',cash[0]+sum(flows),cash[-1])
        ck(kind+'.obligation_conservation',-flows[-1]+unpaid,20)
    support=lambda r:{key(x['history']) for x in r['paths']}
    previous=support(bpaths)
    for types in [cases.TYPES[:2],cases.TYPES[:3],cases.TYPES]:
        m=cases.mechanisms(types);p=cases.identity(m)
        _,policy,paths=run_paths('add.'+types[-1],m,p,cases.choose)
        ck('monotone_support.'+types[-1],previous<=support(paths),True)
        previous=support(paths)
    restrictive=cases.mechanisms(['clear','private_covenant'])
    rp=cases.identity(restrictive);coarse=[{k:k.replace('private_covenant','clear') for k in x} for x in rp]
    rejection=check(restrictive,coarse);models.append(dict(id='illicit_covenant_merge',model=restrictive,partition=coarse,certificate=rejection))
    ck('covenant_merge_rejected',rejection['status'],'rejected')
    ck('covenant_witness',rejection['witness']['component'],'actions')
    run_paths('clear_distribution_allowed',base,bpart,cases.distribute_if_stable)
    refuse('hidden_covenant_blocks_universal_distribution',lambda:supply_policy(restrictive,['base']*3,cases.distribute_if_stable),'action_not_feasible')
    refuse('restricted_result_not_expanded',lambda:scoped.reuse(original,expanded,epart,ep,['base']*3,es),'stale_scope_result')
    refuse('old_scope_not_new_model',lambda:scoped.evaluate(expanded,epart,ep,['base']*3,bs),'scope_model_mismatch')
    changed=deepcopy(es);changed['source_premise']='Different explicit source interpretation'
    refuse('source_scope_change',lambda:scoped.reuse(result,expanded,epart,ep,['base']*3,changed),'stale_scope_result')
    changed=deepcopy(es);changed['unresolved_candidates'].append('unknown private guarantee')
    refuse('unresolved_scope_change',lambda:scoped.reuse(result,expanded,epart,ep,['base']*3,changed),'stale_scope_result')
    ck('unresolved_retained',result['scope']['unresolved_candidates'],es['unresolved_candidates'])
    ck('limitations_not_certified',[result[k] for k in ['source_admission','real_population_complete','mechanism_meanings_verified','probabilities_inferred']],[False]*4)
    ck('relation_has_no_odds',any('probability' in p for p in epaths['paths']),False)
    ck('fresh_scope_reuse',scoped.reuse(result,expanded,epart,ep,['base']*3,es),result)
    for budget in [0,2,5]:
        partial=scoped.evaluate(expanded,epart,ep,['base']*3,es,max_nodes=budget)
        ck('budget'+str(budget)+'.unknown',partial['status'],'unknown')
        ck('budget'+str(budget)+'.frontier',bool(partial['traversal']['unfinished']),True)
        ck('budget'+str(budget)+'.no_extrema',partial['finite_cash_range'],None)
        ck('budget'+str(budget)+'.scope_retained',partial['scope'],es)
        runs.append(dict(id='budget'+str(budget),result=partial))
    compared={}
    for name,kw in [('original',{}),('split_duplicate',dict(duplicate=True)),
                    ('equal_encoding_weights',dict(duplicate=True,equal_weights=True))]:
        m,p=cases.encodings(**kw);_,policy,paths=run_paths(name,m,p,lambda h:'wait')
        law={x['history'][-1]['current_output']['cash']:Q(x['probability']) for x in paths['paths']}
        compared[name]=(law,paths)
        ck(name+'.total_mass',str(sum(law.values())),'1')
    ck('duplicate_preserves_full_observations',compared['original'][1]['paths'],compared['split_duplicate'][1]['paths'])
    for name,mean in [('original','80'),('split_duplicate','80'),('equal_encoding_weights','260/3')]:
        law=compared[name][0];ck(name+'.mean',str(sum(k*v for k,v in law.items())),mean)
    ck('equal_weights_change_law',compared['original'][1]['paths']!=compared['equal_encoding_weights'][1]['paths'],True)
    ck('equal_weights_high_mass',str(compared['equal_encoding_weights'][0][100]),'2/3')
    ck('economic_high_mass',str(compared['original'][0][100]),'1/2')
    changed,p=cases.encodings(duplicate=True,alter=True)
    rejection=check(changed,p);models.append(dict(id='false_economic_alias',model=changed,partition=p,certificate=rejection))
    ck('false_alias_rejected',rejection['status'],'rejected');ck('false_alias_witness',rejection['witness']['component'],'joint_kernel')
    supports=[]
    for duplicate in [False,True]:
        m,p=cases.encodings(duplicate=duplicate,relation=True)
        _,_,paths=run_paths('relation_duplicate'+str(duplicate),m,p,lambda h:'wait');supports.append(paths['paths'])
        ck('relation_no_masses'+str(duplicate),any('probability' in x for x in paths['paths']),False)
    ck('relation_support_preserved',supports[0],supports[1])
    return dict(passed=True,checks=len(checks),models=len(models),path_results=len(runs),refusal_controls=len(controls),original_rows=['SIM-F067','SIM-F008'])

try:
    summary=main();dump('verification.json',summary)
except Exception:
    dump('failure.json',dict(error=traceback.format_exc(),checks_passed=sum(c['passed'] for c in checks)));raise
finally:
    dump('checks.json',checks);dump('models.json',models);dump('paths.json',runs);dump('controls.json',controls)
    for name in ['check.py','cases.py','scope.py']:(OUT/name).write_bytes((H/name).read_bytes())
    sources=[H/n for n in ['check.py','cases.py','scope.py']]+[cases.BASE/n for n in ['fixtures.py','quotient.py','paths.py']]
    dump('source-hashes.json',{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources})
    dump('manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='python3 -B '+str(Path(__file__).relative_to(ROOT))+' '+sys.argv[1],environment=sys.executable,
        python=platform.python_version(),cpu_gpu='CPU only; no GPU framework imported',seeds='N/A deterministic exact enumeration',
        data_version='Explicit teaching models and probability measures, no empirical data',wall_seconds=time.monotonic()-started,
        plan='docs/plans/'+H.name+'.md',result=str(H.relative_to(ROOT)/'result.md'),artifacts=str(OUT.relative_to(ROOT))))
print(json.dumps(summary))
