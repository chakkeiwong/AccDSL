"""Record completed replay and bind the finite result, without changing inputs."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p, value): p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

assert not (HERE / 'replay-observation.json').exists()
log = Path('/tmp/accdsl-indirect-v2-replay.log')
record = Path('/tmp/accdsl-indirect-v2-record.log')
last = json.loads(log.read_text().splitlines()[-1])
assert last == {'passed': True, 'mode': 'read_only_replay', 'focused': 11,
                'regressions': 15, 'cases': 20, 'locked_sources': 54}, last
for name, expected in json.loads((HERE / 'source-lock.json').read_text()).items():
    assert sha(ROOT / name) == expected, name
evidence = json.loads((HERE / 'evidence.json').read_text())
for row in evidence['cases']:
    assert sha(ROOT / row['path']) == row['sha256'], row['name']
shutil.copyfile(log, HERE / 'replay.log')
shutil.copyfile(record, HERE / 'record.log')
dump(HERE / 'replay-observation.json', {**last, 'log_sha256': sha(HERE / 'replay.log'),
     'command': 'python3 -B data/accounting-master/declared-indirect-profit-components-20261025/verify.py',
     'source_lock_sha256': sha(HERE / 'source-lock.json')})
(HERE / 'result.md').write_text('''# Conditional indirect cash explanation: accepted finite repair

25 October 2026. Eleven focused tests and fifteen company-report regressions
pass at record and read-only replay. Twenty complete cases on two charts replay
exactly against 54 locked source/evidence files, with case bytes separately
bound by evidence.json. Sixteen prior supported cases preserve the original
financial report and common numerical projections; four disposal cases add
the explicit gain/loss adjustment. The protected v1 files remain unchanged.

The v1 disposal refusal was a missing classification capability. The v2 repair
adds exact operating/nonoperating classification of gross income and expense
postings per method. Profit plus working-capital, noncash and nonoperating-profit
adjustments equals direct operating cash. A separate event-level exclusion
check must reconcile investing and financing cash. No residual plug is allowed.

For plant with carrying amount10, sale for12 gives profit2 and adjustment−2;
sale for8 gives profit−2 and adjustment+2. Both have operating cash0. In the
combined case, operating interest gives 8.8−5.8=3. Financing interest gives
8.8−8+6.2=7. Total cash and profit remain unchanged. The latter explanation
intentionally moves6.2 from the v1 noncash category to explicit nonoperating
profit; only their sum and other common projections are equal.

The cases include stopped prefixes, carry, a second period, noncash acquisition,
depreciation and gross offsetting postings. Missing/extra classifications,
misclassified gains, forged rehashed execution, dependency changes and recursive
policy input are refused. The evidence also demonstrates that working-capital
and noncash decompositions can be algebraically indistinguishable.

| Decision | Primary criterion | Veto diagnostic | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Accept the bounded v2 explanation | Exact full replay, independent amounts and unchanged v1 common projections pass | All stated integrity, gross-coverage and reconciliation checks pass | Supplied classifications and event population are not admitted | Integrate the explained algebra under the next plan | Accounting compliance, complete cash-flow notes, actual-source admission or whole simulator completion |

This result repairs the candidate, not the entire research direction. One
category per account/method remains a limitation. Classification, source,
accounting and completeness flags remain false. These deterministic cases
support no statistical ranking or forecast claim. The strongest alternative
explanation is that a supplied policy can reconcile while being economically
wrong; the non-uniqueness test preserves exactly that limitation.

The run manifest records the existing git commit, Python/platform, CPU-only
execution, command and 466.270 seconds for recording. No GPU framework was
imported. Full logs and hashes preserve both record and replay. Version4.25
remains governing until the separately reviewed Version4.26 integration passes.
All53 obligations/6 interactions/46 operations remain; no whole requirement
closes. S1–S5 partial, S6 held, S7/E3 deferred.

Next: docs/plans/accounting-indirect-cash-integration-20261025.md.
''')
dump(HERE / 'acceptance-manifest.json', {'artifacts': {
    str((HERE / n).relative_to(ROOT)): sha(HERE / n)
    for n in ['accept.py', 'result.md', 'record.log', 'replay.log',
              'replay-observation.json', 'run-manifest.json', 'evidence.json', 'source-lock.json']}})
print(json.dumps({'accepted': True, **last}))
