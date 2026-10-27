"""Materialize authored proposal exchanges; not an accounting implementation."""
import copy, hashlib, json
from pathlib import Path
B=Path('docs/design/proposal/architecture')
D='accdsl.accounting.integration.v1'
def load(p):return json.loads(Path(p).read_text())
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def digest(d,k,v):return hashlib.sha256((d+'/'+k+'\0'+canon(v)).encode('ascii')).hexdigest()
def pin(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
integration=load(B/'accounting-integration-fixtures-v2.json')
registry={}
imports=[pin(B/n) for n in ['accounting-integration-fixtures-v2.json','accounting-records-fixtures-v1.json']]
for ref in imports:
 for h,row in load(ref['path'])['records'].items():
  domains=[d for d in [D,'accdsl.accounting.records.v1','accdsl.accounting.record.v1'] if digest(d,row['kind'],row['content'])==h]
  assert len(domains)==1
  registry[h]={**row,'domain':domains[0]}
new={}
def put(kind,content):
 h=digest(D,kind,content);row={'kind':kind,'content':content,'domain':D};registry[h]=row;new[h]=row;return h
controls=load(B/'accounting-integration-c09-c10-conditions-field-controls-v1.json')['local_controls']
I={x['id']:x for x in integration['cases']}
by_source={x['source_case']['case_id']:x for x in I.values()}
selected=['F002','F007','F008','F051','F065','F099','F188','F189','F202','F208','F216','F217','F241','F242','F243','F244','F258','F259','F260']
variants=[]
for key in selected:
 c=next(x for x in controls if x['id']==key);base=by_source[c['comparator']['case_id']]
 original=next(e for e in load(base['source_case']['file']['path'])['cases'] if e['id']==base['source_case']['case_id'])
 packet=copy.deepcopy(original['complete_inputs'])
 # Replay explicit edits so removal of a projected parent is preserved too.
 for change in c['mutations']:
  parts=change['path'].split('/')[1:];parent=packet
  for part in parts[:-1]:parent=parent[part]
  if change['op']=='remove':del parent[parts[-1]]
  else:parent[parts[-1]]=copy.deepcopy(change['after'])
 variants.append({'id':'X'+key[1:],'control':base['id'],'source':packet,'field_control':key,'mutations':c['mutations'], 'expected_diagnostics':[{k:d[k] for k in ['stage','path','code']} for d in c['expected_diagnostics']]})
# Independently authored typed/context counterexamples. Rehash the request's
# references but leave the economic comparator fixed to expose mismatches.
contexts=[
 ('K01','I06',['C09','value','required'],False,'SOURCE_CONTEXT_MISMATCH'),
 ('K02','I01',['C09','value','required'],True,'SOURCE_CONTEXT_MISMATCH'),
 ('K03','I06',['C09','value','branch'],'B5.1.2A(a)','SOURCE_CONTEXT_MISMATCH'),
 ('K04','I06',['C10','value','unequal_price_a_method_available'],True,'METHOD_CAPABILITY_MISMATCH'),
 ('K05','I01',['C01','value','within_retained_window'],False,'SOURCE_CONTEXT_MISMATCH'),
 ('K06','I01',['C06','value','price'],'101','SOURCE_CONTEXT_MISMATCH'),
 ('K07','I01',['C06','value','valuation_date'],'2024-06-02','SOURCE_CONTEXT_MISMATCH'),
 ('K08','I01',['C08','value','currency'],'USD','SOURCE_CONTEXT_MISMATCH')]
for key,ik,path,val,code in contexts:
 base=I[ik];original=next(e for e in load(base['source_case']['file']['path'])['cases'] if e['id']==base['source_case']['case_id']);packet=copy.deepcopy(original['complete_inputs']);at=packet
 for k in path[:-1]:at=at[k]
 old=at[path[-1]];at[path[-1]]=val
 # K02 keeps explicit reasons so that its isolated defect is the price relation.
 mutations=[{'op':'replace','path':'source/'+'/'.join(path),'before':old,'after':val}]
 if key=='K02':
  packet['C09']['unknown_reason']='Both routes not assessed; controller intentionally inconsistent'
  mutations.append({'op':'replace','path':'source/C09/unknown_reason','before':None,'after':packet['C09']['unknown_reason']})
 findings=[{'stage':'bindings','path':'source/'+'/'.join(path),'code':code}]
 if key=='K06':findings.append({'stage':'bindings','path':'source/C09/value/required','code':'SOURCE_CONTEXT_MISMATCH'})
 variants.append({'id':key,'control':ik,'source':packet,'mutations':mutations,'field_control':None,'expected_diagnostics':findings})
source_path=B/'accounting-complete-source-packets-v1.json'
save(source_path,{'schema':'accdsl.proposal.source-packets.v1','scope':'Synthetic specified changes only; no actual company facts','cases':[{'id':v['id'],'complete_inputs':v['source'],'comparator':I[v['control']]['source_case'],'mutations':v['mutations']} for v in variants]})
source_ref=pin(source_path)
def closure(obj):
 found=set()
 def walk(v):
  if isinstance(v,dict):
   if 'path' in v and 'sha256' in v:return
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
  elif isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v):
   assert v in registry,v
   if v not in found:found.add(v);walk(registry[v]['content'])
 walk(obj);return sorted(found)
