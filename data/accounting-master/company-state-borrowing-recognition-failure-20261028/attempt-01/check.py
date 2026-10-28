"""Independent event-type oracle for original SIM-F035."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f
ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-borrowing-recognition-failure-20261028.md'
def dump(path,value):path.write_text(json.dumps(value,indent=2)+chr(10))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    checks=[];cases=[];expectations=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def run(n,b):
        before=f.program.digest(b);r=f.program.run(b);ck(n+'/input unchanged',f.program.digest(b),before)
        ck(n+'/complete replay',f.program.verify(b,r),True);cases.append(dict(id=n,input=b,result=r));return r
    old=f.ex.native.Engine.apply;f.ex.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            b,m=f.make(owner);r=run(owner,b);ck(owner+'/status',r['status'],'complete_provisional')
            if r['status']!='complete_provisional':continue
            for index,label,cash,debt,delta in [(0,'borrowing','120/1','-100/1','100/1'),(2,'repayment','80/1','-60/1','-40/1')]:
                prefix=owner+'/'+label;t=r['trace'][index]['result']['transition'];report=r['trace'][index+1]['result']
                balances=deepcopy(b['opening']['balances']);balances.update({m['cash']:cash,m['debt']:debt})
                memory=deepcopy(b['opening']['memory']);memory['finance']['debt']=debt
                journal={k:'0/1' for k in balances};journal.update({m['cash']:delta,m['debt']:f.fmt(-Q(delta))})
                ck(prefix+'/all balances',t['after']['balances'],balances)
                ck(prefix+'/all memory',t['after']['memory'],memory)
                ck(prefix+'/journal',t['journal'],journal)
                ck(prefix+'/flow',[{k:x[k] for k in ['amount','activity','origin','event_id','date']} for x in t['flows']],[dict(amount=delta,activity='financing',origin='debt_issue' if index==0 else 'debt_redeem',event_id='borrow.1' if index==0 else 'repay.1',date='2027-01-01')])
                ck(prefix+'/balance sheet',report['balance_sheet'],dict(total_assets=cash,total_liabilities=f.fmt(-Q(debt)),equity_including_profit='20/1'))
                ck(prefix+'/income',report['income'],dict(income='0/1',expenses='0/1',profit='0/1'))
                ck(prefix+'/equity bridge',[report['equity'][k] for k in ['opening','direct_movements','profit','closing']],['20/1','0/1','0/1','20/1'])
                ck(prefix+'/cash bridge',[report['cash_flows'][k] for k in ['opening_cash','closing_cash','net_movement']],['20/1',cash,f.fmt(Q(cash)-20)])
                activities={k:dict(receipts='100/1' if k=='financing' else '0/1',payments='40/1' if k=='financing' and index==2 else '0/1',net=f.fmt(-Q(debt)) if k=='financing' else '0/1') for k in ['operating','investing','financing']}
                ck(prefix+'/all cash categories',report['cash_flows']['activities'],activities)
                ck(prefix+'/reconciliations',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(prefix+'/all admission flags',[report[k] for k in ['source_admission','accounting_admission','fiscal_complete','notes_complete']],[False]*4)
                expectations.append(dict(id=prefix,balances=balances,memory=memory,journal=journal,cash_activities=activities))
            ck(owner+'/final full state',r['current'],r['trace'][2]['result']['transition']['after'])
            ck(owner+'/gross cash remains two origins',[x['amount'] for x in r['trace'][3]['result']['cash_flows']['gross_origins']],['100/1','-40/1'])
        for name in ['over_redemption','duplicate_issue','missing_approval','later_redemption_without_accrual','tracked_debt_mismatch']:
            b,m=f.make()
            if name=='over_redemption':b['commands'][2]['event']['inputs']['amount']['value']=f.program.engine.known('101/1')
            if name=='duplicate_issue':b['commands'].insert(1,deepcopy(b['commands'][0]))
            if name=='missing_approval':b['commands'][0]['event']['inputs']['approved']['value']=dict(status='unknown',reason='Approval missing; do not assume')
            if name=='later_redemption_without_accrual':b['commands'][2]['event']['date']='2027-01-02'
            if name=='tracked_debt_mismatch':b['opening']['memory']['finance']['debt']='-1/1'
            r=run(name,b);ck(name+'/stopped',r['status'],'stopped_provisional')
            ck(name+'/outcome',r.get('stop',{}).get('status'),'unresolved' if name=='missing_approval' else 'invalid')
            if r.get('current'):
                expected=r['trace'][-1]['after_sha256'] if r['trace'] else f.program.digest(b['opening'])
                ck(name+'/atomic refusal',f.program.digest(r['current']),expected)
            ck(name+'/reason retained',bool(r.get('stop',{}).get('reason')),True)
        for owner,activity in product(['alpha','beta'],['operating','financing']):
            b,m=f.make(owner);f.revenue_mutation(b,m,activity);name=owner+'/revenue_mutation/'+activity;r=run(name,b)
            ck(name+'/generic accepted',r['status'],'complete_provisional')
            if r['status']!='complete_provisional':continue
            report=r['trace'][1]['result'];balances=r['current']['balances']
            ck(name+'/cash correct',balances[m['cash']],'120/1')
            ck(name+'/wrong debt absent',balances[m['debt']],'0/1')
            ck(name+'/wrong revenue credit',balances[m['revenue']],'-100/1')
            ck(name+'/wrong reported profit',report['income']['profit'],'100/1')
            ck(name+'/generic reconciliations pass',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
            ck(name+'/memory consistency also passes',r['current']['memory']['finance']['debt'],balances[m['debt']])
            ck(name+'/financing criterion alone',report['cash_flows']['activities']['financing']['net']=='100/1',activity=='financing')
            ck(name+'/independent borrowing oracle rejects',balances[m['debt']]=='-100/1' and report['income']['profit']=='0/1',False)
    finally:f.ex.native.Engine.apply=old
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    original=[x['original_row'] for x in json.loads(fm.read_text())['rows'] if x['original_row']['id']=='SIM-F035']
    ck('exact original target',[x['discriminating_case'] for x in original],['Borrowing credited to revenue'])
    paths={Path(__file__),H/'fixture.py',ROOT/PLAN,fm}
    paths.update(Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(ROOT))
    hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    failed=[x for x in checks if not x['passed']]
    verdict=dict(status='fail' if failed else 'pass',checks=len(checks),native_cases=len(cases),failed=failed,original_rows=['SIM-F035'],source_admission=False)
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact rational native execution; no accelerator imports',random_seeds='N/A deterministic fixtures',data_version='Original SIM-F035; synthetic borrowing100 and repayment40 on same date',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes=hashes)
    for name,obj in [('verification',verdict),('checks',checks),('native-results',cases),('expected-states',expectations),('original-rows',original),('run-manifest',manifest)]:dump(out/(name+'.json'),obj)
    for name in ['fixture.py','check.py']:(out/name).write_bytes((H/name).read_bytes())
    print(json.dumps(verdict));return bool(failed)
if __name__=='__main__':raise SystemExit(main())

