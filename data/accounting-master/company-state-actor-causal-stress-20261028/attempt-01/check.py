"""Full policy paths and exact causal/joint-law controls for three original rows."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json,platform,subprocess,sys,time,traceback
import information as info
import loan,stress
from quotient import check as certify,reuse,digest
from paths import enumerate_paths,supply_policy,PolicyRefusal

H=Path(__file__).resolve().parent;ROOT=info.ROOT;OUT=H/sys.argv[1]
OUT.mkdir(exist_ok=False);started=time.monotonic();checks=[];runs=[];controls=[]
def dump(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+chr(10))
def ck(name,actual,expected):
    checks.append(dict(id=name,actual=actual,expected=expected,passed=actual==expected))
    if actual!=expected:raise AssertionError((name,actual,expected))
def refused(name,fn,expected):
    try:fn()
    except (ValueError,PolicyRefusal) as e:
        ck(name,str(e),expected);controls.append(dict(id=name,reason=str(e)))
    else:ck(name,'unexpected_acceptance',expected)

def paths(name,built,chooser):
    ck(name+'.construction',built['status'],'constructed')
    m=built['model'];partition=loan.identity(m);cert=certify(m,partition)
    ck(name+'.certificate',cert['status'],'accepted')
    policy=supply_policy(m,['base']*2,chooser)
    full=enumerate_paths(m,['base']*2,policy)
    reduced=enumerate_paths(reuse(cert,m,partition),['base']*2,policy)
    ck(name+'.exact',full['status'],'exact');ck(name+'.reduced_exact',reduced['status'],'exact')
    ck(name+'.full_path_equality',full['paths'],reduced['paths'])
    ck(name+'.no_probabilities',any('probability' in x for x in full['paths']),False)
    runs.append(dict(id=name,built=built,partition=partition,certificate=cert,policy=policy,full=full,reduced=reduced))
    for i,p in enumerate(full['paths']):
        history=p['history'];first=history[0]
        ck(name+f'.{i}.only_permitted_initial_fields',sorted(first),['current_output','observation'])
        ck(name+f'.{i}.message_fields',sorted(first['observation']),['debt','loan_type'])
        cash=[row['current_output']['cash'] for row in history]
        flows=[row['output']['cash_flow'] for row in history[1:]]
        ck(name+f'.{i}.cash_flow_conservation',cash[0]+sum(flows),cash[-1])
        ck(name+f'.{i}.decision_is_nonmonetary',flows[0],0)
        reserve=int(history[1]['action'].replace('reserve',''))
        paid=-flows[-1];last=history[-1]['output']
        ck(name+f'.{i}.reserve_conservation',paid+last['unused_reserve'],reserve)
        ck(name+f'.{i}.coupon_support',paid+last['unpaid'] in [5,7],True)
    return policy,full

def main():
    cutoff='2026-01-02T00:00:00Z'
    manager=loan.build('manager',cutoff);analyst=loan.build('analyst',cutoff)
    mp,mr=paths('private_manager',manager,loan.informed)
    for kind in ['fixed','floating']:
        ck(kind+'.manager_terms',manager['views'][kind]['observation']['loan_type'],kind)
        ck(kind+'.analyst_terms_withheld',analyst['views'][kind]['observation']['loan_type'],None)
        ck(kind+'.same_public_debt',manager['views'][kind]['observation']['debt'],analyst['views'][kind]['observation']['debt'])
    manager_out={p['history'][0]['observation']['loan_type']:[p['history'][1]['action'],p['history'][-1]['current_output']['cash'],p['history'][-1]['output']['unpaid'],p['history'][-1]['output']['unused_reserve']] for p in mr['paths']}
    ck('manager_exact_choices',manager_out,dict(fixed=['reserve5',5,0,0],floating=['reserve7',3,0,0]))
    for reserve in [5,7]:
        policy,result=paths('public_analyst_reserve'+str(reserve),analyst,loan.common(reserve))
        actual=sorted([p['history'][-1]['current_output']['cash'],p['history'][-1]['output']['unpaid'],p['history'][-1]['output']['unused_reserve']] for p in result['paths'])
        expected=[[5,0,0],[5,2,0]] if reserve==5 else [[3,0,0],[5,0,2]]
        ck('analyst_reserve'+str(reserve)+'.full_outcomes',actual,expected)
        ck('analyst_reserve'+str(reserve)+'.one_initial_action',len({p['history'][1]['action'] for p in result['paths']}),1)
    refused('manager_policy_not_public_information',lambda:enumerate_paths(analyst['model'],['base']*2,mp),'missing_observable_history')
    refused('informed_rule_requires_terms',lambda:supply_policy(analyst['model'],['base']*2,loan.informed),'loan_terms_not_observed')
    public=loan.build('analyst','2026-01-03T00:00:00Z')
    ck('publication_without_access',public['views']['fixed']['status'],'not_available')
    accessed=loan.build('analyst','2026-01-03T12:00:00Z');_,ar=paths('analyst_after_access',accessed,loan.informed)
    ck('later_analyst_same_observable_paths',ar['paths'],mr['paths'])
    rows,sources=loan.source('floating')
    baseline=info.view(rows,sources,'manager','loan1',cutoff)
    ck('manager_known',baseline['status'],'known')
    duplicate=info.view(rows+deepcopy(rows),sources,'manager','loan1',cutoff)
    ck('duplicate_assertion_idempotent',duplicate,baseline)
    ck('known_type_no_admission',[baseline['source_admission'],baseline['actual_knowledge_verified']],[False,False])
    ck('fixed_offset_boundary',info.view(rows,sources,'analyst','loan1','2026-01-03T20:00:00+08:00')['status'],'known')
    ck('one_fraction_before_access',info.view(rows,sources,'analyst','loan1','2026-01-03T11:59:59.9999999Z')['status'],'not_available')
    ck('future_authorship_withheld',info.view(rows,sources,'manager','loan1','2025-12-31T00:00:00Z')['status'],'not_available')
    def query(label,records=rows,blobs=sources,actor='manager',wanted='invalid',**kw):
        result=info.view(records,blobs,actor,'loan1',cutoff,**kw)
        ck(label,result['status'],wanted);controls.append(dict(id=label,records=records,sources=blobs,result=result))
        if wanted not in ['known','not_available']:ck(label+'.no_policy_message',result['observation'],None)
    bad=deepcopy(sources);bad[next(iter(bad))]+=' changed';query('source_bytes_changed',blobs=bad)
    query('source_missing',blobs={})
    bad=deepcopy(rows);bad[0]['loan_id']='other_loan';query('wrong_loan',records=bad)
    bad=deepcopy(rows);bad[0]['loan_type']='swap';query('unsupported_loan_meaning',records=bad)
    bad=deepcopy(rows);bad[0]['loan_type']=None;query('unknown_terms',records=bad,wanted='unresolved')
    bad=deepcopy(rows);bad[0]['access']['manager']['at']=None;query('unknown_access',records=bad,wanted='unresolved')
    query('unrepresented_actor',actor='outsider',wanted='unresolved')
    bad=deepcopy(rows);bad[0]['access']['manager']['route']='audit_world';query('unsupported_access_route',records=bad)
    bad=deepcopy(rows);bad[0]['access']['manager']['at']='2025-12-31T00:00:00Z';query('access_before_source',records=bad)
    bad=deepcopy(rows);bad[0]['access']['analyst']['at']='2026-01-02T00:00:00Z';query('public_access_before_publication',records=bad,actor='analyst')
    bad=deepcopy(rows);bad[0]['effective']='2026-01-04T00:00:00Z';query('future_effective_withheld',records=bad,wanted='not_available')
    bad=deepcopy(rows);bad[0]['published']=None;query('private_without_publication',records=bad,wanted='known')
    query('public_unknown_publication',records=bad,actor='analyst',wanted='unresolved')
    bad=deepcopy(rows);bad[0]['authored']=None;query('unknown_authorship',records=bad,wanted='unresolved')
    bad=deepcopy(rows);bad[0]['access']['manager']['at']='2026-01-01T00:00:00-00:00';query('unknown_offset',records=bad)
    query('budget_preserves_unknown',wanted='unresolved_budget',max_records=0)
    fixed,fs=loan.source('fixed');query('conflicting_known_terms',records=rows+fixed,blobs={**sources,**fs},wanted='conflict')
    collision=deepcopy(rows);collision[0]['loan_type']='fixed';query('identity_collision',records=rows+collision)
    # F017: same observed law, different interventional law.
    laws={}
    for mechanism in ['confounded_demand','rate_driven_demand']:
        natural=stress.structural(mechanism);laws[mechanism]=stress.law(natural)
        conditional=stress.condition(natural,2);intervened=stress.structural(mechanism,2)
        ck(mechanism+'.natural_mass',str(sum(Q(r['mass']) for r in natural)),'1')
        ck(mechanism+'.conditional_cash',str(stress.mean(conditional['rows'])),'40')
        ck(mechanism+'.do_mass',str(sum(Q(r['mass']) for r in intervened)),'1')
        ck(mechanism+'.do_cash',str(stress.mean(intervened)),'60' if mechanism=='confounded_demand' else '40')
        ck(mechanism+'.condition_U',[r['u'] for r in conditional['rows']],[1])
        ck(mechanism+'.intervention_preserves_U',[r['u'] for r in intervened],[0,1])
        for row in natural+intervened:ck(mechanism+'.cash_identity.'+str(row),row['cash'],row['demand']-10*row['rate'])
        ck(mechanism+'.zero_condition',stress.condition(natural,3)['status'],'unresolved_zero_condition')
        runs.append(dict(id=mechanism,natural=natural,conditional=conditional,intervened=intervened))
    ck('same_observed_law',laws['confounded_demand'],laws['rate_driven_demand'])
    imposed=[dict(u=u,rate=2,demand=100-40*u,cash=80-40*u,mass='1/2') for u in [0,1]]
    ck('explicit_stress_same_numbers',stress.law(imposed),stress.law(stress.structural('confounded_demand',2)))
    refused('unreviewed_structural_model',lambda:stress.structural('unknown',2),'model_required')
    refused('boolean_intervention',lambda:stress.structural('confounded_demand',True),'supported_intervention')
    # F020: support and measure remain paired, rather than independently recombined.
    scenarios=[dict(id='base',fx='1',demand='100'),dict(id='stress',fx='2',demand='40')]
    joint=stress.joint(scenarios);ck('joint_cash_bounds',joint['cash_bounds'],['30','50'])
    ck('unweighted_no_mean',joint['mean'],None);ck('unweighted_no_probability',joint['negative_cash_probability'],None)
    weights=dict(base='1/2',stress='1/2');weighted=stress.joint(scenarios,weights)
    ck('joint_supplied_mean',weighted['mean'],'40');ck('joint_negative_cash_probability',weighted['negative_cash_probability'],'0')
    rectangle=[dict(id='pair'+str(i),fx=fx,demand=demand) for i,(fx,demand) in enumerate([(a,b) for a in ['1','2'] for b in ['100','40']])]
    wrong=stress.joint(rectangle,{r['id']:'1/4' for r in rectangle})
    ck('rectangular_cash_bounds',wrong['cash_bounds'],['-10','150']);ck('rectangular_mean',wrong['mean'],'55')
    ck('rectangular_negative_cash_probability',wrong['negative_cash_probability'],'1/4')
    for fx,demand,wanted in [('1','100','supported'),('2','40','supported'),('1','40','outside_declared_joint_support'),('2','100','outside_declared_joint_support')]:
        ck('joint_support.'+fx+'.'+demand,stress.supported(scenarios,fx,demand)['status'],wanted)
    ck('unknown_dependence_query',stress.supported(scenarios,None,'40')['status'],'unresolved')
    unknown=deepcopy(scenarios);unknown[1]['demand']=None;ck('unknown_demand_retained',stress.joint(unknown)['status'],'unresolved')
    ck('incomplete_weights_refused',stress.joint(scenarios,dict(base='1'))['status'],'invalid')
    ck('unscaled_weights_refused',stress.joint(scenarios,dict(base='1',stress='1'))['status'],'invalid')
    ck('no_mechanism_admission',[joint['source_admission'],joint['joint_dependence_verified']],[False,False])
    runs.append(dict(id='joint_stress',joint=joint,weighted=weighted,rectangular=wrong))
    return dict(passed=True,checks=len(checks),saved_results=len(runs),refusal_controls=len(controls),original_rows=['SIM-F013','SIM-F017','SIM-F020'])

def wire(value):
    if isinstance(value,dict):return {str(k):wire(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [wire(v) for v in value]
    if isinstance(value,Q):return str(value)
    return value

try:
    summary=main();dump('verification.json',summary)
except Exception:
    dump('failure.json',dict(error=traceback.format_exc(),checks_passed=sum(c['passed'] for c in checks)));raise
finally:
    dump('checks.json',wire(checks));dump('results.json',runs);dump('controls.json',controls)
    for name in ['check.py','information.py','loan.py','stress.py']:(OUT/name).write_bytes((H/name).read_bytes())
    sources={Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and str(ROOT) in str(m.__file__) and str(m.__file__).endswith('.py')}
    sources.add(Path(__file__).resolve())
    dump('source-hashes.json',{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)})
    dump('manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='python3 -B '+str(Path(__file__).relative_to(ROOT))+' '+sys.argv[1],environment=sys.executable,python=platform.python_version(),cpu_gpu='CPU only; no GPU framework imported',seeds='N/A deterministic',data_version='Explicit authored loan assertions, times and causal/joint laws; no empirical data',wall_seconds=time.monotonic()-started,plan='docs/plans/'+H.name+'.md',result=str(H.relative_to(ROOT)/'result.md'),artifacts=str(OUT.relative_to(ROOT))))
print(json.dumps(summary))
