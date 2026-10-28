"""Original collateral/support and allocation/cure discriminators."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import platform,subprocess,sys,time
import fixture as f
ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-support-cure-20261028.md'
ANCHORS=['docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/21-group-contagion.tex','docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/23-memory-case.tex']
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];native=[];timing=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def run(n,b):
        before=f.program.digest(b);r=f.program.run(b);native.append(dict(id=n,input=b,result=r))
        ck(n+'/unchanged input',f.program.digest(b),before);ck(n+'/replay',f.program.verify(b,r),True)
        ck(n+'/source admission',r['source_admission'],False);return r
    def balances(n,b,r,m,changes):
        expected=deepcopy(b['opening']['balances']);expected.update({m[k]:f.fmt(Q(v)) for k,v in changes.items()})
        ck(n+'/full balances',r.get('current',{}).get('balances'),expected)
    def stop(n,b,r,outcome):
        ck(n+'/stopped',r['status'],'stopped_provisional');ck(n+'/outcome',r['stop']['status'],outcome)
        previous=r['trace'][-1]['result']['transition']['after'] if r['trace'] else b['opening']
        ck(n+'/atomic refusal',r['current'],previous)
    ck('retained deficiency anchor','creating a borrowing-base deficiency of 6' in (ROOT/ANCHORS[0]).read_text(),True)
    ck('retained allocation anchor','fees become zero, interest becomes 1 and principal remains 100' in (ROOT/ANCHORS[1]).read_text(),True)
    ck('capacity before',f.fmt(Q(100)*Q(4,5)),'80/1');ck('capacity after',f.fmt(Q(80)*Q(4,5)),'64/1')
    ck('deficiency',f.fmt(max(Q(0),70-Q(80)*Q(4,5))),'6/1')
    ck('parent support',6-4,2);ck('parent subsequent shortfall',4-(5-2),1)
    original=f.ex.native.Engine.apply;f.ex.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            n=owner+'/parent_support_then_payment';b,m=f.parent(owner);r=run(n,b);stop(n,b,r,'invalid')
            balances(n,b,r,m,dict(cash=3,receivables=2));ck(n+'/parent debt retained',r['current']['memory']['finance']['debt'],'-4/1')
            parent_flow=r['current']['flows'][0]
            n=owner+'/subsidiary_supported';b,m=f.subsidiary(owner);r=run(n,b)
            ck(n+'/complete',r['status'],'complete_provisional');balances(n,b,r,m,dict(cash=0,debt=-64,payables=-2))
            ck(n+'/external debt memory',r['current']['memory']['finance']['debt'],'-64/1')
            ck(n+'/support_received',r['current']['flows'][0]['amount'],'2/1');ck(n+'/deficiency_paid',r['current']['flows'][1]['amount'],'-6/1')
            ck(n+'/paired support cash',f.fmt(Q(parent_flow['amount'])+Q(r['current']['flows'][0]['amount'])),'0/1')
            ck(n+'/distinct entities',parent_flow['entity']!=r['current']['flows'][0]['entity'],True)
            ck(n+'/support same currency/date',(parent_flow['currency'],parent_flow['date']),(r['current']['flows'][0]['currency'],r['current']['flows'][0]['date']))
            ck(n+'/no new profit',r['trace'][-1]['result']['income']['profit'],'0/1')
            n=owner+'/subsidiary_no_support';b,m=f.subsidiary(owner,support=False);r=run(n,b);stop(n,b,r,'invalid');balances(n,b,r,m,{})
            n=owner+'/unknown_support';b,m=f.parent(owner)
            b['commands'][0]['event']['inputs']['approved']['value']=dict(status='unknown',reason='No admitted support obligation or permission')
            r=run(n,b);stop(n,b,r,'unresolved');balances(n,b,r,m,{})
            n=owner+'/omitted_parent_support';b,m=f.parent(owner);b['commands']=b['commands'][1:];r=run(n,b)
            ck(n+'/shortcut_completes',r['status'],'complete_provisional');balances(n,b,r,m,dict(cash=1,debt=0))
            ck(n+'/independent_support_history_rejects',any(x['origin']=='supplied_recoverable_support' for x in r['current']['flows']),False)
            ck(n+'/generic_reconciliation',r['trace'][-1]['result']['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
            for order in ['fee_first','principal_first']:
                for amount in [Q(6),Q(7)]:
                    n=owner+'/'+order+'/'+str(amount);b,m=f.allocation(owner,order,amount);r=run(n,b)
                    ck(n+'/complete',r['status'],'complete_provisional')
                    fee,interest,principal=(0,7-amount,100) if order=='fee_first' else (2,5,100-amount)
                    balances(n,b,r,m,dict(cash=0,payables=-fee,interest_payable=-interest,debt=-principal))
                    ck(n+'/remaining total',f.fmt(fee+interest+principal),f.fmt(107-amount))
                    ck(n+'/debt memory',r['current']['memory']['finance']['debt'],f.fmt(-principal))
                    ck(n+'/no reexpense',r['trace'][-1]['result']['income']['profit'],'0/1')
                    ck(n+'/cash paid',r['trace'][-1]['result']['cash_flows']['net_movement'],f.fmt(-amount))
            # Unknown allocation is the two declared alternatives, not an optimized selection.
            alternatives=[x['result'] for x in native if x['id'] in [owner+'/fee_first/6',owner+'/principal_first/6']]
            ck(owner+'/unknown_priority_keeps_two_states',len({f.program.digest(r['current']['balances']) for r in alternatives}),2)
    finally:f.ex.native.Engine.apply=original
    cases=[
        ('day4_full','2027-01-04T20:00:00+00:00','2027-01-04T23:59:59+00:00','7/1','0/1',True,'conditional_cured'),
        ('day4_partial','2027-01-04T20:00:00+00:00','2027-01-04T23:59:59+00:00','6/1','1/1',True,'conditional_not_cured'),
        ('exclusive_boundary','2027-01-04T20:00:00+00:00','2027-01-05T00:00:00+00:00','7/1','0/1',True,'conditional_not_cured'),
        ('day5','2027-01-05T10:00:00+00:00','2027-01-05T11:00:00+00:00','7/1','0/1',True,'conditional_not_cured'),
        ('receipt_after_payment','2027-01-04T23:00:00+00:00','2027-01-04T22:00:00+00:00','7/1','0/1',True,'invalid'),
        ('unknown_terms','2027-01-04T20:00:00+00:00','2027-01-04T21:00:00+00:00','7/1','0/1',False,'unresolved'),
        ('offset_same_instant','2027-01-05T04:00:00+08:00','2027-01-05T07:59:59+08:00','7/1','0/1',True,'conditional_cured'),
        ('timezone_missing','2027-01-04T20:00:00','2027-01-04T21:00:00','7/1','0/1',True,'invalid'),
        ('principal_first7','2027-01-04T20:00:00+00:00','2027-01-04T21:00:00+00:00','7/1','7/1',True,'conditional_not_cured'),
        ('unknown_priority','2027-01-04T20:00:00+00:00','2027-01-04T21:00:00+00:00','7/1',None,True,'unresolved'),
        ('false_full_cure6','2027-01-04T20:00:00+00:00','2027-01-04T21:00:00+00:00','6/1','0/1',True,'invalid')]
    for n,receipt,payment,paid,remaining,known,expected in cases:
        r=f.cure(receipt,payment,paid,remaining,known);timing.append(dict(id=n,input=dict(receipt=receipt,payment=payment,paid=paid,arrears_remaining=remaining,known=known),result=r))
        ck(n+'/status',r['status'],expected);ck(n+'/native intraday unclaimed',r['native_intraday_execution'],False)
    for owner in ['alpha','beta']:
        for order,expected in [('fee_first','conditional_cured'),('principal_first','conditional_not_cured')]:
            row=next(x for x in native if x['id']==owner+'/'+order+'/7')
            roles=row['input']['registry']['entries']['interest_pay']['method']['account_map']
            fee_role=row['input']['registry']['entries']['fee_pay']['method']['account_map']['payables']
            balance=row['result']['current']['balances'];remaining=-Q(balance[roles['interest_payable']])-Q(balance[fee_role])
            r=f.cure('2027-01-01T10:00:00+00:00','2027-01-01T11:00:00+00:00','7/1',f.fmt(remaining))
            timing.append(dict(id=owner+'/'+order+'/allocation_to_cure',native_case=row['id'],native_result_sha256=f.program.digest(row['result']),supplied_intraday_order='10am receipt before11am payment on the native event date',result=r))
            ck(owner+'/'+order+'/cure consumes native remaining arrears',r['status'],expected)
    ck('date-only shortcut misses receipt-after-payment','2027-01-04'=='2027-01-04',True)
    ck('amount-only cure shortcut ignores priority',Q(7)>=7,True)
    ck('principal-first7 leaves arrears7',2+5,7)
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F041','SIM-F044']]
    ck('exact original cases',[r['discriminating_case'] for r in originals],['Collateral deficiency6, subsidiary cash4, parent support2','Fee2 interest5 payment6; receipt before/after cure deadline'])
    for row in checks:
        if len(json.dumps(row))>1400:
            row['actual_sha256']=f.program.digest(row.pop('actual'));row['expected_sha256']=f.program.digest(row.pop('expected'))
    failed=[c for c in checks if not c['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),native_cases=len(native),timing_cases=len(timing),failed=failed,original_rows=['SIM-F041','SIM-F044'],actual_support_admission=False,native_intraday_execution=False,cross_book_atomicity=False)
    for n,obj in [('verification',v),('checks',checks),('timing-cases',timing),('original-rows',originals)]:dump(out/(n+'.json'),obj)
    with gzip.open(out/'native-results.json.gz','wt') as fh:json.dump(native,fh)
    paths={Path(__file__),H/'fixture.py',ROOT/PLAN,fm,*[ROOT/x for x in ANCHORS]}
    paths.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only rational native and timestamp work; no GPU imports',random_seeds='N/A deterministic',data_version='Retained chapters21/23 and original SIM-F041/044 with explicit support and cure premises',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    for n in ['fixture.py','check.py']:(out/n).write_bytes((H/n).read_bytes())
    print(json.dumps(dict(status=v['status'],checks=len(checks),native_cases=len(native),timing_cases=len(timing),failed=[x['name'] for x in failed])));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
