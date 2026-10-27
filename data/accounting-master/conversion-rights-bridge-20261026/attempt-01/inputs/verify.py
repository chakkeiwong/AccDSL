"""Bounded one-shot exact conversion composition evidence."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import traceback
import bridge

HERE, ROOT, runtime = bridge.HERE, bridge.ROOT, bridge.runtime
PLAN='docs/plans/accounting-conversion-rights-bridge-20261026.md'
CHECKS,CASES,CONTROLS=[],[],[]
spec=importlib.util.spec_from_file_location('conversion_independent_strategy_reference',HERE.parent/'two-date-financing-control-20261026/exhaustive_reference.py')
reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)


def encode(v):
    if isinstance(v,F):return str(v)
    if isinstance(v,dict):return {k:encode(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [encode(x) for x in v]
    return v


def save(path,value):path.write_text(json.dumps(encode(value),indent=2,sort_keys=True)+'\n')
def fmt(value):
    v=F(value);return f'{v.numerator}/{v.denominator}'
def check(name,actual,expected=True):
    CHECKS.append(dict(id=name,passed=actual==expected,actual=encode(actual),expected=encode(expected)))
    if actual!=expected:raise AssertionError(name)


def expected_state(body,mapping,carrying,branch):
    after=deepcopy(body['opening'])
    after['seen']=['signal.'+branch]
    state=after['memory']['financing']
    state.update(observed=True,signal=branch)
    journal={key:'0/1' for key in after['accounts']}
    if branch=='conversion':
        state.update(face='0/1',new_shares='120/1',converted=True)
        after['balances'][mapping['convertible']]='0/1'
        after['balances'][mapping['issued_equity']]=fmt(-F(carrying))
        journal[mapping['convertible']]=fmt(carrying)
        journal[mapping['issued_equity']]=fmt(-F(carrying))
    return after,journal


def expected_report(body,after,mapping,carrying,branch,request):
    opening=body['opening'];classes=['asset','liability','equity','income','expense']
    lines={c:[] for c in classes}
    for line in body['mapping']['lines']:
        sign=-1 if line['classification'] in ('liability','equity','income') else 1
        account=line['accounts'][0]
        lines[line['classification']].append({**deepcopy(line),'opening':fmt(sign*F(opening['balances'][account])),'closing':fmt(sign*F(after['balances'][account]))})
    c=F(carrying);converted=branch=='conversion'
    start=dict(asset=F(100),liability=40+c,equity=60-c,income=F(0),expense=F(0))
    end=dict(asset=F(100),liability=F(40) if converted else 40+c,equity=F(60) if converted else 60-c,income=F(0),expense=F(0))
    movements=deepcopy(body['commands'][-1]['equity_movements'])
    return dict(profile='CompanyBookReport/1',**runtime.reports.FLAGS,status='reported',scope='recorded_period_only',
        context=deepcopy(after['context']),period=deepcopy(after['period']),as_of='2028-01-01',statement_lines=lines,
        opening_totals={k:fmt(v) for k,v in start.items()},closing_totals={k:fmt(v) for k,v in end.items()},
        balance_sheet=dict(total_assets='100/1',total_liabilities=fmt(end['liability']),equity_including_profit=fmt(end['equity'])),
        income=dict(income='0/1',expenses='0/1',profit='0/1'),
        cash_flows=dict(activities={a:dict(receipts='0/1',payments='0/1',net='0/1') for a in ('operating','investing','financing')},opening_cash='0/1',closing_cash='0/1',net_movement='0/1',gross_origins=[]),
        equity=dict(opening=fmt(60-c),direct_movements=fmt(c if converted else 0),profit='0/1',closing=fmt(end['equity']),
                    by_account={mapping['capital']:'0/1',mapping['issued_equity']:fmt(c if converted else 0)},movements=movements),
        reconciliations=dict(balance_sheet='0/1',cash='0/1',equity='0/1'),notes=deepcopy(body['commands'][-1]['notes']),
        unresolved=['Event-population completeness','Source and accounting admission','Complete note package','Indirect operating cash-flow bridge'],
        request_sha256=runtime.digest(request),opening_sha256=runtime.digest(opening),closing_sha256=runtime.digest(after),mapping_sha256=runtime.digest(body['mapping']),
        implementation_sha256=hashlib.sha256(Path(runtime.reports.__file__).read_bytes()).hexdigest(),book_sha256=runtime.reports.BOOK_SHA256)


def exercise():
    prior=HERE.parent/'two-date-financing-control-20261026'
    model=json.loads((prior/'model.json').read_text())
    table=json.loads((prior/'independent-payoffs.json').read_text())
    oracle=reference.enumerate_strategies(table)
    for chart in ('alpha','beta'):
        for carrying in ('80','17000/441'):
            rights={}
            for branch in ('debt','conversion'):
                body,mapping=bridge.make(chart,carrying,branch)
                original=deepcopy(body)
                actual=runtime.run(body)
                label=f'{chart}:{carrying}:{branch}'
                CASES.append(dict(id=label,input=body,result=actual))
                check(label+':complete',actual['status'],'complete_provisional')
                check(label+':input_preserved',body,original)
                after,journal=expected_state(body,mapping,carrying,branch)
                transition=actual['trace'][0]['result']['transition']
                check(label+':complete_state',transition['after'],after)
                check(label+':complete_journal',transition['journal'],journal)
                check(label+':flows',transition['flows'],[])
                check(label+':final_state',actual['current'],after)
                command=body['commands'][-1]
                request=runtime.reports.request(body['opening'],after,body['schemas'],body['mapping'],command['equity_movements'],command['notes'])
                report=expected_report(body,after,mapping,carrying,branch,request)
                check(label+':complete_report',actual['trace'][-1]['result'],report)
                state_rights=bridge.project_rights(after,mapping)
                check(label+':complete_rights',state_rights,oracle['branches'][branch]['rights'])
                check(label+':payoffs_from_rights',bridge.decision.branch_payoffs(model,branch,state_rights),oracle['branches'][branch]['policies'])
                rights[branch]=state_rights
                check(label+':no_admission',actual['accounting_admission'],False)
            controllers={k:v['controller'] for k,v in rights.items()}
            check(f'{chart}:{carrying}:controllers',controllers,{'debt':'old','conversion':'new'})
            # Complete rights equality makes the prechecked decision applicable; no repricing of carrying amounts.
            check(f'{chart}:{carrying}:strategy',bridge.decision.analyze(model)['strategies'],oracle['strategies'])
    adverse_controls()


def adverse_controls():
    body,mapping=bridge.make();after,_=expected_state(body,mapping,'80','conversion')
    def refusal(name,mutate,prefix=False):
        changed=deepcopy(body);mutate(changed)
        for entry in changed['registry']['entries'].values():
            entry['method_sha256']=runtime.digest(entry['method'])
        result=runtime.run(changed)
        CONTROLS.append(dict(id=name,input=changed,result=result))
        check(name+':refused',result['status']!='complete_provisional')
        if 'current' in result:
            check(name+':atomic',result['current'],after if prefix else body['opening'])
    method=lambda b:b['registry']['entries']['conversion']['method']
    def drop(b,field):
        ops=method(b)['memory']['definition']['operations']
        ops[:]=[x for x in ops if x['path']!=['financing',field]]
    refusal('missing_face_extinction',lambda b:drop(b,'face'))
    refusal('missing_share_issue',lambda b:drop(b,'new_shares'))
    refusal('missing_conversion_flag',lambda b:drop(b,'converted'))
    refusal('wrong_signal',lambda b:b['commands'][0]['event']['inputs']['signal_input']['value'].update(value='debt'))
    refusal('late_conversion',lambda b:b['commands'][0]['event'].update(date='2028-01-02'))
    refusal('not_approved',lambda b:b['commands'][0]['event']['inputs']['approved']['value'].update(value=False))
    refusal('unbalanced_reclass',lambda b:method(b)['monetary']['definition']['postings'].pop())
    def invented_cash(b):
        method(b)['monetary']['definition']['postings'][1]['account']='cash'
    refusal('invented_cash_without_flow',invented_cash)
    def repeat(b):
        event=deepcopy(b['commands'][0]);event['event']['id']='conversion.again'
        b['commands'].insert(1,event)
    refusal('duplicate_conversion_fresh_id',repeat,True)
    refusal('unexplained_equity_reclass',lambda b:b['commands'][-1].update(equity_movements=[]),True)
    for name,mutate in [('stale_face',lambda s:s['memory']['financing'].update(face='80/1')),
                        ('lost_shares',lambda s:s['memory']['financing'].update(new_shares='0/1')),
                        ('unobserved',lambda s:s['memory']['financing'].update(observed=False)),
                        ('stale_carrying',lambda s:s['balances'].update({mapping['convertible']:'-80/1'}))]:
        changed=deepcopy(after);mutate(changed)
        try:bridge.project_rights(changed,mapping)
        except ValueError as exc:reason=str(exc)
        else:reason='accepted'
        CONTROLS.append(dict(id=name,result=reason))
        check(name+':projection_refused',reason!='accepted')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True);args=parser.parse_args()
    if not re.fullmatch(r'attempt-0[123]',args.attempt):raise SystemExit('invalid attempt')
    out=HERE/args.attempt;out.mkdir(exist_ok=False);start=time.monotonic()
    sources={ROOT/PLAN,HERE/'bridge.py',HERE/'verify.py'}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).resolve().is_relative_to(ROOT) and Path(path).suffix=='.py':sources.add(Path(path).resolve())
    prior=HERE.parent/'two-date-financing-control-20261026'
    sources.update(prior/name for name in ('model.json','independent-payoffs.json','attempt-01/verification.json','attempt-01/source-lock.json','result.md'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}
    save(out/'source-lock.json',hashes)
    inputs=out/'inputs';inputs.mkdir()
    for path in (ROOT/PLAN,HERE/'bridge.py',HERE/'verify.py'):(inputs/path.name).write_bytes(path.read_bytes())
    status,error='FAIL',None
    try:
        check('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1')
        check('bytecode_disabled',os.environ.get('PYTHONDONTWRITEBYTECODE'),'1')
        old_lock=json.loads((prior/'attempt-01/source-lock.json').read_text())
        for path,digest in old_lock.items():check('predecessor_'+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
        exercise()
        for path,digest in hashes.items():check('unchanged_'+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
        status='PASS'
    except Exception:
        error=traceback.format_exc();(out/'error.txt').write_text(error)
    elapsed=time.monotonic()-start
    save(out/'cases.json',CASES);save(out/'controls.json',CONTROLS);save(out/'checks.json',CHECKS)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    save(out/'run-manifest.json',dict(status=status,command=f'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 {HERE.relative_to(ROOT)}/verify.py --attempt {args.attempt}',
        git_commit=git.stdout.strip(),python=platform.python_version(),executable=sys.executable,environment='standard-library CPU; CUDA_VISIBLE_DEVICES=-1; GPU intentionally hidden',
        seed='N/A exact conformance',data_version='Selected conversion fixture; source-lock.json',wall_seconds=elapsed,plan=PLAN,result=str(HERE.relative_to(ROOT)/'result.md'),
        artifact_paths=['cases.json','checks.json','controls.json','source-lock.json','verification.json'],attempt=args.attempt,attempt_budget=3,cpu_seconds_budget=300))
    result=dict(status=status,cases=len(CASES),controls=len(CONTROLS),assertions=len(CHECKS),protected_files=len(hashes),wall_seconds=elapsed,error=error)
    save(out/'verification.json',result);print(json.dumps(result));return 0 if status=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
