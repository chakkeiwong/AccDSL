"""Finite exact partial-policy evidence over accepted source frontiers."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,platform,resource,subprocess,sys,time,traceback
import partial as p
H=Path(__file__).resolve().parent;R=H.parents[2];OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];controls=[];results=[];pins={}
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n')
def ck(n,a,b=True):
 checks.append({'name':n,'pass':a==b})
 if a!=b:raise AssertionError(n+': '+repr(a)[:200]+' != '+repr(b)[:200])
def reject(n,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError,OverflowError):controls.append(n);ck(n,True)
 else:ck(n,False)
try:
 ctx=p.Context();pins.update(ctx.methods.files)
 for folder in ['observation-map-binding-20261027','temporal-frontier-20261027']:
  q=H.parent/folder/'attempt-01/source-lock.json'
  for n,h in json.loads(q.read_text()).items():ck('accepted:'+n,sha(R/n),h);pins[n]=h
  for q in (H.parent/folder/'attempt-01').glob('*.json'):pins[str(q.relative_to(R))]=sha(q)
 for q in [H/'partial.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-partial-frontier-policy-20261027.md']:pins[str(q.relative_to(R))]=sha(q)
 save('source-lock.json',pins)
 for q in H.glob('*.py'):(OUT/q.name).write_bytes(q.read_bytes())
 fulls=json.loads((H.parent/'observation-map-binding-20261027/attempt-01/cases.json').read_text());fronts=json.loads((H.parent/'temporal-frontier-20261027/attempt-01/checkpoints.json').read_text())
 names=['baseline','different_actor','changed_message_labels','coarse_refined_family','equivalent_offset_dates'];diagnostic=len(sys.argv)>2
 if diagnostic:names=['baseline','coarse_refined_family']
 transitions=[];full_refs=[]
 for name in names:
  full=next(x['result'] for x in fulls if x['case']==name);fid=p.identity(full)
  matching=[x for x in fronts if x['expected_input']==full['family']['input_sha256'] and x.get('limit',4096)==4096];ck(name+':one_frontier',len(matching),1);sequence=matching[0]
  domain={'profile':'DeclaredTotalPayDrawDomain/1','full_comparison_sha256':fid,'keys':p.b.canonical(p.schema(full['rows'])),'actions':['pay','draw']};did=p.identity(domain);prior=None;statuses=[]
  chosen=sequence['checkpoints']
  if diagnostic:chosen=[chosen[i] for i in sorted(set([0,1,3,len(chosen)//2,len(chosen)-1]))]
  full_refs.append({'case':name,'full':full,'full_sha256':fid,'domain':domain,'domain_sha256':did})
  for b in chosen:
   eid=sequence['expected_input'];bid=p.identity(b);before=p.identity([b,full,domain])
   got=p.evaluate(b,bid,eid,full,fid,domain,did,ctx);ck(name+':pure:'+str(b['resolved']),p.identity([b,full,domain]),before)
   ck(name+':verify:'+str(b['resolved']),p.verify(got,p.identity(got),b,bid,eid,full,fid,domain,did,ctx))
   candidates={tuple(x) for x in got['candidates']}
   if prior is not None:ck(name+':monotone:'+str(b['resolved']),candidates<=prior)
   prior=candidates;statuses.append({'resolved':b['resolved'],'known_outcomes':len(b['outcomes']),'pending':len(b['pending']),'candidates':len(candidates),'status':got['status']})
   ck(name+':retained_pending:'+str(b['resolved']),got['pending'],b['pending']);ck(name+':retained_supports:'+str(b['resolved']),got['known_supports'],b['supports'])
   if b['resolved']==0:ck(name+':root_unconstrained',len(candidates),2**len(domain['keys']));ck(name+':root_not_feasible',got['status'],'unresolved_pending')
   if b['complete']:
    saved={p.z.t.prior.tuples(x) for x in full['policies']};want=p.extension_set(saved,p.schema(full['rows']));ck(name+':complete_total_extension',candidates,want)
    # Project each total rule back to its reachable complete history keys.
    projected=set();keys=p.schema(full['rows'])
    for c in candidates:
     assignments=dict(zip(keys,c));first={k:('draw' if assignments[('first',k)] else 'pay') for phase,k in keys if phase=='first'}
     active=[r for r in full['rows'] if first[p.b.policy.keys(r,'never')[0]]==r['a1']];reachable={p.b.policy.keys(r,'never')[1] for r in active if r['message2'] is not None};second={k:('draw' if assignments[('second',k)] else 'pay') for k in reachable};projected.add(p.b.policy.canonical(first,second))
    ck(name+':complete_reachable_projection',projected,saved)
   results.append({'case':name,'frontier':b,'result':got})
  transitions.append({'case':name,'states':statuses})
 coarse=next(x for x in transitions if x['case']=='coarse_refined_family')['states'];ck('partial_infeasibility_with_pending',any(x['status']=='conditionally_infeasible' and x['pending'] for x in coarse));ck('coarse_complete_stays_infeasible',coarse[-1]['status'],'conditionally_infeasible')
 baseline=next(x for x in transitions if x['case']=='baseline')['states'];ck('positive_candidates_stay_unresolved_until_complete',all(x['status']=='unresolved_pending' for x in baseline if x['pending']));ck('baseline_complete_feasible',baseline[-1]['status'],'conditionally_feasible')
 ref=full_refs[0];full=ref['full'];fid=ref['full_sha256'];d=ref['domain'];did=ref['domain_sha256'];case=next(x for x in results if x['case']=='baseline' and x['frontier']['resolved']>0);b=case['frontier'];bid=p.identity(b);eid=b['input_sha256'];got=case['result']
 def alteration(n,mut):
  bad=cp(got);mut(bad);reject(n,lambda:p.verify(bad,p.identity(bad),b,bid,eid,full,fid,d,did,ctx))
 alteration('claim_partial_feasible',lambda x:x.__setitem__('status','conditionally_feasible'))
 alteration('drop_pending',lambda x:x['pending'].clear())
 alteration('drop_pending_domains',lambda x:x['pending_domains'].clear())
 alteration('claim_complete',lambda x:x.__setitem__('complete',True))
 alteration('duplicate_candidate',lambda x:x['candidates'].append(cp(x['candidates'][0])))
 alteration('remove_candidate',lambda x:x['candidates'].pop())
 alteration('boolean_candidate_bit',lambda x:x['candidates'][0].__setitem__(0,False))
 alteration('wrong_domain_identity',lambda x:x.__setitem__('domain_sha256','0'*64))
 alteration('wrong_frontier_identity',lambda x:x.__setitem__('frontier_sha256','0'*64))
 alteration('wrong_declared_comparison',lambda x:x.__setitem__('full_comparison_sha256','0'*64))
 alteration('online_claim',lambda x:x.__setitem__('scope','online_inference'))
 alteration('added_field',lambda x:x.__setitem__('probability',1))
 for k in p.b.FLAGS:alteration('admission:'+k,lambda x,n=k:x.__setitem__(n,True))
 nontrivial=next(x for x in results if x['case']=='baseline' and x['result']['rejections']);nb=nontrivial['frontier'];ng=nontrivial['result']
 for n,mut in [('drop_rejection',lambda x:x['rejections'].pop()),('false_rejection_witness',lambda x:x['rejections'][0].__setitem__('row','unknown')),('drop_support',lambda x:x['known_supports'].clear())]:
  bad=cp(ng);mut(bad);reject(n,lambda q=bad:p.verify(q,p.identity(q),nb,p.identity(nb),eid,full,fid,d,did,ctx))
 changed=cp(d);changed['keys'].pop();reject('shrinking_policy_domain',lambda:p.evaluate(b,bid,eid,full,fid,changed,p.identity(changed),ctx))
 changed=cp(d);changed['keys'].reverse();reject('reordered_policy_domain',lambda:p.evaluate(b,bid,eid,full,fid,changed,p.identity(changed),ctx))
 changed=cp(full);changed['declaration']['actor']='Bob';reject('changed_actor_comparison',lambda:p.evaluate(b,bid,eid,changed,p.identity(changed),d,did,ctx))
 for n,h in pins.items():ck('preserved:'+n,sha(R/n),h)
 summary={'status':'PASS','diagnostic':diagnostic,'cases':len(names),'checkpoints':len(results),'assertions':len(checks),'controls':len(controls),'protected_files':len(pins),'scope':'Retrospective fixed total-policy domain; partial known constraints and pending source domains retained; no online domain discovery or actual admission.'}
except Exception:summary={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',results),('transitions.json',locals().get('transitions',[])),('full-references.json',locals().get('full_refs',[]))]:save(n,x)
 save('run-manifest.json',{'git':subprocess.run(['git','rev-parse','HEAD'],cwd=R,text=True,capture_output=True).stdout.strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT)+(' diagnostic' if len(sys.argv)>2 else ''),'environment':'existing Python '+platform.python_version()+'; CPU, GPU deliberately hidden','seeds':'N/A exact deterministic comparison','data_version':'source-lock.json','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-partial-frontier-policy-20261027.md','result':str(OUT/'verification.json')})
 print(json.dumps(summary),flush=True);sys.exit(summary['status']!='PASS')
