"""Bounded source composition over retained authored-program semantics."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,re,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'authored-event-contract-20261026'))
import contract_runner as contracted
import declared_company_text_v2 as syntax
guarded=contracted.contract.prior
methods=contracted.methods;method_text=methods.frontend
core=contracted.core;base=contracted.base;digest=core.digest
PROFILE='AuthoredCompanyText/1'
TARGETS={contracted.PROFILE:contracted,guarded.PROFILE:guarded}
IMPORTS=('opening','schemas','mapping','memory_definition')
NL=chr(10)

class Invalid(ValueError):
 def __init__(self,reason,location=None,stage=None):
  self.reason=str(reason)[:350];self.location=location;self.stage=stage
  super().__init__(self.reason)

def need(ok,reason):
 if not ok:raise Invalid(reason)

def command_source(lines):
 header=['company_program '+syntax.token(syntax.PROFILE)+' "bounded-command";']
 header+=['import_'+k+' "'+'0'*64+'";' for k in syntax.IMPORTS]
 return NL.join(header+lines+['end_program;'])+NL

def compile_text(source,resources):
 location=None;stage='source'
 try:
  need(type(source) is str,'source_type')
  need(all(ord(c)>=32 or c in [chr(9),chr(13),NL] for c in source) and chr(127) not in source,'source_control')
  syntax.lexical.source_text(source);syntax.protected()
  need(type(resources) is dict and len(resources)<=core.MAX_NODES,'resource_population')
  need(len(core.canonical(resources))<=core.MAX_BYTES,'resource_size_limit')
  used=set();spans=[];method_spans=[];rows=[];byte=0
  for number,raw in enumerate(source.splitlines(keepends=True),1):
   line=raw.rstrip(chr(13)+NL)
   loc={'line':number,'byte_start':byte,'byte_end':byte+len(line.encode()),'slice_sha256':sha256(line.encode()).hexdigest()}
   byte+=len(raw.encode());rows.append((raw,line,loc))
  need(sum(bool(line.strip()) for _,line,_ in rows)<=core.MAX_NODES,'declaration_limit')
  def resource(h):
   syntax.digest_token(h);need(h in resources,'missing_resource:'+h)
   value=resources[h];syntax.lexical.bounded(value);need(digest(value)==h,'resource_digest:'+h)
   used.add(h);return deepcopy(value)
  def unique(obj,key,value):need(key not in obj,'duplicate_field:'+key);obj[key]=value
  def parse_old(lines,locations):
   try:return syntax.parse(command_source(lines))[0]['commands'][0]
   except syntax.Invalid as exc:
    n=(exc.line or 6)-6;loc=locations[min(max(n,0),len(locations)-1)].copy()
    if 0<n<len(lines):loc['error_byte']=loc['byte_start']+len(lines[n][:(exc.column or 1)-1].encode())
    raise Invalid(exc.reason,loc,'command') from exc
  state='header';body=None;aliases={};registry=None;entry=None;block=[];block_locations=[]
  i=0;import_index=0;contract_selected=False
  while i<len(rows):
   raw,line,location=rows[i];i+=1
   if not line.strip():continue
   spans.append(deepcopy(location));stage=state
   r=syntax.Reader(line);word=r.take('word')
   if state=='header':
    need(word=='company_program','header_required');need(r.string()==PROFILE,'text_profile')
    target=r.string();need(target in TARGETS,'target_profile')
    body={'profile':target,'name':r.string(),'registries':{},'commands':[]};state='imports'
   elif state=='imports':
    role=IMPORTS[import_index];need(word=='import_'+role,'required_import:'+role)
    body[role]=resource(r.string());import_index+=1
    if import_index==len(IMPORTS):state='invariant'
   elif state=='invariant':
    need(word=='select_invariant','invariant_required');profile=r.string();h=r.string()
    body['state_invariant']=resource(h);need(profile==body['state_invariant']['profile']=='BookStateInvariant/1','invariant_profile')
    body['expected_invariant_sha256']=h;state='definitions'
   elif state=='registry':
    if word=='entry':
     key=r.string();need(key not in registry['entries'],'duplicate_entry')
     entry={'account_classes':{},'event_inputs':{},'metadata_bindings':{}};state='entry'
    else:
     need(word=='end_registry','registry_declaration');need(bool(registry['entries']),'empty_registry')
     h=digest(registry);need(h not in body['registries'],'duplicate_registry_content')
     body['registries'][h]=registry;aliases[alias]=h;registry=None;state='definitions'
   elif state=='entry':
    if word in ['entry_schemas','entry_memory_definition']:
     unique(entry,'schemas' if word=='entry_schemas' else 'memory_definition',resource(r.string()))
    elif word in ['account_class','supplied_input','metadata_input']:
     field={'account_class':'account_classes','supplied_input':'event_inputs','metadata_input':'metadata_bindings'}[word]
     name=r.string();unique(entry[field],name,r.take('value') if word=='supplied_input' else r.string())
    elif word=='clock':unique(entry,'clock',{'kind':r.string()})
    elif word=='begin_method_source':
     need('source' not in entry,'duplicate_method_source');r.finish()
     start=i;parts=[]
     while i<len(rows) and rows[i][1].strip()!='end_method_source;':parts.append(rows[i][0]);i+=1
     need(i<len(rows),'unterminated_method_source');method_source=''.join(parts)
     need(method_source.endswith(NL),'method_source_final_newline')
     try:lowered=method_text.lower(method_source)
     except Exception as exc:
      match=re.match(r'line (\d+):',str(exc));relative=int(match.group(1))-1 if match else 0
      loc=rows[min(start+relative,i-1)][2] if parts else location
      raise Invalid(str(exc),loc,'method') from exc
     entry.update(source=method_source,source_sha256=lowered['source_sha256'],method=lowered['method'],
      method_sha256=digest(lowered['method']),transition_profile=lowered['transition_profile'])
     start_byte=rows[start][2]['byte_start'];start_line=rows[start][2]['line']
     method_spans.append({'registry':alias,'entry':key,'byte_start':start_byte,'byte_end':start_byte+len(method_source.encode()),
      'source_sha256':lowered['source_sha256'],'declarations':[dict(s,line=s['line']+start_line-1,byte_start=s['byte_start']+start_byte,byte_end=s['byte_end']+start_byte) for s in lowered['source_spans']]})
     i+=1;continue
    else:
     need(word=='end_entry','entry_declaration');need(all(k in entry for k in ['source','clock','schemas']),'incomplete_entry')
     fields=methods.FIELDS+(['memory_definition'] if entry['transition_profile']==method_text.v2.PROFILE else [])
     base.closed(entry,fields);registry['entries'][key]=entry;need(len(registry['entries'])<=methods.MAX_ENTRIES,'entry_limit')
     entry=None;state='registry'
   elif state=='contract':
    selected=body['event_contract']
    if word=='contract_role':unique(selected['roles'],r.string(),r.string())
    elif word=='unit_cost_pointer':unique(selected,word,r.string())
    elif word=='policy':
     policy={'profile':r.string()};r.word('past_due');policy['past_due']=r.string();r.word('carry');policy['carry']=r.string()
     r.word('because');policy['provenance']=r.string();unique(selected,'policy',policy)
    else:need(word=='end_event_contract','contract_declaration');need('policy' in selected and 'unit_cost_pointer' in selected,'incomplete_contract');state='definitions'
   elif state=='command':
    if word=='intent':
     need(kind=='event' and body['profile']==contracted.PROFILE and intent is None,'unexpected_or_duplicate_intent')
     intent={'id':r.string()};r.word('on');intent.update(date=r.string(),inputs={});core.scalar(intent['date'],'date')
    elif word=='intent_input':
     need(intent is not None,'intent_header_required');name=r.string();status=r.take('word');need(status in ['known','unknown'],'input_status')
     val={'status':status,'value':r.scalar()} if status=='known' else {'status':status,'reason':r.string()}
     r.word('because');unique(intent['inputs'],name,{'value':val,'provenance':r.string()})
    else:
     block.append(line);block_locations.append(location)
     if word!='end_'+kind:continue
     command=parse_old(block,block_locations)
     if kind=='event':
      command['registry_sha256']=aliases[event_alias];entry=body['registries'][aliases[event_alias]]['entries'].get(command['method_key'])
      need(entry is not None,'unregistered_method');declared=entry['event_inputs'];inputs=command['event']['inputs']
      need(set(inputs)==set(declared),'exact_projected_inputs')
      for name,rec in inputs.items():rec['type']=deepcopy(declared[name])
      if body['profile']==contracted.PROFILE:
       need(intent is not None,'full_intent_required')
       declared=contracted.contract.native.event_types(body['opening'],command['method_key'])
       need(set(intent['inputs'])==set(declared),'exact_full_intent_inputs')
       for name,rec in intent['inputs'].items():rec['type']=deepcopy(declared[name])
       unique(body['event_contract']['intents'],command['event']['id'],intent)
     elif kind=='carry':
      for pointer,policy in command['memory_policies'].items():
       if policy['kind']=='reset':
        need(pointer in body['opening']['memory_types'],'reset_type_requires_opening_leaf')
        policy['type']=deepcopy(body['opening']['memory_types'][pointer])
     body['commands'].append(command);need(len(body['commands'])<=contracted.MAX_COMMANDS,'command_limit');state='commands'
   elif state in ['definitions','commands']:
    if word=='registry':
     need(state=='definitions' and not contract_selected,'definition_order');alias=r.string();need(alias not in aliases,'duplicate_registry_alias')
     registry={'profile':methods.REGISTRY,'context':deepcopy(body['opening']['context']),'entries':{}};state='registry'
     need(len(aliases)<contracted.MAX_COMMANDS,'registry_limit')
    elif word=='select_event_contract':
     need(state=='definitions' and body['profile']==contracted.PROFILE and not contract_selected,'unexpected_contract')
     selected={'profile':r.string()};need(selected['profile']==contracted.contract.PROFILE,'event_contract_profile')
     r.word('native');selected['native_sha256']=syntax.digest_token(r.string());selected.update(roles={},intents={})
     body['event_contract']=selected;contract_selected=True;state='contract'
    elif word=='end_program':need(bool(body['commands']),'commands_required');state='done'
    else:
     need(word in ['event','report','carry'],'program_declaration');need(bool(aliases),'registries_required')
     need(body['profile']!=contracted.PROFILE or contract_selected,'event_contract_required');kind=word;ident=r.string();intent=None
     if kind=='event':
      r.word('registry');event_alias=r.string();need(event_alias in aliases,'unknown_registry_alias')
      r.word('method');method_key=r.string();r.word('on');day=r.string()
      rewritten='event '+syntax.token(ident)+' method '+syntax.token(method_key)+' on '+syntax.token(day)+';'
     else:
      r.word('at');day=r.string();rewritten=line
     block=[rewritten];block_locations=[location];state='command'
   else:raise Invalid('declaration_after_end')
   r.finish()
  need(state=='done','incomplete_program:'+state);stage='resources';need(set(resources)==used,'exact_resource_population')
  if body['profile']==contracted.PROFILE:
   body['expected_event_contract_sha256']=digest(body['event_contract']);contracted.contract.validate(body)
  stage='program';TARGETS[body['profile']].validate(body)
  return {'profile':PROFILE,'status':'compiled_structural','program':body,'program_sha256':digest(body),
   'source_sha256':sha256(source.encode()).hexdigest(),'source_spans':spans,'method_spans':method_spans,
   'resource_sha256':sorted(used),'executed':False,'accounting_admission':False,'source_admission':False}
 except Exception as exc:
  return {'profile':PROFILE,'status':'invalid','reason':getattr(exc,'reason',str(exc))[:350],
   'stage':getattr(exc,'stage',None) or stage,'location':getattr(exc,'location',None) or location,
   'executed':False,'accounting_admission':False,'source_admission':False}

def execute_text(source,resources):
 compiled=compile_text(source,resources)
 return TARGETS[compiled['program']['profile']].run(compiled['program']) if compiled['status']=='compiled_structural' else compiled
