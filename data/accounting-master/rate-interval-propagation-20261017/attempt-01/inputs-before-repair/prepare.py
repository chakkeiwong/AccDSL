"""Author successor requests and minimally extend protected numerical modules."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'data/accounting-master/dated-credit-schedules-20261016'


def write(name, value):
    p = OUT / name
    assert not p.exists(), p
    p.write_text(json.dumps(value, indent=2) + '\n')


def successor(req):
    r = deepcopy(req)
    r['wire'] = r['wire'].replace('Schedule/1', 'IntervalSchedule/1')
    r['acquisition'].pop('rate')
    r['acquisition']['rate_search'] = dict(lower='-1/2', upper='1/2', max_width='1/1000000000000')
    r['numerical'].update(max_width='1/10000000')
    return r


def main():
    old = json.loads((PRIOR / 'authored-cases.json').read_text())['cases']
    templates = {c['id']: c for c in old}
    cases = []
    for name, profit in [('partial-early-writeoff','0'), ('unchanged-annual','10'),
                         ('adverse-without-no-recovery-finding','-12'), ('full-early-writeoff','-100'),
                         ('performing-prepayment','5'), ('negative-rate','-10')]:
        r = successor(templates[name]['request'])
        negative = name == 'negative-rate'
        r['acquisition']['expected'] = {'2026-01-01':'40','2027-01-01':'50'} if negative else {'2026-01-01':'50','2027-01-01':'60'}
        r['acquisition']['contract'] = ({'2026-01-01':'60','2027-01-01':'72'} if r['wire'].startswith('POCI') else deepcopy(r['acquisition']['expected']))
        for e in r['events']:
            if e['operation'] == 'credit_revision' and e['id'] != 'full':
                e['expected'] = {'2027-01-01':'60'} if e['id'] == 'improvement' else {'2026-01-01':'40','2027-01-01':'48'}
            if e['operation'] == 'collect':
                if name == 'performing-prepayment': continue
                e['amount'] = ('40' if e['id'] == 'first' else '60') if name == 'partial-early-writeoff' else (
                    ('40' if e['id'] == 'first' else '48') if name.startswith('adverse') else r['acquisition']['expected'][e['date']])
        targets = dict(final_cash=str(300+int(profit)), final_profit=profit,
                       rate_expression='(sqrt(54)-8)/10' if negative else '(sqrt(265)-15)/20')
        if name == 'partial-early-writeoff':
            targets['stages'] = {'july': {'gross':'80*f','net':'80*f','allowance':'0','impairment':'-20*f'},
                'first':{'gross':'48/x','net':'48/x','allowance':'0'},
                'improvement':{'gross':'48/x','net':'60/x','allowance':'-12/x'},
                'final_accrual':{'gross':'48','net':'60','allowance':'-12','profit':'0'}}
        cases.append(dict(id=name, request=r, expected=targets))
    write('authored-cases.json', dict(cases=cases,
        analytic_definitions='Positive case x=(5+sqrt(265))/20; negative x=(2+sqrt(54))/10; f=x^(181/365).'))
    write('regression-requests.json', dict(cases=[dict(id=c['id'], request=successor(c['request']), expected=c['expected']) for c in old]))
    paths = [ROOT/'docs/plans/accounting-rate-interval-propagation-20261017.md', OUT/'source-reading.md', OUT/'authored-cases.json', OUT/'regression-requests.json',
             ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt']
    paths += [PRIOR/n for n in ('bounds.py','reference.py','authored-cases.json','input-lock.json','source-reading.md')]
    write('input-lock.json', dict(files=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]))
    text = (PRIOR/'bounds.py').read_text()
    text = text.replace('def between(r,s,t,scale):return factor(Q(r),(day(t)-day(s)).days,scale)', '''def between(r,s,t,scale):
    days=(day(t)-day(s)).days
    if isinstance(r,I):
        return I(factor(r.lo,days,scale).lo, factor(r.hi,days,scale).hi)
    return factor(Q(r),days,scale)''')
    assert 'if isinstance(r,I)' in text
    (OUT/'bounds.py').write_text(text)
    text = (PRIOR/'reference.py').read_text()
    text = text.replace('from bounds import I,day,between,pv', 'from bounds import I,day,between,pv,solve_rate')
    text = text.replace('POCIDatedSchedule/1','POCIDatedIntervalSchedule/1').replace('PerformingEIRSchedule/1','PerformingEIRIntervalSchedule/1')
    text = text.replace("'fee_received','rate','contract'", "'fee_received','rate_search','contract'")
    text = text.replace("r=number(a['rate'],'rate');initial=price+cost-fee;opening=positive(req['opening_cash'],'opening_cash')", "initial=price+cost-fee;opening=positive(req['opening_cash'],'opening_cash')")
    text = text.replace("if r<=-1 or r>10 or initial<=0:fail('acquisition_domain')", "if initial<=0:fail('acquisition_domain')")
    text = text.replace("    residual=pv(expected,t,r,scale)-initial\n    if residual.lo < -tol or residual.hi>tol:fail('initial_pv_mismatch')", '''    search=a['rate_search'];shape(search,{'lower','upper','max_width'},'rate_search_shape')
    low=number(search['lower'],'rate_lower');high=number(search['upper'],'rate_upper')
    width=positive(search['max_width'],'rate_width')
    if low<=-1 or high>10 or low>=high or not 0<width<=Q(1,1000):fail('rate_search_domain','unsupported')
    try:certificate=solve_rate(expected,t,initial,low,high,width,scale)
    except ValueError as error:fail(str(error),'unsupported')
    r=I(Q(certificate['rate']['lower']),Q(certificate['rate']['upper']))
    residual=pv(expected,t,r,scale)-initial
    if not residual.contains(0):fail('initial_pv_certificate_mismatch')''')
    text = text.replace("initial_pv_residual=residual,initial_credit_shortfall=", "rate_certificate=certificate,shared_rate=r,interval_semantics='one immutable original root; marginal enclosures are not independently selectable amounts',\n                        initial_pv_residual=residual,initial_credit_shortfall=")
    text = text.replace("reason='finite_dated_profile'", "reason='finite_dated_interval_profile'")
    text = text.replace('# Initial rate tolerance propagates; no claim that tolerance means exact equality.', '# Root equality is certified; interval widths include numerical dependence inflation.')
    assert "a['rate']" not in text and 'initial_pv_certificate_mismatch' in text
    (OUT/'reference.py').write_text(text)
    print(json.dumps(dict(authored_cases=len(cases), regression_cases=len(old), protected_inputs=len(paths))))


if __name__ == '__main__':
    main()
