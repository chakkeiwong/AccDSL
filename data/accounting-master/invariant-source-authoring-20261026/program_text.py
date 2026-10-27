"""Inline invariant source lowered through the unchanged complete-program compiler."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re,sys
import invariant_text as invariant
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'common-program-authoring-20261026'))
import common_text as prior
import source_export
PROFILE='AuthoredCompanyText/2'
NL=chr(10)

def compile_text(source,resources):
 location=None
 try:
  rows=invariant.lines(source);nonblank=[i for i,(_,line,_) in enumerate(rows) if line.strip()]
  invariant.need(bool(nonblank),'header_required');first=nonblank[0]
  r=prior.syntax.Reader(rows[first][1]);invariant.need(r.take('word')=='company_program','header_required')
  invariant.need(r.string()==PROFILE,'source_profile');target,name=r.string(),r.string();r.finish()
  starts=[i for i,(_,line,_) in enumerate(rows) if line.strip()=='begin_invariant_source;']
  ends=[i for i,(_,line,_) in enumerate(rows) if line.strip()=='end_invariant_source;']
  invariant.need(len(starts)==len(ends)==1 and first<starts[0]<ends[0],'exact_invariant_source_block')
  start,end=starts[0],ends[0];nested=''.join(raw for raw,_,_ in rows[start+1:end])
  try:lowered=invariant.lower(nested)
  except invariant.Invalid as exc:
   loc=deepcopy(exc.location)
   if loc is not None:
    loc['line']+=start+1;loc['byte_start']+=rows[start+1][2]['byte_start'];loc['byte_end']+=rows[start+1][2]['byte_start']
   raise invariant.Invalid(exc.reason,loc) from exc
  h=lowered['invariant_sha256'];invariant.need(type(resources) is dict,'resource_population')
  invariant.need(h not in resources,'inline_invariant_supplied_as_resource')
  imports=deepcopy(resources);imports[h]=lowered['invariant']
  translated=[];line_map=[]
  for i,(raw,line,loc) in enumerate(rows):
   if i==first:out='company_program '+' '.join(prior.syntax.token(x) for x in [prior.PROFILE,target,name])+';'+NL
   elif i==start:out='select_invariant '+prior.syntax.token(lowered['invariant']['profile'])+' '+prior.syntax.token(h)+';'+NL
   elif start<i<=end:continue
   else:out=raw
   translated.append(out);line_map.append(deepcopy(loc))
  lowered_source=''.join(translated);result=prior.compile_text(lowered_source,imports)
  def restore(loc):
   if loc is None:return rows[first][2]
   number=loc.get('line',1);invariant.need(1<=number<=len(line_map),'generated_line_mapping')
   return deepcopy(line_map[number-1])
  if result['status']!='compiled_structural':
   raise invariant.Invalid(result['reason'],restore(result.get('location')))
  result=deepcopy(result);result['profile']=PROFILE
  result['source_sha256']=sha256(source.encode()).hexdigest()
  result['source_spans']=[deepcopy(loc) for _,line,loc in rows if line.strip()]
  for block in result['method_spans']:
   loc=next(loc for loc in result['source_spans'] if loc['line']==line_map[block['declarations'][0]['line']-1]['line'])
   delta=loc['byte_start']-block['byte_start'];block['byte_start']+=delta;block['byte_end']+=delta
   block['declarations']=[restore(loc) for loc in block['declarations']]
  offset=rows[start+1][2]['byte_start']
  result['invariant_source']={'source_sha256':lowered['source_sha256'],'invariant_sha256':h,
   'byte_start':offset,'byte_end':offset+len(nested.encode()),
   'declarations':[dict(loc,line=loc['line']+start+1,byte_start=loc['byte_start']+offset,byte_end=loc['byte_end']+offset) for loc in lowered['source_spans']]}
  result['resource_sha256']=sorted(resources)
  return result
 except Exception as exc:
  return {'profile':PROFILE,'status':'invalid','reason':getattr(exc,'reason',str(exc))[:350],
   'location':getattr(exc,'location',None) or location,'executed':False,'source_admission':False,'accounting_admission':False}

def from_program(body):
 source,resources=source_export.from_program(body)
 rows=source.splitlines(keepends=True);r=prior.syntax.Reader(rows[0].rstrip(NL));r.take('word');r.string()
 rows[0]='company_program '+' '.join(prior.syntax.token(x) for x in [PROFILE,r.string(),r.string()])+';'+NL
 index=next(i for i,line in enumerate(rows) if line.startswith('select_invariant '))
 invariant_source=invariant.render(body['state_invariant'])
 rows[index]='begin_invariant_source;'+NL+invariant_source+'end_invariant_source;'+NL
 h=prior.digest(body['state_invariant']);resources.pop(h)
 output=''.join(rows);compiled=compile_text(output,resources)
 invariant.need(compiled['status']=='compiled_structural','export_compile:'+compiled.get('reason',''))
 invariant.need(compiled['program']==body,'export_program_correspondence')
 return output,resources

def execute_text(source,resources):
 compiled=compile_text(source,resources)
 return prior.TARGETS[compiled['program']['profile']].run(compiled['program']) if compiled['status']=='compiled_structural' else compiled
