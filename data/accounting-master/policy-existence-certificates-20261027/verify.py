"""Check exact certificates and all protected small-domain populations."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
from itertools import product
import json,os,platform,resource,subprocess,sys,time,traceback
import existence as x
import logic
m=x.m
H=Path(__file__).resolve().parent;R=H.parents[2]
def digest(p):return sha256(p.read_bytes()).hexdigest()

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];controls=[];cases=[];logic_cases=[];pins={};brief=[]
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+chr(10))
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def refuse(n,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,AssertionError,IndexError) as err:
            controls.append(dict(name=n,reason=str(err)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'revised-source-actor-messages-20261027/attempt-02';e=m.b.Evidence()
        ck('message_binding_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==v);pins[n]=v
        for q in list(B.glob('*.json'))+[H/n for n in ('logic.py','existence.py','verify.py','contract.md')]+[R/'docs/plans/accounting-policy-existence-certificates-20261027.md']:
            pins[str(q.relative_to(R))]=digest(q)
        save('source-lock.json',pins)
        for n in ('logic.py','existence.py','verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        vocabulary=[((i,b),) for i in range(2) for b in (0,1)]+[((0,a),(1,b)) for a,b in product((0,1),repeat=2)]
        authored=[]
        for mask in range(256):
            terms=[(v,'clause-'+str(i)) for i,v in enumerate(vocabulary) if mask&(1<<i)]
            expected=[list(rule) for rule in product((0,1),repeat=2) if not any(all(rule[i]==bit for i,bit in term) for term,source in terms)]
            authored.append(dict(case='two-variable-'+str(mask),variables=2,terms=terms,expected=expected))
        for name,n,terms in [('unused',4,[(((0,0),),'unary')]),('empty',3,[]),('tautology',2,[(((0,0),(0,1)),'tautology')]),
                             ('long_cycle',4,[(((0,0),),'unit')]+[(((i,1),(i+1,0)),'forward-'+str(i)) for i in range(3)]+[(((3,1),(0,1)),'return')])]:
            expected=[list(rule) for rule in product((0,1),repeat=n) if not any(all(rule[i]==bit for i,bit in term) for term,source in terms)]
            authored.append(dict(case=name,variables=n,terms=terms,expected=expected))
        plans=json.loads((B/'inputs-and-expectations.json').read_text())
        save('inputs-and-expectations.json',dict(logical=authored,source_cases=[dict(case=v['case'],input_identity=m.identity(v),expected='checked certificate; protected population equivalence where assessed') for v in plans]))
        for item in authored:
            cert=logic.solve(item['variables'],item['terms'])
            ck(item['case']+':certificate',logic.verify(item['variables'],item['terms'],cert))
            ck(item['case']+':brute_force_equivalence',(cert['kind']=='assignment')==bool(item['expected']))
            if cert['kind']=='assignment':ck(item['case']+':member',cert['rule'] in item['expected'])
            logic_cases.append(dict(case=item['case'],certificate=cert))
        old={v['case']:v['result'] for v in json.loads((B/'cases.json').read_text())}
        for item in plans:
            name,cs,decl=item['case'],item['contexts'],item['declaration'];before=m.identity(cs)
            result=x.evaluate(cs,decl,e)
            ck(name+':certificate',x.verify(result,m.identity(result),cs,decl,e))
            ck(name+':pure',before==m.identity(cs))
            ck(name+':same_keys_rows',result['keys']==old[name]['keys'] and result['row_ids']==[r['id'] for r in old[name]['rows']])
            ck(name+':same_contexts',result['contexts']==old[name]['contexts'])
            if old[name]['candidates'] is not None:
                ck(name+':protected_population',(result['certificate']['kind']=='assignment')==bool(old[name]['candidates']))
                if result['certificate']['kind']=='assignment':ck(name+':witness_in_protected_population',result['certificate']['rule'] in old[name]['candidates'])
            if result['unresolved_contexts']:ck(name+':no_full_feasibility',result['status']!='conditionally_feasible')
            cases.append(dict(case=name,result=result));brief.append(dict(case=name,status=result['status'],keys=result['required_keys'],certificate=None if result['certificate'] is None else result['certificate']['kind']))
        byname={v['case']:v['result'] for v in cases}
        ck('new_large_domain_certificate',byname['between:numeric_and_reported_receipt']['required_keys']==38 and byname['between:numeric_and_reported_receipt']['certificate'] is not None)
        # Corrupt a complete positive witness and a genuine contradiction.
        pos=byname['protected_viable_between:numeric'];posin=next(v for v in plans if v['case']=='protected_viable_between:numeric')
        neg=byname['between:numeric'];negin=next(v for v in plans if v['case']=='between:numeric')
        ck('positive_control',pos['certificate']['kind']=='assignment');ck('negative_control',neg['certificate']['kind']=='contradiction')
        alterations=[('drop_key',lambda z:z['keys'].pop()),('drop_row',lambda z:z['row_ids'].pop()),
                     ('drop_support',lambda z:z['contexts'][0]['world_binding']['source_supports'].clear()),
                     ('claim_actual_information',lambda z:z.update(actual_information_claim=True)),
                     ('fabricate_population',lambda z:z.update(population='all_policies_enumerated')),
                     ('wrong_scope',lambda z:z.update(scope='actual_company')),
                     ('wrong_status',lambda z:z.update(status='conditionally_infeasible')),
                     ('truncate_assignment',lambda z:z['certificate']['rule'].pop()),
                     ('wrong_assignment_type',lambda z:z['certificate']['rule'].__setitem__(0,True))]
        for flag in m.w.FLAGS:alterations.append(('admission_'+flag,lambda z,k=flag:z.update({k:True})))
        for name,change in alterations:
            bad=cp(pos);change(bad);refuse(name,lambda z=bad:x.verify(z,m.identity(z),posin['contexts'],posin['declaration'],e))
        for name,change in [('empty_path',lambda z:z['certificate']['forward'].clear()),
                            ('missing_row',lambda z:z['certificate']['forward'][0].update(row='missing')),
                            ('wrong_endpoint',lambda z:z['certificate']['forward'][-1].update(end=2*z['certificate']['variable'])),
                            ('wrong_literal',lambda z:z['certificate'].update(variable=z['required_keys'])),
                            ('remove_certificate',lambda z:z.update(certificate=None))]:
            bad=cp(neg);change(bad);refuse(name,lambda z=bad:x.verify(z,m.identity(z),negin['contexts'],negin['declaration'],e))
        invalid=next(rule for rule in product((0,1),repeat=pos['required_keys']) if list(rule) not in old['protected_viable_between:numeric']['candidates'])
        bad=cp(pos);bad['certificate']['rule']=list(invalid)
        refuse('invalid_full_assignment',lambda:x.verify(bad,m.identity(bad),posin['contexts'],posin['declaration'],e))
        refuse('stale_result',lambda:x.verify(pos,'0'*64,posin['contexts'],posin['declaration'],e))
        # A retained row must justify each edge, not merely exist in the file.
        bad=cp(neg);bad['certificate']['forward'][0]['row']=next(r['id'] for r in old['between:numeric']['rows'] if r['status']=='accepted')
        refuse('accepted_row_as_implication',lambda:x.verify(bad,m.identity(bad),negin['contexts'],negin['declaration'],e))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),logical_formulas=len(authored),assertions=len(checks),controls=len(controls),protected_files=len(pins),
                     certificates=sum(v['certificate'] is not None for v in brief),new_large_domains=sum(v['keys']>12 and v['certificate'] is not None for v in brief))
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases),('logical-cases.json',logic_cases),('summary.json',brief)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,
             git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,
             seeds='N/A exact finite logic',data_version='source-lock.json',plan='docs/plans/accounting-policy-existence-certificates-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
