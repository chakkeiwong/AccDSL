from copy import deepcopy
from datetime import date, datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import shared_book_statements_v1 as statements
book = statements.book
native = book.returns.structure.native
LOCK = 'b1c37cd2e46c63956de3478234ea02b270cad662b158c5e649aa34cd0c1849fc'
def sha(p): return sha256(p.read_bytes()).hexdigest()
def same(a,b): return book.caller.canonical(a) == book.caller.canonical(b)
def dump(name,value): (HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def conformance():
    checks=[]
    def check(name,ok):
        assert ok,name
        checks.append(name)
    check('source_lock',sha(HERE/'source-lock.json')==LOCK)
    locks=json.loads((HERE/'source-lock.json').read_text())
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    native_rows=json.loads((ROOT/'data/accounting-master/company-return-execution-20261024/trace.json').read_text())['trace']
    controls=[]
    for i,row in enumerate(native_rows):
        if row['event']['kind']!='tax':continue
        before=deepcopy(native_rows[i-1]['proposal']['after']);event=deepcopy(row['event'])
        original=book.digest(before)
        proposal=native.propose(before,event)
        check(row['id']+':complete_proposal',same(proposal,row['proposal']))
        after=native.apply(before,event,proposal)
        check(row['id']+':complete_state',same(after,row['proposal']['after']))
        check(row['id']+':immutable',book.digest(before)==original)
        controls.append({'case':row['id'],'before':before,'event':event,'proposal':proposal})
    check('two_original_controls',len(controls)==2)
    saved=json.loads((ROOT/'data/accounting-master/shared-book-statements-20261024/cases.json').read_text())
    row=next(x for x in saved if x['case']=='mixed_lifecycle');request=row['request']
    check('complete_mixed_replay',same(statements.calculate(request),row['result']))
    mixed=deepcopy(row['result']['execution']['after']);identity=book.digest(mixed)
    try:native.propose(mixed,controls[-1]['event'])
    except native.Rejected as exc:direct={'status':exc.status,'reason':exc.reason}
    else:raise AssertionError('unexpected direct tax admission')
    check('direct_reuse_closed_state_refusal',direct=={'status':'invalid','reason':'closed state fields'})
    check('refusal_preserves_state',book.digest(mixed)==identity)
    original_income=set(native.INCOME)-{'current_tax','deferred_tax'}
    shared_income=set(statements.INCOME)-{'current_tax','deferred_tax'}
    old_profit=native.pretax(mixed['balances'])
    shared_profit=-sum(Q(mixed['balances'][k]) for k in shared_income)
    missing=sorted(shared_income-original_income)
    check('omitted_income_exactly_lease_gain',missing==['other_gains'])
    check('original_scope_profit',old_profit==Q(-15))
    check('shared_scope_profit',shared_profit==Q(5))
    check('omitted_gain_difference',shared_profit-old_profit==-Q(mixed['balances']['other_gains'])==Q(20))
    adjustments=sum(Q(x['amount']) for x in mixed['tax_adjustments'])
    check('retained_return_adjustment',adjustments==Q(-24))
    # Arithmetic diagnostics only: lease tax bases and recognition are absent.
    old_mechanical=(old_profit+adjustments)*Q(1,4)
    complete_mechanical=(shared_profit+adjustments)*Q(1,4)
    check('mechanical_difference',complete_mechanical-old_mechanical==Q(5))
    check('both_need_loss_route',old_mechanical<0 and complete_mechanical<0)
    day_before=deepcopy(mixed);day_before['date']='2025-12-31'
    book.invariant(day_before)
    incompatible=deepcopy(day_before);incompatible['tax_closed_until']='2026-01-01'
    try:book.invariant(incompatible)
    except book.Refused as exc:timing={'status':exc.status,'reason':exc.reason}
    else:raise AssertionError('unexpected exclusive-close admission')
    check('exclusive_close_timing_conflict',timing=={'status':'invalid','reason':'tax_close_date'})
    rights=[r for item in mixed['leases'] for r in item['component']['rights']]
    check('remaining_rou_needs_tax_basis',sum(Q(r['rou']) for r in rights)==Q(90))
    check('lease_tax_basis_not_in_state',all('tax_base' not in r for r in rights))
    check('no_tax_or_period_completion',row['result']['coverage']['tax_assessment']==row['result']['coverage']['annual_completion']=='unresolved')
    period_days=(date.fromisoformat(mixed['period']['end_exclusive'])-date.fromisoformat(mixed['period']['start'])).days
    check('declared_period_spans_two_calendar_years',period_days==731)
    diagnosis={'direct_native_refusal':direct,'unchanged_state_sha256':identity,
        'income_coverage':{'original_accounts':sorted(original_income),'shared_accounts':sorted(shared_income),
            'omitted_accounts':missing,'original_function_on_shared_balances':native.fmt(old_profit),
            'complete_shared_pretax':native.fmt(shared_profit),'difference':native.fmt(shared_profit-old_profit)},
        'arithmetic_diagnostic_only':{'return_adjustment':native.fmt(adjustments),
            'original_fixture_rate':'1/4','omitted_income_formula':native.fmt(old_mechanical),
            'complete_income_formula':native.fmt(complete_mechanical),
            'actual_tax_assessed':False,'meaning':'Mechanical reuse is not a valid mixed-book tax assessment'},
        'exclusive_close':{'before':day_before,'candidate':incompatible,'result':timing},
        'period_scope':{'declared':mixed['period'],'days':period_days,
            'interpretation':'Two calendar years; an annual tax/reporting interval is not established'},
        'missing_facts':['Lease-right tax bases and deduction timing','Tax treatment of lease modification gain',
            'Current-tax loss/refund or carryforward route','Deferred-tax recognition and recovery evidence',
            'Complete fiscal-period activity and source admission'],
        'direct_reuse':'rejected','research_direction':'continue with explicit tax facts and separate timing design',
        'actual_accounting_admission':False,'annual_close_ready':False}
    return {'passed':True,'checks':len(checks),'protected_files':len(locks),'native_tax_controls':len(controls),
            'direct_reuse':'rejected','continuation_veto':False,'whole_requirements_closed':0},checks,controls,diagnosis


def main():
    start=time.monotonic();mode=sys.argv[1] if len(sys.argv)>1 else '--check'
    assert mode in ['--check','--record','--replay']
    if mode=='--record':assert not (HERE/'manifest.json').exists(),'already recorded'
    report,checks,controls,diagnosis=conformance()
    outputs={'checks.json':report,'check-names.json':checks,'native-tax-controls.json':controls,'diagnosis.json':diagnosis}
    if mode=='--record':
        for name,value in outputs.items():dump(name,value)
        files=[p for p in HERE.iterdir() if p.is_file()]
        dump('manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'recorded_at':datetime.now(timezone.utc).isoformat(),'command':'python3 -B data/accounting-master/shared-tax-compatibility-20261024/verify.py --record',
            'environment':{'python':platform.python_version(),'executable':sys.executable},
            'cpu_gpu':'CPU-only; no GPU framework imported','random_seeds':'N/A: deterministic checks',
            'wall_seconds':time.monotonic()-start,'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-shared-tax-compatibility-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'files':{str(p.relative_to(ROOT)):sha(p) for p in files}})
    elif mode=='--replay':
        for name,value in outputs.items():assert same(value,json.loads((HERE/name).read_text())),name
        for name,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/name)==h,name
    print(json.dumps(report))


if __name__=='__main__':main()
