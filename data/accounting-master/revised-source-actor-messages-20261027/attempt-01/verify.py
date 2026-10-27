"""Bounded exact comparison; preserve full outputs without printing large payloads."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import json,os,platform,resource,subprocess,sys,time,traceback
import messages as m
import checker as c

H=Path(__file__).resolve().parent;R=H.parents[2]
def digest(p):return sha256(p.read_bytes()).hexdigest()

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];controls=[];cases=[];pins={};brief=[]
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+chr(10))
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def refuse(n,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,AssertionError) as err:
            controls.append(dict(name=n,reason=str(err)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'financial-source-world-binding-20261027/attempt-01';e=m.b.Evidence()
        ck('world_binding_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in {**e.dependencies,**e.method_files,**json.loads((B/'source-lock.json').read_text())}.items():
            ck('source:'+n,digest(R/n)==v);pins[n]=v
        for pth in list(B.glob('*.json'))+[H/n for n in ('messages.py','checker.py','verify.py','contract.md')]+[R/'docs/plans/accounting-revised-source-actor-messages-20261027.md',H.parent/'joint-stage-policy-20261027/binding.py',H.parent/'partial-frontier-policy-20261027/partial.py',H.parent/'prospective-policy-domain-20261027/fixtures.py']:
            pins[str(pth.relative_to(R))]=digest(pth)
        save('source-lock.json',pins)
        for n in ('messages.py','checker.py','verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        saved=json.loads((B/'inputs-and-expectations.json').read_text());contexts={}
        for record in saved:
            f=record['family'];contexts[record['case']]=dict(family=f,world=record['declaration'],mapping=m.fx.declaration(f['input']['original'],e))
        plans=[]
        for name,ctx in contexts.items():
            for mode in ('numeric','numeric_and_reported_receipt'):
                cs=[ctx];plans.append(dict(case=name+':'+mode,contexts=cs,declaration=m.declaration(cs,mode),expectation='exact independently constructed rows and total policies if within bound; otherwise explicit unassessed state'))
        for name,names in [('two_worlds',['between','reverse_receipt_correction']),('resolved_and_unknown',['between','unknown'])]:
            for mode in ('numeric','numeric_and_reported_receipt'):
                cs=[contexts[n] for n in names];plans.append(dict(case=name+':'+mode,contexts=cs,declaration=m.declaration(cs,mode),expectation='one shared rule on equal messages; unresolved alternatives block full feasibility'))
        cs=[contexts['same_financial_head']]
        plans.append(dict(case='forced_overflow',contexts=cs,declaration=m.declaration(cs,'numeric',1),expectation='unresolved_domain_budget'))
        save('inputs-and-expectations.json',plans)
        for item in plans:
            name,cs,decl=item['case'],item['contexts'],item['declaration'];before=m.identity(cs)
            result=m.evaluate(cs,decl,m.identity(decl),e)
            ck(name+':independent',c.verify(result,m.identity(result),cs,decl,e))
            ck(name+':pure',before==m.identity(cs))
            ck(name+':memory',all(m.b.policy.keys(r,'never')[1][0]==m.b.policy.keys(r,'never')[0] and m.b.policy.keys(r,'never')[1][1]==r['a1'] for r in result['rows'] if r['message2'] is not None))
            if result['required_keys']>decl['max_policy_keys']:ck(name+':overflow_no_claim',result['candidates'] is None and result['status']=='unresolved_domain_budget')
            if result['unresolved_contexts']:ck(name+':unknown_not_feasible',result['status']!='conditionally_feasible')
            cases.append(dict(case=name,result=result));brief.append(dict(case=name,status=result['status'],keys=result['required_keys'],rows=len(result['rows']),candidates=None if result['candidates'] is None else len(result['candidates'])))
        byname={v['case']:v['result'] for v in cases}
        # Same-head and same-world baseline reproduces protected row meanings,
        # key order and complete policies, modulo external provenance IDs.
        old=m.j.t.prior.load('actor_protected_joint_stage',H.parent/'joint-stage-policy-20261027/binding.py')
        base=contexts['same_financial_head'];family=base['family'];x=family['input'];pair=family['outcomes'][0]
        decl=dict(profile='JointStageObservationMap/1',joint_request_sha256=m.identity(x),mapping=base['mapping'])
        olddomain=old.derive(x,m.identity(x),decl,m.identity(decl),e)
        oldrows=old.rows(x,decl,e,(pair[0]['heads']['financial_family'],pair[0]['heads']['observation_scheme'],pair[1]['heads']['observation_scheme']))
        baseline=byname['same_financial_head:numeric'];trim=lambda rows:[{k:v for k,v in r.items() if k!='id'} for r in rows]
        ck('same_head_complete_row_meanings',trim(oldrows)==trim(baseline['rows']))
        ck('same_head_prospective_keys',olddomain['keys']==baseline['keys'])
        ks=[m.j.t.prior.tuples(k) for k in baseline['keys']]
        ck('same_head_complete_policy_population',{tuple(p) for p in baseline['candidates']}==m.p.oracle(oldrows,ks))
        # Corrected receipt remains an observation of a report at its own date.
        between=byname['between:numeric_and_reported_receipt']
        ck('first_report_is_7',all(json.loads(json.loads(r['message1'])[0])[1]==7 for r in between['rows']))
        ck('second_report_is_6',all(json.loads(r['message2'][0])[1]==6 for r in between['rows'] if r['message2'] is not None))
        ck('actual_world_receipt_is_6',all(v['world_binding']['world_assumption']['receipt']==6 for v in between['contexts']))
        numeric=byname['two_worlds:numeric'];ks=[m.j.t.prior.tuples(k) for k in numeric['keys']]
        ck('two_world_numeric_assessed',numeric['candidates'] is not None)
        groups={m.identity(contexts[n]):[] for n in ('between','reverse_receipt_correction')}
        for r in numeric['rows']:groups[r['id'].split('/')[0]].append(r)
        sets=[m.p.oracle(rs,ks) for rs in groups.values()]
        ck('common_is_intersection',{tuple(q) for q in numeric['candidates']}==set.intersection(*sets))
        commonkeys=set.intersection(*(set(c.keys(rs)) for rs in groups.values()));ck('shared_visible_messages',bool(commonkeys))
        ck('hidden_world_never_in_keys',all(all(h not in repr(k) for h in groups) for k in ks))
        # Exact small counterexample: each world permits an action, but no rule
        # can take both required actions at the same first message.
        toy=[]
        for world,allowed in [('one','pay'),('two','draw')]:
            for a in ('pay','draw'):
                for z in ('pay','draw'):
                    toy.append(dict(id=world+a+z,support=world,mechanism='hidden',a1=a,a2=z,message1='same',message2=['same',''] if a==allowed else None,status='accepted' if a==allowed else 'refused1'))
        tk=c.keys(toy);individual=[m.p.oracle([r for r in toy if r['support']==w],tk) for w in ('one','two')]
        ck('individual_policy_existence',all(individual));ck('no_common_policy_counterexample',not m.p.oracle(toy,tk))
        save('common-policy-counterexample.json',dict(rows=toy,keys=m.b.canonical(tk),individual_counts=list(map(len,individual)),common_count=0))
        # Check saved-result corruption controls, including refusal witnesses.
        item=next(v for v in plans if v['case']=='between:numeric');cs,decl=item['contexts'],item['declaration'];res=byname[item['case']]
        mutations=[('drop_row',lambda z:z['rows'].pop()),('wrong_numeric_message',lambda z:z['rows'][0].update(message1='future-world')),
                   ('expose_world',lambda z:z['rows'][0].update(mechanism='revealed')),('drop_key_memory',lambda z:z['keys'].pop()),
                   ('erase_source_support',lambda z:z['contexts'][0]['world_binding']['source_supports'].clear()),
                   ('fake_world',lambda z:z['contexts'][0]['world_binding']['world_assumption'].update(receipt=7)),
                   ('claim_actual_information',lambda z:z.update(actual_information_claim=True)),('fake_status',lambda z:z.update(status='production_ready'))]
        if res['candidates']:mutations.append(('drop_candidate',lambda z:z['candidates'].pop()))
        if res['rejections']:
            accepted=next(r['id'] for r in res['rows'] if r['status']=='accepted')
            mutations.append(('false_refusal_witness',lambda z:z['rejections'][0].update(row=accepted)))
        for flag in m.w.FLAGS:mutations.append(('admission_'+flag,lambda z,k=flag:z.update({k:True})))
        for name,change in mutations:
            bad=cp(res);change(bad);refuse(name,lambda z=bad:c.verify(z,m.identity(z),cs,decl,e))
        item=next(v for v in plans if v['case']=='between:numeric_and_reported_receipt');bad=cp(between)
        token=json.loads(json.loads(bad['rows'][0]['message1'])[0]);token[1]=6;bad['rows'][0]['message1']=c.wire([c.wire(token),None])
        refuse('future_corrected_report_at_first',lambda:c.verify(bad,m.identity(bad),item['contexts'],item['declaration'],e))
        overflow=cp(byname['forced_overflow']);overflow.update(candidates=[],rejections=[])
        item=next(v for v in plans if v['case']=='forced_overflow')
        refuse('fabricated_overflow_population',lambda:c.verify(overflow,m.identity(overflow),item['contexts'],item['declaration'],e))
        bad=cp(decl);bad['max_policy_keys']=13;refuse('silent_budget_increase',lambda:m.evaluate(cs,bad,m.identity(bad),e))
        badcs=cp(cs);badcs[0]['mapping']['maps'][0]['first'][0]['token']='world6';bad=m.declaration(badcs,'numeric')
        refuse('undeclared_world_tag',lambda:m.evaluate(badcs,bad,m.identity(bad),e))
        refuse('stale_result',lambda:c.verify(res,'0'*64,cs,decl,e))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),
                     assessed_cases=sum(v['candidates'] is not None for v in brief),overflow_cases=sum(v['status']=='unresolved_domain_budget' for v in brief),scope='supplied dated messages and common finite policies only')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases),('summary.json',brief)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,
             git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,
             seeds='N/A exact finite comparison',data_version='source-lock.json',plan='docs/plans/accounting-revised-source-actor-messages-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')

if __name__=='__main__':main()
