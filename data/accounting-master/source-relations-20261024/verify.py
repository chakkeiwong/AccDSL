"""Preserved-ledger, arithmetic, interval and adversarial relation checks."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from itertools import product
from hashlib import sha256
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
from relations import (HERE,ROOT,STATE,LEDGERS,OPS,COMPOSED,state,canonical,digest,
    fixture,evaluate,verify_result,interval_sum,displayed_residual,schema,sha)
PLAN='docs/plans/accounting-source-relations-20261024.md'
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def add_rounding(body):
    s=body['state_request'];s['assumptions']=[{'id':'q1','rule':'nearest_ties_away_from_zero','quantum':'1/1',
        'provenance':'Diagnostic only; no retained source admission.','disposition':'proposed_not_admitted'}]
    for b in s['bindings']:b['interpretation']={'mode':'assumed_rounding','assumption_id':'q1'}
    return fixture(s)

def add_identities(body):
    out=deepcopy(body)
    for i,r in enumerate(out['relations']):r['measurement_identity']={'id':'identity-'+str(i),
        'provenance':'Diagnostic proposed same-measurement identity, not inferred from displayed residual.',
        'disposition':'proposed_not_admitted'}
    return out

def conformance():
    checks=[]
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    def reject(name,fn):
        try:fn()
        except Exception:check(name,True)
        else:check(name,False)
    locks={};m=json.loads((STATE/'manifest.json').read_text())
    for group in ['inputs','implementation','outputs']:locks.update(m[group])
    for p in [STATE/'manifest.json',ROOT/PLAN,
        ROOT/'data/accounting-master/company-source-integration-20261024/run-manifest.json',
        ROOT/'docs/design/proposal/manuscript-company-source-20261024/accounting-product-proposal.pdf']:
        locks[str(p.relative_to(ROOT))]=sha(p)
    for name,h in locks.items():check('source_hash:'+name,sha(ROOT/name)==h)
    b=fixture();r=evaluate(b);rounded=add_rounding(deepcopy(b));cr=evaluate(rounded)
    hypotheses=add_identities(rounded);hr=evaluate(hypotheses)
    outputs={'display_only':r,'rounding_only':cr,'rounding_and_identities':hr}
    requests={'display_only':b,'rounding_only':rounded,'rounding_and_identities':hypotheses}
    check('selected_18',len(r['relations'])==18)
    check('all_143_accounted',len(r['ledger_dispositions'])==143)
    check('deferred_125',sum(x['status']=='deferred' for x in r['ledger_dispositions'])==125)
    for group,path in LEDGERS.items():
        original=json.loads(path.read_text());check('whole_ledger:'+group,r['preserved_ledgers'][group]==original)
        entries=[x for x in r['ledger_dispositions'] if x['id'].startswith(group+'.')]
        check('original_order:'+group,[x['source_record'] for x in entries]==original['relations'])
        for i,(source,entry) in enumerate(zip(original['relations'],entries)):
            check('entry_identity:'+group+':'+str(i),entry['source_pointer']=='/relations/'+str(i) and entry['source_record']==source)
            check('entry_has_disposition:'+group+':'+str(i),entry['status']=='bound_displayed_relation' or bool(entry['reason'] and entry['next']))
        readings=json.loads((ROOT/state.prior.load_packet()['source_inputs'][group+'-readings']).read_text())['rows']
        by_id={x['id']:x for x in readings}
        for source in original['relations']:
            hit=next((x for x in r['relations'] if x['id']==group+'.'+source['id']),None)
            if hit is None:continue
            expected=sum(Q(t['coefficient'])*Q(by_id[t['row']]['value']) for t in source['terms'])-Q(by_id[source['target']]['value'])
            check('independent_residual:'+group+':'+source['id'],Q(hit['displayed']['residual'])==expected==0)
            check('retained_residual_comparison:'+group+':'+source['id'],expected==Q(source['residual']))
    check('default_no_identity',all(x['identity_status']=='not_asserted' for x in r['relations']))
    check('default_no_interval',all(x['conditional_residual']['status']=='unresolved' for x in r['relations']))
    check('rounding_still_no_identity',all(x['identity_status']=='not_asserted' for x in cr['relations']))
    check('optional_local_compatibility',all(x['identity_status']=='locally_compatible_only' for x in hr['relations']))
    no_rounding=add_identities(b);nr=evaluate(no_rounding)
    check('identity_without_intervals_unresolved',all(x['identity_status']=='unresolved' for x in nr['relations']))
    for key,out in outputs.items():
        check('no_joint_claim:'+key,out['joint_feasibility']=='uncomputed' and out['actual_history']=='unknown')
        check('no_execution:'+key,out['executable_opening'] is None and not out['executed'])
        check('dependencies_retained:'+key,out['dependencies']==state.evaluate(requests[key]['state_request'])['dependencies'])
    current=next(x for x in hr['relations'] if x['id']=='annual.balance:current_assets')
    check('seven_term_residual_interval',current['conditional_residual']['interval']=={'lower':'-7/2','upper':'7/2','lower_inclusive':False,'upper_inclusive':False})
    # Independent vertex enumeration checks affine interval extrema for closed boxes.
    refs={k:{'digest':k} for k in ['x','y']}
    intervals={'x':{'lower':'-2/1','upper':'3/1','lower_inclusive':True,'upper_inclusive':True},
        'y':{'lower':'1/1','upper':'4/1','lower_inclusive':True,'upper_inclusive':True}}
    for a,beta in product([-2,-1,0,1,2],repeat=2):
        terms=[{'coefficient':str(a)+'/1','observation_ref':refs['x']},{'coefficient':str(beta)+'/1','observation_ref':refs['y']}]
        out=interval_sum(terms,intervals)['interval'];vertices=[a*x+beta*y for x,y in product([-2,3],[1,4])]
        check('closed_vertex_extrema:'+str((a,beta)),Q(out['lower'])==min(vertices) and Q(out['upper'])==max(vertices) and out['lower_inclusive'] and out['upper_inclusive'])
    cancellation=[{'coefficient':'1/1','observation_ref':refs['x']},{'coefficient':'-1/1','observation_ref':refs['x']}]
    check('same_variable_cancels',interval_sum(cancellation,{})['interval']=={'lower':'0/1','upper':'0/1','lower_inclusive':True,'upper_inclusive':True})
    value=displayed_residual([{'coefficient':'1/1','observation_ref':refs['x']}],{'x':{'tag':'reported_dash','literal':'—'}})
    check('dash_stays_unresolved',value=={'status':'unresolved','missing':['x']})
    # Open endpoints and negative coefficients must change containment correctly.
    for lower,upper,li,ui,contains in [('0/1','1/1',False,True,False),('0/1','1/1',True,False,True),('-1/1','0/1',True,False,False),('-1/1','0/1',False,True,True)]:
        out=interval_sum([{'coefficient':'-1/1','observation_ref':refs['x']}],{'x':dict(lower=lower,upper=upper,lower_inclusive=li,upper_inclusive=ui)})
        check('signed_open_zero:'+str((lower,li,ui)),out['zero_contained']==contains)
    reject('invalid_empty_interval',lambda:interval_sum([{'coefficient':'1/1','observation_ref':refs['x']}],{'x':{'lower':'1/1','upper':'1/1','lower_inclusive':False,'upper_inclusive':True}}))
    # Both local equalities x=0 and x=1 meet x in [0,1]; they cannot hold jointly.
    local=[]
    for const in [0,1]:
        terms=[{'coefficient':'1/1','observation_ref':refs['x']},{'coefficient':'-1/1','observation_ref':refs['y']}]
        boxes={'x':{'lower':'0/1','upper':'1/1','lower_inclusive':True,'upper_inclusive':True},'y':{'lower':str(const)+'/1','upper':str(const)+'/1','lower_inclusive':True,'upper_inclusive':True}}
        local.append(interval_sum(terms,boxes)['zero_contained'])
    check('local_not_joint_counterexample',all(local) and {Q(0)}.isdisjoint({Q(1)}))
    for view,count in [('annual',9),('interim',9),('combined',18)]:
        q=fixture(state.fixture(view=view));out=evaluate(q);check('view_selection:'+view,len(out['relations'])==count)
    for label,mutate in [
        ('coefficient',lambda q:q['relations'][0]['terms'][0].update(coefficient='2/1')),
        ('extra_alias',lambda q:q['relations'][0]['terms'].append(deepcopy(q['relations'][0]['terms'][0]))),
        ('drop_relation',lambda q:q['relations'].pop()),
        ('drop_ledger',lambda q:q['ledgers'].pop()),
        ('ledger_hash',lambda q:q['ledgers'][0].update(sha256='0'*64)),
        ('target_substitution',lambda q:q['relations'][0].update(target_ref=q['relations'][1]['target_ref'])),
        ('cross_source_target',lambda q:q['relations'][0].update(target_ref=q['relations'][9]['target_ref'])),
        ('source_pointer',lambda q:q['relations'][0].update(source_pointer='/relations/0')),
        ('context_change',lambda q:q['state_request']['bindings'][0]['context'].update(perimeter='Legal Apple')),
        ('false_state_hash',lambda q:q.update(state_result_sha256='0'*64))]:
        bad=deepcopy(b);mutate(bad);reject('reject:'+label,lambda:evaluate(bad))
    bad=deepcopy(hypotheses);bad['relations'][0]['measurement_identity']['disposition']='accepted';reject('promoted_identity',lambda:evaluate(bad))
    for label,mutate in [
        ('false_zero',lambda x:x['relations'][0]['displayed'].update(residual='1/1')),
        ('dropped_ledger_row',lambda x:x['ledger_dispositions'].pop()),
        ('lost_original',lambda x:x['preserved_ledgers']['annual']['relations'].pop()),
        ('claimed_joint',lambda x:x.update(joint_feasibility='feasible')),
        ('invented_opening',lambda x:x.update(executable_opening={'cash':29943})),
        ('identity_promotion',lambda x:x['relations'][0].update(identity_status='proved'))]:
        bad=deepcopy(r);mutate(bad);check('forged_result:'+label,not verify_result(requests['display_only'],bad))
    check('honest_result',verify_result(requests['display_only'],r))
    return {'passed':all(c['passed'] for c in checks),'checks':checks},requests,outputs,locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'already recorded'
    start=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in m[group].items():assert sha(ROOT/name)==h,name
    checks,requests,outputs,locks=conformance()
    obs={'mode':mode,'passed':checks['passed'],'checks':len(checks['checks']),
        'failures':[c['name'] for c in checks['checks'] if not c['passed']],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-clock}
    if not checks['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),checks)
    elif mode=='--record':
        for n,x in [('checks.json',checks),('requests.json',requests),('relations.json',outputs),('schema.json',schema()),('source-lock.json',locks)]:dump(HERE/n,x)
        dump(HERE/'manifest.json',{'started_utc':start,'wall_seconds':obs['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version(),'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1',
            'random_seeds':'N/A: deterministic symbolic/interval checks','data_version':{g:sha(p) for g,p in LEDGERS.items()},
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','requests.json','relations.json','schema.json','source-lock.json']}})
    elif mode=='--replay':
        assert checks==json.loads((HERE/'checks.json').read_text())
        assert requests==json.loads((HERE/'requests.json').read_text())
        assert outputs==json.loads((HERE/'relations.json').read_text())
    print(json.dumps(obs));return 0 if checks['passed'] else 1
if __name__=='__main__':sys.exit(main())
