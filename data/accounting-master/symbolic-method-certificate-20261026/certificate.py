"""Selected quantified affine/Boolean certificate; unsupported syntax refuses."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as F
import sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'data/accounting-master/guarded-memory-runtime-20261026'))
import bridge as b
rt=b.rt
class Unsupported(ValueError):pass
def need(p,msg):
 if not p:raise ValueError(msg)
def template(chart):
 need(chart in ('alpha','beta'),'chart_domain')
 body,m=b.build(chart=chart);money=rt.engine.money_type(body['opening'])
 parameters={'I1':money,'I2':money,'R':money,'mode':b.TEXT,'right':b.BOOL}
 for key,entry in body['registry']['entries'].items():
  for row in entry['method']['preconditions']['manifest']['requirements']:
   if row['id']=='selected_coupon':row['predicate']['right']={'op':'parameter','id':'I'+key[-1],'type':money}
   if row['id']=='selected_receipt':row['predicate']['right']={'op':'parameter','id':'R','type':money}
   if row['id']=='mode':row['predicate']['right']={'op':'parameter','id':'mode','type':b.TEXT}
  entry['method_sha256']='recompute_after_literalization'
 body['opening']['memory']['mode']={'parameter_value':'mode'}
 body['opening']['memory']['right']={'parameter_value':'right'}
 for command in body['commands']:
  k=command['method_key']
  if k.startswith('accrue') or k=='receipt2':command['event']['inputs']['amount']['value']['value']={'parameter_value':'R' if k=='receipt2' else 'I'+k[-1]}
 return {'profile':'SelectedGuardedTemplate/1','chart':chart,'parameters':parameters,'body':body,'mapping':m}

def literalize(T,mode,right,r1,r2,receipt,a1,a2):
 need(type(right)==bool and F(receipt) in (6,7) and a1 in ('pay','draw') and a2 in ('pay','draw'),'parameter_domain')
 values={'I1':b.fmt(b.coupon(mode,r1)),'I2':b.fmt(b.coupon(mode,r2)),'R':b.fmt(receipt),'mode':mode,'right':right}
 def walk(v):
  if isinstance(v,dict):
   if set(v)=={'parameter_value'}:return values[v['parameter_value']]
   if v.get('op')=='parameter':
    need(set(v)=={'op','id','type'} and v['type']==T['parameters'][v['id']],'parameter_type')
    return {'op':'const','type':cp(v['type']),'value':values[v['id']]}
   return {k:walk(x) for k,x in v.items()}
  if isinstance(v,list):return [walk(x) for x in v]
  return v
 body=walk(T['body'])
 for index,action in [(1,a1),(5,a2)]:
  key=action+('1' if index==1 else '2');body['commands'][index]['method_key']=key;body['commands'][index]['event']['id']=key
 for entry in body['registry']['entries'].values():entry['method_sha256']=rt.digest(entry['method'])
 return body

# Value normal form: (kind, mathematical content), retaining types separately.
def lin(coeff=None,c=0):return ('linear',tuple(sorted((k,str(F(v))) for k,v in (coeff or {}).items() if F(v))),str(F(c)))
def add(a,b,sign=1):
 need(a[0]==b[0]=='linear','not_affine');d={k:F(v) for k,v in a[1]}
 for k,v in b[1]:d[k]=d.get(k,F(0))+sign*F(v)
 return lin(d,F(a[2])+sign*F(b[2]))
def symbol(typ,name):return lin({name:1}) if typ['kind']=='rational' else ('symbol',typ['kind'],name)
def constant(typ,v):
 if typ['kind']=='rational':rt.core.scalar(v,'rational');return lin(c=F(v))
 rt.core.scalar(v,typ['kind']);return ('literal',typ['kind'],v)
def binding_name(v):
 kind=v['kind']
 if kind=='memory':need(set(v)=={'kind','pointer'},'memory_binding');return 'memory'+v['pointer']
 if kind=='account':need(set(v)=={'kind','role'},'account_binding');return 'account/'+v['role']
 if kind=='event':need(set(v)=={'kind','name'},'event_binding');return 'event/'+v['name']
 raise Unsupported('binding:'+str(kind))
def expr(node,decls,bindings,params):
 op=node.get('op')
 if op=='ref':
  need(set(node)=={'op','id'} and node['id'] in decls and node['id'] in bindings,'ref')
  typ=decls[node['id']]['type'];return typ,symbol(typ,binding_name(bindings[node['id']]))
 if op=='const':
  need(set(node)=={'op','type','value'},'const');return node['type'],constant(node['type'],node['value'])
 if op=='parameter':
  need(set(node)=={'op','type','id'} and params.get(node['id'])==node['type'],'parameter');return node['type'],symbol(node['type'],'parameter/'+node['id'])
 if op in ('add','sub','eq','le','lt'):
  need(set(node)=={'op','left','right'},'binary')
  ta,a=expr(node['left'],decls,bindings,params);tb,z=expr(node['right'],decls,bindings,params);need(ta==tb,'type_mismatch')
  if op in ('add','sub'):need(ta['kind']=='rational','arithmetic_type');return ta,add(a,z,1 if op=='add' else -1)
  if op in ('le','lt'):need(ta['kind'] in ('date','rational'),'order_type')
  return b.BOOL,(op,add(a,z,-1)) if ta['kind']=='rational' else (op,a,z)
 if op in ('all','any'):
  need(set(node)=={'op','args'} and node['args'],'boolean_args');items=[expr(x,decls,bindings,params) for x in node['args']];need(all(t==b.BOOL for t,_ in items),'boolean_types')
  return b.BOOL,(op,tuple(sorted((v for _,v in items),key=repr)))
 if op=='not':
  need(set(node)=={'op','arg'},'not');typ,v=expr(node['arg'],decls,bindings,params);need(typ==b.BOOL,'not_type');return b.BOOL,('not',v)
 raise Unsupported('operator:'+str(op))

def method_form(key,entry,T):
 m=entry['method'];money=rt.engine.money_type(T['body']['opening']);params=T['parameters'];out={'pre':{},'post':{},'postings':{},'flows':{},'memory':{}}
 need(m['account_map']==T['mapping'] and len(set(T['mapping'].values()))==len(T['mapping']),'account_mapping')
 need(entry['account_classes']==b.CLASSES,'account_classes');need(entry['clock']=={'kind':'direct_event_date'},'clock');need(entry['metadata_bindings']=={'event_date':'date'},'metadata')
 for part,dest in [('preconditions','pre'),('postconditions','post')]:
  manifest=m[part]['manifest'];decl=manifest['inputs'];bindings=m[part]['bindings']
  need(set(decl)==set(bindings),'binding_population')
  need(manifest['required_known']==[] and manifest['capabilities']==[],'capabilities')
  for row in manifest['requirements']:
   need(row['id'] not in out[dest],'duplicate_guard')
   gt,g=expr(row['guard'],decl,bindings,params);pt,p=expr(row['predicate'],decl,bindings,params)
   need(gt==pt==b.BOOL and g==('literal','boolean',True),'guard_activation')
   need(row['guard_requires']==[] and row['admission_refs']==[] and row['on_false']=='invalid' and row['on_unknown']=='unresolved','condition_policy')
   need(set(row['requires'])==refs(row['predicate']),'condition_dependencies')
   out[dest][row['id']]=p
 amount=m['monetary'];definition=amount['definition'];decl=definition['inputs'];bindings=amount['bindings']
 need(definition['calculations']==[],'unsupported_calculations');need(definition['accounts']=={k:money for k in b.CLASSES} and definition['cash_account']=='cash','account_types')
 for row in definition['postings']:
  typ,val=expr(row['expression'],decl,bindings,params);need(typ==money,'posting_type');need(row['account'] not in out['postings'],'duplicate_posting');need(set(row['requires'])==refs(row['expression']),'posting_dependencies')
  out['postings'][row['account']]=val
 for row in definition['flows']:
  typ,val=expr(row['expression'],decl,bindings,params);need(typ==money,'flow_type');need(row['id'] not in out['flows'],'duplicate_flow');need(set(row['requires'])==refs(row['expression']),'flow_dependencies')
  out['flows'][row['id']]=(row['activity'],row['origin'],val)
 mem=m['memory'];md=mem['definition'];need(md['state_schema']==T['body']['opening']['memory_schema'],'memory_schema')
 for row in md['operations']:
  need(row['op']=='replace' and len(row['path'])==1,'memory_operation');field=row['path'][0];need(field not in out['memory'],'duplicate_memory')
  val=row['value'];target=T['body']['opening']['memory_types']['/'+field]
  if val['kind']=='literal':out['memory'][field]=constant(target,val['value'])
  elif val['kind']=='read':
   need(val['source']=='inputs','memory_read_source');source=mem['input_bindings'][val['pointer'][1:]];need(source['kind']=='monetary_input','memory_read_kind');name=source['name'];need(decl[name]['type']==target,'memory_type')
   out['memory'][field]=symbol(target,binding_name(bindings[name]))
  else:raise Unsupported('memory value')
 return out

def refs(n):
 if not isinstance(n,dict):return set()
 if n.get('op')=='ref':return {n['id']}
 return set().union(*(refs(x) for x in n.values() if isinstance(x,dict)),*(refs(z) for x in n.values() if isinstance(x,list) for z in x))

def check(T,expected):
 need(T['profile']=='SelectedGuardedTemplate/1','template_profile');body=T['body'];need(set(body['registry']['entries'])==set(expected),'method_population')
 coverage(T)
 forms={k:method_form(k,e,T) for k,e in body['registry']['entries'].items()}
 for k in expected:need(forms[k]==expected[k],'certificate_mismatch:'+k)
 return forms


def parameter_paths(value,path=()):
 out={}
 if isinstance(value,dict):
  if value.get('op')=='parameter':out[path]=('expression',value['id'],value['type'])
  elif 'parameter_value' in value:out[path]=('value',value['parameter_value'])
  else:
   for k,x in value.items():out.update(parameter_paths(x,path+(k,)))
 elif isinstance(value,list):
  for i,x in enumerate(value):out.update(parameter_paths(x,path+(i,)))
 return out

def shell(T):
 """Mask exactly the semantic leaves independently compared by method_form."""
 out=cp(T)
 for entry in out['body']['registry']['entries'].values():
  m=entry['method']
  for part in ('preconditions','postconditions'):
   for row in m[part]['manifest']['requirements']:
    row['guard']='CHECKED_GUARD';row['predicate']='CHECKED_PREDICATE'
  for rows in ('postings','flows'):
   for row in m['monetary']['definition'][rows]:row['expression']='CHECKED_EXPRESSION'
  for row in m['memory']['definition']['operations']:row['value']='CHECKED_MEMORY_VALUE'
 return out

def coverage(T):
 from expected_forms import bindings as expected_bindings
 need(set(T)=={'profile','chart','parameters','body','mapping'},'template_fields')
 need(T['chart'] in ('alpha','beta'),'chart_domain')
 baseline=template(T['chart'])
 need(T['parameters']==baseline['parameters'],'parameter_population_and_types')
 need(parameter_paths(T)==parameter_paths(baseline),'parameter_occurrences')
 need(shell(T)==shell(baseline),'unmatched_template_metadata')
 for key,entry in T['body']['registry']['entries'].items():
  m=entry['method']
  for part,target in [('preconditions','pre'),('postconditions','post'),('monetary','monetary')]:
   need(m[part]['bindings']==expected_bindings(key,target),'independent_bindings:'+key+'/'+part)
  for part in ('preconditions','postconditions'):
   man=m[part]['manifest'];used=set().union(*(refs(r['predicate']) for r in man['requirements']))
   need(set(man['inputs'])==used,'no_unused_condition_input')
  definition=m['monetary']['definition'];used=set().union(*(refs(r['expression']) for r in definition['postings']+definition['flows']))
  need(set(definition['inputs'])==set(m['monetary']['bindings'])==used,'no_unused_monetary_input')
 return True
