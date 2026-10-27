"""Export explicit retained fields and method source; generate no algorithms."""
from copy import deepcopy
import common_text as text
j=text.syntax.token;NL=chr(10)

def from_program(body):
 text.need(body['profile'] in text.TARGETS,'target_profile')
 text.TARGETS[body['profile']].validate(body)
 if body['profile']==text.contracted.PROFILE:text.contracted.contract.validate(body)
 resources={};rows=[];aliases={}
 def add(command,*values):rows.append(command+' '+' '.join(j(v) for v in values)+';')
 def resource(value):
  h=text.digest(value);resources[h]=deepcopy(value);return h
 add('company_program',text.PROFILE,body['profile'],body['name'])
 for role in text.IMPORTS:add('import_'+role,resource(body[role]))
 add('select_invariant',body['state_invariant']['profile'],resource(body['state_invariant']))
 for n,(h,registry) in enumerate(body['registries'].items()):
  alias='registry_'+str(n+1);aliases[h]=alias;add('registry',alias)
  for key,entry in registry['entries'].items():
   add('entry',key);add('entry_schemas',resource(entry['schemas']))
   for role,kind in entry['account_classes'].items():add('account_class',role,kind)
   for name,typ in entry['event_inputs'].items():add('supplied_input',name,typ)
   for name,field in entry['metadata_bindings'].items():add('metadata_input',name,field)
   add('clock',entry['clock']['kind'])
   if 'memory_definition' in entry:add('entry_memory_definition',resource(entry['memory_definition']))
   source=entry['source'];text.need(source.endswith(NL),'method_source_final_newline')
   rows.append('begin_method_source;')
   # Remove only the separator LF; joining restores the identical method bytes.
   rows.append(source[:-1]);rows.extend(['end_method_source;','end_entry;'])
  rows.append('end_registry;')
 if body['profile']==text.contracted.PROFILE:
  selected=body['event_contract'];rows.append('select_event_contract '+j(selected['profile'])+' native '+j(selected['native_sha256'])+';')
  for role,account in selected['roles'].items():add('contract_role',role,account)
  add('unit_cost_pointer',selected['unit_cost_pointer']);p=selected['policy']
  rows.append('policy '+j(p['profile'])+' past_due '+j(p['past_due'])+' carry '+j(p['carry'])+' because '+j(p['provenance'])+';')
  rows.append('end_event_contract;')
 for command in body['commands']:
  c=deepcopy(command)
  if c['kind']=='event':
   h=c.pop('registry_sha256')
   for rec in c['event']['inputs'].values():rec.pop('type')
  elif c['kind']=='carry':
   for policy in c['memory_policies'].values():
    if policy['kind']=='reset':policy.pop('type')
  author={'profile':text.syntax.PROFILE,'name':'bounded-command','imports':{k:'0'*64 for k in text.syntax.IMPORTS},'commands':[c]}
  lines=text.syntax.render(author).splitlines()[5:-1]
  if c['kind']=='event':
   e=c['event'];lines[0]='event '+j(e['id'])+' registry '+j(aliases[h])+' method '+j(c['method_key'])+' on '+j(e['date'])+';'
   if body['profile']==text.contracted.PROFILE:
    intent=body['event_contract']['intents'][e['id']]
    extra=['intent '+j(intent['id'])+' on '+j(intent['date'])+';']
    for name,rec in intent['inputs'].items():
     v=rec['value'];status=v['status'];value=v['value'] if status=='known' else v['reason']
     extra.append('intent_input '+j(name)+' '+status+' '+j(value)+' because '+j(rec['provenance'])+';')
    lines[-1:-1]=extra
  rows+=lines
 rows.append('end_program;');source=NL.join(rows)+NL
 compiled=text.compile_text(source,resources)
 text.need(compiled['status']=='compiled_structural','export_compile:'+compiled.get('reason',''))
 text.need(text.core.canonical(compiled['program'])==text.core.canonical(body),'export_program_correspondence')
 return source,resources
