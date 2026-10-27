"""Inventory retained typed programs without execution or method generation."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=HERE.parent/'authored-event-contract-20261026';NL=chr(10)
OWNERS={
 'profile':'Explicit target; contracted runner validates',
 'name':'Existing company_program header',
 'opening':'Hashed book facts; typed_book validates',
 'schemas':'Hashed shared report schema set; typed_book/report owners',
 'mapping':'Hashed statement mapping; native reports validate',
 'memory_definition':'Hashed memory type definition; typed-memory owner',
 'registries':'Explicit registry/entry declarations; authored registry owner',
 'commands':'Existing commands plus registry and intent selection',
 'state_invariant':'Hashed BookStateInvariant selection; guards owner',
 'expected_invariant_sha256':'Selected resource identity',
 'event_contract':'Explicit native selection, roles, policy and full intents',
 'expected_event_contract_sha256':'Derived identity of explicit contract',
}
ENTRY={
 'method':'Complete inline CompanyMethodAuthoring/1 source; existing lower',
 'method_sha256':'Derived from lowered method',
 'source':'Exact inline source without normalization',
 'source_sha256':'Derived UTF-8 identity',
 'transition_profile':'Explicit method header, not registry version',
 'schemas':'Explicit hash of entry schemas, separate from report schemas',
 'account_classes':'Explicit role/class declarations',
 'event_inputs':'Explicit supplied-input types',
 'metadata_bindings':'Explicit input-to-id/date bindings',
 'clock':'Explicit direct_event_date selection',
 'memory_definition':'Explicit entry resource for transition v2 only',
}
INVARIANT={k:'Exact typed rule resource; guards and collection totals own semantics' for k in
 ['profile','context','definition','globals','collections','residual_prerequisites']}
CONTRACT={
 'profile':'Explicit contract selection','native_sha256':'Pinned implementation identity',
 'roles':'Explicit role/account declarations','unit_cost_pointer':'Explicit memory pointer',
 'policy':'Explicit profile, past_due, carry and provenance',
 'intents':'Full id/date/input values and provenance inside each event block',
}
COMMAND={
 'event':['kind','registry_sha256','method_key','event'],
 'report':['kind','id','cutoff','equity_movements','notes'],
 'carry':['kind','id','cutoff','equity_movements','notes','retained_account','next_end_exclusive','memory_policies'],
}
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
def main():
 lock=json.loads((PRIOR/'source-lock.json').read_text())
 files=[PRIOR/n for n in ['contract.py','contract_runner.py','verify.py','checks.json','result.md']]
 files += [ROOT/'scripts'/n for n in ['declared_company_text_v2.py','declared_receivable_text_v1.py']]
 files += list((PRIOR/'examples').glob('*.program.json'))+list((PRIOR/'examples').glob('*.result.json'))
 for p in files:lock[str(p.relative_to(ROOT))]=sha256(p.read_bytes()).hexdigest()
 for name,h in lock.items():assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
 rows=[]
 for company in ['alpha','beta']:
  b=json.loads((PRIOR/'examples'/f'{company}.program.json').read_text())
  assert set(b)==set(OWNERS) and set(b['state_invariant'])==set(INVARIANT)
  assert set(b['event_contract'])==set(CONTRACT)
  assert set(b['event_contract']['policy'])=={'profile','past_due','carry','provenance'}
  entries=0
  for registry in b['registries'].values():
   assert set(registry)=={'profile','context','entries'}
   for e in registry['entries'].values():
    assert set(e)==set(ENTRY)-({'memory_definition'} if e['transition_profile']=='CompanyBookTransition/1' else set())
    entries+=1
  for c in b['commands']:
   assert set(c)==set(COMMAND[c['kind']])
   if c['kind']=='event':
    assert set(c['event'])=={'id','date','inputs'}
    for event in [c['event'],b['event_contract']['intents'][c['event']['id']]]:
     for v in event['inputs'].values():assert set(v)=={'type','value','provenance'}
  rows.append({'company':company,'top_level_fields':len(b),'registries':len(b['registries']),'entries':entries,'commands':len(b['commands'])})
 dump(HERE/'field-ownership.json',{'program':OWNERS,'registry_entry':ENTRY,'state_invariant':INVARIANT,'event_contract':CONTRACT,'command_fields':COMMAND,'examples':rows})
 dump(HERE/'source-lock.json',lock)
 dump(HERE/'checks.json',{'passed':True,'field_inventory_complete':True,'matched_typed_examples':rows,'protected_files':len(lock),'frontend_implemented':False,'general_language_complete':False})
 print(json.dumps({'passed':True,'companies':len(rows),'commands':sum(x['commands'] for x in rows),'protected_files':len(lock)}))
if __name__=='__main__':main()
