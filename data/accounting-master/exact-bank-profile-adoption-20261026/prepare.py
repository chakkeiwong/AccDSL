"""Generate explicit successor schema and two narrowly changed date owners."""
from pathlib import Path
from hashlib import sha256
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'exact-native-timing-20261026'))
import checker as prior
NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
def main():
 assert not (HERE/'record-schemas.json').exists()
 schema=json.loads((prior.ATT/'record-schemas.json').read_text());ids=schema['schema_ids'];changed={'Profile'};old=set()
 while old!=changed:
  old=set(changed)
  for name,d in schema['$defs'].items():
   if any(ids[k] in json.dumps(d) for k in changed):changed.add(name)
 expected={'Profile','OperationSignature','OperationRequest','OperationResult','TransportObservation','QueryPublicationReceipt','Domain','Region'}
 assert changed==expected
 replacements={ids[k]:'accdsl.bank-assessment-exact-time.'+k.lower()+'.v1' for k in changed}
 def walk(v):
  if isinstance(v,str):return replacements.get(v,v)
  if isinstance(v,dict):return {k:walk(x) for k,x in v.items()}
  if isinstance(v,list):return [walk(x) for x in v]
  return v
 successor=walk(schema);successor['$defs']['Profile']['properties']['profile_id']={'const':'BankAssessmentExactTime/1'}
 dump(HERE/'record-schemas.json',successor)
 native=(prior.ATT/'inputs/verify_exchanges.py').read_text()
 lines=native[native.index(' def expected_capital('):native.index(' def expected_policy(')]
 assert lines.count("instant(self.body(v)['decision_at']).date()") == 2
 lines=lines.replace("instant(self.body(v)['decision_at']).date()","utc_day(self.body(v)['decision_at'])")
 lines=NL.join(x[1:] if x.startswith(' ') else x for x in lines.splitlines())+NL
 header='"""Pinned native capital/loss methods with exact UTC-day projection only."""'+NL
 header+='from checker import native as n, exact'+NL+'from datetime import date,timedelta'+NL
 header+='need=n.need;day=n.day;capital=n.capital;loss=n.loss;unique=n.unique;FinancialRefusal=n.FinancialRefusal;Refusal=n.Refusal'+NL
 header+='def utc_day(value):return date.fromordinal(int(exact(value)//86400)+1)'+NL*2
 (HERE/'adapted_methods.py').write_text(header+lines)
 lock=json.loads((HERE.parent/'exact-bank-request-conformance-20261026/source-lock.json').read_text())
 files=[HERE.parent/'exact-bank-request-conformance-20261026'/x for x in ['fixtures.py','verify.py','checks.json','result.md','comparisons.json']]
 files += [ROOT/'docs/plans/accounting-exact-bank-profile-adoption-20261026.md']
 for p in files:lock[str(p.relative_to(ROOT))]=sha(p)
 dump(HERE/'source-lock.json',lock)
 dump(HERE/'schema-delta.json',{'successor':'BankAssessmentExactTime/1','changed_schema_kinds':sorted(changed),
  'unchanged_schema_kinds':sorted(set(schema['$defs'])-changed),'schema_id_replacements':replacements,
  'source_schema_sha256':sha(prior.ATT/'record-schemas.json'),'successor_schema_sha256':sha(HERE/'record-schemas.json'),
  'adapted_native_methods':['expected_capital','expected_loss'],'exact_call_replacements':2,'adapted_methods_sha256':sha(HERE/'adapted_methods.py')})
 print(json.dumps({'changed_schema_kinds':len(changed),'exact_day_owners':2,'protected_files':len(lock)}))
if __name__=='__main__':main()
