"""SIM-F001: retained repeated concepts plus native context refusal controls."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as E
import zipfile
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'data/accounting-master/company-state-debt-measurement-20261028'))
import context_chronology_v1 as context
import debt_measurement as debt
from check_debt_measurement import BUDGET,FILES
PLAN='docs/plans/company-state-context-failure-20261028.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
 out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();checks=[];results=[]
 def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
 archive=ROOT/'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip'
 prior=json.loads((ROOT/'data/accounting-master/company-state-source-card-20261028/attempt-01/source-lock.json').read_text())
 ck('retained archive identity',sha256(archive.read_bytes()).hexdigest(),prior[str(archive.relative_to(ROOT))])
 with zipfile.ZipFile(archive) as z:raw=z.read('aapl-20240928_htm.xml')
 root=E.fromstring(raw);ns={'x':'http://www.xbrl.org/2003/instance'};contexts={c.get('id'):c for c in root.findall('x:context',ns)};units={u.get('id'):u for u in root.findall('x:unit',ns)}
 rows=[]
 for f in root:
  local=f.tag.split('}',1)[-1]
  if local not in ['DebtInstrumentCarryingAmount','ProceedsFromIssuanceOfLongTermDebt']:continue
  c=contexts[f.get('contextRef')];unit=units[f.get('unitRef')]
  rows.append(dict(id=f.get('id'),concept=f.tag,value=f.text,context_ref=f.get('contextRef'),unit_ref=f.get('unitRef'),decimals=f.get('decimals'),context=E.tostring(c,encoding='unicode'),unit=E.tostring(unit,encoding='unicode'),period={x.tag.split('}',1)[-1]:x.text for x in c.find('x:period',ns)},has_segment=c.find('x:entity/x:segment',ns) is not None))
 by={r['id']:r for r in rows};ck('complete selected concept occurrence set',sorted(by),['f-325','f-326','f-327','f-936','f-939','f-942','f-943','f-961'])
 expected={'f-325':('0','2023-10-01','2024-09-28'),'f-326':('5228000000','2022-09-25','2023-09-30'),'f-327':('5465000000','2021-09-26','2022-09-24')}
 for key,(amount,begin,end) in expected.items():
  ck(key+'/literal',by[key]['value'],amount);ck(key+'/period',by[key]['period'],dict(startDate=begin,endDate=end));ck(key+'/unit',by[key]['unit_ref'],'usd')
 ck('principal current value',by['f-942']['value'],'97341000000');ck('principal prior value',by['f-943']['value'],'106572000000')
 ck('principal current date',by['f-942']['period'],dict(instant='2024-09-28'));ck('principal prior date',by['f-943']['period'],dict(instant='2023-09-30'))
 ck('same tag not unique',len([r for r in rows if r['concept']==by['f-942']['concept']]),5)
 ck('same current amount not same context',by['f-936']['value']==by['f-942']['value'] and by['f-936']['context_ref']!=by['f-942']['context_ref'],True)
 ck('dimensional candidate preserved',by['f-936']['has_segment'],True);ck('selected total unsegmented',by['f-942']['has_segment'],False)
 ck('duplicate selected total',by['f-942']['value']==by['f-961']['value'] and by['f-942']['context_ref']==by['f-961']['context_ref'],True)
 cards={k:json.loads((ROOT/p).read_text()) for k,p in FILES.items()};identities={k:debt.identity(v) for k,v in cards.items()}
 built=debt.construct(cards['debt'],cards['timing'],cards['issuance'],identities)
 ck('source instance matches card',sha256(raw).hexdigest(),cards['debt']['instance_sha256'])
 ck('principal duplicate provenance',[r['id'] for r in built['source_mapping']['principal']],['f-942','f-961'])
 ck('principal not summed twice',built['definition']['observations']['principal']['interval'],debt.point('97341/1'))
 # Context-level native controls use the same label but explicitly different metadata.
 c=dict(concept='Total term debt principal',entity='0000320193',perimeter='reported_consolidated',perimeter_version='Apple2024',basis='as_reported',measurement='displayed_principal',unit='USD million',currency='USD',calendar='gregorian',dimensions={},gross_net='gross',scale='1000000/1',sign='1',precision='-6')
 ck('same context identity',context.compatible_context(c,c)['kind'],'identity')
 for field,value in [('unit','USD'),('currency','EUR'),('scale','1/1'),('sign','-1'),('precision','0'),('dimensions',{'InstrumentAxis':'FixedRateMember'}),('perimeter','single_legal_entity'),('concept','Total term debt')]:
  other=deepcopy(c);other[field]=value
  try:r=context.compatible_context(c,other);reason=None
  except context.P06Error as exc:r=dict(status='refused',code=exc.code,message=str(exc));reason=exc.code
  expected_code={'unit':'UNIT_MISMATCH','currency':'CURRENCY_MISMATCH','scale':'UNSUPPORTED_MEASUREMENT_CONVERSION','sign':'DISPLAY_METADATA_MISMATCH','precision':'DISPLAY_METADATA_MISMATCH','dimensions':'DIMENSION_MISMATCH','perimeter':'PARENT_GROUP_MISMATCH','concept':'CONTEXT_MISMATCH'}[field]
  ck('same label different '+field,reason,expected_code);results.append(dict(id='context '+field,input=other,result=r))
 # Two repeated labels/values still need equal dates, units and economic context.
 value_type=deepcopy(debt.VALUE_TYPE);typ=dict(value_type=value_type,time=dict(kind='instant',at='2024-09-28'),quantity='displayed_term_principal')
 obs=dict(type=typ,interval=debt.point('97341/1'),interval_premise=debt.premise('synthetic-equality','Exact displayed duplicate only'),source_ref='retained same total occurrences f-942/f-961')
 definition=dict(profile=debt.temporal.PROFILE,observations={'table_one':deepcopy(obs),'table_two':deepcopy(obs)},relations=[dict(id='duplicate_total',kind='same_time',terms=[dict(observation='table_one',coefficient='1/1'),dict(observation='table_two',coefficient='-1/1')],rhs='0/1',identity_premise=debt.premise('same_total','Explicit inspected duplicate total, not generic identical labels'))])
 a=debt.temporal.assess(definition,BUDGET);ck('same dated total feasible',a['status'],'conditionally_feasible');results.append(dict(id='same total',input=definition,result=a))
 changes=[('prior reporting date',lambda d:d['observations']['table_two']['type'].update(time=dict(kind='instant',at='2023-09-30')),'same_time_mismatch'),('period instead of instant',lambda d:d['observations']['table_two']['type'].update(time=dict(kind='period',start='2023-10-01',end_exclusive='2024-09-29')),'same_time_mismatch'),('future maturity',lambda d:d['observations']['table_two']['type'].update(time=dict(kind='instant',at='2025-09-28')),'same_time_mismatch'),('unit scale',lambda d:d['observations']['table_two']['type']['value_type'].update(scale='1/1'),'economic_context_mismatch'),('currency',lambda d:d['observations']['table_two']['type']['value_type'].update(dimensions={'currency:EUR':1}),'economic_context_mismatch')]
 for label,change,reason in changes:
  d=deepcopy(definition);change(d);a=debt.temporal.assess(d,BUDGET);ck(label+'/status',a['status'],'invalid');ck(label+'/reason',a['reason'],reason);results.append(dict(id=label,input=d,result=a))
 d=deepcopy(definition);d['observations']['table_two']['interval']=debt.point('106572/1');a=debt.temporal.assess(d,BUDGET);ck('wrong year value relabelled current',a['status'],'conditionally_infeasible');results.append(dict(id='wrong year value',input=d,result=a))
 # Rehashing cannot bless role/context changes in the selected adapter.
 for label,change in [('old fact in current slot',lambda d:d['debt']['facts'][0].update(context='c-22',reported_usd='106572000000',reported_usd_million=106572)),('wrong sign',lambda d:d['debt']['facts'][1].update(pdf_reconciliation_sign=1)),('wrong scale',lambda d:d['debt'].update(unit='USD')),('wrong currency',lambda d:d['issuance']['source'].update(unit='EUR')),('wrong current fact id',lambda d:d['debt']['facts'][0].update(id='f-943'))]:
  altered=deepcopy(cards);change(altered)
  try:r=debt.construct(altered['debt'],altered['timing'],altered['issuance'],{k:debt.identity(v) for k,v in altered.items()});reason=None
  except ValueError as exc:reason=str(exc);r=dict(status='refused',reason=reason)
  ck(label+'/refused after rehash',reason is not None,True);results.append(dict(id=label,result=r))
 ck('source/time admission remains false',built['source_admission'],False);ck('no executable source opening',built['executable_opening'],None)
 files=[Path(__file__),ROOT/PLAN,archive,Path(context.__file__),Path(debt.__file__),Path(debt.temporal.__file__),*[ROOT/p for p in FILES.values()]]
 locks={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}
 failed=[r['name'] for r in checks if not r['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),source_occurrences=len(rows),native_results=len(results),failures=failed)
 for name,data in [('source-occurrences.json',rows),('native-results.json',results),('checks.json',checks),('verification.json',v)]:dump(out/name,data)
 dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='python3 -B '+str(Path(__file__).relative_to(ROOT))+' --output '+str(out.relative_to(ROOT)),environment=sys.version,z3=debt.temporal.joint.z3.get_version_string(),cpu_gpu='CPU-only XML/ZIP and exact rational native checks',random_seeds='N/A deterministic',data_version='Retained Apple2024 XBRL plus explicitly synthetic context mutations',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,source_hashes=locks,plan=PLAN,result=str(out.relative_to(ROOT))))
 print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())

