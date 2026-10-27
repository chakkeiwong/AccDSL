"""Explicit finite invariant declarations; native engines own every predicate."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'authored-state-invariants-20261026'))
import guards as g
import method_requirement_text_v2 as rules
core=g.core
PROFILE='BookStateInvariantText/1'
NL=chr(10)
j=rules.prior.json_token

class Invalid(ValueError):
 def __init__(self,reason,location=None):
  self.reason=str(reason)[:350];self.location=location;super().__init__(self.reason)

def need(ok,reason):
 if not ok:raise Invalid(reason)

def lines(source):
 need(type(source) is str,'source_type')
 need(len(source.encode())<=core.MAX_BYTES,'source_size_limit')
 need(not source.startswith(chr(65279)),'bom_unsupported')
 need(chr(13) not in source.replace(chr(13)+NL,''),'lone_cr')
 need(all(ord(c)>=32 or c in (chr(9),chr(13),NL) for c in source) and chr(127) not in source,'source_control')
 result=[];offset=0
 pieces=source.split(NL)
 for number,piece in enumerate(pieces,1):
  raw=piece+(NL if number<len(pieces) else '')
  text=raw.rstrip(chr(13)+NL)
  result.append((raw,text,{'line':number,'byte_start':offset,'byte_end':offset+len(text.encode()),'slice_sha256':sha256(text.encode()).hexdigest()}))
  offset+=len(raw.encode())
 need(sum(bool(row[1].strip()) for row in result)<=core.MAX_NODES,'declaration_limit')
 return result

def lower(source):
 location=None
 try:
  rows=lines(source);spec=None;state='header';seen=set();spans=[];current=None;manifest=None;rule_parent=None
  def unique(obj,key,value):need(key not in obj,'duplicate_declaration:'+key);obj[key]=value
  def declaration(r):return {'type':r.take('value'),'role':r.take('word'),'source_ref':r.string()}
  for raw,line,location in rows:
   if not line.strip():continue
   spans.append(deepcopy(location));need(state!='done','declaration_after_end')
   r=rules.Reader(rules.prior.tokens(line));word=r.take('word')
   if state=='header':
    need(word=='book_invariant' and r.string()==PROFILE,'invariant_source_profile')
    spec={'profile':r.string(),'globals':{},'collections':{},'residual_prerequisites':[]};state='body'
   elif state=='rules':
    if word=='input':unique(manifest['inputs'],r.string(),declaration(r))
    elif word=='guarded':
     rule={'id':r.string(),'on_false':r.take('word'),'on_unknown':r.take('word'),
      'guard_requires':r.take('value'),'requires':r.take('value'),'admission_refs':r.take('value'),
      'guard':r.expression(),'predicate':r.expression()}
     manifest['requirements'].append(rule)
    elif word=='required_known':
     need(not known_seen,'duplicate_required_known');manifest['required_known']=r.take('value');known_seen=True
    elif word in ('capability','residual'):
     manifest['capabilities' if word=='capability' else 'residual_prerequisites'].append(r.string())
    else:
     need(word=='end_rules' and known_seen,'incomplete_rules')
     g.totals.guarded.compile_manifest(manifest)
     if rule_parent=='each':current['definition']=manifest
     else:spec['definition']['assessment']=manifest
     state=rule_parent;manifest=None
   elif state=='collection':
    if word=='field':
     name=r.string();decl=declaration(r);kind=r.take('word');binding={'kind':kind}
     if kind=='field':binding['pointer']=r.string()
     unique(spec['definition']['snapshot']['collections'][collection]['fields'],name,decl)
     unique(spec['collections'][collection]['fields'],name,binding)
    else:need(word=='end_collection','collection_declaration');state='body'
   elif state in ('each','assessment'):
    if word=='begin_rules':
     need(('definition' not in current) if state=='each' else ('assessment' not in spec['definition']),'duplicate_rules')
     manifest={'profile':r.string(),'method_id':r.string(),'version':r.string(),'inputs':{},'requirements':[],
      'required_known':[],'capabilities':[],'residual_prerequisites':[]}
     need(manifest['profile']=='MethodRequirements/3','explicit_guard_profile');known_seen=False;rule_parent=state;state='rules'
    elif word=='row_binding':
     need(state=='each','row_binding_outside_each');name=r.string()
     unique(current['bindings'],name,{'scope':r.take('word'),'field':r.string()})
    else:
     need(word=='end_'+state,'block_declaration')
     if state=='each':
      need('definition' in current,'row_rules_required');current=None
     else:need('assessment' in spec['definition'],'assessment_rules_required')
     state='body'
   elif state=='body':
    if word=='context':unique(spec,'context',r.take('value'))
    elif word=='totals':
     unique(spec,'definition',{'profile':r.string(),'method_id':r.string(),'version':r.string(),'bindings':{},'residual_prerequisites':[]})
    elif word=='snapshot':
     need('definition' in spec,'totals_required')
     unique(spec['definition'],'snapshot',{'profile':r.string(),'method_id':r.string(),'version':r.string(),
      'inputs':{},'collections':{},'constraints':[],'residual_prerequisites':[]})
    elif word=='global':
     need('snapshot' in spec.get('definition',{}),'snapshot_required');name=r.string();decl=declaration(r)
     kind=r.take('word');binding={'kind':kind}
     if kind in ('balance','memory'):binding['account' if kind=='balance' else 'pointer']=r.string()
     unique(spec['definition']['snapshot']['inputs'],name,decl);unique(spec['globals'],name,binding)
    elif word=='collection':
     collection=r.string();kind=r.take('word');binding={'kind':kind,'fields':{}}
     if kind=='memory_map':binding['pointer']=r.string()
     unique(spec['collections'],collection,binding);unique(spec['definition']['snapshot']['collections'],collection,{'fields':{}});state='collection'
    elif word in ('unique','ordered','references','each'):
     ident=r.string();need(ident not in seen,'duplicate_constraint:'+ident);seen.add(ident)
     current={'id':ident,'op':word}
     if word in ('unique','ordered'):current.update(collection=r.string(),field=r.string())
     elif word=='references':current.update(source=r.string(),field=r.string(),target=r.string(),target_field=r.string())
     else:current.update(collection=r.string(),bindings={});state='each'
     spec['definition']['snapshot']['constraints'].append(current)
     if state!='each':current=None
    elif word=='begin_assessment':
     need('assessment' not in spec['definition'],'duplicate_assessment');state='assessment'
    elif word=='total_binding':
     name=r.string();kind=r.take('word');binding={'kind':kind}
     if kind=='global':binding['input']=r.string()
     elif kind=='sum':binding.update(collection=r.string(),field=r.string())
     else:raise Invalid('total_binding_kind')
     unique(spec['definition']['bindings'],name,binding)
    elif word in ('snapshot_residual','totals_residual','residual'):
     obj=spec['definition']['snapshot'] if word=='snapshot_residual' else spec['definition'] if word=='totals_residual' else spec
     obj['residual_prerequisites'].append(r.string())
    else:
     need(word=='end_invariant','unknown_declaration:'+word);g.validate(spec);state='done'
   r.finish()
  need(state=='done','incomplete_invariant:'+state)
  return {'profile':PROFILE,'status':'lowered_structural','invariant':spec,'invariant_sha256':g.digest(spec),
   'source_sha256':sha256(source.encode()).hexdigest(),'source_spans':spans,'executed':False,
   'source_admission':False,'accounting_admission':False}
 except Exception as exc:
  raise Invalid(getattr(exc,'reason',str(exc)),getattr(exc,'location',None) or location) from exc

def render_rules(d):
 # Reuse the original exchange renderer, removing exchange-only selection.
 exchange={'profile':rules.EXCHANGE,'definition':d,'selected_digest':g.digest(d),'values':{},'available_capabilities':[]}
 body=rules.render(exchange).rstrip(NL).split(NL)
 return ['begin_rules '+' '.join(j(d[k]) for k in ['profile','method_id','version'])+';']+body[1:-2]+['end_rules;']

def render(spec):
 g.validate(spec);d=spec['definition'];s=d['snapshot'];rows=[]
 def add(word,*values):rows.append(word+' '+' '.join(j(x) for x in values)+';')
 def decl(name,value):return ' '.join([j(name),j(value['type']),value['role'],j(value['source_ref'])])
 add('book_invariant',PROFILE,spec['profile']);add('context',spec['context'])
 for word,obj in [('totals',d),('snapshot',s)]:add(word,*[obj[k] for k in ['profile','method_id','version']])
 for name,value in s['inputs'].items():
  binding=spec['globals'][name];kind=binding['kind'];suffix=''
  if kind in ('balance','memory'):suffix=' '+j(binding['account' if kind=='balance' else 'pointer'])
  rows.append('global '+decl(name,value)+' '+kind+suffix+';')
 for name,value in s['collections'].items():
  binding=spec['collections'][name];kind=binding['kind'];suffix=' '+j(binding['pointer']) if kind=='memory_map' else ''
  rows.append('collection '+j(name)+' '+kind+suffix+';')
  for key,value in value['fields'].items():
   binding=spec['collections'][name]['fields'][key];kind=binding['kind'];suffix=' '+j(binding['pointer']) if kind=='field' else ''
   rows.append('field '+decl(key,value)+' '+kind+suffix+';')
  rows.append('end_collection;')
 for rule in s['constraints']:
  op=rule['op']
  if op in ('unique','ordered'):add(op,rule['id'],rule['collection'],rule['field'])
  elif op=='references':add(op,*[rule[k] for k in ['id','source','field','target','target_field']])
  else:
   add('each',rule['id'],rule['collection']);rows+=render_rules(rule['definition'])
   for key,b in rule['bindings'].items():rows.append('row_binding '+j(key)+' '+b['scope']+' '+j(b['field'])+';')
   rows.append('end_each;')
 rows.append('begin_assessment;');rows+=render_rules(d['assessment']);rows.append('end_assessment;')
 for key,b in d['bindings'].items():
  args=[b['input']] if b['kind']=='global' else [b['collection'],b['field']]
  rows.append('total_binding '+j(key)+' '+b['kind']+' '+' '.join(j(x) for x in args)+';')
 for word,obj in [('snapshot_residual',s),('totals_residual',d),('residual',spec)]:
  for value in obj['residual_prerequisites']:add(word,value)
 rows.append('end_invariant;');source=NL.join(rows)+NL
 need(core.canonical(lower(source)['invariant'])==core.canonical(spec),'render_roundtrip')
 return source
