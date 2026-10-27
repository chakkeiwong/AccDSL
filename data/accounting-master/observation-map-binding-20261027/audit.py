"""Saved independent replay plus added exact source-time and tag boundaries."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,platform,subprocess,time
import binding as m
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=H/'audit-01';OUT.mkdir(exist_ok=False);start=time.monotonic();checks=[];extra=[]
fx=m.load('binding_audit_fixtures',H/'fixtures.py');expected=m.load('binding_audit_expected',H/'expected.py');tf=m.load('binding_audit_temporal_fixtures',m.f.T/'fixtures.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):checks.append({'name':n,'pass':bool(v)});assert v,n
e=m.Evidence();saved=json.loads((H/'attempt-01/cases.json').read_text());base=saved[0]['result'];distinct={}
for case in saved:
 r=case['result'];name=case['case'];status,bound,rows,kernel=m.prepare(r['family'],r['binding']['family_sha256'],r['declaration'],r['binding']['declaration_sha256'],e)
 ck(name+':saved_binding',status==r['status'] and bound==r['binding'] and rows==r['rows'] and kernel==r['kernel'])
 if status=='complete_conditional':
  raw=expected.rows(r['family'],r['declaration'],e);policies,_=m.oracle.solve(raw,('pay','draw'),('pay','draw'),'never');ck(name+':full_saved_policy',r['policies']==m.canonical(sorted(policies,key=repr)));distinct[m.identity(kernel)]=r['count']
 else:ck(name+':saved_unknown_not_zero',r['policies'] is None and r['count'] is None)
# A later-arriving correction remains in the original full registry but cannot replace the selected old view.
old=next(c for c in tf.oldcases.suite() if c['name']=='future_correction_old_view');fixture=tf.convert(old['fixture']);wire=m.f.wire(fixture);b=m.f.evaluate(wire,m.identity(wire),e)
d=fx.declaration(b,e);r=m.evaluate(b,m.identity(b),d,m.identity(d),e,base,m.identity(base));ck('future_correction_retained',len(b['input']['registry'])==3);ck('future_correction_old_policies',r['reused'] and r['count']==4 and r['binding_changed']);extra.append({'case':'future_correction_old_view','result':r})
# Clock spelling preserves numerical meaning but the declaration binding still changes.
d=fx.declaration(base['family'],e,reveal='first');key=d['maps'][0]['tag']['observation_sha256'];o=d['tag_observations'].pop(key);o['at']['value']='2026-01-02T08:00:00+08:00';new=m.identity(o);d['tag_observations'][new]=o;d['maps'][0]['tag']['observation_sha256']=new;d['trusted_tag_observations']=[new]
r=m.evaluate(base['family'],m.identity(base['family']),d,m.identity(d),e);ck('tag_exact_offset_boundary',r['status']=='complete_conditional' and r['count']==4);extra.append({'case':'tag_exact_offset_boundary','result':r})
# Distinct tags that look like a JSON composite are still encoded as opaque tokens, never parsed into hidden fields.
d=fx.declaration(base['family'],e);d['maps'][0]['first'][0]['token']='["channel", "secret"]';r=m.evaluate(base['family'],m.identity(base['family']),d,m.identity(d),e,base,m.identity(base));ck('opaque_token_does_not_parse_metadata',r['status']=='complete_conditional' and r['count']==4 and not r['reused']);extra.append({'case':'opaque_token','result':r})
# Changes to late-only instructions cannot alter stage-one messages.
d=fx.declaration(base['family'],e);before=m.prepare(base['family'],m.identity(base['family']),d,m.identity(d),e)[2];d['maps'][0]['second'][0]['token']='renamed_late_message';r=m.evaluate(base['family'],m.identity(base['family']),d,m.identity(d),e,base,m.identity(base));ck('second_stage_change_keeps_first_history',[x['message1'] for x in before]==[x['message1'] for x in r['rows']]);ck('second_labels_invalidate_payload',not r['reused'] and r['count']==4);extra.append({'case':'second_message_relabel','result':r})
for n,h in json.loads((H/'attempt-01/source-lock.json').read_text()).items():ck('source_preserved:'+n,sha(R/n)==h)
for n,h in e.dependencies.items():ck('accepted_dependency:'+n,sha(R/n)==h)
result={'status':'PASS','saved_cases':len(saved),'distinct_numerical_kernels':len(distinct),'additional_cases':len(extra),'assertions':len(checks),'scope':'Independent saved full-policy replay and exact late/source/token boundaries; no empirical actor knowledge.'}
for n,x in [('verification.json',result),('checks.json',checks),('cases.json',extra)]: (OUT/n).write_text(json.dumps(x,indent=2)+'\n')
(OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R)),'environment':'Python '+platform.python_version()+'; CPU; GPU intentionally hidden','seeds':'N/A deterministic','data':'saved bound declarations/policies and protected source-time fixtures','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-observation-map-binding-20261027.md','result':str(OUT/'verification.json'),'artifacts':str(OUT)},indent=2)+'\n');print(json.dumps(result))
