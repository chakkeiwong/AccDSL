"""Independent analytic targets, predecessor regressions and numerical vetoes."""
from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import ast
import hashlib
import importlib.util
import json
from math import isqrt
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'data/accounting-master/dated-credit-schedules-20261016'
import reference
from bounds import I


def dec(x):
    q = Q(x)
    return Decimal(q.numerator) / Decimal(q.denominator)


def interval(w):
    return I(Q(w['lower']), Q(w['upper']))


def expression(s, x, f):
    def walk(n):
        if isinstance(n, ast.Constant): return Decimal(n.value)
        if isinstance(n, ast.Name): return {'x':x, 'f':f}[n.id]
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub): return -walk(n.operand)
        if isinstance(n, ast.BinOp):
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Add): return a+b
            if isinstance(n.op, ast.Sub): return a-b
            if isinstance(n.op, ast.Mult): return a*b
            if isinstance(n.op, ast.Div): return a/b
        raise ValueError('Unexpected authored expression')
    return walk(ast.parse(s, mode='eval').body)


def main():
    started = time.monotonic()
    numbers = [int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    dest = OUT / ('attempt-%02d' % (max(numbers, default=0)+1)); dest.mkdir()
    checks, reports = [], {}
    def check(name, ok, detail=None):
        row = dict(name=name, passed=bool(ok))
        if detail is not None: row['detail'] = detail
        checks.append(row)
    def contains(name, w, value):
        value = Decimal(value)
        # Diagnostic Decimal precision is far below certified enclosure widths.
        check(name, dec(w['lower'])-Decimal('1e-65') <= value <= dec(w['upper'])+Decimal('1e-65'))
    cases = json.loads((OUT/'authored-cases.json').read_text())['cases']
    regression = json.loads((OUT/'regression-requests.json').read_text())['cases']
    original = json.loads((PRIOR/'authored-cases.json').read_text())['cases']
    roots = {}
    with localcontext() as context:
        context.prec = 80
        for name, radicand, shift, denominator in [('positive',265,5,20),('negative',54,2,10)]:
            grid = 10**80; k = isqrt(radicand*grid*grid)
            check(name+'/sqrt-integer-certificate', k*k <= radicand*grid*grid < (k+1)*(k+1))
            roots[name] = (Decimal(radicand).sqrt()+shift)/denominator
        for case in cases+regression:
            is_regression = case in regression
            ident = ('regression/' if is_regression else 'new/')+case['id']
            result = reference.calculate(case['request']); reports[ident] = result
            check(ident+'/accepted', result['status']=='conditional_complete', result.get('reason'))
            if result['status'] != 'conditional_complete': continue
            if is_regression:
                old = next(c for c in original if c['id']==case['id'])
                x = 1+dec(old['request']['acquisition']['rate'])
            else: x = roots['negative' if case['id']=='negative-rate' else 'positive']
            f = x ** (Decimal(181)/365)
            cert = result['rate_certificate']
            contains(ident+'/analytic-rate', cert['rate'], x-1)
            check(ident+'/endpoint-signs', Q(cert['low_pv_residual']['lower'])>=0 and Q(cert['high_pv_residual']['upper'])<=0)
            check(ident+'/root-width', interval(cert['rate']).width<=Q(case['request']['acquisition']['rate_search']['max_width']))
            check(ident+'/shared-origin', 'one immutable original root' in result['interval_semantics'])
            check(ident+'/not-posted', result['posts'] is False and result['mutations']==[])
            for key in ('cash','profit'):
                contains(ident+'/final-'+key, result['closing'][key], dec(case['expected']['final_'+key]))
            for stage in result['stages']:
                at = stage['date']; pv = sum((dec(v)/x**(Decimal((date.fromisoformat(d)-date.fromisoformat(at)).days)/365) for d,v in stage['expected'].items()), Decimal(0))
                contains(ident+'/'+stage['id']+'/direct-net-pv', stage['net'], pv)
                for field,w in stage.items():
                    if isinstance(w,dict) and set(w)=={'lower','upper','width','exact'}:
                        check(ident+'/'+stage['id']+'/'+field+'/width', interval(w).width<=Q(case['request']['numerical']['max_width']))
                balance=interval(stage['cash'])+interval(stage['net'])-interval(stage['equity'])
                check(ident+'/'+stage['id']+'/balance-enclosure', balance.contains(0))
            stages={s['id']:s for s in result['stages']}
            for stage,fields in case['expected'].get('stages',{}).items():
                for field,value in fields.items():
                    if isinstance(value,dict): target=dec(value['f_coefficient'])*f+dec(value['constant'])
                    else: target=expression(value,x,f)
                    contains(ident+'/'+stage+'/'+field+'/authored',stages[stage][field],target)
            for journal in result['journals']:
                total=sum((interval(w) for w in journal['entries'].values()),I.point(0))
                check(ident+'/journal/'+journal['id'],total.contains(0))
        # The predecessor remains an independently executable comparator.
        new_bounds = sys.modules['bounds']
        def module(name,path):
            spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
        module('bounds',PRIOR/'bounds.py')
        oldref=module('protected_reference',PRIOR/'reference.py')
        for case in original:
            result=oldref.calculate(case['request']);new=reports['regression/'+case['id']]
            check('predecessor/'+case['id'],result['status']=='conditional_complete')
            if result['status']!='conditional_complete' or new['status']!='conditional_complete':continue
            for a,b in zip(result['stages'],new['stages']):
                for key in ('gross','allowance','net','interest','impairment','catchup','profit','cash','equity'):
                    check('predecessor/'+case['id']+'/'+a['id']+'/'+key, interval(a[key]).overlaps(interval(b[key])))
        sys.modules['bounds']=new_bounds
        # Strong target checks supplement overlap regressions.
        main_result=reports['new/partial-early-writeoff']
        if main_result['status']=='conditional_complete':
            stage=next(s for s in main_result['stages'] if s['id']=='final_accrual')
            for field,wrong in [('gross',60),('allowance',0),('net',48),('profit',12)]:
                check('wrong-target-excluded/'+field,not interval(stage[field]).contains(wrong))
        altered=deepcopy(cases[1]['request']);altered['acquisition']['cost']='0'
        alt=reference.calculate(altered);reports['fee-omitted']=alt
        check('fee-omission-changes-rate',alt['status']=='conditional_complete' and not interval(alt['shared_rate']).overlaps(interval(reports['new/unchanged-annual']['shared_rate'])))
        tight=deepcopy(cases[0]['request']);tight['acquisition']['rate_search']['max_width']='1/100000000000000'
        tighter=reference.calculate(tight);reports['tighter-root']=tighter
        check('tighter-root-accepted',tighter['status']=='conditional_complete')
        if tighter['status']=='conditional_complete':
            oldstage=next(s for s in main_result['stages'] if s['id']=='july');newstage=next(s for s in tighter['stages'] if s['id']=='july')
            check('tighter-root-reduces-net-width',interval(newstage['net']).width<interval(oldstage['net']).width)
        adverse=[]
        def bad(name,change):
            req=deepcopy(cases[0]['request']);change(req);res=reference.calculate(req)
            adverse.append(dict(id=name,result=res))
            check('adverse/'+name,res['status']!='conditional_complete' and res['closing'] is None and not res['stages'] and res['posts'] is False)
        bad('invalid-rate-domain',lambda r:r['acquisition']['rate_search'].update(lower='-1'))
        bad('bracket-excludes-root',lambda r:r['acquisition']['rate_search'].update(lower='1/5'))
        bad('reversed-bracket',lambda r:r['acquisition']['rate_search'].update(lower='3/4'))
        bad('zero-root-width',lambda r:r['acquisition']['rate_search'].update(max_width='0'))
        bad('wide-state',lambda r:r['acquisition']['rate_search'].update(max_width='1/1000'))
        bad('sign-changing-cash',lambda r:r['acquisition']['expected'].update({'2027-01-01':'-60'}))
        bad('no-expected-cash',lambda r:r['acquisition'].update(expected={}))
        bad('same-day-initial',lambda r:r['acquisition']['expected'].update({'2025-01-01':'1'}))
        bad('rounded-initial-tolerance',lambda r:r['numerical'].update(initial_pv_tolerance='1/1000'))
        bad('missing-no-recovery',lambda r:r['events'][0]['writeoff'].update(no_reasonable_recovery=None))
        bad('future-information',lambda r:r['events'][0].update(information_date='2027-01-01'))
        bad('changed-calendar',lambda r:r['context'].update(calendar='ACT/360'))
        bad('wrong-terminal-cash',lambda r:r['events'][-1].update(amount='61'))
        bad('second-point-rate',lambda r:r['acquisition'].update(rate='1/10'))
        protected=json.loads((OUT/'input-lock.json').read_text())['files']
        for item in protected:
            def reader(p,target=item['path']): return (ROOT/p).read_bytes()+(b'changed' if p==target else b'')
            res=reference.calculate(cases[0]['request'],reader)
            check('protected/'+item['path'],res['status']=='rejected' and res['reason']=='changed_protected_input' and res['closing'] is None)
        widths={name:max((interval(w).width for s in report.get('stages',[]) for w in s.values() if isinstance(w,dict) and set(w)=={'lower','upper','width','exact'}),default=Q(0)) for name,report in reports.items()}
    failures=sum(not c['passed'] for c in checks)
    result=dict(checks=len(checks),failures=failures,authored_cases=len(cases),regression_cases=len(regression),adverse_cases=len(adverse),protected_input_challenges=len(protected),detail=checks,
                max_monetary_widths={k:str(v) for k,v in widths.items()},scope='Deterministic documentary numerical/accounting evidence; no empirical ranking')
    for name,value in [('checks.json',result),('reports.json',reports),('adverse.json',adverse)]:
        (dest/name).write_text(json.dumps(value,indent=2)+'\n')
    manifest=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='python3 data/accounting-master/rate-interval-propagation-20261017/verify.py',environment=sys.executable+'; standard library',
        gpu_status='N/A: no numerical framework or device calls',random_seeds='N/A: deterministic',data_version='authored-cases.json and protected predecessor',
        wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-rate-interval-propagation-20261017.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((dest/n).relative_to(ROOT)) for n in ('checks.json','reports.json','adverse.json')],
        executed_source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'reference.py',OUT/'bounds.py',Path(__file__))})
    (dest/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('checks','failures','authored_cases','regression_cases','adverse_cases','protected_input_challenges')}))
    if failures: print(json.dumps([c for c in checks if not c['passed']][:12]))
    raise SystemExit(bool(failures))


if __name__=='__main__':main()