exchanges=[]
for v in variants:
 base=I[v['control']];q=copy.deepcopy(registry[base['request']]['content']);elig=copy.deepcopy(registry[q['eligibility']]['content']);sr={'file':source_ref,'case_id':v['id']}
 elig['source_case']=sr
 for cond in elig['conditions']:
  cond['case']=sr
  # The source may deliberately be malformed; source-version checking is later
  # than shape and must not invent a version from an absent/scalar packet.
  packet=v['source'].get(cond['condition_id'])
  if isinstance(packet,dict) and 'version' in packet:cond['value_version']=packet['version']
 q['eligibility']=put('eligibility_input',elig);qh=put('request',q);raw=canon(q);sh=put('submission',{'wire_format':'ASCII_JSON','raw_text':raw})
 response=copy.deepcopy(registry[base['response']]['content']);response['submission']=sh
 bad=bool(v['expected_diagnostics']);ah=None
 if bad:
  response.update(request=None,status='rejected',reason_codes=list(dict.fromkeys(d['code'] for d in v['expected_diagnostics'])),assessment=None,diagnostic_journal=None,diagnostic_delta=None,receipt=None,observed_state=None,commit_status='not_committed',additional_commit=False)
  response['statuses'].update(structural_validity='invalid',mathematical_status='unresolved',computation_status='not_computed')
 else:
  assessment=copy.deepcopy(registry[base['assessment']]['content']);assessment.update(request=qh,eligibility=q['eligibility'],source_assessment=sr);ah=put('assessment',assessment);response.update(request=qh,assessment=ah)
 rh=put('response',response)
 exchanges.append({'id':v['id'],'control':{'file':imports[0],'case_id':base['id']},'field_control':v['field_control'],'source_case':sr,'mutations':v['mutations'],'raw_request':raw,'request':qh,'submission':sh,'required_record_closure':closure(q),'assessment':ah,'response':rh,'expected_diagnostics':v['expected_diagnostics'],'lookup':not bad,'freshness':not bad,'assess':not bad,'before':base['before'],'after':base['before']})
fixture={'schema':'accdsl.proposal.accounting.complete-exchanges.v1','scope':'Complete specified exchange resolution, no runtime execution','imports':imports,'specification':pin(B/'accounting-complete-exchanges-v1.md'),'source_packets':source_ref,'field_controls':pin(B/'accounting-integration-c09-c10-conditions-field-controls-v1.json'),'retained_controls':[{'file':imports[0],'case_id':k} for k in I],'retained_adverse_outputs':pin(B/'accounting-integration-field-validation-fixtures-v1.json'),'records':new,'exchanges':exchanges}
save(B/'accounting-complete-exchanges-v1.json',fixture)
print({'new_exchanges':len(exchanges),'retained_controls':len(I),'records':len(new)})
