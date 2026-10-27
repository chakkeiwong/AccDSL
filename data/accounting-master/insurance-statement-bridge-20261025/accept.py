"""Preserve exact statement composition acceptance without altering engines."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'acceptance-manifest.json').exists()
for mode in ['record','replay']:
    p=Path('/tmp/accdsl-insurance-statement-'+mode+'.log')
    last=json.loads(p.read_text().splitlines()[-1])
    assert last=={'passed':True,'mode':'record' if mode=='record' else 'read_only_replay',
        'focused':8,'regressions':26,'cases':24,'locked_files':347},last
    (HERE/(mode+'.log')).write_bytes(p.read_bytes())
for name,expected in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==expected,name
for row in json.loads((HERE/'evidence.json').read_text())['cases']:assert sha(ROOT/row['path'])==row['sha256'],row['name']
dump(HERE/'replay-observation.json',{**last,'command':'python3 -B data/accounting-master/insurance-statement-bridge-20261025/verify.py',
    'log_sha256':sha(HERE/'replay.log')})
(HERE/'result.md').write_text('''# Fiscal insurer statements reconcile under explicit alternative classifications

25 October2026. Eight focused tests,26 regressions and24 complete exchanges
pass record and exact read-only replay against347 locked files. The cases span
two charts, two retained native cases, two supplied policies and three fiscal
years, with the unrelated equipment/equity complement present. This is a
composition of unchanged fiscal and indirect reporting engines.

The split policy gives P,W,N,R of0,0,0,0 in2025; -5,-55,10,0 in2026; and
10,-50,-5,0 in2027. Operating cash is respectively0,-50,-45. Every financial
report and its complete period opening/closing matches the accepted fiscal
trace. Each gross posting, including zero loss reversal, remains classified.
K and its six origins remain memory evidence rather than another journal.

Under the second supplied policy all liability movements are noncash-profit
adjustments: W=0 and N=-45/-55 in the nonempty years. Cash and complete fiscal
financial reports are identical to the split policy. This proves exact
correspondence under two premises; reconciliation does not select one policy.

Missing liability classifications refuse as unsupported; omitted zero-reversal
profit classification, stale pre-fiscal method hashes, cross-period policies
and rehashed false traces refuse. The empty2025 policy has no methods or events
and exactly zero contributions. No residual, inferred source fact or accounting
default is inserted. No original engine or accepted case changes.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept finite statement composition | Exact annual statements, gross postings, periods and both decompositions replay | Integrity, policy completeness, zero posting and stale-method controls pass | Applicable cash-flow presentation and event completeness | Add a short local explanation, then audit the interval-valued credit boundary | Unique classification, standard compliance, full insurer scope or predictive accuracy |

The strongest alternative explanation is a valid algebraic decomposition under
an inapplicable accounting premise. The alternative split exposes that ambiguity;
all classification/source/admission flags remain false. Actual source facts or
a different admissible policy would require a separately evidenced comparison.
This deterministic check supports no stochastic ranking or speed claim. The
manifest preserves actual commands, environment, wall time, git base and hashes
of executed uncommitted files. No GPU framework was imported. All53/6/46 remain;
S1-S5 partial,S6 held,S7/E3 deferred.4.29 governs until integration passes.
Next: docs/plans/accounting-insurance-statement-integration-20261025.md.
''')
names=['accept.py','result.md','record.log','replay.log','replay-observation.json','run-manifest.json','evidence.json','source-lock.json']
dump(HERE/'acceptance-manifest.json',{'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}})
print(json.dumps({'accepted':True,**last}))
