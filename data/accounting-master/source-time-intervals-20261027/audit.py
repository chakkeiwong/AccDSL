"""Independent saved-family interpretation and source/trust adversarial audit."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as Q
from itertools import product
import hashlib,json,sys,time,subprocess,platform
import temporal as t
f=t.prior.load('temporal_independent_fixture_audit',Path(__file__).resolve().parent/'fixtures.py')
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=H/'audit-01';OUT.mkdir(exist_ok=False);start=time.monotonic();checks=[];controls=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):checks.append({'name':n,'pass':bool(v)});assert v,n

def independent_outcome(p,eligible):
 # Select a record only when no other eligible same-slot record replaces it.
 maxima={s:[] for s in t.SLOTS}
 for h,r in p['records'].items():
  if not eligible[h]:continue
  replaced=False
  for k,q in p['records'].items():
   if not eligible[k]:continue
   a=q['supersedes']
   while a is not None:
    if a==h:replaced=True
    a=p['records'][a]['supersedes']
  if not replaced:maxima[r['slot']].append(h)
 heads={};issues=[]
 for s in t.SLOTS:
  hs=sorted(maxima[s])
  if len(hs)!=1:issues.append({'slot':s,'reason':'missing_or_conflicting_head','heads':hs});continue
  h=hs[0];r=p['records'][h]
  if r['disposition']=='retraction':issues.append({'slot':s,'reason':'retracted','head':h});continue
  parent=r['supersedes'];missing=False
  while parent is not None:
   if not eligible[parent]:missing=True
   parent=p['records'][parent]['supersedes']
  if missing:issues.append({'slot':s,'reason':'ancestor_unavailable','head':h});continue
  heads[s]=h
 if issues:return {'status':'unresolved','issues':issues}
 return {'status':'selected_conditional','heads':heads,'scenario':{**p['records'][heads['financial_family']]['payload'],**p['records'][heads['observation_scheme']]['payload']}}

saved=json.loads((H/'attempt-01/proofs.json').read_text());leaves=0
for row in saved:
 p=row['prepared'];found={}
 def visit(node):
  global leaves
  if 'eligible' in node:
   want=independent_outcome(p,node['eligible']);ck('independent_leaf:'+row['case'],want==node['outcome']);found[t.identity(want)]=want;leaves+=1
  for child in node.get('children',[]):visit(child)
 visit(row['result']['tree']);ck('full_view_set:'+row['case'],[found[k] for k in sorted(found)]==row['result']['outcomes'])
# Exact independent endpoint-cell enumeration for the two correlated uncertain clocks.
fixture=next(x[1] for x in f.extended_cases() if x[0]=='correction_public_and_access_correlated');p,res=t.assess(fixture)
new=next(h for h,r in p['records'].items() if r['supersedes']);lo=t.instant('2026-01-01T23:59:59.9999999Z');cut=t.instant('2026-01-02T00:00:00Z');hi=t.instant('2026-01-02T00:00:00.0000001Z');delta=Q(1,30000000)
grid=[lo,lo+delta,lo+2*delta,cut,cut+delta,cut+2*delta];expected={};assignments=0
for publication,access in product(grid,repeat=2):
 if publication>access:continue
 eligible={h:True for h in p['records']};eligible[new]=publication<=cut and access<=cut;o=independent_outcome(p,eligible);expected[t.identity(o)]=o;assignments+=1
ck('full_correlated_clock_view_set',[expected[k] for k in sorted(expected)]==res['outcomes'])
# New input/trust controls; each complete family is still conditionally synthetic.
def control(name,change,wanted='invalid'):
 fixture=f.convert(f.oldcases.base());change(fixture);p,out=t.assess(fixture);ck(name,out['status']==wanted);controls.append({'name':name,'status':out['status'],'reason':out.get('reason')});return out
control('altered_source',lambda f:f['sources'].__setitem__(next(iter(f['sources'])),'changed'))
control('altered_record',lambda f:f['registry'][f['names']['financial_family']]['payload'].__setitem__('receipt',6))
control('missing_clock_bytes',lambda f:f['observations'].pop(next(iter(f['observations']))))
control('altered_clock_bytes',lambda f:f['observations'][next(iter(f['observations']))].__setitem__('subject','foreign'))
# External trust removal widens the time family, never retains supplied exact clocks as admitted.
out=control('untrusted_is_unknown',lambda f:f.update(trusted=frozenset()),'complete_family');ck('untrusted_unknown_markers',bool(out['unknown_clocks']));ck('untrusted_multiple_views',len(out['outcomes'])>1)
# Same bytes for trusted actor access cannot be relabeled to another actor.
def wrong_actor(fixture):
 h=fixture['names']['observation_scheme'];r=fixture['registry'].pop(h);r['access']['Alice']['observation']=r['access']['Bob']['observation'];nh=t.identity(r);fixture['registry'][nh]=r
control('actor_observation_substitution',wrong_actor)
def missing_parent(fixture):
 h=fixture['names']['observation_scheme'];r=fixture['registry'].pop(h);r['supersedes']='0'*64;fixture['registry'][t.identity(r)]=r
control('missing_ancestry',missing_parent)
# Unknown public release does not become the known access timestamp.
base=f.oldcases.base();h=base['names']['observation_scheme'];fixture=f.convert(base,{h:{'published':f.unknown(),'access:Alice':f.point('2026-01-02T00:00:00Z')}});p,res=t.assess(fixture);ck('unknown_publication_marker',any(k.endswith(':published') for k in res['unknown_clocks']));ck('chronology_entails_eligibility',len(res['outcomes'])==1 and res['outcomes'][0]['status']=='selected_conditional')
for n,h in json.loads((H/'attempt-01/source-lock.json').read_text()).items():ck('preserved:'+n,sha(R/n)==h)
result={'status':'PASS','assertions':len(checks),'nonempty_leaves':leaves,'saved_families':len(saved),'correlated_order_assignments':assignments,'input_controls':len(controls),'scope':'Independent full outcome selection and finite correlated-order check; exact saved proof trees remain the continuum evidence.'}
for n,x in [('verification.json',result),('checks.json',checks),('controls.json',controls)]: (OUT/n).write_text(json.dumps(x,indent=2)+'\n')
(OUT/'run-manifest.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R)),'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'python':platform.python_version(),'environment':'CPU; GPU intentionally hidden','wall_seconds':time.monotonic()-start,'seeds':'N/A deterministic','data':'attempt-01 saved proofs and independent full-view comparator','plan':'docs/plans/accounting-source-time-intervals-20261027.md','result':str(OUT/'verification.json')},indent=2)+'\n');print(json.dumps(result))
