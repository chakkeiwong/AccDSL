"""Accept only the exact recorded and replayed insurer correspondence."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'acceptance-manifest.json').exists()
for mode in ['record','replay']:
    source=Path('/tmp/accdsl-insurance-loss-'+mode+'.log')
    last=json.loads(source.read_text().splitlines()[-1])
    assert last=={'passed':True,'mode':'record' if mode=='record' else 'read_only_replay',
        'focused':16,'regressions':57,'cases':8,'locked_files':279},last
    (HERE/(mode+'.log')).write_bytes(source.read_bytes())
for name,expected in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==expected,name
for row in json.loads((HERE/'evidence.json').read_text())['cases']:assert sha(ROOT/row['path'])==row['sha256'],row['name']
dump(HERE/'replay-observation.json',{**last,'command':'python3 -B data/accounting-master/insurance-loss-book-20261025/verify.py','log_sha256':sha(HERE/'replay.log')})
(HERE/'result.md').write_text('''# Exact insurer journals now propose a declared company-book trace

25 October 2026. Sixteen focused tests, 57 regressions and eight complete cases
pass record and read-only replay. The 279-file lock includes dynamically loaded
regression fixtures and retained annual-report data. Case bytes are separately
hashed. Both named and numbered charts preserve all six native journals and
six loss-component origins, with and without the unrelated equipment balance.

InsuranceLossBook/1 recomputes one of two retained native requests before
compiling six dated methods. It checks account classes, injective role and
memory mappings, opening balances, source context, progress and dates. Native
report-only output remains unchanged. The new trace is proposed and provisional;
it neither writes a durable book nor grants native accounting admission.

For the nonzero-loss case, cash moves from 200 to 150 to 105, liability from
100 to 55 to zero, and cumulative profit from zero to -5 to 5. The loss
component moves from 20 to 11 to zero within the liability; it is never posted
as another liability. Its finance, claim and risk-adjustment origins remain
separate even where the corresponding memory update combines two releases.
The zero-loss case has identical cash, liability and profit but a different
revenue/reversal split; zero gross reversal entries remain explicit.

Native CU is mapped explicitly to the host's illustrative XCU at scale 1/1,
bound to both complete contexts. This is a syntactic alias, not FX conversion
or ISO currency admission. The January 1 event dates remain unchanged in a
host interval from 2025-01-01 to exclusive 2027-01-02. Reports are cumulative;
no annual close or carry is claimed. Operating claim payments are a supplied
classification premise. Fixed loss allocation and historical source findings
remain conditional assumptions of the retained calculator.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept finite proposed adapter | Exact journals, memory, cash and cumulative reports match native results and independent arithmetic | Context, integrity, role, date, state and refusal checks pass | Applicability of supplied measurement and classification assumptions | Integrate the checked mechanism into Version 4.28 | General insurance execution, current standards, full sources, fiscal carry or whole-company completeness |

The strongest alternative explanation is a perfectly consistent calculation
under assumptions that do not apply to a real insurer. Unknown/false findings
retain refusal, and all admission/completeness flags remain false. Additional
source admission or broader input support would require new evidence. This
deterministic conformance result supports no stochastic ranking or speed claim.
The run manifest records environment, actual command, wall time and git base;
hashes identify executed uncommitted files. No GPU framework was imported.
All 53 obligations, six interactions and 46 operations remain. S1-S5 partial,
S6 held, S7/E3 deferred. Version 4.27 remains governing until integration passes.
Next: docs/plans/accounting-insurance-loss-integration-20261025.md.
''')
names=['accept.py','result.md','record.log','replay.log','replay-observation.json','run-manifest.json','source-lock.json','evidence.json']
dump(HERE/'acceptance-manifest.json',{'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}})
print(json.dumps({'accepted':True,**last}))
