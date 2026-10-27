"""Preserve the inspected boundary and replay the two selected native cases."""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'evidence.json').exists()
started=time.monotonic();native=ROOT/'data/accounting-master/insurance-service-finance-origins-20261016'
spec=importlib.util.spec_from_file_location('sector_boundary_insurance',native/'reference.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
saved=json.loads((native/'attempt-02/exchanges.json').read_text());cases=[]
for name in ['loss-service-finance','zero-loss-boundary']:
    row=next(r for r in saved if r['id']==name)
    result=module.calculate(row['request'])
    assert result==row['result'] and result['status']=='conditional_complete',name
    assert result['posts'] is False and result['mutations']==[]
    cases.append({'id':name,'request_sha256':sha256(json.dumps(row['request'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'full_result_equal':True,'journals':len(result['report']['journals']),'loss_origins':len(result['report']['loss_origins'])})
paths=['scripts/sector_reference_binding_v1.py','scripts/module_invocation_v1.py',
       'scripts/company_book_transition_v1.py','scripts/declared_company_program_v2.py',
       'scripts/company_book_reports_v1.py','scripts/company_memory_types_v1.py',
       'docs/plans/accounting-sector-posting-boundary-20261025.md',
       'docs/plans/accounting-insurance-loss-book-20261025.md']
for folder,names in {
    'sector-company-composition-20261016':['reference.py','semantic-contract.md','result.md','input-lock.json'],
    'dated-credit-schedules-20261016':['reference.py','semantic-contract.md','source-reading.md','input-lock.json'],
    'insurance-service-finance-origins-20261016':['reference.py','semantic-contract.md','source-reading.md','input-lock-v2.json',
        'authored-cases-v2.json','attempt-02/exchanges.json']}.items():
    paths.extend('data/accounting-master/'+folder+'/'+n for n in names)
locks={p:sha(ROOT/p) for p in paths}
for row in json.loads((native/'input-lock-v2.json').read_text())['files']:
    assert sha(ROOT/row['path'])==row['sha256'],row['path'];locks[row['path']]=row['sha256']
locks[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
locks[str((HERE/'audit.md').relative_to(ROOT))]=sha(HERE/'audit.md')
dump(HERE/'source-lock.json',locks)
dump(HERE/'evidence.json',{'selected_cases':cases,'source_files':len(locks),
    'decision':'Exact insurance loss_schedule is ready for a separately audited book adapter; interval-valued credit posting remains open'})
(HERE/'result.md').write_text('''# Sector posting boundary resolved for the next bounded work unit

25 October2026. The retained insurer loss schedule supplies exact signed journals
and loss-component origins. Both selected native cases replay byte-for-byte as
structured results: six journals and six loss origins each. The broader bank
schedule preserves intervals; an exact-rational posting policy cannot select
rounded values implicitly. Assessment-only reference bindings cannot produce
journals, and SectorCompany/1 remains a finite report rather than execution.

The reviewed next repair is InsuranceLossBook/1: bind the exact insurer case to
explicit owner/currency/account/memory/period context, preserve unrelated state,
reproduce every journal and origin, and never post opening cash/capital again.
Loss component K remains within liability L, represented in memory. Native event
dates are retained; annual carry is not fabricated. Historical source assumptions
and false admission flags survive. The audit, source locks and two-case replay
preserve the basis for selecting this repair.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Proceed with exact insurer adapter | Full native results replay and all signed movements are present | No missing origin or source mismatch | Host state/time/mapping contract needs implementation and checks | Execute the separately audited insurance-loss-book plan | General insurance/bank engine or standards admission |

Version4.27 remains524 pages,not_ready. All53/6/46 obligations remain; no whole
requirement closes. S1–S5 partial,S6 held,S7/E3 deferred. Next:
docs/plans/accounting-insurance-loss-book-20261025.md.
''')
dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'command':'python3 -B data/accounting-master/sector-posting-boundary-20261025/verify.py',
    'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU deterministic rational replay; no GPU framework imported',
    'seeds':'N/A deterministic','data_version':'Retained historical native profiles and exact two loss_schedule cases',
    'wall_seconds':time.monotonic()-started,'plan':'docs/plans/accounting-sector-posting-boundary-20261025.md',
    'result':str((HERE/'result.md').relative_to(ROOT)),
    'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['audit.md','evidence.json','source-lock.json','result.md']}})
print(json.dumps({'passed':True,'native_cases':len(cases),'locked_sources':len(locks)}))
