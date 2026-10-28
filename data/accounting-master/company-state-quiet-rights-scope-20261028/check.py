"""Original quiet-right, signal-law and query-scope discriminators."""
import argparse
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

H = Path(__file__).resolve().parent
ROOT = H.parents[2]
BASE = ROOT / 'data/accounting-master/observation-quotient-20261026'
sys.path.insert(0, str(BASE))
import fixtures as f
from paths import PolicyRefusal, enumerate_paths, supply_policy
from quotient import Refusal, bindings, check, key, reuse
from cases import identity_partition, quiet_rights, maturity, choose_maturity
from evaluation import binding, evaluate, reuse_evaluation
PLAN = 'docs/plans/company-state-quiet-rights-scope-20261028.md'


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    out = ap.parse_args().output.resolve()
    out.mkdir(exist_ok=False)
    started = time.monotonic()
    checks, models, runs, controls = [], [], [], []

    def ck(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))

    def checked(name, m, p, expected='accepted', component=None, **kw):
        result = check(m, p, **kw)
        models.append(dict(name=name, model=deepcopy(m), partition=deepcopy(p), result=result))
        ck(name + '/status', result['status'], expected)
        if component:
            ck(name + '/witness', result.get('witness', {}).get('component'), component)
        return result

    def refused(name, fn, code):
        try:
            result = fn()
        except (Refusal, PolicyRefusal) as e:
            actual = e.code if isinstance(e, Refusal) else str(e)
            controls.append(dict(name=name, status='refused', reason=actual))
            ck(name, actual, code)
        else:
            controls.append(dict(name=name, status='unexpected_acceptance', result=result))
            ck(name, 'accepted', code)

    def paths(name, m, p, cert, chooser):
        sc = ['base'] * m['horizon']
        policy = supply_policy(m, sc, chooser)
        full = enumerate_paths(m, sc, policy, max_nodes=1000)
        reduced = enumerate_paths(reuse(cert, m, p), sc, policy, max_nodes=1000)
        ck(name + '/full exact', full['status'], 'exact')
        ck(name + '/compressed exact', reduced['status'], 'exact')
        ck(name + '/full path equality', full.get('paths'), reduced.get('paths'))
        runs.append(dict(name=name, policy=policy, scenarios=sc, original=full, compressed=reduced))
        return full, policy

    # F045: two identical quiet coupon periods retain future action rights.
    for fee in [0, 8, 9, 12]:
        m, fine, coarse, choose = quiet_rights(fee)
        cert = checked('rights fine fee' + str(fee), m, fine)
        checked('rights merge fee' + str(fee), m, coarse, 'rejected', 'actions')
        full, policy = paths('rights fee' + str(fee), m, fine, cert, choose)
        got = {x['history'][0]['observation']: x['history'][-1]['current_output']['cash'] for x in full['paths']}
        ck('right cost decision fee' + str(fee), got, {'call': 190-min(110, 102+fee), 'locked': 80})
        for path in full['paths']:
            ck('quiet coupons fee' + str(fee) + path['history'][0]['observation'],
               [s['output']['cash_flow'] for s in path['history'][1:3]], [-5, -5])
        short = deepcopy(m)
        short['horizon'] = 2
        short['dates'] = short['dates'][:3]
        for st in short['dates'][-1]['states']:
            st['actions'] = []
        short['dates'][-1]['transitions'] = []
        short_cert = checked('quiet-only merge fee' + str(fee), short, coarse[:3])
        paths('quiet-only fee' + str(fee), short, coarse[:3], short_cert, lambda h: 'coupon')
        refused('quiet certificate cannot extend fee' + str(fee), lambda: reuse(short_cert, m, coarse), 'stale_binding')

    m, fine, coarse, choose = quiet_rights()
    wait = lambda h: 'coupon' if len(h) < 3 else 'wait'
    full, _ = paths('retained rights wait policy', m, fine, checked('wait valid model', m, fine), wait)
    ck('same right supports wait as well', [x['history'][-1]['current_output']['cash'] for x in full['paths']], [80, 80])
    deleted = deepcopy(m)
    deleted['dates'][2]['states'][0]['actions'] = ['wait']
    deleted['dates'][2]['transitions'] = [t for t in deleted['dates'][2]['transitions'] if t['action'] != 'refinance']
    deleted_cert = checked('deleted right negative model', deleted, fine)
    refused('deleted right prevents valid original policy', lambda: supply_policy(deleted, ['base']*3, choose), 'action_not_feasible')
    wrong_paths, _ = paths('deleted right loses saving', deleted, fine, deleted_cert, wait)
    ck('deleted right final cash call', next(p['history'][-1]['current_output']['cash'] for p in wrong_paths['paths'] if p['history'][0]['observation']=='call'), 80)
    unknown, uf, _, _ = quiet_rights(known=False)
    unknown_cert = checked('unknown right keeps both states', unknown, uf)
    paths('unknown right common feasible wait', unknown, uf, unknown_cert, wait)
    refused('unknown right cannot grant universal exercise', lambda: supply_policy(unknown, ['base']*3, lambda h: 'coupon' if len(h)<3 else 'refinance'), 'action_not_feasible')

    # F046: exact joint laws, all four observation-adapted second policies.
    signal, merged = f.signals(Q(9,10), Q(1,2))
    checked('different signal quality', signal, merged, 'rejected', 'joint_kernel')
    def marginal(outs, field):
        d = defaultdict(Q)
        for x in outs:
            d[key(x[field])] += Q(x['probability'])
        return {k: str(v) for k,v in d.items()}
    for field in ['next', 'observation', 'output']:
        ck('equal immediate marginal/' + field, marginal(signal['dates'][0]['transitions'][0]['outcomes'], field), marginal(signal['dates'][0]['transitions'][1]['outcomes'], field))
    laws = {}
    for origin, quality in [('x', Q(9,10)), ('y', Q(1,2))]:
        single = deepcopy(signal)
        single['initial'] = [{'state': origin, 'observation': 'start', 'probability': '1'}]
        part = identity_partition(single)
        cert = checked('signal retained/' + origin, single, part)
        for green, red in product(['lend','wait'], repeat=2):
            choose = lambda h, g=green, r=red: 'observe' if len(h)==1 else (g if h[-1]['observation']=='green' else r)
            name = '/'.join([origin, green, red])
            full, _ = paths(name, single, part, cert, choose)
            law = defaultdict(Q)
            for p in full['paths']:
                law[p['history'][-1]['output']['cash_flow']] += Q(p['probability'])
            expected = defaultdict(Q)
            for observation, truth, mass in [('green','good',quality/2),('red','bad',quality/2),('red','good',(1-quality)/2),('green','bad',(1-quality)/2)]:
                a = green if observation=='green' else red
                expected[0 if a=='wait' else (2 if truth=='good' else -4)] += mass
            ck(name+'/independent law', {str(k):str(v) for k,v in law.items()}, {str(k):str(v) for k,v in expected.items()})
            expectation = sum(Q(k)*v for k,v in law.items())
            laws[name] = str(expectation)
    ck('informative green-lend mean', laws['x/lend/wait'], '7/10')
    ck('uninformative green-lend mean', laws['y/lend/wait'], '-1/2')
    ck('both lend expectations coincide', laws['x/lend/lend'], laws['y/lend/lend'])
    same, same_part = f.signals()
    same_cert = checked('equal-law duplicate positive control', same, same_part)
    paths('equal-law duplicate full path', same, same_part, same_cert, f.choose_signal)
    mixed_cert = checked('mixed fine signal model', signal, identity_partition(signal))
    mixed, _ = paths('mixed signal actual', signal, identity_partition(signal), mixed_cert, f.choose_signal)
    wrong = deepcopy(signal)
    wrong['dates'][0]['transitions'][1]['outcomes'] = deepcopy(wrong['dates'][0]['transitions'][0]['outcomes'])
    wrong_cert = checked('representative signal substitution control', wrong, merged)
    collapsed, _ = paths('wrong representative signal', wrong, merged, wrong_cert, f.choose_signal)
    ck('substitution changes complete law', key(mixed['paths']) == key(collapsed['paths']), False)
    dump(out/'signal-expectations.json', laws)

    # F049: structural sufficiency versus a policy-specific result cache.
    short, sp = maturity()
    long, lp = maturity(extended=True)
    cov, cp = maturity(extended=True, covenant=True)
    scert = checked('short maturity', short, sp)
    lcert = checked('extended maturity', long, lp)
    ccert = checked('added covenant', cov, cp)
    a, apolicy = paths('short distribution', short, sp, scert, choose_maturity())
    b, bpolicy = paths('extended distribution', long, lp, lcert, choose_maturity())
    c, cpolicy = paths('covenant hold', cov, cp, ccert, choose_maturity('hold'))
    ck('short cash', a['paths'][0]['history'][-1]['current_output']['cash'], 25)
    ck('extended cash', b['paths'][0]['history'][-1]['current_output']['cash'], 3)
    ck('covenant cash', c['paths'][0]['history'][-1]['current_output']['cash'], 8)
    ck('supplied covenant rejects distribution5', 30-5>=28, False)
    ck('supplied covenant admits hold', 30>=28, True)
    refused('horizon change stale structural certificate', lambda: reuse(scert, long, lp), 'stale_binding')
    refused('covenant change stale structural certificate', lambda: reuse(lcert, cov, cp), 'stale_binding')
    refused('covenant removes distribution policy', lambda: supply_policy(cov,['base']*2,choose_maturity()), 'action_not_feasible')
    ev = {'identity': 'supplied-maturity-case', 'revision': 'v1'}
    memo = evaluate(lcert,long,lp,bpolicy,['base']*2,ev)
    ck('exact evaluation created', memo['status'], 'exact')
    ck('unchanged memo recomputes', reuse_evaluation(memo,lcert,long,lp,bpolicy,['base']*2,ev), memo)
    hold_policy = supply_policy(long,['base']*2,choose_maturity('hold'))
    ck('structural certificate is policy independent', reuse(lcert,long,lp), lcert['quotient'])
    refused('policy-specific cache cannot reuse', lambda: reuse_evaluation(memo,lcert,long,lp,hold_policy,['base']*2,ev), 'stale_evaluation')
    held = evaluate(lcert,long,lp,hold_policy,['base']*2,ev)
    ck('fresh other policy differs', held['paths']==memo['paths'], False)
    ev2 = dict(ev, revision='v2')
    refused('evidence revision invalidates evaluation', lambda: reuse_evaluation(memo,lcert,long,lp,bpolicy,['base']*2,ev2), 'stale_evaluation')
    short_policy = supply_policy(short,['base'],choose_maturity())
    smemo = evaluate(scert,short,sp,short_policy,['base'],ev)
    refused('evaluation horizon changes', lambda: reuse_evaluation(smemo,lcert,long,lp,bpolicy,['base']*2,ev), 'stale_evaluation')
    refused('evaluation covenant changes', lambda: reuse_evaluation(memo,ccert,cov,cp,cpolicy,['base']*2,ev), 'stale_evaluation')
    tamper = deepcopy(memo)
    tamper['paths'][0]['history'][-1]['current_output']['cash'] = 999
    refused('edited cached result', lambda: reuse_evaluation(tamper,lcert,long,lp,bpolicy,['base']*2,ev), 'evaluation_mismatch')
    rebound = deepcopy(memo)
    rebound['bindings'] = binding(long,lp,hold_policy,['base']*2,ev)
    refused('rebound old policy result', lambda: reuse_evaluation(rebound,lcert,long,lp,hold_policy,['base']*2,ev), 'evaluation_mismatch')
    rebound_cert = deepcopy(scert)
    rebound_cert['bindings'] = bindings(long,lp)
    refused('rebound horizon certificate', lambda: reuse(rebound_cert,long,lp), 'certificate_mismatch')
    unknown = checked('zero comparison budget', long, lp, 'unknown', max_obligations=0)
    ck('unknown retains obligations', bool(unknown.get('frontier')), True)
    refused('unknown certificate not reusable', lambda: reuse(unknown,long,lp), 'not_accepted_certificate')
    ueval = evaluate(lcert,long,lp,bpolicy,['base']*2,ev,max_nodes=0)
    ck('zero evaluation budget unknown', ueval['status'], 'unknown')
    ck('unknown evaluation retains paths frontier', bool(ueval['original'].get('unfinished')), True)
    refused('unknown evaluation not reusable', lambda: reuse_evaluation(ueval,lcert,long,lp,bpolicy,['base']*2,ev), 'not_exact_evaluation')
    multi = deepcopy(long)
    multi['scenarios'].append('stress')
    for d in multi['dates']:
        for tr in list(d['transitions']):
            other=deepcopy(tr);other['scenario']='stress';d['transitions'].append(other)
    mc = checked('explicit alternative scenario label', multi, lp)
    mm = evaluate(mc,multi,lp,bpolicy,['base']*2,ev)
    refused('scenario sequence cache scope', lambda: reuse_evaluation(mm,mc,multi,lp,bpolicy,['stress']*2,ev), 'stale_evaluation')
    ck('identical supplied scenario consequences', evaluate(mc,multi,lp,bpolicy,['stress']*2,ev)['paths'], mm['paths'])
    detached = reuse_evaluation(memo,lcert,long,lp,bpolicy,['base']*2,ev)
    detached['paths'][0]['history'][-1]['current_output']['cash']=999
    ck('returned evaluation detached', memo['paths'][0]['history'][-1]['current_output']['cash'], 3)
    dump(out/'evaluations.json', dict(exact=memo,hold=held,short=smemo,unknown=ueval))

    fm = ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals = [r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F045','SIM-F046','SIM-F049']]
    ck('original target discriminators', [r['discriminating_case'] for r in originals], ['Identical past coupons but different early-call rights','Same immediate output but different later signal quality','Extend horizon past a maturity or add a covenant'])
    failed = [x for x in checks if not x['passed']]
    verification = dict(status='fail' if failed else 'pass', checks=len(checks), finite_models=len(models), path_comparisons=len(runs), refusal_controls=len(controls), failed=[x['name'] for x in failed], original_rows=[x['id'] for x in originals], source_admission=False, native_accounting_method=False, empirical_probability_claim=False)
    for name, value in [('verification',verification),('checks',checks),('models',models),('path-comparisons',runs),('controls',controls),('original-rows',originals)]:
        dump(out/(name+'.json'),value)
    sources={ROOT/PLAN,fm,Path(__file__)}
    sources.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), command=[sys.executable,*sys.argv], environment=dict(python=platform.python_version()), cpu_gpu='CPU-only finite exact rational enumeration; no GPU imports',random_seeds='N/A deterministic',data_version='Original F045/046/049 and explicitly supplied finite models',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-started,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}))
    for p in [Path(__file__),H/'cases.py',H/'evaluation.py']:
        (out/p.name).write_bytes(p.read_bytes())
    print(json.dumps(verification))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
