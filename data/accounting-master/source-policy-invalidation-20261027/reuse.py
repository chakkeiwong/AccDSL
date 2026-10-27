"""Explicit dependency reuse over the preserved conditional source selector."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'certified-source-views-20261026'))
import views as v
NAMES=('evidence','financial','observation','policy','financial_source','observation_source','actor_binding')

def content(raw):return sha256(raw).hexdigest()
def need(ok,msg):v.need(ok,msg)
class Evidence:
 def __init__(self,raw,expected):
  need(set(raw)==set(expected)=={'rows','comparisons','observations','policy','constraint'},'external_evidence_population')
  for name,b in raw.items():need(type(b) is bytes and content(b)==expected[name],'external_content_identity:'+name)
  self.ids=dict(expected);self.rows=json.loads(raw['rows']);self.comparisons=json.loads(raw['comparisons'])
  ids=[r['row_id'] for r in self.rows];need(len(set(ids))==len(ids)==3884,'unique_expected_rows')
  need(len(self.comparisons)==8 and {(x['receipt'],x['family'],x['view']) for x in self.comparisons}=={(r,f,w) for r in (6,7) for f in ('mixed','committed') for w in ('coarse','refined')},'complete_eight_problem_reference')
  need(content(Path(v.policy.__file__).read_bytes())==expected['policy'] and content(Path(v.independent.__file__).read_bytes())==expected['constraint'],'executed_method_identity')
  self.audit_identity=v.identity(self.ids)

def nodes(selection,evidence):
 b=selection['binding'];s=b['scenario'];ids={};spec={}
 def node(name,parents,payload):
  spec[name]={'parents':{p:ids[p] for p in parents},'payload':payload};ids[name]=v.identity(spec[name])
 node('evidence',[],evidence.ids)
 node('financial',['evidence'],{k:s[k] for k in ['receipt','family']})
 node('observation',['financial'],{'view':s['view']})
 node('policy',['observation'],{'meaning':'complete_reachable_robust_policy_set'})
 for slot,node_name,semantic in [('financial_family','financial_source','financial'),('observation_scheme','observation_source','observation')]:
  node(node_name,[semantic],{'head':b['heads'][slot],'ancestry':b['ancestry'][slot]})
 node('actor_binding',['policy','financial_source','observation_source'],{'request':b['request'],'scope':b['scope']})
 return ids,spec

def evaluate(fixture,evidence,previous=None,trusted_prior_sha256=None):
 selection=v.select(**{k:fixture[k] for k in ['request','registry','sources','observations','trusted']})
 if selection['status']!='selected_conditional':return {**selection,'cache_reused':False}
 ids,spec=nodes(selection,evidence);prior_ids={}
 if previous is not None:
  need(isinstance(trusted_prior_sha256,str) and v.identity(previous)==trusted_prior_sha256,'external_prior_identity')
  need(previous.get('status')=='complete_conditional' and previous['evidence_identity']==evidence.audit_identity,'prior_evidence_scope')
  original={'binding':previous['binding']};expected_ids,expected_spec=nodes(original,evidence)
  need(previous['node_ids']==expected_ids and previous['node_specs']==expected_spec,'prior_dependency_graph')
  need(previous['policy_payload_sha256']==v.identity(previous['numerical']),'prior_payload_identity')
  prior_ids=previous['node_ids']
 changed=[n for n in NAMES if prior_ids.get(n)!=ids[n]];unchanged=[n for n in NAMES if n not in changed]
 if previous is not None and ids['policy']==prior_ids['policy']:
  numerical=deepcopy(previous['numerical']);computation='reused_external_bound_complete_set'
 else:
  result=v.policy_result(selection,evidence.rows,evidence.comparisons,evidence.ids)
  numerical={k:result[k] for k in ['scenario','policy_set','count','row_ids','policy_meaning']};computation='cold_complete_two_formulation_comparison'
 return {**v.FLAGS,'status':'complete_conditional','binding':selection['binding'],'evidence_identity':evidence.audit_identity,'node_ids':ids,'node_specs':spec,'numerical':numerical,'policy_payload_sha256':v.identity(numerical),'changed_nodes':changed,'unchanged_nodes':unchanged,'computation':computation,'cache_reused':computation.startswith('reused'),'scope':'trusted_local_completed_results_only; no authentication_or_durability'}
