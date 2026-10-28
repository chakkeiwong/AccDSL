"""Exact independent state/report checks for original SIM-F036."""
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
PLAN='docs/plans/company-state-accrual-settlement-failure-20261028.md'

def dump(path,value):path.write_text(json.dumps(value,indent=2)+chr(10))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    checks=[];cases=[];expectations=[];controls=[]
    def ck(name,actual,expected):checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected))
    def run(name,body):
        original=deepcopy(body);result=f.program.run(body)
        ck(name+'/input unchanged',body,original)
        ck(name+'/replay',f.program.verify(body,result),True)
        cases.append(dict(id=name,input=body,result=result));return result
    def compact_input_checks():
        for row in checks:
            if row['name'].endswith('/input unchanged'):
                row['actual']=f.program.digest(row['actual']);row['expected']=f.program.digest(row['expected'])
    original_apply=f.ex.native.Engine.apply
    f.ex.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner,activity in product(['alpha','beta'],['operating','financing']):
            name=owner+'/'+activity;body,m=f.make(owner,activity);r=run(name,body)
            ck(name+'/status',r['status'],'complete_provisional')
            if r['status']!='complete_provisional':continue
            opening=body['opening'];accrued=deepcopy(opening['balances'])
            accrued.update({m['interest']:'5/1',m['interest_payable']:'-5/1'})
            carried=deepcopy(accrued);carried.update({m['interest']:'0/1',m['retained']:'5/1'})
            settled=deepcopy(carried);settled.update({m['cash']:'15/1',m['interest_payable']:'0/1'})
            memory=deepcopy(opening['memory']);memory['finance']['cursor']='2028-01-01'
            accrual_j={k:'0/1' for k in opening['balances']};accrual_j.update({m['interest']:'5/1',m['interest_payable']:'-5/1'})
            carry_j={k:'0/1' for k in opening['balances']};carry_j.update({m['interest']:'-5/1',m['retained']:'5/1'})
            payment_j={k:'0/1' for k in opening['balances']};payment_j.update({m['cash']:'-5/1',m['interest_payable']:'5/1'})
            ta=r['trace'][0]['result']['transition'];tc=r['trace'][2]['result'];tp=r['trace'][3]['result']['transition']
            for label,t,b,j in [('accrual',ta,accrued,accrual_j),('payment',tp,settled,payment_j)]:
                ck(name+'/'+label+'/all balances',t['after']['balances'],b)
                ck(name+'/'+label+'/all memory',t['after']['memory'],memory)
                ck(name+'/'+label+'/journal',t['journal'],j)
                ck(name+'/'+label+'/balanced',sum(Q(v) for v in b.values())==0,True)
            ck(name+'/accrual has no cash flow',ta['flows'],[])
            ck(name+'/payment flow count',len(tp['flows']),1)
            ck(name+'/payment cash/category/origin',[[x[k] for k in ['amount','activity','origin','date','event_id']] for x in tp['flows']],[['-5/1',activity,'interest_pay','2028-01-01','pay.2028']])
            ck(name+'/carry full balances',tc['next_opening']['balances'],carried)
            ck(name+'/carry all memory',tc['next_opening']['memory'],memory)
            ck(name+'/carry journal',tc['journal'],carry_j)
            ck(name+'/carry cash flows',tc['cash_flows'],[])
            ck(name+'/carry resets annual flows',tc['next_opening']['flows'],[])
            ck(name+'/carry period',tc['next_opening']['period'],dict(start='2028-01-01',end_exclusive='2029-01-01'))
            ck(name+'/final full balances',r['current']['balances'],settled)
            ck(name+'/final full memory',r['current']['memory'],memory)
            ck(name+'/archive count',len(r['archives']),1)
            for index,year,assets,liabilities,expense,profit,opening_eq,closing_eq,closing_cash,movement in [
                (1,2027,'120/1','105/1','5/1','-5/1','20/1','15/1','20/1','0/1'),
                (4,2028,'115/1','100/1','0/1','0/1','15/1','15/1','15/1','-5/1')]:
                report=r['trace'][index]['result'];prefix=name+'/'+str(year)
                ck(prefix+'/balance sheet',report['balance_sheet'],dict(total_assets=assets,total_liabilities=liabilities,equity_including_profit=closing_eq))
                ck(prefix+'/income',report['income'],dict(income='0/1',expenses=expense,profit=profit))
                ck(prefix+'/equity bridge',[report['equity'][k] for k in ['opening','direct_movements','profit','closing']],[opening_eq,'0/1',profit,closing_eq])
                ck(prefix+'/cash bridge',[report['cash_flows'][k] for k in ['opening_cash','closing_cash','net_movement']],['20/1',closing_cash,movement])
                expected_activities={key:dict(receipts='0/1',payments='5/1' if key==activity and year==2028 else '0/1',net='-5/1' if key==activity and year==2028 else '0/1') for key in ['operating','investing','financing']}
                ck(prefix+'/all cash activities',report['cash_flows']['activities'],expected_activities)
                ck(prefix+'/reconciliation',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(prefix+'/admission and completion',[report[k] for k in ['source_admission','accounting_admission','fiscal_complete','notes_complete']],[False]*4)
            ck(name+'/partial2028 cutoff',r['trace'][4]['result']['as_of'],'2028-01-01')
            ck(name+'/total recognized expense',f.fmt(sum(Q(r['trace'][i]['result']['income']['expenses']) for i in [1,4])),'5/1')
            expectations.append(dict(id=name,accrued_balances=accrued,carried_balances=carried,settled_balances=settled,all_memory=memory,journals=[accrual_j,carry_j,payment_j]))
        for name in ['overpay','cash_shortfall','duplicate_payment_id','fresh_id_second_payment','missing_carry_policy','repeat_accrual','wrong_accrual_date']:
            body,m=f.make(cash='4/1' if name=='cash_shortfall' else '20/1')
            if name=='overpay':body['commands'][3]['event']['inputs']['amount']['value']=f.program.engine.known('6/1')
            if name in ['duplicate_payment_id','fresh_id_second_payment']:
                again=deepcopy(body['commands'][3])
                if name=='fresh_id_second_payment':again['event']['id']='pay.2028.again'
                body['commands'].insert(4,again)
            if name=='missing_carry_policy':del body['commands'][2]['memory_policies']['/finance/cursor']
            if name=='repeat_accrual':
                again=deepcopy(body['commands'][0]);again['event']['id']='accrue.2027.again';body['commands'].insert(1,again)
            if name=='wrong_accrual_date':body['commands'][0]['event']['date']='2027-12-30'
            r=run(name,body);ck(name+'/refused',r['status'],'stopped_provisional')
            ck(name+'/invalid',r.get('stop',{}).get('status'),'invalid')
            if r.get('current'):
                expected_hash=r['trace'][-1]['after_sha256'] if r['trace'] else f.program.digest(body['opening'])
                ck(name+'/atomic refusal',f.program.digest(r['current']),expected_hash)
            ck(name+'/reason retained',bool(r.get('stop',{}).get('reason')),True)
        body,m=f.make();body['commands']=body['commands'][:3];r=run('carry_for_tamper_check',body)
        request=deepcopy(r['trace'][2]['request']);proposal=deepcopy(r['trace'][2]['result'])
        proposal['next_opening']['balances'][m['interest_payable']]='0/1'
        proposal['next_opening']['balances'][m['retained']]='0/1'
        ck('dropped payable still balanced',sum(Q(v) for v in proposal['next_opening']['balances'].values())==0,True)
        outcome=f.program.carry.apply(request,proposal)
        ck('dropped payable tamper rejected',outcome['status'],'invalid')
        ck('dropped payable recomputation reason',outcome.get('reason'),'proposal_recomputation_mismatch')
        controls.append(dict(id='tampered-carry',request=request,tampered_proposal=proposal,result=outcome))
        for owner in ['alpha','beta']:
            body,m=f.make(owner);f.reexpense_mutation(body,m);name=owner+'/deliberate_reexpense';r=run(name,body)
            ck(name+'/generic execution',r['status'],'complete_provisional')
            if r['status']=='complete_provisional':
                report=r['trace'][4]['result'];current=r['current']['balances']
                ck(name+'/wrong payable retained',current[m['interest_payable']],'-5/1')
                ck(name+'/wrong second expense',current[m['interest']],'5/1')
                ck(name+'/cash alone passes',current[m['cash']],'15/1')
                ck(name+'/generic reconciliations pass',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(name+'/independent settlement criterion rejects',current[m['interest_payable']]=='0/1' and current[m['interest']]=='0/1',False)
    finally:f.ex.native.Engine.apply=original_apply
    compact_input_checks()
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    original=[x['original_row'] for x in json.loads(fm.read_text())['rows'] if x['original_row']['id']=='SIM-F036']
    ck('original target count',len(original),1)
    ck('original discriminating target',original[0]['discriminating_case'],'Coupon5 unpaid in year1, paid in year2')
    paths={Path(__file__),H/'fixture.py',H/'setup-diagnostics.md',ROOT/PLAN,fm}
    paths.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    failed=[x for x in checks if not x['passed']]
    verdict=dict(status='fail' if failed else 'pass',checks=len(checks),native_cases=len(cases),carry_tamper_cases=len(controls),failed=failed,original_rows=['SIM-F036'],actual_company_admission=False,complete2028=False)
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact rational native execution; no GPU framework imports',random_seeds='N/A deterministic finite fixtures',data_version='Original SIM-F036 plus explicit synthetic opening/rate/daycount and cash policies',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes=hashes)
    for name,obj in [('verification',verdict),('checks',checks),('native-results',cases),('expected-states',expectations),('carry-tamper-results',controls),('original-rows',original),('run-manifest',manifest)]:dump(out/(name+'.json'),obj)
    for name in ['fixture.py','check.py']:(out/name).write_bytes((H/name).read_bytes())
    print(json.dumps(verdict));return bool(failed)
if __name__=='__main__':raise SystemExit(main())

