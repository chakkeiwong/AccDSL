"""Check governing return/stock/tax design against retained complete legal books."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
import traceback

os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
BASE=HERE.parent/'company-composition-20261016/attempt-03'
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def same(a,b): return canonical(a)==canonical(b)
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,indent=2)+'\n')
def need(ok,reason,*status):
    if not ok: raise ValueError(reason)


def conformance():
    prior=json.loads((BASE/'validation-01.json').read_text()); packet_path=BASE/'portable-exchanges.json'
    assert sha(packet_path)==prior['packet_sha256'] and prior['failed']==0
    packet=json.loads(packet_path.read_text()); reg=packet['record_registry']; alias=packet['aliases']
    body=lambda ref: reg[ref['digest']]['body']
    locks={str(packet_path.relative_to(ROOT)):prior['packet_sha256'],str((BASE/'validation-01.json').relative_to(ROOT)):sha(BASE/'validation-01.json')}
    for row in packet['input_snapshots'].values():
        assert sha(ROOT/row['path'])==row['sha256']; locks[row['path']]=row['sha256']
    for row in packet['blobs'].values():
        if 'eu-2023-1803-original' in row['path']:
            assert sha(ROOT/row['path'])==row['sha256']; locks[row['path']]=row['sha256']
    method=ROOT/packet['input_snapshots']['financial_checks.py']['path']
    assert sha(method)==prior['financial_sha256']
    spec=importlib.util.spec_from_file_location('native_return_retained_financial',method)
    financial=importlib.util.module_from_spec(spec); spec.loader.exec_module(financial)
    records=[]; checks=[]; traces=[]
    def check(name,value): checks.append({'name':name,'passed':bool(value)})
    current=deepcopy(body(alias['opening'])); initial=deepcopy(current)
    for transition in packet['transitions']:
        key=transition['id'].removesuffix('.commit'); event=body(alias['event.'+key])
        next_state,journal,flows=financial.derive(current,event,need)
        expected=body(alias['state.'+key]); proposal=body(alias['proposal.'+key])
        check(key+'_whole_state',same(next_state,expected))
        check(key+'_whole_journal',same(journal,proposal['journals']))
        check(key+'_gross_cash',same(flows,proposal['cash']))
        check(key+'_balanced_each_legal_book',all(sum(Q(v) for v in row.values())==0 for row in next_state['books'].values()))
        check(key+'_return_inventory_control',Q(next_state['books']['P']['inventory'])==Q(next_state['return_inventory'])+(Q(0) if next_state['lot']['transferred'] else Q(next_state['lot']['original_cost'])))
        traces.append({'id':key,'date':event['date'],'parent_balances':next_state['books']['P'],
            'parent_journal':journal['P'],'parent_cash_events':[f for f in flows if f['entity']=='P'],
            'return_component':next_state['returns'],'recovered_inventory':next_state['return_inventory']})
        current=next_state
    for key,start_index,end_index in [('h1',0,8),('h2',8,13),('annual',0,13)]:
        opening=body(packet['states'][start_index]); closing=body(packet['states'][end_index])
        saved=body(alias['report.'+key]); report=financial.report(opening,closing,saved['start'],saved['end'],need)
        check(key+'_legal_report',same(report[1],saved['legal']))
    r=initial['returns']; settlement=body(alias['event.returns'])['parameters']; rate=Q(initial['tax_rate'])
    units=Q(settlement['actual_units']); refund=units*Q(r['unit_refund']); handling=units*Q(settlement['unit_handling'])
    stock=min(units*(Q(r['unit_cost'])-Q(settlement['unit_deterioration'])),Q(settlement['inventory_nrv']))
    book_profit=Q(r['refund'])-refund-Q(r['recovery'])+stock-handling
    taxable=-refund-handling+stock; adjustment=Q(r['recovery'])-Q(r['refund'])
    check('settlement_book_loss_4',book_profit==-4)
    check('settlement_taxable_loss_28',taxable==-28)
    check('tax_adjustment_minus_24',taxable-book_profit==adjustment==-24)
    check('opening_dta_10',Q(r['refund'])*rate==Q(initial['books']['P']['dta'])==10)
    check('opening_dtl_4',Q(r['recovery'])*rate==-Q(initial['books']['P']['dtl'])==4)
    check('deferred_expense_6',Q(initial['books']['P']['dta'])+Q(initial['books']['P']['dtl'])==6)
    h1=body(alias['state.tax-h1'])['books']['P']; final=current['books']['P']
    beforetax=lambda b:-sum(Q(b[k]) for k in financial.INCOME if k not in ['current_tax','deferred_tax'])
    check('h1_current_tax_8',(beforetax(h1)+adjustment)*rate==Q(h1['current_tax'])==8)
    check('annual_current_tax_10_5',(beforetax(final)+adjustment)*rate==Q(final['current_tax'])==Q(21,2))
    check('second_close_only_increment_2_5',Q(final['current_tax'])-Q(h1['current_tax'])==Q(5,2))
    check('h1_naive_book_tax_wrong',beforetax(h1)*rate==14 and beforetax(h1)*rate!=Q(h1['current_tax']))
    check('profit_includes_deferred_tax',financial.profit({k:Q(v) for k,v in final.items()})==Q(99,2))
    parent_flows=[f for f in current['flows'] if f['entity']=='P']
    net={k:sum((Q(f['amount']) for f in parent_flows if f['activity']==k),Q(0)) for k in ['operating','investing','financing']}
    check('parent_legal_cfo_101_5',net['operating']==Q(203,2))
    check('parent_investing_minus20',net['investing']==-20)
    check('parent_financing_minus90',net['financing']==-90)
    check('parent_cash_bridge',Q(initial['books']['P']['cash'])+sum(net.values())==Q(final['cash'])==Q(983,2))
    initial_equity=financial.equity({k:Q(v) for k,v in initial['books']['P'].items()})
    ending_equity=financial.equity({k:Q(v) for k,v in final.items()})
    check('parent_equity_bridge',initial_equity==622 and initial_equity+Q(99,2)==ending_equity==Q(1343,2))
    old_interest=Q(initial['compound']['debt'])-Q(initial['compound']['debt_cash_basis'])
    check('opening_interest_paid_without_current_expense',old_interest==10 and Q(final['finance_expense'])==0)
    indirect=Q(99,2)+20+6-(Q(final['inventory'])-Q(initial['books']['P']['inventory']))-(Q(final['recovery_asset'])-Q(initial['books']['P']['recovery_asset']))-(Q(final['refund_liability'])-Q(initial['books']['P']['refund_liability']))-old_interest
    check('indirect_cash_with_return_balances',indirect==net['operating'])
    native_path=ROOT/'data/accounting-master/company-family-20261023/fixture.json'
    native=json.loads(native_path.read_text())['members'][0]['path']['initial_year']; locks[str(native_path.relative_to(ROOT))]=sha(native_path)
    native_cost=Q(native['inventory']['unit_cost'])
    check('old_homogeneous_inventory_cannot_absorb_recovered_cost',units*native_cost!=stock)
    check('separate_recovered_lot_preserves_value',stock/units==10)
    # Explicitly exercise scope/missing-data vetoes on the retained tax method.
    pre_tax=deepcopy(body(alias['state.internal-settle'])); tax_event=deepcopy(body(alias['event.tax-h1']))
    for key in ['rate_enacted','recovery_supported','temporary_difference_inventory_complete','outside_basis_timing_control','outside_basis_no_foreseeable_reversal']:
        bad=deepcopy(tax_event);bad['parameters'][key]=None
        try: financial.derive(pre_tax,bad,need); rejected=False
        except ValueError: rejected=True
        check('missing_'+key+'_blocks_tax',rejected)
    for name,h in locks.items(): assert sha(ROOT/name)==h,name
    derived={'settlement_book_profit':str(book_profit),'settlement_taxable_profit':str(taxable),
        'tax_adjustment':str(adjustment),'recovered_stock':str(stock),
        'native_unit_cost':str(native_cost),'parent_cash':str(Q(final['cash'])),
        'parent_profit':str(Q(99,2)),'parent_equity':str(ending_equity),
        'parent_cash_flows':{k:str(v) for k,v in net.items()}}
    return {'passed':all(x['passed'] for x in checks),'checks':checks,'derived':derived},traces,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'; assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record already exists'
    started=datetime.now(timezone.utc).isoformat(); timer=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in m[group].items(): assert sha(ROOT/name)==h,name
    result,trace,locks=conformance()
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
        'failed':[x['name'] for x in result['checks'] if not x['passed']],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-timer}
    if not result['passed']: dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        dump(HERE/'checks.json',result);dump(HERE/'legal-trace.json',trace);dump(HERE/'source-lock.json',locks)
        outputs={str(p.relative_to(ROOT)):sha(p) for p in [HERE/'checks.json',HERE/'legal-trace.json',HERE/'source-lock.json']}
        implementation={str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']}
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; retained exact legal-book method',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1 before imports','random_seeds':'N/A: deterministic',
            'inputs':locks,'implementation':implementation,'outputs':outputs,
            'plan':'docs/plans/accounting-company-native-return-design-20261023.md',
            'result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':
        assert same(result,json.loads((HERE/'checks.json').read_text())),'checks differ'
        assert same(trace,json.loads((HERE/'legal-trace.json').read_text())),'trace differs'
    print(json.dumps(observation));return 0 if result['passed'] else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        p=HERE/('failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc())
        print(json.dumps({'status':'failed','error':type(exc).__name__+': '+str(exc)[:400],'diagnostic':str(p.relative_to(ROOT))}));sys.exit(1)
