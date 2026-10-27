"""Conditional exact source-clock family over the existing eight policy problems."""
from pathlib import Path
from copy import deepcopy
from datetime import date,timedelta
from fractions import Fraction as Q
import sys,re
import difference as dc
import proofcheck as pc
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'certified-source-views-20261026'))
import views as prior
PROFILE='ExactSourceTimeViews/1';SLOTS=prior.SLOTS;FLAGS=prior.FLAGS
identity=prior.identity;instant=prior.instant;need=prior.need;fields=prior.fields
MAX=instant('9999-12-31T23:59:59.999999999999999999Z')

def edge(u,v,b,strict=False):return {'u':u,'v':v,'bound':str(Q(b)),'strict':strict}
def component(r):return identity({k:r[k] for k in ['slot','information_id','source_sha256','payload','effective_at','disposition']})
def bounds(clock):
 kind=clock.get('kind')
 if kind=='unknown':fields(clock,['kind','reason'],'unknown_clock');need(isinstance(clock['reason'],str) and clock['reason'],'unknown_reason');return None
 if kind=='point':fields(clock,['kind','value'],'point_clock');q=instant(clock['value']);return q,q,False
 if kind=='interval':
  fields(clock,['kind','start','end'],'interval_clock');lo,hi=instant(clock['start']),instant(clock['end']);need(lo<hi,'positive_half_open_interval');return lo,hi,True
 if kind=='day_utc':
  fields(clock,['kind','date'],'day_clock');s=clock['date'];need(isinstance(s,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',s),'canonical_day');d=date.fromisoformat(s);n=d+timedelta(days=1);return instant(s+'T00:00:00Z'),instant(n.isoformat()+'T00:00:00Z'),True
 raise ValueError('unsupported_clock')

def prepare(request,registry,sources,observations,trusted):
 fields(request,['profile','actor','decision_at','system_asof','effective_at'],'request_fields');need(request['profile']==PROFILE and isinstance(request['actor'],str) and request['actor'],'request_profile_actor')
 cutoff={k:instant(request[k]) for k in ['decision_at','system_asof','effective_at']};need(type(trusted) is frozenset,'caller_trust_set')
 need(type(registry) is dict and type(sources) is dict and type(observations) is dict,'registry_maps');records={h:r for h,r in registry.items() if r.get('slot') in SLOTS};need(0<len(records)<=6,'one_to_six_revisions')
 variables=[];constraints=[];clockinfo={};guards={};ancestry={}
 def addclock(name,clock,trusted_clock):
  b=bounds(clock);variables.append(name);constraints.extend([edge(name,'zero',0),edge('zero',name,MAX)])
  if b is not None and trusted_clock:
   lo,hi,strict=b;constraints.extend([edge(name,'zero',-lo),edge('zero',name,hi,strict)])
  clockinfo[name]={'original':deepcopy(clock),'trusted':trusted_clock,'unknown':b is None or not trusted_clock}
 def observed(r,h,event,ref,actor=None):
  if ref.get('status')=='unknown':
   fields(ref,['status','reason'],'unknown_reference');need(isinstance(ref['reason'],str) and ref['reason'],'reference_reason');addclock(h+':'+event,{'kind':'unknown','reason':ref['reason']},False);return
  fields(ref,['status','observation_sha256'],'observed_reference');need(ref['status']=='observed_synthetic','reference_status');digest=ref['observation_sha256'];need(digest in observations,'missing_observation');o=observations[digest]
  fields(o,['profile','component_sha256','event','subject','channel','clock','provenance'],'observation_fields')
  need(identity(o)==digest and o['profile']=='SyntheticExactClock/1','observation_identity');need(o['component_sha256']==component(r) and o['event']==event,'observation_binding');need(o['provenance']=='authored_test_clock_not_historical_evidence','observation_provenance')
  need(o['subject']==(actor if event=='accessed' else 'source_system'),'observation_subject')
  need(o['channel'] in ['public','internal','public_document','private_delivery'],'observation_channel')
  if event=='published':need(o['channel'] in ['public','internal'],'publication_channel')
  elif event=='accessed':need(o['channel']==r['access'][request['actor']]['route'],'access_channel')
  else:need(o['channel']=='internal','system_channel')
  addclock(h+':'+event,o['clock'],digest in trusted)
 for h,r in sorted(records.items()):
  fields(r,['profile','slot','information_id','source_sha256','payload','effective_at','disposition','supersedes','access','events'],'record_fields');need(identity(r)==h and r['profile']=='SyntheticScenarioSource/2','record_identity');need(r['information_id']==r['slot'],'information_identity')
  need(r['source_sha256'] in sources and prior.iv.source_identity(sources[r['source_sha256']])==r['source_sha256'],'source_identity');need(r['disposition'] in ['assertion','retraction'],'disposition')
  if r['disposition']=='retraction':need(r['payload'] is None,'retracted_payload')
  elif r['slot']=='financial_family':fields(r['payload'],['receipt','family'],'financial_payload');need(type(r['payload']['receipt']) is int and r['payload']['receipt'] in [6,7] and r['payload']['family'] in ['mixed','committed'],'financial_scope')
  else:fields(r['payload'],['view'],'observation_payload');need(r['payload']['view'] in ['coarse','refined'],'observation_scope')
  fields(r['events'],['authored','published','ingested','accepted'],'event_coverage');need(type(r['access']) is dict,'actor_access_map')
  access=r['access'].get(request['actor']);need(access is not None,'actor_route_required');fields(access,['route','observation'],'access_fields');need(access['route'] in ['public_document','private_delivery'],'explicit_access_route')
  for event,ref in r['events'].items():observed(r,h,event,ref)
  observed(r,h,'accessed',access['observation'],request['actor']);addclock(h+':effective',r['effective_at'],True)
  for a,b in [('authored','ingested'),('ingested','accepted'),('authored','accessed'),('authored','published')]:constraints.append(edge(h+':'+b,h+':'+a,0))
  if access['route']=='public_document':
   ref=r['events']['published']
   if ref['status']=='observed_synthetic':need(observations[ref['observation_sha256']]['channel']=='public','public_release_context_required')
   constraints.append(edge(h+':accessed',h+':published',0))
  required=[('authored','decision_at'),('accessed','decision_at'),('authored','system_asof'),('ingested','system_asof'),('accepted','system_asof'),('effective','effective_at')]
  if access['route']=='public_document':required.insert(1,('published','decision_at'))
  guards[h]=[edge('zero',h+':'+e,cutoff[c]) for e,c in required]
 for h,r in records.items():
  seen=[];current=r['supersedes'];child=h
  while current is not None:
   need(current in records and current not in seen and current!=h,'missing_or_cyclic_ancestry');p=records[current];need(p['slot']==r['slot'] and p['information_id']==r['information_id'],'replacement_subject');seen.append(current)
   for event in ['authored','ingested','accepted','accessed']:
    constraints.append(edge(child+':'+event,current+':'+event,0))
   if records[child]['events']['published']['status']=='observed_synthetic' and p['events']['published']['status']=='observed_synthetic':constraints.append(edge(child+':published',current+':published',0))
   child=current;current=p['supersedes']
  ancestry[h]=seen
 return {'request':deepcopy(request),'records':records,'variables':variables,'constraints':constraints,'clocks':clockinfo,'guards':guards,'ancestry':ancestry}

def outcome(p,eligible):
 live=set(h for h,v in eligible.items() if v);anc=set().union(*(set(p['ancestry'][h]) for h in live)) if live else set();heads=live-anc;selected={};issues=[]
 for slot in SLOTS:
  match=sorted(h for h in heads if p['records'][h]['slot']==slot)
  if len(match)!=1:issues.append({'slot':slot,'reason':'missing_or_conflicting_head','heads':match});continue
  h=match[0]
  if p['records'][h]['disposition']=='retraction':issues.append({'slot':slot,'reason':'retracted','head':h});continue
  if any(a not in live for a in p['ancestry'][h]):issues.append({'slot':slot,'reason':'ancestor_unavailable','head':h});continue
  selected[slot]=h
 if issues:return {'status':'unresolved','issues':issues}
 scenario={**p['records'][selected['financial_family']]['payload'],**p['records'][selected['observation_scheme']]['payload']}
 return {'status':'selected_conditional','heads':selected,'scenario':scenario}

class Budget(ValueError):pass

def enumerate_views(p,max_nodes=4096):
 need(type(max_nodes) is int and 1<=max_nodes<=4096,'node_budget');order=sorted(p['records']);count=0;out={}
 def node(edges,i,eligible):
  nonlocal count
  count+=1
  if count>max_nodes:raise Budget('node_budget_exhausted')
  proof=dc.solve(p['variables'],edges);pc.verify(p['variables'],edges,proof)
  if proof['kind']=='empty':return {'proof':proof}
  if i==len(order):
   o=outcome(p,eligible);out[identity(o)]=o;return {'proof':proof,'outcome':o,'eligible':dict(eligible)}
  h=order[i];gs=p['guards'][h];children=[node(edges+gs,i+1,{**eligible,h:True})]
  for k,g in enumerate(gs):children.append(node(edges+gs[:k]+[dc.opposite(g)],i+1,{**eligible,h:False}))
  return {'proof':proof,'record':h,'children':children}
 try:
  tree=node(p['constraints'],0,{})
  return {**FLAGS,'status':'complete_family' if out else 'inconsistent_clocks','tree':tree,'outcomes':[out[k] for k in sorted(out)],'nodes':count,'unknown_clocks':sorted(k for k,v in p['clocks'].items() if v['unknown']),'certainty':'one_view' if len(out)==1 else 'multiple_views' if out else 'no_admissible_clock_assignment'}
 except Budget:return {**FLAGS,'status':'unresolved_budget','nodes':count-1,'max_nodes':max_nodes,'outcomes':[],'complete':False,'reason':'Unexplored temporal cells remain; no complete view family is returned.'}

def verify_tree(p,tree):
 order=sorted(p['records']);out={};count=0
 def visit(t,edges,i,eligible):
  nonlocal count
  count+=1;kind=pc.verify(p['variables'],edges,t['proof'])
  if kind=='empty':need(set(t)=={'proof'},'empty_node_fields');return
  if i==len(order):
   need(set(t)=={'proof','outcome','eligible'},'leaf_fields');need(t['eligible']==eligible,'leaf_eligibility');want=outcome(p,eligible);need(want==t['outcome'],'leaf_outcome');out[identity(want)]=want;return
  need(set(t)=={'proof','record','children'} and t['record']==order[i],'branch_fields');h=order[i];gs=p['guards'][h];need(len(t['children'])==len(gs)+1,'complete_complement_partition')
  visit(t['children'][0],edges+gs,i+1,{**eligible,h:True})
  for k,g in enumerate(gs):
   # The checker reconstructs the strict complement directly.
   neg=edge(g['v'],g['u'],-Q(g['bound']),not g['strict']);visit(t['children'][k+1],edges+gs[:k]+[neg],i+1,{**eligible,h:False})
 visit(tree,p['constraints'],0,{})
 return [out[k] for k in sorted(out)],count

def assess(f,max_nodes=4096):
 try:p=prepare(**{k:f[k] for k in ['request','registry','sources','observations','trusted']});return p,enumerate_views(p,max_nodes)
 except (ValueError,KeyError,TypeError,OverflowError) as e:return None,{**FLAGS,'status':'invalid','reason':str(e)}
