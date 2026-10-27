"""Integrity of a negative assessment; never a substitute for promotion review."""
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
start = time.monotonic()
checks = []


def read(path):
    return json.loads((ROOT/path).read_text())


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def check(name, passed, details=None):
    checks.append({'name': name, 'passed': bool(passed), 'details': details})


d = read('data/accounting-master/deliverables/P19/readiness.json')
entry = read('data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
for field, expected in [('requirements', {f'MC{i:02d}' for i in range(1,36)}),
                        ('gaps', {f'G{i}' for i in range(1,19)}),
                        ('open_decisions', {f'P15-E{i:02d}' for i in range(1,15)})]:
    rows = d[field]
    check(field+' complete and unique', len(rows)==len(expected) and {r['id'] for r in rows}==expected)
acceptance = {l.split('|')[1].strip(): l.split('|')[3].strip()
              for l in (ROOT/'docs/plans/accounting-mission-requirements.md').read_text().splitlines()
              if l.startswith('| MC')}
for r in d['requirements']:
    check(r['id']+' original acceptance retained', r['acceptance_obligation']==acceptance[r['id']])
for r in d['requirements']+d['gaps']:
    check(r['id']+' support and residual explicit', all(r.get(k) for k in ['status','contract','remaining_work','evidence']))
    check(r['id']+' located evidence', all(x.get('locator') for x in r['evidence']))

refs = []


def visit(x):
    if isinstance(x, dict):
        if isinstance(x.get('path'), str) and isinstance(x.get('sha256'), str):
            refs.append((x['path'],x['sha256']))
        for v in x.values():
            visit(v)
    elif isinstance(x,list):
        for v in x:
            visit(v)


visit(d)
for path, expected in sorted(set(refs)):
    check('assessment reference: '+path, (ROOT/path).is_file() and digest(path)==expected)
for category in ['protected_hashes','upstream_reference_hashes','controller_hashes']:
    wrong = [p for p,h in entry[category].items() if not (ROOT/p).is_file() or digest(p)!=h]
    check(category+' preserved', not wrong, {'count':len(entry[category]),'mismatches':wrong})

expected = set()
for stage, filename in [('P15','coverage.json'),('P16','architecture.json'),('P17','methods.json')]:
    for r in read(f'data/accounting-master/deliverables/{stage}/{filename}')['open_decisions']:
        if r['blocks_proposal']:
            expected.add((stage,r['id']))
rows = d['decision_dispositions']
check('all inherited blocking occurrences disposed exactly once',
      len(rows)==len(expected) and {(r['stage'],r['decision_id']) for r in rows}==expected)
by_id = {r['id']:r for r in d['open_decisions']}
for r in rows:
    check('disposition agrees: '+r['stage']+'/'+r['decision_id'],
          r['status']==by_id[r['decision_id']]['status'] and r['answer']==by_id[r['decision_id']]['proposed_answer'])
blockers = sorted(r['id'] for r in d['open_decisions'] if r['blocks_proposal'])
check('blocker summary equals actual decisions', blockers==sorted(d['remaining_blockers']))
check('negative readiness explicit', d['ready'] is False and d['status']=='not_ready' and bool(blockers))
check('implementation disabled', d['implementation_enabled'] is False and d['product_implemented'] is False)
check('human acceptance pending', d['human_acceptance']=='pending')
md = (ROOT/'docs/design/proposal/readiness/assessment-v1.md').read_text()
for r in d['requirements']+d['gaps']:
    check('markdown agrees: '+r['id'], f"| {r['id']} | {r['status']} |" in md)

report = {'schema_version':'accdsl.p19.negative-assessment-integrity.v1',
          'recorded_at':datetime.now(timezone.utc).isoformat(),
          'passed':all(r['passed'] for r in checks),'checks':checks,
          'counts':{'requirements':len(d['requirements']),'gaps':len(d['gaps']),
                    'decisions':len(by_id),'inherited_blocker_occurrences':len(rows),
                    'remaining_blockers':len(blockers),'unique_references':len(set(refs)),
                    'protected_files':len(entry['protected_hashes'])},
          'command':['python3',str(Path(__file__).relative_to(ROOT))],
          'wall_seconds':time.monotonic()-start,
          'inputs':{'data/accounting-master/deliverables/P19/readiness.json':digest('data/accounting-master/deliverables/P19/readiness.json'),
                    'docs/design/proposal/readiness/assessment-v1.md':digest('docs/design/proposal/readiness/assessment-v1.md')},
          'scope':'Coverage, inherited-decision accounting and exact-file integrity only. No semantic completeness, accounting validity or proposal readiness is certified.'}
(OUT/'assessment-integrity-v1.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'counts':report['counts'],
                  'failures':[r for r in checks if not r['passed']]}))
sys.exit(0 if report['passed'] else 1)
