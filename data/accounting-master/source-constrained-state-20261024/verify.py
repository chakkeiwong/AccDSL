"""Finite source-state checks; independent date and rounding comparators."""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction as Q
from hashlib import sha256
import json, os, platform, subprocess, sys, time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
from partial_state import (HERE,ROOT,READINESS,OPS,COMPOSED,fixture,evaluate,validate,
    canonical,digest,schema,rounding_interval,verify_result,upstream)
from partial_state_text import render,lower
PLAN='docs/plans/accounting-source-constrained-state-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def conditional(body):
    out=deepcopy(body);out['assumptions']=[{'id':'round-to-million','rule':'nearest_ties_away_from_zero',
        'quantum':'1/1','provenance':'Optional diagnostic hypothesis; retained source does not establish tie-breaking.',
        'disposition':'proposed_not_admitted'}]
    for b in out['bindings']:b['interpretation']={'mode':'assumed_rounding','assumption_id':'round-to-million'}
    return out

def conformance():
    checks=[]
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    def reject(name,fn):
        try:fn()
        except Exception:check(name,True)
        else:check(name,False)
    locks={}
    m=json.loads((READINESS/'manifest.json').read_text())
    for group in ['inputs','implementation','outputs']:locks.update(m[group])
    for p in [READINESS/'manifest.json',ROOT/PLAN,
        ROOT/'docs/design/proposal/manuscript-company-returns-20261024/chapters/02-history.tex',
        ROOT/'docs/design/proposal/manuscript-company-returns-20261024/sections/fiscal-loss-closing.tex']:
        locks[str(p.relative_to(ROOT))]=sha(p)
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    examples={};outputs={}
    for target in [OPS,COMPOSED]:
        for view,expected in [('annual',27),('interim',27),('combined',54)]:
            key=target+':'+view;b=fixture(target,view);r=evaluate(b)
            examples[key]=b;outputs[key]=r
            check('roundtrip:'+key,lower(render(b))==b)
            check('execution_equivalence:'+key,evaluate(lower(render(b)))==r)
            check('selected_count:'+key,len(r['constraints'])==expected)
            check('display_only:'+key,all(c['underlying_measurement']=={'status':'unresolved','interval':None} for c in r['constraints']))
            check('no_opening:'+key,r['executable_opening'] is None and not r['executed'])
            check('no_feasibility_claim:'+key,r['actual_history']=={'feasibility':'unknown','measure':None,'joint_constraints_solved':False})
            _,p=upstream(target,view)
            check('dependencies_retained:'+key,r['dependencies']==p['dependencies'])
            check('missing_retained:'+key,r['unavailable_required_state']==p['unavailable_required_state'])
            check('unsupported_retained:'+key,r['unsupported_target_scope']==p['unsupported_target_scope'])
            observed={x['ref']['digest']:x for g in ['annual_refs','interim_refs'] for x in p['known_evidence'][g] if x['record']['body']['row_id'].startswith('balance.')}
            for c in r['constraints']:check('original_observation:'+key+':'+c['id'],c['observation']==observed[c['observation']['ref']['digest']])
    b=fixture();r=evaluate(b);cb=conditional(b);cr=evaluate(cb)
    examples['conditional_rounding']=cb;outputs['conditional_rounding']=cr
    check('dates_independently_known',[(p['start'],p['end_exclusive'],p['day_count']) for p in r['periods']]==[('2023-10-01','2024-09-29',364),('2024-09-29','2024-12-29',91)])
    check('conditional_roundtrip',lower(render(cb))==cb)
    check('assumption_distinct_identity',cr['program_sha256']!=r['program_sha256'])
    check('assumption_no_state_resolution',cr['dependencies']==r['dependencies'] and cr['unavailable_required_state']==r['unavailable_required_state'])
    cash=next(c for c in cr['constraints'] if c['id']=='annual.balance.cash')
    check('cash_interval',cash['underlying_measurement']['interval']=={'lower':'59885/2','upper':'59887/2','lower_inclusive':True,'upper_inclusive':False})
    retained=next(c for c in cr['constraints'] if c['id']=='annual.balance.retained')
    check('negative_interval',retained['underlying_measurement']['interval']=={'lower':'-38309/2','upper':'-38307/2','lower_inclusive':False,'upper_inclusive':True})
    # An independent Decimal rounding operator checks membership at and around ties.
    for q in [Q(1),Q(2),Q(1,10)]:
        for k in [-3,-1,0,1,3]:
            d=k*q;interval=rounding_interval(d,q)
            lo,hi=Q(interval['lower']),Q(interval['upper'])
            for offset in [Q(-51,100),Q(-1,2),Q(-49,100),Q(0),Q(49,100),Q(1,2),Q(51,100)]:
                x=d+offset*q
                inside=(x>lo or (x==lo and interval['lower_inclusive'])) and (x<hi or (x==hi and interval['upper_inclusive']))
                z=x/q;rounded=(Decimal(z.numerator)/Decimal(z.denominator)).quantize(Decimal(1),rounding=ROUND_HALF_UP)
                check('rounding_membership:'+str((q,k,offset)),inside==(Q(rounded)*q==d))
    reject('off_grid_display',lambda:rounding_interval(Q(1,2),Q(1)))
    reject('zero_quantum',lambda:rounding_interval(1,0))
    reject('negative_quantum',lambda:rounding_interval(1,-1))
    for key,mutate in [
        ('overlap',lambda x:x['periods'][1].update(start='2024-09-28')),
        ('gap',lambda x:x['periods'][1].update(start='2024-09-30')),
        ('reverse',lambda x:x['periods'][0].update(start='2025-01-01')),
        ('invalid_day',lambda x:x['periods'][0].update(start='2024-02-30')),
        ('wrong_instant',lambda x:x['bindings'][0].update(measurement_date='2024-09-29')),
        ('wrong_perimeter',lambda x:x['bindings'][0]['context'].update(perimeter='Apple legal')),
        ('wrong_unit',lambda x:x['bindings'][0]['context'].update(unit='USD')),
        ('exact_latent',lambda x:x['bindings'][0]['interpretation'].update(mode='exact')),
        ('drop_binding',lambda x:x['bindings'].pop()),
        ('drop_requirement',lambda x:x['requirement_ids'].pop()),
        ('duplicate_requirement',lambda x:x['requirement_ids'].append(x['requirement_ids'][0])),
        ('duplicate_snapshot',lambda x:x['bindings'].append(deepcopy(x['bindings'][0]))),
        ('source_period_change',lambda x:x['periods'][0].update(source_period='FY2024: 2024-01-01 through 2024-12-31')),
        ('false_source_hash',lambda x:x['source'].update(readiness_result_sha256='0'*64)),
        ('multiline_name',lambda x:x.update(name='Apple\nother')),
        ('undeclared_premise',lambda x:x['bindings'][0]['interpretation'].update(mode='assumed_rounding',assumption_id='missing'))]:
        bad=deepcopy(b);mutate(bad);reject('rejected:'+key,lambda:evaluate(bad))
    bad=deepcopy(cb);bad['assumptions'][0]['quantum']='0/1';reject('zero_premise',lambda:evaluate(bad))
    bad=deepcopy(cb);bad['assumptions'][0]['disposition']='accepted_source_fact';reject('promoted_premise',lambda:evaluate(bad))
    unicode=deepcopy(b);unicode['name']='財務 — Apple';check('unicode_roundtrip',lower(render(unicode))==unicode)
    # Generic structural dates need not be calendar years; source binding remains separate.
    synthetic=deepcopy(fixture(view='annual'));synthetic['periods'][0].update(start='2023-09-24')
    check('structural_53_week_date_support',validate(synthetic)==synthetic)
    reject('source_53_week_relabel',lambda:evaluate(synthetic))
    for text in [render(b).replace('end_partial_company;',''),render(b)+'unknown;',
                 render(b).replace('source ', 'unknown ',1),render(b).replace('requirement identity;','requirement identity;\nrequirement identity;')]:
        reject('malformed_text:'+str(len(checks)),lambda:lower(text))
    for field,value in [('executable_opening',{'cash':29943}),('status','ready'),('executed',True),('dependencies',[]),('actual_history',{'feasibility':'feasible'})]:
        bad=deepcopy(r);bad[field]=value;check('forged_result:'+field,not verify_result(b,bad))
    bad=deepcopy(cr);bad['constraints'][0]['underlying_measurement']['interval']['upper_inclusive']=True
    check('changed_endpoint_rejected',not verify_result(cb,bad))
    check('honest_result',verify_result(b,r))
    return {'passed':all(c['passed'] for c in checks),'checks':checks},examples,outputs,locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'already recorded'
    start=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in m[group].items():assert sha(ROOT/name)==h,name
    checks,examples,outputs,locks=conformance()
    obs={'mode':mode,'passed':checks['passed'],'checks':len(checks['checks']),
        'failures':[c['name'] for c in checks['checks'] if not c['passed']],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-clock}
    if not checks['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),checks)
    elif mode=='--record':
        for n,x in [('checks.json',checks),('examples.json',examples),('partial-states.json',outputs),('schema.json',schema()),('source-lock.json',locks)]:dump(HERE/n,x)
        (HERE/'example.accdsl').write_text(render(examples[OPS+':combined']))
        (HERE/'conditional.accdsl').write_text(render(examples['conditional_rounding']))
        dump(HERE/'manifest.json',{'started_utc':start,'wall_seconds':obs['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version(),'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1',
            'random_seeds':'N/A: deterministic date and rational checks','data_version':sha(READINESS/'readiness.json'),
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','examples.json','partial-states.json','schema.json','source-lock.json','example.accdsl','conditional.accdsl']}})
    elif mode=='--replay':
        assert checks==json.loads((HERE/'checks.json').read_text())
        assert examples==json.loads((HERE/'examples.json').read_text())
        assert outputs==json.loads((HERE/'partial-states.json').read_text())
    print(json.dumps(obs));return 0 if checks['passed'] else 1
if __name__=='__main__':sys.exit(main())
