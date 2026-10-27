"""One-shot full-book and reciprocal funding comparisons."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
import hashlib
from itertools import permutations
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import traceback
import funding

HERE,ROOT,runtime=funding.HERE,funding.ROOT,funding.runtime
PLAN='docs/plans/accounting-dated-funding-bundle-20261026.md'
CHECKS,CASES,CONTROLS=[],[],[]


def fmt(x):
    x=F(x);return f'{x.numerator}/{x.denominator}'
def encode(v):
    if isinstance(v,F):return str(v)
    if isinstance(v,dict):return {k:encode(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [encode(x) for x in v]
    return v
def save(p,v):p.write_text(json.dumps(encode(v),indent=2,sort_keys=True)+'\n')
def check(name,actual,expected=True):
    CHECKS.append(dict(id=name,passed=actual==expected))
    if actual!=expected:raise AssertionError(name+': '+str(actual)[:250]+' != '+str(expected)[:250])


def expected(request,actor):
    book=deepcopy(request['books'][actor]);mapping=request['mapping'];q=F(17000,441);c=F(9460,441)
    changes={r:F(0) for r in funding.ROLES}
    if actor=='company':changes.update(project=F(60),convertible=-q,capital=-c);rows=[('new_issue','financing',q),('owner_contribution','financing',c),('investment_purchase','investing',F(-60))]
    elif actor=='owner':changes.update(cash=-c,investment=c);rows=[('owner_contribution','investing',-c)]
    elif actor=='new_holder':changes.update(cash=-q,investment=q);rows=[('new_issue','investing',-q)]
    else:changes.update(cash=F(60),project=F(-60));rows=[('investment_purchase','investing',F(60))]
    journal={mapping[r]:fmt(v) for r,v in changes.items()}
    for account,v in journal.items():book['balances'][account]=fmt(F(book['balances'][account])+F(v))
    event_id='funding.'+actor;book['seen']=[event_id];book['memory']['settled']=True
    if actor=='company':book['memory']['face']='80/1'
    book['flows']=[dict(id=runtime.digest([event_id,ident]),entity=book['context']['entity'],book=book['context']['book'],currency='USD',
                        event_id=event_id,date='2027-01-01',activity=activity,origin=ident,amount=fmt(amount)) for ident,activity,amount in rows]
    return book,journal


def expected_report(request,actor,after,program):
    opening=request['books'][actor];mapping=request['mapping'];groups={c:[] for c in ('asset','liability','equity','income','expense')}
    start={c:F(0) for c in groups};end={c:F(0) for c in groups}
    for role in funding.ROLES:
        cl=funding.CLASSES[role];sign=-1 if cl in ('liability','equity','income') else 1
        a=sign*F(opening['balances'][mapping[role]]);b=sign*F(after['balances'][mapping[role]])
        groups[cl].append(dict(id=role,label=role,classification=cl,accounts=[mapping[role]],opening=fmt(a),closing=fmt(b)));start[cl]+=a;end[cl]+=b
    activities={}
    for activity in ('operating','investing','financing'):
        flows=[F(f['amount']) for f in after['flows'] if f['activity']==activity]
        receipts=sum((x for x in flows if x>=0),F(0));payments=-sum((x for x in flows if x<0),F(0))
        activities[activity]=dict(receipts=fmt(receipts),payments=fmt(payments),net=fmt(receipts-payments))
    cash0=opening['balances'][mapping['cash']];cash1=after['balances'][mapping['cash']]
    movements=[] if actor!='company' else [dict(id='owner_contribution',event_id='funding.company',date='2027-01-01',account=mapping['capital'],amount='9460/441',description='Supplied owner capital contribution')]
    notes=[dict(id='scope',label='Synthetic funding',status='unresolved',reason=funding.SCOPE)]
    report_request=runtime.reports.request(opening,after,program['schemas'],program['mapping'],movements,notes)
    return dict(profile='CompanyBookReport/1',**runtime.reports.FLAGS,status='reported',scope='recorded_period_only',context=deepcopy(after['context']),period=deepcopy(after['period']),as_of='2027-01-01',
        statement_lines=groups,opening_totals={k:fmt(v) for k,v in start.items()},closing_totals={k:fmt(v) for k,v in end.items()},
        balance_sheet=dict(total_assets=fmt(end['asset']),total_liabilities=fmt(end['liability']),equity_including_profit=fmt(end['equity'])),income=dict(income='0/1',expenses='0/1',profit='0/1'),
        cash_flows=dict(activities=activities,opening_cash=cash0,closing_cash=cash1,net_movement=fmt(F(cash1)-F(cash0)),gross_origins=deepcopy(after['flows'])),
        equity=dict(opening=fmt(start['equity']),direct_movements='9460/441' if actor=='company' else '0/1',profit='0/1',closing=fmt(end['equity']),
                    by_account={mapping['capital']:'9460/441' if actor=='company' else '0/1',mapping['issued_equity']:'0/1'},movements=movements),
        reconciliations=dict(balance_sheet='0/1',cash='0/1',equity='0/1'),notes=notes,
        unresolved=['Event-population completeness','Source and accounting admission','Complete note package','Indirect operating cash-flow bridge'],
        request_sha256=runtime.digest(report_request),opening_sha256=runtime.digest(opening),closing_sha256=runtime.digest(after),mapping_sha256=runtime.digest(program['mapping']),
        implementation_sha256=hashlib.sha256(Path(runtime.reports.__file__).read_bytes()).hexdigest(),book_sha256=runtime.reports.BOOK_SHA256)


def exercise():
    for chart in ('alpha','beta'):
        for cash in ('22','9460/441'):
            request=funding.fixture(chart,cash);before=deepcopy(request);result=funding.propose(request)
            label=chart+':'+cash;CASES.append(dict(id=label,request=request,result=result))
            check(label+':accepted',result['status'],'proposed_joint_funding');check(label+':input',request,before)
            for actor in funding.PARTIES:
                after,journal=expected(request,actor);observed=result['diagnostics'][actor]
                check(label+':'+actor+':state',result['current'][actor],after)
                check(label+':'+actor+':journal',observed['trace'][0]['result']['transition']['journal'],journal)
                check(label+':'+actor+':flows',observed['trace'][0]['result']['transition']['flows'],after['flows'])
                check(label+':'+actor+':report',observed['trace'][-1]['result'],expected_report(request,actor,after,result['programs'][actor]))
                check(label+':'+actor+':cash_nonnegative',F(after['balances'][request['mapping']['cash']])>=0)
            for transfer in request['transfers']:
                legs=[f for book in result['current'].values() for f in book['flows'] if f['origin']==transfer['id']]
                check(label+':'+transfer['id']+':two_legs',len(legs),2)
                check(label+':'+transfer['id']+':cash_sum',sum(F(f['amount']) for f in legs),F(0))
                check(label+':'+transfer['id']+':one_date',{f['date'] for f in legs}=={'2027-01-01'})
            check(label+':not_durable',result['durable'],False)
    controls()
    base=funding.fixture()
    for order in permutations(range(3)):
        request=deepcopy(base);request['transfers']=[deepcopy(base['transfers'][i]) for i in order]
        result=funding.propose(request);label='order_'+''.join(str(i) for i in order)
        CONTROLS.append(dict(id=label,request=request,result=result))
        check(label+':ordering',result['status'],'proposed_joint_funding' if order[-1]==2 else 'refused')
        if order[-1]!=2:
            check(label+':reason',result['reason'],'cash_shortfall:company');check(label+':atomic',result['current'],base['books'])
        else:
            cash=dict(company=F(0),owner=F(22),new_holder=F(40),seller=F(0));expected_schedule=[]
            for index in order:
                before={k:fmt(v) for k,v in cash.items()}
                payer,payee,amount=[('new_holder','company',F(17000,441)),('owner','company',F(9460,441)),('company','seller',F(60))][index]
                cash[payer]-=amount;cash[payee]+=amount
                expected_schedule.append(dict(transfer=deepcopy(base['transfers'][index]),before=before,after={k:fmt(v) for k,v in cash.items()}))
            check(label+':complete_cash_prefixes',result['cash_schedule'],expected_schedule)


def controls():
    base=funding.fixture()
    def refuse(name,mutate,reason=None):
        request=deepcopy(base);mutate(request);before=deepcopy(request);result=funding.propose(request)
        CONTROLS.append(dict(id=name,request=request,result=result))
        check(name+':refused',result['status'],'refused');check(name+':atomic',result['current'],before['books']);check(name+':input_preserved',request,before)
        if reason is not None:check(name+':reason',reason in result['reason'])
    def cash(request,actor,value):
        m=request['mapping'];request['books'][actor]['balances'].update({m['cash']:fmt(value),m['capital']:fmt(-F(value))})
    refuse('cash20',lambda r:cash(r,'owner',20),'insufficient_owner_cash')
    refuse('new_holder_cash38',lambda r:cash(r,'new_holder',38),'cash_shortfall:new_holder')
    refuse('stale_policy',lambda r:r['strategy'].update(conversion='risky'),'continuation_deviation')
    def wrong_quote(r):r['quote']='15500/441';r['transfers']=funding.transfers(r['quote'])
    refuse('wrong_quote',wrong_quote,'quote_payoff_mismatch')
    refuse('wrong_date',lambda r:r.update(date='2027-01-02'),'funding_date')
    refuse('missing_transfer',lambda r:r['transfers'].pop(),'transfer_contract')
    refuse('duplicate_transfer',lambda r:r['transfers'].append(deepcopy(r['transfers'][0])),'transfer_contract')
    refuse('one_sided_amount',lambda r:r['transfers'][0].update(amount='40/1'),'transfer_contract')
    refuse('different_transfer_date',lambda r:r['transfers'][0].update(date='2027-01-02'),'transfer_contract')
    refuse('wrong_face',lambda r:r['books']['company']['memory'].update(face='80/1'),'party_refusal:company')
    refuse('invented_shares',lambda r:r['books']['company']['memory'].update(new_shares='120/1'),'party_refusal:company')
    refuse('corrupt_project',lambda r:r['books']['company']['balances'].update({r['mapping']['project']:'41/1',r['mapping']['capital']:'-1/1'}),'opening_premise')
    original_program=funding.program
    def corrupt_program(book,schemas,mapping,actor,quote):
        body=original_program(book,schemas,mapping,actor,quote)
        if actor=='seller':
            method=body['registry']['entries']['settle']['method'];method['monetary']['definition']['flows']=[]
            body['registry']['entries']['settle']['method_sha256']=runtime.digest(method)
        return body
    try:
        funding.program=corrupt_program
        refuse('late_seller_failure',lambda r:None,'party_refusal:seller')
    finally:funding.program=original_program
    # A balanced-but-wrong party program is caught by transfer reconciliation.
    def wrong_cash_program(book,schemas,mapping,actor,quote):
        body=original_program(book,schemas,mapping,actor,quote)
        if actor=='seller':
            entry=body['registry']['entries']['settle'];method=entry['method']
            for row in method['monetary']['definition']['postings']:
                row['expression']['value']=funding.h.fmt(59 if row['account']=='cash' else -59)
            for row in method['monetary']['definition']['flows']:row['expression']['value']='59/1'
            entry['method_sha256']=runtime.digest(method)
        return body
    try:
        funding.program=wrong_cash_program
        refuse('balanced_wrong_seller_amount',lambda r:None,'joint_cash')
        check('balanced_wrong_seller_locally_complete',CONTROLS[-1]['result']['diagnostics']['seller']['status'],'complete_provisional')
    finally:funding.program=original_program


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True);args=parser.parse_args()
    if not re.fullmatch(r'attempt-0[123]',args.attempt):raise SystemExit('invalid attempt')
    out=HERE/args.attempt;out.mkdir(exist_ok=False);start=time.monotonic()
    sources={ROOT/PLAN,HERE/'funding.py',HERE/'verify.py'}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).resolve().is_relative_to(ROOT) and Path(path).suffix=='.py':sources.add(Path(path).resolve())
    prior=HERE.parent/'two-date-financing-control-20261026'
    sources.update(prior/name for name in ('model.json','attempt-01/source-lock.json','attempt-01/verification.json'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)};save(out/'source-lock.json',hashes)
    inp=out/'inputs';inp.mkdir()
    for p in (ROOT/PLAN,HERE/'funding.py',HERE/'verify.py'):(inp/p.name).write_bytes(p.read_bytes())
    status,error='FAIL',None
    try:
        check('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1');check('bytecode_disabled',os.environ.get('PYTHONDONTWRITEBYTECODE'),'1')
        for name,digest in json.loads((prior/'attempt-01/source-lock.json').read_text()).items():check('prior_'+name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        exercise()
        for name,digest in hashes.items():check('protected_'+name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        status='PASS'
    except Exception:
        error=traceback.format_exc();(out/'error.txt').write_text(error)
    elapsed=time.monotonic()-start
    save(out/'cases.json',CASES);save(out/'controls.json',CONTROLS);save(out/'checks.json',CHECKS)
    save(out/'run-manifest.json',dict(status=status,command=f'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 {HERE.relative_to(ROOT)}/verify.py --attempt {args.attempt}',
        git_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),python=platform.python_version(),executable=sys.executable,
        cpu_gpu='CPU only; GPU intentionally hidden',seed='N/A deterministic exact arithmetic',data_version='SelectedDatedFunding/1 source-lock.json',wall_seconds=elapsed,
        plan=PLAN,result=str(HERE.relative_to(ROOT)/'result.md'),artifact_paths=['cases.json','controls.json','checks.json','source-lock.json','verification.json'],attempt=args.attempt))
    summary=dict(status=status,cases=len(CASES),controls=len(CONTROLS),assertions=len(CHECKS),protected_files=len(hashes),wall_seconds=elapsed,error=error)
    save(out/'verification.json',summary);print(json.dumps(summary));return 0 if status=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
