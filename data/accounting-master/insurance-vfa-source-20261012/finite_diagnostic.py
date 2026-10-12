"""Exact arithmetic for a declared settlement component; no accounting engine."""
import json
import time
from fractions import Fraction as F
from pathlib import Path

OUT = Path(__file__).resolve().parent
assert (OUT / 'diagnostic-contract.md').exists()
assert not (OUT / 'completion.json').exists()
start = time.monotonic()
def payoff(u, floor=F(90), share=F(9, 10)):
    u = F(u)
    payment = max(floor, share*u)
    extra = max(floor-share*u, F(0))
    residual = u-payment
    return [u, payment, residual, extra]

checks = []
def ck(name, value):
    checks.append({'name': name, 'passed': bool(value)})
expected = [[80, 90, -10, 18], [100, 90, 10, 0], [120, 108, 12, 0]]
rows = [payoff(u) for u in [80, 100, 120]]
for actual, wanted in zip(rows, expected):
    ck('predeclared U=' + str(wanted[0]), actual == list(map(F, wanted)))
    u, p, r, extra = actual
    ck('pool cash decomposition U=' + str(u), p+r == u)
    ck('share-minus-floor identity U=' + str(u), r == F(1, 10)*u-extra)
ck('binding interval residual change 20', rows[1][2]-rows[0][2] == 20)
ck('binding interval component changes 2 plus 18', F(1, 10)*(rows[1][0]-rows[0][0]) == 2 and rows[0][3]-rows[1][3] == 18)
ck('nonbinding interval residual change 2', rows[2][2]-rows[1][2] == 2)
ck('zero-value pool pays guarantee', payoff(0) == list(map(F, [0, 90, -90, 90])))
ck('zero guarantee proportional payoff', payoff(80, floor=F(0)) == list(map(F, [80, 72, 8, 0])))
ck('kink derived from terms', F(90)/F(9, 10) == 100)
failed = [r['name'] for r in checks if not r['passed']]
result = {'scope': 'Authored unweighted settlement component; not FCF, CSM, profit or eligibility evidence',
          'rows': [dict(zip(['pool','policyholder_payment','amount_left','extra_floor_payment'], map(str, r))) for r in rows],
          'checks': checks, 'passed': len(checks)-len(failed), 'failed': failed, 'wall_seconds': time.monotonic()-start}
(OUT / 'finite-diagnostic.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['rows','passed','failed','wall_seconds']}))
raise SystemExit(bool(failed))
