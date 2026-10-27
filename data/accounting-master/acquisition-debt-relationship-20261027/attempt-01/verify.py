"""One-shot deterministic scope comparison; no numeric or accounting admission."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from itertools import product
import json,os,platform,subprocess,sys,time
import reference as candidate
import fixtures as independent
H=Path(__file__).resolve().parent;R=H.parents[2]
attempt=H/('attempt-'+sys.argv[1]);attempt.mkdir(exist_ok=False)
started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
def digest(p):return sha256(p.read_bytes()).hexdigest()
def save(name,obj):(attempt/name).write_text(json.dumps(obj,indent=2)+chr(10))
checks=[];outputs=[];controls=[];grid=[]
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)));assert value,name
paths=[H/'reference.py',H/'fixtures.py',H/'verify.py',H/'contract.md',
 R/'docs/plans/accounting-debt-conversion-relationship-20261027.md',
 H/'source-attempt-01/int19-may2019.pdf',H/'source-attempt-01/int19-page.html',
 H.parent/'conversion-control-scope-20261026/source-attempt-02/aasb3-2026.pdf',
 H.parent/'contingent-conversion-authority-20261026/source-attempt-02/aasb9-2026.pdf']
for folder in ['acquisition-prior-interest-20261027','acquisition-prior-interest-scope-20261027','acquisition-prior-worksheet-20261027']:
    old=H.parent/folder/'attempt-01'
    paths += [old/'verification.json',old/'source-lock.json',old/'cases.json']
    check('prior_pass:'+folder,json.loads((old/'verification.json').read_text())['status']=='PASS')
    for name,h in json.loads((old/'source-lock.json').read_text()).items():
        check('prior_lock:'+name,digest(R/name)==h);paths.append(R/name)
lock={str(p.relative_to(R)):digest(p) for p in sorted(set(paths))}
save('source-lock.json',lock)
for name in ['reference.py','fixtures.py','verify.py','contract.md']:
    (attempt/name).write_bytes((H/name).read_bytes())
try:
    check('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
    for row in independent.cases():
        out=candidate.derive(row['request']);check('complete_expected:'+row['id'],out==row['expected'])
        outputs.append(dict(id=row['id'],request=row['request'],expected=row['expected'],actual=out))
    keys=['renegotiated','original_terms','creditor_existing_shareholder','acts_as_owner',
          'common_control_before_after','equity_distribution_or_contribution']
    for values in product(['yes','no','unknown'],repeat=len(keys)):
        facts=dict(zip(keys,values));r=independent.request(changes=facts)
        possible=[]
        domains=[[True,False] if v=='unknown' else [v=='yes'] for v in values]
        for reneg,orig,share,owner,common,substance in product(*domains):
            e=set()
            if orig:e.add('original_terms')
            if share and owner:e.add('existing_shareholder_acting_as_owner')
            if common and substance:e.add('common_control_equity_substance')
            possible.append(e)
        certain=set.intersection(*possible);possible_keys=set.union(*possible);uncertain=possible_keys-certain
        deps=list(independent.BASE)
        if certain:
            status='conditional_scope';route='debtor_int19_excluded'
            deps+=['alternative_debtor_method']+['unresolved_other_exclusion:'+k for k in uncertain]
        elif facts['renegotiated']=='no':
            status='conditional_scope';route='debtor_int19_not_established'
            deps+=['renegotiated_exchange_not_established']+['unresolved_other_exclusion:'+k for k in uncertain]
        elif uncertain or facts['renegotiated']=='unknown':
            status='unresolved';route='debtor_scope_unresolved';deps+=['scope_fact:'+k for k in uncertain]
            if facts['renegotiated']=='unknown':deps+=['scope_fact:renegotiated']
        else:
            status='conditional_scope';route='debtor_int19_method_required';deps=list(independent.DEBTOR)
        expected=independent.expected(r,status,route,deps,sorted(certain));actual=candidate.derive(r)
        check('truth_table:'+','.join(values),actual==expected)
        grid.append(dict(assertions=facts,expected=expected,actual=actual))
    def refuse(name,mutate,rebind=True,reason=None):
        r=independent.request();mutate(r)
        if rebind:independent.bind(r)
        o=candidate.derive(r);check('refusal:'+name,o['status']=='invalid')
        if reason:check('reason:'+name,o['reason']==reason)
        check('permission:'+name,all(o.get(k) is False for k in candidate.FLAGS))
        controls.append(dict(id=name,request=r,actual=o))
    refuse('profile',lambda r:r.update(profile='Other'),False,'profile')
    refuse('payload_hash',lambda r:r.update(expected_payload_sha256='0'*64),False,'payload_binding')
    refuse('prior_equity',lambda r:r['payload'].update(prior_instrument='equity'),True,'prior_debt_required')
    refuse('cash_exchange',lambda r:r['payload'].update(transaction='cash_purchase'),True,'transaction_scope')
    refuse('extra_measurement',lambda r:r['payload'].update(amount=100),True,'payload_fields')
    refuse('bad_perspective',lambda r:r['payload'].update(perspective='both'),True,'perspective')
    refuse('wrong_subject',lambda r:r['payload']['context'].update(subject='P'),True,'subject_perspective')
    refuse('same_parties',lambda r:r['payload']['context'].update(creditor='S'),True,'distinct_parties')
    refuse('actor_mismatch',lambda r:r['payload']['source'].update(actor='other'),True,'source_context')
    refuse('source_subject',lambda r:r['payload']['source'].update(subject='P'),True,'source_context')
    refuse('future_event',lambda r:r['payload']['context'].update(cutoff='2026-10-26T00:00:00Z'),True,'event_after_cutoff')
    refuse('source_event',lambda r:r['payload']['source'].update(at='2026-10-26T00:00:00Z'),True,'source_event_date')
    refuse('naive_date',lambda r:r['payload']['context'].update(at='2026-10-27T00:00:00'),True,'timestamp_utc')
    refuse('blank_basis',lambda r:r['payload']['source'].update(rationale=' '),True,'source_rationale')
    refuse('bad_status',lambda r:r['payload']['assertions'].update(original_terms='maybe'),True,'assertion_original_terms')
    refuse('bool_status',lambda r:r['payload']['assertions'].update(original_terms=False),True,'assertion_original_terms')
    refuse('extra_fact',lambda r:r['payload']['assertions'].update(percentage=75),True,'assertions_fields')
    def stale_assertions(r):
        r['payload']['assertions']['original_terms']='yes'
        r['expected_payload_sha256']=independent.digest(r['payload'])
    refuse('stale_assertion_binding',stale_assertions,False,'assertion_source_binding')
    def stale_source(r):
        r['payload']['source']['text']='Changed source';r['expected_payload_sha256']=independent.digest(r['payload'])
    refuse('stale_evidence_binding',stale_source,False,'evidence_binding')
    for name,h in lock.items():check('preserved:'+name,digest(R/name)==h)
    save('cases.json',outputs);save('truth-table.json',grid);save('controls.json',controls);save('checks.json',checks)
    result=dict(status='PASS',cases=len(outputs),truth_table_cases=len(grid),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),**candidate.FLAGS)
    save('verification.json',result);print(json.dumps(result))
except Exception as exc:
    save('failure.json',dict(error=str(exc),checks=checks,cases=outputs,controls=controls));raise
finally:
    save('run-manifest.json',dict(command=sys.argv,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
      environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',CUDA_VISIBLE_DEVICES=os.environ.get('CUDA_VISIBLE_DEVICES'),
      started_utc=started,wall_seconds=time.monotonic()-clock,random_seeds='N/A deterministic exhaustive finite scope',
      data_version='source-lock.json',plan='docs/plans/accounting-debt-conversion-relationship-20261027.md',
      result=str((H/'result.md').relative_to(R)),artifacts=str(attempt.relative_to(R))))
