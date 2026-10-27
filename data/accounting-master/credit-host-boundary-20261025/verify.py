"""Read-only projection inventory and real host validation probes."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import platform
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import credit_linked_schedule_v1 as linked
import credit_linked_algebra_v1 as algebra
import company_book_transition_v1 as host
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def fmt(q):q=Q(q);return str(q.numerator)+'/'+str(q.denominator)
def outcome(book,schemas):
    before=deepcopy(book)
    try:host.validate_book(book,schemas);result={'accepted':True}
    except Exception as exc:result={'accepted':False,'reason':str(exc)}
    assert book==before
    return result
def main():
    record='--record' in sys.argv;started=time.monotonic()
    if record:assert not (HERE/'evidence.json').exists()
    prior=ROOT/'data/accounting-master/credit-linked-measurements-20261025'
    locks=json.loads((prior/'source-lock.json').read_text())
    for n,h in locks.items():assert sha(ROOT/n)==h,n
    rows=[];full=[]
    for old in linked.retained():
        req=linked.request(old['id']);r=linked.calculate(req)
        assert r==json.loads((prior/'cases'/(old['id']+'.json')).read_text())['result']
        root=algebra.Root.create(r['root']['context'],r['root']['rate'])
        amounts=[c for c in r['certificates']['containment'] if not c['path'].startswith('/factor_bounds/')]
        rational=0;nonrational=[]
        for c in amounts:
            x=algebra.Expr.from_wire(root,c['exact_expression'])
            try:
                q=x.rational_projection();assert host.monetary.rational(fmt(q))==q;rational+=1
            except algebra.Refusal as exc:
                assert exc.reason=='rational_projection_not_certified';nonrational.append(c['path'])
        rows.append({'id':old['id'],'monetary_occurrences':len(amounts),'rational_projections':rational,
                     'nonrational_count':len(nonrational),'nonrational_paths':nonrational})
        full.append({'request':req,'result':r})
    spec=importlib.util.spec_from_file_location('host_probe_examples',ROOT/'data/accounting-master/company-book-transition-20261025/examples.py')
    ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
    book,request=ex.fixture();schemas=request['schemas']
    valid=outcome(book,schemas);assert valid['accepted']
    selected=full[0]['result'];root=algebra.Root.create(selected['root']['context'],selected['root']['rate'])
    exact=next(c for c in selected['certificates']['containment'] if c['path']=='/journals/1/entries/gross')['exact_expression']
    symbolic=deepcopy(book);symbolic['balances'][book['cash_account']]=exact
    rejected=outcome(symbolic,schemas);assert not rejected['accepted']
    cu=deepcopy(book);cu['context']['currency']='CU';currency=outcome(cu,schemas)
    assert not currency['accepted'] and currency['reason']=='currency_code'
    zero=deepcopy(book);zero['balances'][book['cash_account']]='0/1'
    capital=next(a for a,v in book['accounts'].items() if v['classification']=='equity')
    zero['balances'][capital]=fmt(Q(book['balances'][capital])+Q(book['balances'][book['cash_account']]))
    rational_zero=outcome(zero,schemas);assert rational_zero['accepted']
    probes={'unchanged_rational_book':valid,'linked_expression_in_rational_balance':rejected,
            'native_two_letter_unit_label':currency,'balanced_zero_rational_cash':rational_zero,
            'symbolic_value':exact,'native_root':root.wire()}
    evidence={'cases':rows,'all_rational_cases':[r['id'] for r in rows if not r['nonrational_count']],
              'probes':probes,'host_amount_type':host.money_type(book),
              'scope':'Type/projection boundary only; no ledger transitions or accounting admission'}
    for name,value in [('evidence.json',evidence),('complete-exchanges.json',full),('host-probes.json',
         {'original_book':book,'schemas':schemas,'expression_book':symbolic,'native_currency_book':cu,'results':probes})]:
        p=HERE/name
        if record:dump(p,value)
        else:assert value==json.loads(p.read_text()),name
        locks[str(p.relative_to(ROOT))]=sha(p)
    for p in [Path(__file__),HERE/'audit.md',ROOT/'docs/plans/accounting-credit-host-boundary-20261025.md',
              ROOT/'data/accounting-master/company-book-transition-20261025/examples.py']:
        locks[str(p.relative_to(ROOT))]=sha(p)
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name and Path(name).resolve().parent==ROOT/'scripts' and Path(name).suffix=='.py':
            p=Path(name).resolve();locks[str(p.relative_to(ROOT))]=sha(p)
    if record:
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/credit-host-boundary-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU exact arithmetic; no GPU framework imported',
            'seeds':'N/A deterministic','data_version':'Accepted CreditLinkedSchedule/1 and unchanged CompanyBook/1',
            'wall_seconds':time.monotonic()-started,'plan':'docs/plans/accounting-credit-host-boundary-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']}})
    else:
        assert locks==json.loads((HERE/'source-lock.json').read_text())
        for n,h in locks.items():assert sha(ROOT/n)==h,n
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','cases':len(rows),
        'all_rational_cases':evidence['all_rational_cases'],'host_expression_refusal':rejected,
        'monetary_occurrences':sum(r['monetary_occurrences'] for r in rows),
        'nonrational_occurrences':sum(r['nonrational_count'] for r in rows),'locked_files':len(locks)}))
if __name__=='__main__':main()
