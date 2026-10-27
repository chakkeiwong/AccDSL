"""Reproduce the source supplement's rational arithmetic; no product engine."""
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'docs/design/proposal/readiness/sources-20261007'
start = time.monotonic()
checks = []


def check(name, actual, expected):
    checks.append({'name': name, 'actual': str(actual), 'expected': str(expected),
                   'passed': actual == expected})


def ref(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


# Compute from cash flows; the expected values are the reviewed manuscript's
# literal examples, not values obtained from the same recurrence.
rate, tax, payment = F(1, 10), F(1, 4), F(121)
pv = sum((payment / (1 + rate) ** t for t in (1, 2)), F(0))
check('cash-flow present value', pv, F(210))
liability = [pv]
interest = []
for _ in range(2):
    interest.append(liability[-1] * rate)
    liability.append(liability[-1] + interest[-1] - payment)
rou = [pv - t * pv / 2 for t in range(3)]
check('liability roll-forward', liability, [F(210), F(110), F(0)])
check('interest expense', interest, [F(21), F(11)])
check('ROU straight-line balances', rou, [F(210), F(105), F(0)])
check('total interest equals payments less principal', sum(interest), 2*payment-pv)
check('lease expense by period', [pv/2+x for x in interest], [F(126), F(116)])

# Zero tax bases and sufficient recoverability are assumptions of this example.
dta = [x*tax for x in liability]
dtl = [x*tax for x in rou]
check('gross DTA', dta, [F('52.5'), F('27.5'), F(0)])
check('gross DTL', dtl, [F('52.5'), F('26.25'), F(0)])
deferred = [(dtl[t]-dtl[t-1])-(dta[t]-dta[t-1]) for t in (1, 2)]
check('deferred expense (negative means benefit)', deferred, [F('-1.25'), F('1.25')])
check('lifetime deferred expense', sum(deferred), F(0))
check('commencement gross entry balances', dta[0], dtl[0])
check('first-close gross recognition differs despite equal opening', dta[1]-dtl[1], F('1.25'))

cash, old_equity = F(500), F(495)
check('transition opening book balances', cash+rou[1], liability[1]+old_equity)
equity_adjustment = dta[1]-dtl[1]
assets = cash+rou[1]+dta[1]
liabilities = liability[1]+dtl[1]
equity = old_equity+equity_adjustment
check('opening retained earnings adjustment', equity_adjustment, F('1.25'))
check('transition assets', assets, F('632.5'))
check('transition liabilities', liabilities, F('136.25'))
check('transition equity', equity, F('496.25'))
check('transition balance-sheet identity', assets, liabilities+equity)
check('transition journal balances', dta[1], dtl[1]+equity_adjustment)

inspection = json.loads((SOURCE/'inspection-v1.json').read_text())
for source in inspection['sources']:
    for item in source['files']:
        p = ROOT/item['path']
        check('source hash: '+item['path'], hashlib.sha256(p.read_bytes()).hexdigest(), item['sha256'])
    for anchor in source['anchors']:
        source_text = (ROOT/anchor['path']).read_text()
        check('located excerpt: '+source['id']+' / '+anchor['locator'],
              anchor['quote'] in source_text, True)
        offset = source_text.find(anchor['quote'])
        check('excerpt line: '+source['id']+' / '+anchor['locator'],
              source_text[:offset].count('\n')+1 if offset >= 0 else None,
              anchor['line'])
check('Interpretation 16 original PDF', (SOURCE/'interpretation16.pdf').read_bytes().startswith(b'%PDF-'), True)
check('issued lease standard OOXML original', (SOURCE/'asbe21-issued.doc').read_bytes().startswith(b'PK\x03\x04'), True)

report = {
    'schema_version': 'accdsl.p19.source-repair-check.v1',
    'recorded_at': datetime.now(timezone.utc).isoformat(),
    'passed': all(x['passed'] for x in checks), 'checks': checks,
    'command': ['python3', str(Path(__file__).relative_to(ROOT))],
    'environment': 'Python '+platform.python_version()+'; standard-library exact fractions',
    'cpu_gpu': 'CPU arithmetic and file reads; no GPU framework imported',
    'random_seeds': 'N/A: deterministic rational checks',
    'wall_seconds': time.monotonic()-start,
    'inputs': [ref(Path(__file__)), ref(SOURCE/'inspection-v1.json'),
               ref(ROOT/'docs/design/proposal/readiness/asbe-tax-source-repair-v1.md')],
    'plan': 'docs/plans/accounting-p19-session-recovery-20261007.md',
    'scope': 'Example arithmetic, original-byte integrity and quote locations only. Source interpretation is reviewed separately. No actual tax law, recoverability, offset eligibility or whole-framework compliance is established.'}
(OUT/'source-repair-checks-v1.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
print(json.dumps({'passed': report['passed'], 'checks': len(checks),
                  'failures': [x for x in checks if not x['passed']]}))
raise SystemExit(0 if report['passed'] else 1)
