from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from itertools import product
from datetime import datetime,timezone
import importlib.util,json,os,platform,subprocess,sys,time
import domain as m
H=Path(__file__).resolve().parent;R=H.parents[2];A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False)
fspec=importlib.util.spec_from_file_location('prospective_own_fixtures',H/'fixtures.py')
f=importlib.util.module_from_spec(fspec);fspec.loader.exec_module(f)
clock=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];cases=[];controls=[];pins={}
p=m.b.f.t.prior.load('prospective_partial_oracles',H.parent/'partial-frontier-policy-20261027/partial.py')
def sha(q):return sha256(q.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n
def tuples(x):return tuple(tuples(v) for v in x) if isinstance(x,list) else x
try:
    e=m.b.Evidence();pins.update(e.dependencies);pins.update(e.method_files)
    for q in [H/'domain.py',H/'fixtures.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-prospective-policy-domain-20261027.md',
              H.parent/'partial-frontier-policy-20261027/partial.py',H.parent/'partial-frontier-policy-20261027/attempt-01/verification.json']:
        pins[str(q.relative_to(R))]=sha(q)
    save('source-lock.json',pins)
    for n in ['domain.py','fixtures.py','verify.py','contract.md']:(A/n).write_bytes((H/n).read_bytes())
    ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
    prepared=[]
    for name,x,options in f.inputs():
        d=f.declaration(x,e,**options);did=m.identity(d);domain=m.derive(x,m.identity(x),d,did,e)
        ck(name+':domain_before_family',domain['status'],'conditional_domain')
        ck(name+':no_feasibility_claim',domain['candidate_feasibility'],'not_assessed')
        prepared.append(dict(case=name,input=x,declaration=d,domain=domain))
    # Persist all domain artifacts BEFORE the first complete temporal evaluation.
    save('declared-before-evaluation.json',prepared)
    for item in prepared:
        name=item['case'];x=item['input'];d=item['declaration'];domain=item['domain'];keys=[tuples(k) for k in domain['keys']]
        family=m.b.f.evaluate(x,m.identity(x),e)
        maps={z['source_head']:z for z in d['maps']}
        full_decl=dict(profile='FiniteActorObservationMap/1',family_sha256=m.identity(family),actor=d['actor'],first_at=d['first_at'],second_at=d['second_at'],
          actions=cp(d['actions']),maps=[],tag_observations={},trusted_tag_observations=[])
        known_rows=[]
        for o in family['outcomes']:
            if o['outcome']['status']!='selected_conditional':continue
            heads=o['outcome']['heads'];head=heads['observation_scheme'];entry=cp(maps[head]);entry['outcome_sha256']=o['outcome_sha256']
            # Full binding demands exact selected keys; prospective maps may
            # include keys from a different original financial head.
            scenario=o['outcome']['scenario'];raw=[z for z in e.rows if z['receipt']==scenario['receipt'] and (scenario['family']=='mixed' or z['right'])]
            k1={m.b.wirekey(m.b.observation_keys(z,scenario['view'])[0]) for z in raw};k2={m.b.wirekey(m.b.observation_keys(z,scenario['view'])[1]) for z in raw if z['obs2'] is not None}
            entry['first']=[z for z in entry['first'] if m.b.wirekey(z['key']) in k1];entry['second']=[z for z in entry['second'] if m.b.wirekey(z['key']) in k2]
            full_decl['maps'].append(entry)
            rows=m.map_rows(x,d,e,(heads['financial_family'],head));known_rows+=rows
            ck(name+':covered:'+o['outcome_sha256'],set(m.keys(rows))<=set(keys))
        full=m.b.evaluate(family,m.identity(family),full_decl,m.identity(full_decl),e)
        direct,rejected=p.restrictions(known_rows,keys);want=p.oracle(known_rows,keys)
        ck(name+':independent_all_candidates',{tuple(z) for z in direct},want)
        if full['status']=='complete_conditional':
            ck(name+':full_extensions',{tuple(z) for z in direct},p.extension_set({tuples(z) for z in full['policies']},keys))
            actual_keys=m.keys(full['rows']);indices=[keys.index(k) for k in actual_keys]
            projected={tuple(z[i] for i in indices) for z in direct};expected_projection=p.extension_set({tuples(z) for z in full['policies']},actual_keys)
            ck(name+':projection',projected,expected_projection)
            status='conditionally_feasible' if direct else 'conditionally_infeasible'
        else:status='unresolved_source_family'
        if name in ['unknown_access','retraction']:ck(name+':unresolved_preserved',status,'unresolved_source_family')
        if name=='baseline':ck('baseline_feasible',status,'conditionally_feasible')
        ck(name+':domain_immutable',item['domain'],m.derive(x,m.identity(x),d,m.identity(d),e))
        cases.append(dict(**item,family=family,complete_observation=full,known_row_count=len(known_rows),candidates=direct,status=status,
                          unknown_outcomes=[o for o in family['outcomes'] if o['outcome']['status']!='selected_conditional']))
    base=prepared[0];x=base['input'];d=base['declaration']
    def refuse(name,mut):
        bad=cp(d);mut(bad)
        try:m.derive(x,m.identity(x),bad,m.identity(bad),e)
        except (ValueError,KeyError,TypeError,AssertionError) as exc:controls.append(dict(name=name,reason=str(exc)));ck('refusal:'+name,True)
        else:ck('refusal:'+name,False)
    refuse('missing_map',lambda z:z['maps'].pop())
    refuse('duplicate_head',lambda z:z['maps'].append(cp(z['maps'][0])))
    refuse('wrong_actor',lambda z:z.update(actor='other'))
    refuse('wrong_source',lambda z:z['maps'][0].update(source_sha256='0'*64))
    refuse('wrong_input',lambda z:z.update(input_sha256='0'*64))
    refuse('first_time',lambda z:z.update(first_at='2026-01-01T00:00:00Z'))
    refuse('second_time',lambda z:z.update(second_at=z['first_at']))
    refuse('changed_actions',lambda z:z['actions'].update(first=['pay']))
    refuse('missing_key',lambda z:z['maps'][0]['first'].pop())
    refuse('duplicated_key',lambda z:z['maps'][0]['first'].append(cp(z['maps'][0]['first'][0])))
    refuse('hidden_tag',lambda z:z['maps'][0].update(tag={'reveal':'first'}))
    refuse('hindsight_field',lambda z:z.update(family_sha256='0'*64))
    refuse('invalid_bound',lambda z:z.update(max_policy_keys=13))
    small=cp(d);small['max_policy_keys']=1;stopped=m.derive(x,m.identity(x),small,m.identity(small),e)
    ck('bound_no_truncation',stopped['status'],'unresolved_domain_budget');ck('bound_retains_input',stopped['request'],x);ck('bound_no_keys',stopped['keys'],None)
    save('budget-case.json',stopped)
    for name,h in pins.items():ck('protected:'+name,sha(R/name),h)
    save('cases.json',cases);save('checks.json',checks);save('controls.json',controls)
    summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='prospective original-registry finite domain; no partial frontier binding yet')
    save('verification.json',summary);print(json.dumps(summary))
except Exception as exc:
    save('failure.json',dict(error=str(exc),checks=checks,cases=cases,controls=controls));raise
finally:
    save('run-manifest.json',dict(command=sys.argv,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),
      cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-clock,seeds='N/A exact finite comparison',data_version='source-lock.json',
      plan='docs/plans/accounting-prospective-policy-domain-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
