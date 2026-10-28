"""SIM-F021 through the preserved declared issue method; synthetic pricing only."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'data/accounting-master/literature-closure-20261026/runtime-integration.py'
PLAN = 'docs/plans/company-state-face-proceeds-failure-20261028.md'
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('retained_issue_example', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
program, native = base.program, base.native

def fmt(x):
    x = Q(x)
    return str(x.numerator) + '/' + str(x.denominator)

def encode(x):
    if isinstance(x, Q): return fmt(x)
    if isinstance(x, dict): return {k: encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [encode(v) for v in x]
    return x

def dump(path, data):
    path.write_text(json.dumps(encode(data), indent=2) + chr(10))

def pricing(face, pd, recovery, gross):
    # Independent finite state expansion; inputs explicitly represent pricing weights.
    states = [('solvent', 1-pd, face), ('default', pd, recovery)]
    contributions = [weight * payment / gross for _, weight, payment in states]
    return sum(contributions, Q()), [dict(state=k, weight=p, payment=v, discounted_contribution=c)
        for (k,p,v),c in zip(states, contributions)]

def body_for(face, proceeds, quote, owner='alpha'):
    body, mapping = base.make('fixed', owner)
    fields = body['commands'][3]['event']['inputs']
    for key, value in dict(face=face, proceeds=proceeds, quote=quote).items():
        fields[key]['value'] = program.engine.known(fmt(value))
        fields[key]['provenance'] = 'Synthetic SIM-F021 pricing-law diagnostic, no actual offer admission'
    return body, mapping

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    checks, outputs = [], []
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=encode(actual), expected=encode(expected)))
    def execute(label, body):
        before = deepcopy(body)
        result = program.run(body)
        check(label+'/inputs unchanged', body == before, True)
        check(label+'/native replay', program.verify(body, result), True)
        outputs.append(dict(id=label, input=body, result=result))
        return result
    paths = [SOURCE, ROOT/'data/accounting-master/literature-closure-20261026/exact_cases.py',
             ROOT/'data/accounting-master/unified-program-20261028/failure-map.json']
    paths += [Path(m.__file__).resolve() for m in list(sys.modules.values())
              if getattr(m, '__file__', None) and Path(m.__file__).resolve().parent == ROOT/'scripts']
    hashes = {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
    dump(out/'source-lock.json', hashes)
    original = native.Engine.apply
    native.Engine.apply = lambda *a, **k: (_ for _ in ()).throw(AssertionError('undeclared fallback forbidden'))
    try:
        cases = [
            ('original', Q(100), Q(1,10), Q(40), Q(21,20)),
            ('no_default', Q(100), Q(0), Q(40), Q(21,20)),
            ('certain_default', Q(100), Q(1), Q(40), Q(21,20)),
            ('zero_recovery', Q(100), Q(1,10), Q(0), Q(21,20)),
            ('full_recovery', Q(100), Q(1,10), Q(100), Q(21,20)),
            ('zero_rate', Q(100), Q(1,10), Q(40), Q(1)),
            ('larger_face_fixed_recovery', Q(200), Q(1,10), Q(40), Q(21,20)),
            ('larger_face_scaled_recovery', Q(200), Q(1,10), Q(80), Q(21,20))]
        price_rows = []
        for label, face, pd, recovery, gross in cases:
            proceeds, states = pricing(face, pd, recovery, gross)
            quote = proceeds/face
            # Independent closed form from the original failure's lender equation.
            expected = ((1-pd)*face + pd*recovery)/gross
            check(label+'/state expansion', proceeds, expected)
            check(label+'/lender break even', gross*proceeds, (1-pd)*face+pd*recovery)
            check(label+'/state weight normalization', sum(x['weight'] for x in states), Q(1))
            body, mapping = body_for(face, proceeds, quote)
            result = execute(label, body)
            check(label+'/native status', result['status'], 'complete_provisional')
            if result['status'] != 'complete_provisional': continue
            trace = result['trace']
            issue = trace[3]['result']['transition']
            before, after = trace[2]['result']['transition']['after'], issue['after']
            check(label+'/predecessor hash', issue['before_sha256'], program.digest(before))
            expected_balances = dict(before['balances'])
            expected_balances[mapping['cash']] = fmt(Q(expected_balances[mapping['cash']])+proceeds)
            expected_balances[mapping['debt']] = fmt(Q(expected_balances[mapping['debt']])-proceeds)
            check(label+'/all balances', after['balances'], expected_balances)
            expected_memory = deepcopy(before['memory'])
            expected_memory['terms']['face'] = fmt(Q(expected_memory['terms']['face'])+face)
            expected_memory['terms']['stage'] = '4/1'
            check(label+'/all memory', after['memory'], expected_memory)
            check(label+'/journal cash', Q(issue['journal'][mapping['cash']]), proceeds)
            check(label+'/journal debt', Q(issue['journal'][mapping['debt']]), -proceeds)
            check(label+'/journal conserved', sum(Q(v) for v in issue['journal'].values()), Q(0))
            check(label+'/cash flow proceeds', sum(Q(v['amount']) for v in issue['flows']), proceeds)
            report = trace[-1]['result']
            check(label+'/report status', report['status'], 'reported')
            check(label+'/reported liabilities', Q(report['balance_sheet']['total_liabilities']), Q(100)+proceeds)
            check(label+'/reported assets', Q(report['balance_sheet']['total_assets']), Q(109)+proceeds)
            check(label+'/reported equity', Q(report['equity']['closing']), Q(9))
            price_rows.append(dict(id=label,face=face,default_weight=pd,recovery_amount=recovery,
                gross_return=gross,states=states,proceeds=proceeds,quote=quote))
        p, states = pricing(Q(100),Q(1,10),Q(40),Q(21,20))
        check('SIM-F021 price', p, Q(1880,21))
        check('SIM-F021 yield', Q(100)/p-1, Q(11,94))
        check('SIM-F021 need95 shortfall', Q(95)-p, Q(115,21))
        check('SIM-F021 face not proceeds', p == Q(100), False)
        check('SIM-F021 face-as-cash lender gap', Q(21,20)*100-Q(94), Q(11))
        check('SIM-F021 original retained convention',
              'Face-based price equals discounted recovery/solvent payoff' in paths[1].read_text(), True)
        wrong_rate = (Q(100)*Q(21,20)-Q(1,10)*40)/(100*Q(9,10))-1
        mixed = Q(100)/(1+wrong_rate)
        check('mixed-convention proceeds', mixed, Q(9000,101))
        check('mixed-convention lender gap', Q(21,20)*mixed-Q(94), -Q(44,101))
        for label, amount in [('face_as_proceeds',Q(100)),('mixed_convention',mixed),('wrong_scale',p*1000)]:
            body, _ = body_for(Q(100), amount, p/100)
            result = execute(label, body)
            check(label+'/refused', result['status'], 'stopped_provisional')
            check(label+'/three-event prefix', len(result['trace']), 3)
            check(label+'/atomic refusal', result['current'], result['trace'][-1]['result']['transition']['after'])
        # A valid arithmetic identity alone cannot admit the price from an economic law.
        body, mapping = body_for(Q(100), Q(100), Q(1))
        result = execute('self_consistent_wrong_quote', body)
        check('wrong quote passes native identity', result['status'], 'complete_provisional')
        check('wrong quote violates original lender law', Q(100)*Q(21,20)-Q(94), Q(11))
        check('wrong quote pays excessive issue cash',
              Q(result['current']['balances'][mapping['cash']])-5, Q(100))
        # The zero-recovery certain-default boundary has zero proceeds and no invented cash.
        body, mapping = body_for(Q(100), Q(0), Q(0))
        result = execute('zero_value_claim', body)
        check('zero value scope status', result['status'], 'complete_provisional')
        check('zero value adds no cash', result['current']['balances'][mapping['cash']], '5/1')
        check('zero value retains promised face', result['current']['memory']['terms']['face'], '200/1')
        # Fixed recovery is not automatically a face percentage after a face change.
        prices={x['id']:x['proceeds'] for x in price_rows}
        check('fixed versus scaled recovery differs', prices['larger_face_scaled_recovery']-prices['larger_face_fixed_recovery'], Q(80,21))
        dump(out/'pricing-states.json', price_rows)
    finally:
        native.Engine.apply = original
        dump(out/'native-cases.json', outputs)
        dump(out/'checks.json', checks)
    for path, expected in hashes.items():
        check('protected/'+path, sha256((ROOT/path).read_bytes()).hexdigest(), expected)
    dump(out/'checks.json', checks)
    result = dict(status='pass' if all(x['passed'] for x in checks) else 'fail',
        checks=len(checks),cases=len(outputs),failures=[x['name'] for x in checks if not x['passed']],
        scope='Synthetic declared issue/recording and independent finite pricing law; no price or source admission')
    dump(out/'verification.json',result)
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='python3 -B '+str(Path(__file__).relative_to(ROOT))+' --output '+str(out.relative_to(ROOT)),
        environment=sys.version,platform=platform.platform(),cpu_gpu='CPU exact standard-library arithmetic; no GPU import or detection',
        data_version='SIM-F021 original row and declared synthetic one-period pricing law',random_seeds='N/A deterministic',
        wall_seconds=time.monotonic()-started,started_utc=datetime.now(timezone.utc).isoformat(),
        source_hashes=hashes,plan=PLAN,results=str(out.relative_to(ROOT)),
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest()))
    print(json.dumps(result))
    return 0 if result['status']=='pass' else 1

if __name__ == '__main__': raise SystemExit(main())

