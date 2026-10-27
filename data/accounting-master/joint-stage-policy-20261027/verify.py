from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback
H=Path(__file__).resolve().parent;R=H.parents[2]
s=importlib.util.spec_from_file_location('own_joint_stage_binding',H/'binding.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];cases=[];pins={}
s=m.j.t.prior.load('joint_stage_original_mapping',H.parent/'prospective-policy-domain-20261027/fixtures.py')
def sha(q):return sha256(q.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
def ck(n,a,b=True):checks.append(dict(name=n,passed=a==b));assert a==b,n
def refuse(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):controls.append(n);ck('refusal:'+n,True)
 else:ck('refusal:'+n,False)
def independent_rows(x,decl,e,pair):
 one,two=pair;fh=one['heads']['financial_family'];h1=one['heads']['observation_scheme'];h2=two['heads']['observation_scheme'];a=next(z for z in decl['mapping']['maps'] if z['source_head']==h1);b=next(z for z in decl['mapping']['maps'] if z['source_head']==h2);fin=one['scenario'];out=[]
 for r in e.rows:
  if r['receipt']!=fin['receipt'] or fin['family']!='mixed' and not r['right']:continue
  raw1=list(r['obs1']) if fin['view']=='refined' else list(r['obs1'][:1]);first=next(z['token'] for z in a['first'] if z['key']==raw1)
  second=None if r['obs2'] is None else next(z['token'] for z in b['second'] if z['key']==list(r['obs2'][-2:]))
  out.append(dict(id='/'.join([fh,h1,h2])+'/'+r['row_id'],support=r['row_id'],mechanism='hidden',a1=r['a1'],a2=r['a2'],message1=json.dumps([first,None],separators=(',',':'),ensure_ascii=False),message2=None if second is None else [second,''],status=r['status']))
 return out
try:
 P=H.parent/'two-decision-source-views-20261027/attempt-01';e=m.b.Evidence();pins.update(e.dependencies);pins.update(e.method_files)
 for n,h in json.loads((P/'source-lock.json').read_text()).items():ck('accepted:'+n,sha(R/n),h);pins[n]=h
 for q in P.glob('*.json'):pins[str(q.relative_to(R))]=sha(q)
 for q in [H/'binding.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-joint-stage-policy-20261027.md',H.parent/'partial-frontier-policy-20261027/partial.py']:pins[str(q.relative_to(R))]=sha(q)
 save('source-lock.json',pins)
 for n in ['binding.py','verify.py','contract.md']:(A/n).write_bytes((H/n).read_bytes())
 ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1');source=json.loads((P/'inputs-and-expectations.json').read_text());prepared=[]
 for row in source:
  x=row['input'];mapping=s.declaration(x['original'],e);decl=dict(profile='JointStageObservationMap/1',joint_request_sha256=m.identity(x),mapping=mapping)
  variants=[('original',cp(decl))]
  if row['case'] in ['between','interval_both']:
   altered=cp(decl)
   for v in altered['mapping']['maps']:
    if x['original']['registry'][v['source_head']]['supersedes'] is not None:
     v['second'][0]['token']='correction_second'
   variants.append(('second_token',altered));collapsed=cp(altered)
   for v in collapsed['mapping']['maps']:
    for entry in v['first']:entry['token']='first'
   variants.append(('collapsed_wiring',collapsed))
  if row['case']=='before_both':
   small=cp(decl);small['mapping']['max_policy_keys']=1;variants.append(('domain_limit',small))
  for label,d in variants:
   domain=m.derive(x,m.identity(x),d,m.identity(d),e);prepared.append(dict(case=row['case']+':'+label,input=x,declaration=d,domain=domain))
 save('domains-before-joint-evaluation.json',prepared)
 refs=json.loads((P/'cases.json').read_text());families={r['case']:r['result'] for r in refs}
 for item in prepared:
  name=item['case'];x=item['input'];d=item['declaration'];domain=item['domain'];family=families[name.split(':')[0]];before=m.identity([x,d,domain,family])
  out=m.evaluate(x,m.identity(x),d,m.identity(d),domain,m.identity(domain),family,m.identity(family),e);ck(name+':pure',m.identity([x,d,domain,family]),before)
  manual=[]
  for pair in family['outcomes']:
   if all(v['status']=='selected_conditional' for v in pair):manual+=independent_rows(x,d,e,pair)
  ck(name+':independent_row_population',out['rows'],manual)
  if out['candidates'] is not None:
   keys=[m.j.t.prior.tuples(k) for k in domain['keys']];expected=m.p.oracle(manual,keys);ck(name+':full_oracle',{tuple(v) for v in out['candidates']},expected)
   ck(name+':domain_coverage',set(m.d.keys(manual))<=set(keys))
  if name.split(':')[0] in ['late_retraction','late_conflict']:ck(name+':unresolved_preserved',out['status'],'unresolved_source_family')
  if name=='inconsistent:original':ck(name+':inconsistent_preserved',out['status'],'inconsistent_clocks')
  if name=='before_both:domain_limit':ck('budget_not_truncated',out['status'],'unresolved_domain_budget');ck('budget_no_candidates',out['candidates'],None)
  cases.append(dict(**item,result=out,family_sha256=m.identity(family)))
 # The original profile's first-stage labels permit only11 keys;changing second labels may exceed12.
 between=next(c for c in cases if c['case']=='between:collapsed_wiring');ck('positive_wiring_admitted',between['domain']['status'],'conditional_domain')
 ref=families['between'];pair=ref['outcomes'][0];wrong=[pair[0],pair[0]];badrows=independent_rows(between['input'],between['declaration'],e,wrong)
 actual=between['result']['rows'];ck('wrong_stage_map_detected',[r['message2'] for r in actual]!=[r['message2'] for r in badrows])
 ck('first_message_unchanged',[r['message1'] for r in actual],[r['message1'] for r in badrows]);ck('first_action_memory',all(m.b.policy.keys(r,'never')[1][1]==r['a1'] for r in actual if r['message2'] is not None))
 # Same-head mappings agree with unchanged prospective map_rows under identical declarations.
 for name in ['before_both:original','after_both:original']:
  c=next(v for v in cases if v['case']==name);pair=families[name.split(':')[0]]['outcomes'][0];heads=pair[0]['heads'];same=m.d.map_rows(c['input']['original'],c['declaration']['mapping'],e,(heads['financial_family'],heads['observation_scheme']))
  trim=lambda rr:[{k:v for k,v in r.items() if k!='id'} for r in rr]
  ck(name+':single_head_population',trim(c['result']['rows']),trim(same))
 cap=json.loads((P/'budget-case.json').read_text());base=next(c for c in cases if c['case']=='interval_both:original');out=m.evaluate(base['input'],m.identity(base['input']),base['declaration'],m.identity(base['declaration']),base['domain'],m.identity(base['domain']),cap,m.identity(cap),e)
 ck('timing_budget_no_policy',out['status'],'unresolved_timing_budget');ck('timing_budget_no_candidates',out['candidates'],None);save('timing-budget.json',out)
 c=next(v for v in cases if v['case']=='between:original');x=c['input'];d=c['declaration'];domain=c['domain'];family=families['between']
 for n,mut in [('second_date',lambda v:v['mapping'].update(second_at='2026-01-04T00:00:00Z')),('actor',lambda v:v['mapping'].update(actor='Bob')),('source',lambda v:v['mapping']['maps'][0].update(source_sha256='0'*64)),('hidden_tag',lambda v:v['mapping']['maps'][0].update(tag={'reveal':'first'})),('wrong_joint_identity',lambda v:v.update(joint_request_sha256='0'*64))]:
  bad=cp(d);mut(bad);refuse(n,lambda q=bad:m.derive(x,m.identity(x),q,m.identity(q),e))
 bad=cp(domain);bad['keys'].pop();refuse('drop_mixed_stage_key',lambda:m.evaluate(x,m.identity(x),d,m.identity(d),bad,m.identity(bad),family,m.identity(family),e))
 badf=cp(family);badf['outcomes'].reverse();badf['supports'].clear();refuse('drop_temporal_support',lambda:m.evaluate(x,m.identity(x),d,m.identity(d),domain,m.identity(domain),badf,m.identity(badf),e))
 for n,h in pins.items():ck('protected:'+n,sha(R/n),h)
 summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='joint stage-specific messages andexact finite policies;no actual actor access or joint partial search')
except Exception:summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,x)
 save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact finite sets',data_version='source-lock.json',plan='docs/plans/accounting-joint-stage-policy-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
 print(json.dumps(summary),flush=True)
sys.exit(summary['status']!='PASS')

