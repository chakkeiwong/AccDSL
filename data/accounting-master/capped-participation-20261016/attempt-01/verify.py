"""Hand-derived targets, independent subset enumeration, and fail-closed checks."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from itertools import combinations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
sys.dont_write_bytecode = True
from reference import OUT, ROOT, SOURCE, FINDINGS, SERIES_FINDINGS, calculate


def world(request, subset):
    """Alternative derivation: ordinary per-share claims, then class totals."""
    E = Q(request['earnings']) + sum((Q(s['gross_after_tax_adjustment']) for s in subset), Q(0))
    n = Q(request['ordinary_shares']) + sum((Q(s['ordinary_share_increment']) for s in subset), Q(0))
    f = Q(request['senior_entitlement'])
    m = Q(request['preferred_shares']) * Q(request['residual_weight'])
    cap = Q(request['total_preferred_cap'])
    if E < f:
        eps = (E-f)/n
    else:
        # An uncapped claim shares each residual unit; a capped claim leaves
        # all further earnings to ordinary holders. Choose the applicable limb.
        eps = max((E-f)/(n+m), (E-cap)/n)
    ordinary = eps*n
    return dict(earnings=str(E), preferred=str(E-ordinary), ordinary=str(ordinary),
                denominator=str(n), eps=str(eps))


def main():
    started = time.monotonic()
    attempts = [int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt = OUT / ('attempt-%02d' % (max(attempts, default=0)+1))
    attempt.mkdir()
    for name in ('reference.py', 'verify.py', 'authored-cases.json', 'input-lock.json', 'resume-audit.md'):
        shutil.copy2(OUT/name, attempt/name)
    checks, exchanges, enumeration, adverse = [], [], [], []
    def check(name, ok, detail=None):
        checks.append(dict(name=name, passed=bool(ok), detail=detail))
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('protected/'+row['path'], hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'])
    if not all(c['passed'] for c in checks):
        (attempt/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
        raise SystemExit('Protected input mismatch; no calculation admitted.')
    cases = json.loads((OUT/'authored-cases.json').read_text())['cases']
    for case in cases:
        req = deepcopy(case['request']); before = deepcopy(req); r = calculate(req)
        prefix = case['id']+'/'
        exchanges.append(dict(id=case['id'], request=req, result=r))
        check(prefix+'status', r['status'] == 'conditional_complete', r['reason'])
        check(prefix+'readonly-repeatable', req == before and r == calculate(req) and r['mutations'] == [])
        if r['status'] != 'conditional_complete':
            continue
        for category in ('basic', 'diluted'):
            for key, value in case['expected'][category].items():
                check(prefix+category+'/'+key, r[category][key] == value,
                      dict(expected=value, actual=r[category][key]))
        check(prefix+'selected', r['selected'] == case['expected']['selected'])
        worlds = []
        for size in range(len(req['series'])+1):
            for subset in combinations(req['series'], size):
                worlds.append(dict(selected=sorted(s['id'] for s in subset), **world(req, subset)))
        enumeration.append(dict(id=case['id'], worlds=worlds))
        check(prefix+'subset-minimum', Q(r['diluted']['eps']) == min(Q(w['eps']) for w in worlds))
        chosen = next(w for w in worlds if w['selected'] == sorted(r['selected']))
        check(prefix+'selected-world', all(chosen[k] == r['diluted'][k] for k in ('earnings','preferred','ordinary','denominator','eps')))
        check(prefix+'basic-world', all(world(req, [])[k] == r['basic'][k] for k in ('earnings','preferred','ordinary','denominator','eps')))
        reverse = deepcopy(req); reverse['series'].reverse()
        check(prefix+'input-order', calculate(reverse) == r)
        for index, allocation in enumerate([r['basic'], r['diluted']]+[t['if_included'] for t in r['trace']]):
            check(prefix+'conservation/'+str(index), Q(allocation['preferred'])+Q(allocation['ordinary']) == Q(allocation['earnings']))
            check(prefix+'class-rights/'+str(index), Q(req['senior_entitlement']) <= Q(allocation['preferred']) <= Q(req['total_preferred_cap']))
            check(prefix+'class-eps/'+str(index), Q(allocation['preferred_eps'])*Q(req['preferred_shares']) == Q(allocation['preferred']))
        for step in r['trace']:
            check(prefix+'strict/'+step['id'], step['included'] == (Q(step['if_included']['eps']) < Q(step['before']['eps'])))
    byid = {x['id']:x['result'] for x in exchanges}
    check('independent-treasury-shares', Q(100)-Q(100)*10/20 == 50)
    check('fixed-numerator-is-wrong', byid['option-reallocates']['diluted']['eps'] == '12/17' and Q('12/17') != Q(100,150))
    check('strict-equality-excluded', byid['strict-equality']['selected'] == [])
    check('loss-and-zero-excluded', all(byid[k]['selected'] == [] for k in ('priority-only','zero-profit','loss-no-participation')))

    baseline = next(c['request'] for c in cases if c['id'] == 'both')
    def add(id, status, reason, change):
        req = deepcopy(baseline); change(req)
        adverse.append(dict(id=id, expected_status=status, expected_reason=reason, request=req))
    for field in sorted(FINDINGS):
        for value, status, stem in ((None,'unresolved','missing_'),(False,'unsupported','outside_')):
            add('finding/'+field+'/'+str(value), status, stem+field, lambda r,k=field,v=value:r['findings'].update({k:v}))
    for field in sorted(SERIES_FINDINGS):
        for value, status, stem in ((None,'unresolved','missing_'),(False,'unsupported','outside_')):
            add('series-finding/'+field+'/'+str(value), status, stem+field, lambda r,k=field,v=value:r['series'][0]['findings'].update({k:v}))
    for field in ('earnings','ordinary_shares','preferred_shares','residual_weight','senior_entitlement','total_preferred_cap'):
        add('missing/'+field,'unresolved','missing_'+field,lambda r,k=field:r.update({k:None}))
    for value in ('1.0','01','1/0','NaN',1,True):
        add('numeric/'+repr(value),'rejected','number_encoding',lambda r,v=value:r.update(earnings=v))
    for field in ('ordinary_shares','preferred_shares'):
        add('zero/'+field,'rejected','number_domain',lambda r,k=field:r.update({k:'0'}))
        add('fractional/'+field,'unsupported','whole_period_share_population',lambda r,k=field:r.update({k:'3/2'}))
    for field in ('residual_weight','senior_entitlement','total_preferred_cap'):
        add('negative/'+field,'rejected','number_domain',lambda r,k=field:r.update({k:'-1'}))
    add('cap-below-senior','rejected','cap_below_senior',lambda r:r.update(total_preferred_cap='19'))
    add('negative-gross','unsupported','negative_gross_effect',lambda r:r['series'][0].update(gross_after_tax_adjustment='-1'))
    add('zero-increment','rejected','number_domain',lambda r:r['series'][0].update(ordinary_share_increment='0'))
    add('missing-effect','unresolved','missing_gross_after_tax_adjustment',lambda r:r['series'][0].update(gross_after_tax_adjustment=None))
    add('duplicate-series','rejected','series_identity',lambda r:r['series'].append(deepcopy(r['series'][0])))
    add('empty-series-id','rejected','series_identity',lambda r:r['series'][0].update(id=''))
    add('spaced-series-id','rejected','series_identity',lambda r:r['series'][0].update(id=' debt '))
    add('invalid-date','rejected','date_encoding',lambda r:r['series'][0].update(start='2025-02-30'))
    add('partial-period','unsupported','partial_period_series',lambda r:r['series'][0].update(start='2025-02-01'))
    add('effect-omitted','rejected','series_shape',lambda r:r['series'][0].pop('gross_after_tax_adjustment'))
    add('conditional-terms','rejected','series_shape',lambda r:r['series'][0].update(requires='option'))
    add('unknown-field','rejected','request_shape',lambda r:r.update(prior_arrears='20'))
    add('wrong-context','rejected','context',lambda r:r['context'].update(book='legal'))
    add('wrong-wire','rejected','wire',lambda r:r.update(wire='OrderedEPS/1'))
    add('post','rejected','report_only',lambda r:r.update(operation='post'))
    add('finding-not-bool','rejected','finding_encoding',lambda r:r['findings'].update(rights_fixed=1))
    add('series-not-list','rejected','series_shape',lambda r:r.update(series={}))
    for case in adverse:
        req = case['request']; before = deepcopy(req); r = calculate(req)
        case['actual'] = r
        check(case['id']+'/refusal', (r['status'],r['reason']) == (case['expected_status'],case['expected_reason']))
        check(case['id']+'/atomic', req == before and r['basic'] is None and r['diluted'] is None and r['trace'] == r['selected'] == r['mutations'] == [])
    def missing(_):
        raise FileNotFoundError(SOURCE)
    challenges = []
    for name, reader, status, reason in [('missing',missing,'unresolved','source_unavailable'),('changed',lambda _:b'changed','rejected','source_changed')]:
        r = calculate(baseline, reader)
        check('source/'+name, r['status'] == status and r['reason'] == reason and r['basic'] is None and r['diluted'] is None and r['trace'] == r['selected'] == r['mutations'] == [])
        challenges.append(dict(id=name,result=r))
    summary = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), attempt=attempt.name,
        checks=len(checks), failures=sum(not c['passed'] for c in checks), failed=[c for c in checks if not c['passed']],
        cases=len(cases), subset_worlds=sum(len(x['worlds']) for x in enumeration), adverse_inputs=len(adverse), source_challenges=len(challenges),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/capped-participation-20261016/verify.py',
        environment=sys.executable+'; standard library/Fraction; no ML import', gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES') == '-1' else 'not hidden',
        random_seeds='N/A deterministic', data_version='18 frozen authored cases; input-lock.json',
        wall_seconds=round(time.monotonic()-started,3), plan='docs/plans/accounting-capped-participation-20261016.md',
        result=str((OUT/'result.md').relative_to(ROOT)),outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','subsets.json','adverse.json','source-challenges.json')])
    for name,value in [('checks.json',dict(summary=summary,checks=checks)),('exchanges.json',exchanges),('subsets.json',enumeration),('adverse.json',adverse),('source-challenges.json',challenges),('run-manifest.json',summary)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','cases','subset_worlds','adverse_inputs','source_challenges','wall_seconds')}))
    if summary['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
