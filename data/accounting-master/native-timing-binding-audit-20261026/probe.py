from datetime import date
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_requirement_versions as versions
ATT=ROOT/'data/accounting-master/extended-method-exchanges-20261015/bank-assessment/attempt-03'
sys.path.insert(0,str(ATT/'inputs'))
spec=importlib.util.spec_from_file_location('retained_timing_auditor',ATT/'inputs/verify_exchanges.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native);native.ROOT=ROOT
from jsonschema import Draft202012Validator,FormatChecker
schema=Draft202012Validator({'type':'string','format':'date-time'},format_checker=FormatChecker())
pairs=[('same-day-later','2026-04-01T00:00:01Z','2026-04-01T00:00:00Z',False),
       ('equivalent-offset','2026-04-01T01:00:00+01:00','2026-04-01T00:00:00Z',True),
       ('submicrosecond-later','2026-04-01T00:00:00.0000002Z','2026-04-01T00:00:00.0000001Z',False)]
rows=[]
for name,a,b,expected in pairs:
    accepted=not list(schema.iter_errors(a)) and not list(schema.iter_errors(b))
    actual=native.instant(a)<=native.instant(b)
    rows.append({'case':name,'left':a,'right':b,'exact_le':expected,'schema_accepts':accepted,
                 'native_le':actual,'date_only_le':a[:10]<=b[:10],
                 'native_equal':native.instant(a)==native.instant(b)})
assert rows[0]['native_le'] is False and rows[0]['date_only_le'] is True
assert rows[1]['native_equal'] is True
assert rows[2]['schema_accepts'] and rows[2]['native_equal'] and rows[2]['native_le'] is True
rejections=[]
for profile in ('MethodRequirements/1','MethodRequirements/2','MethodRequirements/3'):
    try:versions.typed(profile,{'kind':'instant','context':{}})
    except ValueError as exc:rejections.append({'profile':profile,'reason':str(exc)})
assert len(rejections)==3
packet=json.loads((ATT/'portable-exchanges.json').read_text())
times=sorted({v for r in packet['record_registry'].values() for k,v in r['body'].items()
              if k in ['available_at','ingested_at','decision_at','system_asof']})
assert len(times)==5 and all('.' not in t for t in times)
inputs=[ROOT/'scripts/method_requirements_v1.py',ROOT/'scripts/method_requirements_v2.py',ROOT/'scripts/method_requirements_v3.py',ROOT/'scripts/temporal_measurement_constraints_v1.py',ROOT/'scripts/context_chronology_v1.py',ROOT/'scripts/receivable_source_contract_v1.py',ROOT/'data/accounting-master/company-information-20261023/information.py',ATT/'inputs/verify_exchanges.py',ATT/'inputs/schema_design.py',ATT/'portable-exchanges.json']
result={'passed_diagnostic':True,'pairs':rows,'unsupported_instant_types':rejections,
        'retained_unique_timestamps':times,'retained_fractional_times':0,
        'inputs':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in inputs},
        'boundary':'diagnostic only; no source, accounting or execution admission'}
(HERE/'checks.json').write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','retained_unique_timestamps']}))
