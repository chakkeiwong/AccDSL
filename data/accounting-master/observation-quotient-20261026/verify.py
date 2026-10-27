"""Finite deterministic conformance, with an independently coded path oracle."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import itertools
import json
import os
import subprocess
import sys
import time

import fixtures as f
from paths import PolicyRefusal, enumerate_paths, supply_policy
from quotient import Refusal, check, digest, key, reuse, validate

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
START=time.monotonic()
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(name,v): (HERE/name).write_text(json.dumps(v,indent=2)+'\n')

protected=[
 'docs/design/proposal/manuscript-adopted-profiles-20261026/simulation/08-compression.tex',
 'docs/design/proposal/manuscript-adopted-profiles-20261026/accounting-product-proposal.pdf',
 'data/accounting-master/uncertainty-representation-20261026/result.md',
 'data/accounting-master/adopted-profile-effects-20261026/checks.json']
lock=HERE/'source-lock.json'
if not lock.exists(): dump(lock.name,{p:sha(ROOT/p) for p in protected})
locked=json.loads(lock.read_text())
for p,h in locked.items(): assert sha(ROOT/p)==h,p
records=[]; controls=[]; comparisons=[]; assertions=[]
def ensure(ok,label):
    assertions.append({'check':label,'passed':bool(ok)})
    assert ok,label

def accepted(label,m,p,chooser,scenarios=None):
    sc=scenarios or ['base']*m['horizon']
    cert=check(m,p)
    ensure(cert['status']=='accepted',label+':condition')
    q=reuse(cert,m,p)
    qpart=[{s['id']:s['id'] for s in d['states']} for d in q['dates']]
    validate(q,qpart)
    policy=supply_policy(m,sc,chooser)
    original=enumerate_paths(m,sc,policy)
    compressed=enumerate_paths(q,sc,policy)
    ensure(original['status']==compressed['status']=='exact',label+':complete_enumeration')
    ensure(key(original['paths'])==key(compressed['paths']),label+':full_path_equality')
    if m['mode']=='probability':
        ensure(sum(Fraction(x['probability']) for x in original['paths'])==1,label+':total_path_mass')
    records.append({'case':label,'model':m,'partition':p,'certificate':cert})
    comparisons.append({'case':label,'scenarios':sc,'policy':policy,'original':original,'compressed':compressed})
    return cert,original

def rejected(label,m,p,component):
    result=check(m,p)
    ensure(result['status']=='rejected',label+':rejected')
    ensure(result['witness']['component']==component,label+':specific_witness')
    records.append({'case':label,'model':m,'partition':p,'certificate':result})
    return result

def refuses(label,fn,expected,exception=Refusal):
    try: fn()
    except exception as e:
        actual=e.code if isinstance(e,Refusal) else str(e)
        ensure(actual==expected,label+':exact_refusal')
        controls.append({'case':label,'status':'refused','reason':actual})
    else: raise AssertionError('control_accepted:'+label)

m,p=f.signals()
before=key(m)
detached=check(m,p)
detached['quotient']['dates'][0]['states'][0]['current']['cash']=999
ensure(key(m)==before,'quotient_does_not_alias_input_state')
cert,paths=accepted('duplicate_state_signal_policy',m,p,f.choose_signal)
law=defaultdict(Fraction)
for path in paths['paths']:
    h=path['history']; law[(h[1]['observation'],h[2]['output']['cash_flow'])]+=Fraction(path['probability'])
ensure(dict(law)=={('green',2):Fraction(9,20),('green',-4):Fraction(1,20),('red',0):Fraction(1,2)},'hand_signal_law')
for green,red in itertools.product(('lend','wait'),repeat=2):
    accepted('policy_'+green+'_'+red,m,p,lambda h,g=green,r=red:'observe' if len(h)==1 else (g if h[-1]['observation']=='green' else r))
dm,dp=f.duplicate_successors()
accepted('duplicate_successor_mass_summing',dm,dp,f.choose_signal)
weighted_initial=deepcopy(m)
weighted_initial['initial']=[{'state':'x','observation':'private_x','probability':'1/3'}, {'state':'y','observation':'private_y','probability':'2/3'}]
accepted('joint_initial_information',weighted_initial,p,f.choose_signal)
initial_decision=f.model('probability',[
 {'states':[f.state('x',['lend','wait'],10),f.state('y',['lend','wait'],10)],'transitions':[]},
 {'states':[f.state('paid',[],12),f.state('kept',[],10)],'transitions':[]}],
 [{'state':'x','observation':'green','probability':'1/3'}, {'state':'y','observation':'red','probability':'2/3'}])
for x in ('x','y'):
    initial_decision['dates'][0]['transitions'].extend([
        f.transition(x,'lend',[f.out('paid','settled',2,1)]),
        f.transition(x,'wait',[f.out('kept','settled',0,1)])])
_,initpaths=accepted('first_action_uses_initial_observation',initial_decision,
 [{'x':'merged','y':'merged'},{'paid':'paid','kept':'kept'}],
 lambda h:'lend' if h[0]['observation']=='green' else 'wait')
ensure({(x['history'][0]['observation'],x['history'][1]['action'],x['probability']) for x in initpaths['paths']}==
       {('green','lend','1/3'),('red','wait','2/3')},'initial_observation_action_mass')

relation=deepcopy(dm);relation['mode']='relation'
for i in relation['initial']: del i['probability']
for d in relation['dates']:
    for tr in d['transitions']:
        for o in tr['outcomes']: del o['probability']
accepted('unweighted_duplicate_successors',relation,dp,f.choose_signal)

pm,pfine,pcoarse=f.persistent_type()
pcert,ppaths=accepted('persistent_type_retained',pm,pfine,lambda h:'pay')
actual={tuple(step['output']['cash_flow'] for step in x['history'][1:]) for x in ppaths['paths']}
ensure(actual=={(-5,-5),(-7,-7)},'persistent_type_exact_two_paths')
naive=set(itertools.product((-5,-7),repeat=2))
ensure(naive-actual=={(-5,-7),(-7,-5)},'marginal_recombination_adds_impossible_paths')
dump('persistent-counterexample.json',{'actual_paths':sorted(actual),'naive_marginal_product':sorted(naive),'spurious_paths':sorted(naive-actual),'probabilities':'not supplied; none inferred'})
hidden=deepcopy(pm)
hidden['requested_outputs']['current']=[]
for d in hidden['dates']:
    for st in d['states']: st['current']={}
rejected('persistent_type_merge',hidden,pcoarse,'joint_kernel')

bad_signal,bsp=f.signals(Fraction(9,10),Fraction(1,2))
rejected('different_signal_quality',bad_signal,bsp,'joint_kernel')
anti,ap=f.signals(Fraction(9,10),Fraction(1,10))
rejected('same_marginals_different_state_signal_dependence',anti,ap,'joint_kernel')
def marginal(outs,field):
    values=defaultdict(Fraction)
    for o in outs: values[key(o[field])]+=Fraction(o['probability'])
    return dict(values)
for field in ('next','observation','output'):
    ensure(marginal(anti['dates'][0]['transitions'][0]['outcomes'],field)==marginal(anti['dates'][0]['transitions'][1]['outcomes'],field),'anti_equal_marginal_'+field)
joint,jp=f.joint_only()
rejected('same_marginals_different_observation_output_dependence',joint,jp,'joint_kernel')
for field in ('next','observation','output'):
    ensure(marginal(joint['dates'][0]['transitions'][0]['outcomes'],field)==marginal(joint['dates'][0]['transitions'][1]['outcomes'],field),'joint_equal_marginal_'+field)

# Compare deliberately wrong representative merges against the full path oracle.
# These copies are evidence of failure, never admitted quotient outputs.
negative_paths=[]
for label,original,chooser in [('state_signal',anti,f.choose_signal),('observation_output',joint,lambda h:'pay')]:
    collapsed=deepcopy(original)
    collapsed['dates'][0]['states']=[deepcopy(original['dates'][0]['states'][0])]
    collapsed['dates'][0]['states'][0]['id']='merged'
    collapsed['dates'][0]['transitions']=[deepcopy(original['dates'][0]['transitions'][0])]
    collapsed['dates'][0]['transitions'][0]['state']='merged'
    collapsed['initial']=[{'state':'merged','observation':'start','probability':'1'}]
    sc=['base']*original['horizon']
    policy=supply_policy(original,sc,chooser)
    full=enumerate_paths(original,sc,policy)
    wrong=enumerate_paths(collapsed,sc,policy)
    ensure(key(full['paths'])!=key(wrong['paths']),'false_merge_changes_full_path:'+label)
    negative_paths.append({'case':label,'original_model':original,'inadmissible_representative_model':collapsed,'policy':policy,'scenarios':sc,'original_paths':full,'wrong_merge_paths':wrong})
dump('negative-path-comparisons.json',negative_paths)

different=deepcopy(m);different['dates'][0]['states'][1]['current']['cash']=11
rejected('different_current_output',different,p,'current')
different=deepcopy(m);different['dates'][0]['states'][1]['actions'].append('wait')
different['dates'][0]['transitions'].append(f.transition('y','wait',[f.out('good','green',0,1)]))
rejected('different_permitted_actions',different,p,'actions')

multiscenario=deepcopy(m);multiscenario['scenarios'].append('stress')
for d in multiscenario['dates']:
    for tr in list(d['transitions']):
        copy=deepcopy(tr);copy['scenario']='stress';d['transitions'].append(copy)
accepted('every_supplied_scenario',multiscenario,p,f.choose_signal,['stress','base'])
bad=deepcopy(multiscenario)
next(tr for tr in bad['dates'][0]['transitions'] if tr['state']=='y' and tr['scenario']=='stress')['outcomes'][0]['observation']='changed'
rejected('scenario_specific_mismatch',bad,p,'joint_kernel')

# Terminal-only models check the base case and joint initial pushforward.
terminal=f.model('probability',[{'states':[f.state('a',[],1),f.state('b',[],1)],'transitions':[]}],
                 [{'state':'a','observation':'seen','probability':'1/4'},{'state':'b','observation':'seen','probability':'3/4'}])
accepted('zero_horizon',terminal,[{'a':'same','b':'same'}],lambda h:'unused')

# Rejection is sufficient-condition failure, not a necessity theorem. Unreachable
# states still belong to declared scope, so a bad unused merge must be rejected.
unreachable=deepcopy(bad_signal)
unreachable['initial']=[{'state':'x','observation':'start','probability':'1'}]
rejected('unreachable_state_still_checked',unreachable,p,'joint_kernel')

bad=deepcopy(m);bad['dates'][0]['transitions'][0]['outcomes'][0]['probability']='0'
refuses('zero_mass',lambda:check(bad,p),'nonpositive_mass')
bad=deepcopy(m);bad['dates'][0]['transitions'][0]['outcomes'][0]['probability']='0.45'
refuses('decimal_mass',lambda:check(bad,p),'invalid_mass')
bad=deepcopy(m);bad['dates'][0]['transitions'][0]['outcomes'][0]['probability']='1/3'
refuses('kernel_mass_not_one',lambda:check(bad,p),'kernel_mass')
bad=deepcopy(m);bad['initial'][0]['probability']='1/2'
refuses('initial_mass_not_one',lambda:check(bad,p),'initial_mass')
bad=deepcopy(m);bad['dates'][0]['transitions'].pop()
refuses('missing_kernel',lambda:check(bad,p),'missing_kernel')
bad=deepcopy(m);bad['dates'][0]['transitions'][0]['outcomes'][0]['next']='unknown'
refuses('unknown_successor',lambda:check(bad,p),'successor_coverage')
bad=deepcopy(m);bad['dates'][0]['states'][0]['current']['cash']=10.0
refuses('float_output',lambda:check(bad,p),'non_exact_json')
bad=deepcopy(m);bad['information']['private_state']=True
refuses('private_state_information',lambda:check(bad,p),'unsupported_information')
bad=deepcopy(m);bad['dates'][0]['transitions'][0]['outcomes'].append(deepcopy(bad['dates'][0]['transitions'][0]['outcomes'][0]))
refuses('duplicate_outcome',lambda:check(bad,p),'duplicate_outcome')
bad=deepcopy(m);bad['initial'].append(deepcopy(bad['initial'][0]))
refuses('duplicate_initial',lambda:check(bad,p),'duplicate_initial')
bad=deepcopy(m);bad['dates'][0]['transitions'].append(deepcopy(bad['dates'][0]['transitions'][0]))
refuses('duplicate_kernel',lambda:check(bad,p),'transition_coverage')
bad=deepcopy(m);bad['dates'][0]['states'][0]['current']['extra']=0
refuses('undeclared_current_output',lambda:check(bad,p),'current_output_interface')
bad=deepcopy(m);bad['dates'][0]['transitions'][0]['outcomes'][0]['output']['extra']=0
refuses('undeclared_step_output',lambda:check(bad,p),'step_output_interface')
bad=deepcopy(m);bad['dates'][-1]['states'][0]['actions']=['wait']
refuses('terminal_action',lambda:check(bad,p),'terminal_action')
bad=deepcopy(m);bad['horizon']=True
refuses('boolean_horizon',lambda:check(bad,p),'invalid_horizon')
bp=deepcopy(p);del bp[0]['x']
refuses('partition_missing_state',lambda:check(m,bp),'partition_coverage')
bad=deepcopy(relation);bad['initial'][0]['probability']='1/2'
refuses('probability_in_unweighted_initial',lambda:check(bad,dp),'initial_fields')
bad=deepcopy(relation);bad['dates'][0]['transitions'][0]['outcomes'][0]['probability']='1/2'
refuses('probability_in_unweighted_outcome',lambda:check(bad,dp),'outcome_fields')
bad=deepcopy(m);del bad['initial'][0]['probability']
refuses('missing_probability',lambda:check(bad,p),'initial_fields')

policy=supply_policy(m,['base','base'],f.choose_signal)
badpolicy=deepcopy(policy);badpolicy['actions'].pop(next(iter(badpolicy['actions'])))
refuses('missing_policy_history',lambda:enumerate_paths(m,['base','base'],badpolicy),'missing_observable_history',PolicyRefusal)
badpolicy=deepcopy(policy);badpolicy['actions'][next(iter(badpolicy['actions']))]='unavailable'
refuses('invalid_policy_action',lambda:enumerate_paths(m,['base','base'],badpolicy),'action_not_feasible',PolicyRefusal)
badpolicy={'schema':'HiddenStatePolicy/1','actions':{'x':'observe'}}
refuses('hidden_state_policy_interface',lambda:enumerate_paths(m,['base','base'],badpolicy),'policy_interface',PolicyRefusal)
refuses('undeclared_scenario',lambda:enumerate_paths(m,['unknown','base'],policy),'scenario_scope',PolicyRefusal)

for budget in (0,1,cert['checked']-1):
    limited=check(m,p,budget)
    ensure(limited['status']=='unknown' and 'quotient' not in limited,'budget_unknown_'+str(budget))
    ensure(limited['checked']+len(limited['frontier'])==cert['checked'],'full_frontier_'+str(budget))
    controls.append({'case':'comparison_budget_'+str(budget),'result':limited})
ensure(check(m,p,cert['checked'])==cert,'exact_budget_completes')
limitedpaths=enumerate_paths(m,['base','base'],policy,1)
ensure(limitedpaths['status']=='unknown' and bool(limitedpaths['unfinished']),'path_budget_unknown')
controls.append({'case':'path_budget','result':limitedpaths})
bad=deepcopy(m);bad['dates'][0]['transitions'].pop()
refuses('zero_budget_does_not_hide_invalid_model',lambda:check(bad,p,0),'missing_kernel')

refuses('changed_model_binding',lambda:reuse(cert,bad_signal,p),'stale_binding')
changedp=deepcopy(p);changedp[0]['y']='other'
refuses('changed_partition_binding',lambda:reuse(cert,m,changedp),'stale_binding')
changed=deepcopy(m);changed['requested_outputs']['current']=['balance']
for d in changed['dates']:
    for st in d['states']:st['current']={'balance':st['current']['cash']}
refuses('changed_requested_output_binding',lambda:reuse(cert,changed,p),'stale_binding')
refuses('changed_horizon_binding',lambda:reuse(cert,terminal,[{'a':'same','b':'same'}]),'stale_binding')
tampered=deepcopy(cert);tampered['quotient']['dates'][0]['states'][0]['current']['cash']=999
refuses('changed_quotient_certificate',lambda:reuse(tampered,m,p),'certificate_mismatch')
tampered=deepcopy(cert);tampered['bindings']['information']='0'*64
refuses('changed_information_binding',lambda:reuse(tampered,m,p),'stale_binding')
refuses('unknown_is_not_certificate',lambda:reuse(check(m,p,0),m,p),'not_accepted_certificate')
reordered=deepcopy(m)
reordered['dates'][0]['states'].reverse()
ensure(check(reordered,p)['status']=='accepted','reordered_model_still_valid')
refuses('reordered_bytes_require_recheck',lambda:reuse(cert,reordered,p),'stale_binding')
bad=deepcopy(m);bad['dates'][0]['transitions'][0]['outcomes'][0]['probability']='1/0'
refuses('zero_denominator',lambda:check(bad,p),'invalid_mass')
refuses('negative_budget',lambda:check(m,p,-1),'invalid_budget')

# Persist complete inputs and independently read them back for recomputation.
dump('cases.json',records);dump('path-comparisons.json',comparisons);dump('controls.json',controls)
for record in json.loads((HERE/'cases.json').read_text()):
    ensure(check(record['model'],record['partition'])==record['certificate'],'saved_case:'+record['case'])
lookup={r['case']:r for r in records}
for comparison in json.loads((HERE/'path-comparisons.json').read_text()):
    r=lookup[comparison['case']]
    ensure(enumerate_paths(r['model'],comparison['scenarios'],comparison['policy'])==comparison['original'],'saved_original:'+r['case'])
    ensure(enumerate_paths(r['certificate']['quotient'],comparison['scenarios'],comparison['policy'])==comparison['compressed'],'saved_quotient:'+r['case'])
for path,h in locked.items():ensure(sha(ROOT/path)==h,'protected:'+path)
dump('check-detail.json',assertions)
summary={'passed':True,'accepted_cases':sum(r['certificate']['status']=='accepted' for r in records),
         'rejected_cases':sum(r['certificate']['status']=='rejected' for r in records),
         'complete_path_comparisons':len(comparisons),'negative_path_comparisons':len(negative_paths),'boundary_controls':len(controls),'checks':len(assertions),
         'protected_files':len(locked),'source_admission':False,'accounting_admission':False,
         'production_ready':False,'forecast_evidence':False}
dump('checks.json',summary)
git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
dump('run-manifest.json',{'git_commit':git.stdout.strip() if git.returncode==0 else 'unavailable; no repository initialized',
 'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/observation-quotient-20261026/verify.py',
 'environment':sys.version,'cpu_gpu':'CPU scalar exact arithmetic; GPU intentionally hidden','cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),
 'random_seeds':'N/A deterministic rational laws/relations, no sampling', 'wall_seconds':time.monotonic()-START,
 'data_version':digest(records),'source_hashes':locked,
 'implementation_hashes':{n:sha(HERE/n) for n in ['quotient.py','paths.py','fixtures.py','verify.py','design.md']},
 'plan_file':'docs/plans/accounting-observation-quotient-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),
 'artifact_paths':['cases.json','path-comparisons.json','controls.json','persistent-counterexample.json','checks.json','check-detail.json'],
 'timestamp_utc':datetime.now(timezone.utc).isoformat()})
print(json.dumps(summary))
