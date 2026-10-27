"""Accept fiscal carry only after the complete recorded cases replay exactly."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'acceptance-manifest.json').exists()
for mode in ['record','replay']:
    p=Path('/tmp/accdsl-insurance-fiscal-'+mode+'.log');last=json.loads(p.read_text().splitlines()[-1])
    assert last=={'passed':True,'mode':'record' if mode=='record' else 'read_only_replay',
        'focused':14,'regressions':71,'cases':8,'locked_files':317},last
    (HERE/(mode+'.log')).write_bytes(p.read_bytes())
for name,expected in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==expected,name
for row in json.loads((HERE/'evidence.json').read_text())['cases']:assert sha(ROOT/row['path'])==row['sha256'],row['name']
for source,target in [('accdsl-insurance-fiscal-discriminator.log','naive-discriminator.log'),
                      ('accdsl-insurance-fiscal-probe-02.log','repaired-discriminator.log')]:
    (HERE/target).write_bytes((Path('/tmp')/source).read_bytes())
dump(HERE/'replay-observation.json',{**last,'command':'python3 -B data/accounting-master/insurance-fiscal-book-20261025/verify.py',
    'log_sha256':sha(HERE/'replay.log')})
(HERE/'result.md').write_text('''# Exact insurer journals survive explicitly declared calendar-year carry

25 October2026. Fourteen focused tests,71 regressions and8 complete cases pass
record and read-only replay against317 locked files. Two charts, two retained
native cases and complements present/absent preserve all6 gross journals,
native event identities/dates, full monetary diagnostics and every memory state.

InsuranceFiscalBook/1 recomputes the full cumulative baseline from its request
and checks the expected result hash. It inserts explicit hypothetical year-end
observations and closing/reopening proposals for2025,2026 and2027. Each memory
leaf has an explicit preserve policy; the selected retained account is equity.
No observation establishes that unobserved business was absent.

The naive carry stops at the fourth native method after6 valid commands:
expense is0 after closing while its old precondition requires10. The new
compiler subtracts the2026 temporary closing vector from only the pre/post
balance conditions of the three2027 methods. Reversing24 substitutions recovers
the original methods exactly; monetary/memory definitions and dates stay fixed.

Annual profit is0,-5,10; operating payments are0,50,45. Cash closes200,150,105;
liability100,55,0; equity100,95,105 without the equipment complement, or117,112,
122 with it. All temporary accounts reset and opening2028 profit/cash flows
are0. Closing has no cash effect; K, progress, case identity and unrelated
memory survive. The original cumulative profit5 remains a checked comparator.

The first wrapper probe failed an inherited size bound because it embedded
the full baseline result. Its code/log are retained in attempt-01. Requiring
the expected hash and recomputing the result removes that redundancy without
relaxing limits. Actual transition flows are compared under their existing
field name. Neither repair changes the frozen native or general-book engines.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Accept bounded calendar carry | Exact native correspondence, period arithmetic, archive links and replay pass | Wrong dates, missing carries, stale conditions, policy resets and integrity faults refuse | Actual fiscal policy, event population and source applicability | Explain the checked transformation in4.29, then compose statement bridges | Fiscal completeness, current standards, general insurer support or durable posting |

Strongest alternative explanation: consistent recorded balances omit actual
business or use inapplicable measurement assumptions. Unknown completeness
and all admission flags remain false. New actual facts could require different
methods; arithmetic cannot settle them. No stochastic ranking or performance
claim is made. CPU-only deterministic execution imports no GPU frameworks.
Manifest and locks bind actual commands, environment, wall time, git base and
executed uncommitted bytes. All53/6/46 obligations remain; S1-S5 partial,S6 held,
S7/E3 deferred.4.28 governs until integration passes. Next:
docs/plans/accounting-insurance-fiscal-integration-20261025.md.
''')
names=['accept.py','result.md','record.log','replay.log','replay-observation.json','run-manifest.json',
       'evidence.json','source-lock.json','naive-discriminator.log','repaired-discriminator.log']
dump(HERE/'acceptance-manifest.json',{'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}})
print(json.dumps({'accepted':True,**last}))
