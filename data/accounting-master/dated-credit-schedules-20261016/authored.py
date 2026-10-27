"""Authored requests and analytic stage targets, independent of calculator."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
context=dict(entity='Synthetic Bank',book='asset',currency='CU',unit='currency units',rule='EU2023/1803-original-IFRS9',contract='dated-claim',calendar='ACT/365F-annual-compound')
common=['amortised_cost','integral_cash_classified','complete_contract_and_expected_cash','information_view_valid','no_modification_fx_tax','no_initial_writeoff_required']
ef=['information_view_valid','no_earlier_writeoff_required','complete_cash_since_previous','unchanged_terms','no_writeoff_required_after_event']
zero=dict(fraction='0',portion_id=None,no_reasonable_recovery=None,portion_expected_cash='0')
def event(id,kind,date,**kw):return dict(id=id,operation=kind,date=date,information_date=date,context=deepcopy(context),findings={k:True for k in ef},**kw)
def request(poci=True):
    return dict(wire='POCIDatedSchedule/1' if poci else 'PerformingEIRSchedule/1',operation='report',context=deepcopy(context),opening_cash='300',
        numerical=dict(scale=18,max_width='1/10000000000',initial_pv_tolerance='0'),
        acquisition=dict(date='2025-01-01',price='98' if poci else '102',cost='2' if poci else '0',fee_received='0' if poci else '2',rate='1/10',
            contract={'2026-01-01':'66','2027-01-01':'363/5'} if poci else {'2026-01-01':'55','2027-01-01':'121/2'},
            expected={'2026-01-01':'55','2027-01-01':'121/2'},findings={k:True for k in common+(['poci_at_origin','price_equals_fair_value'] if poci else ['zero_credit_loss_assessed','performing_at_origin'])}),events=[])
def linear(a,b=0):return dict(f_coefficient=str(Q(a)),constant=str(Q(b)))
cases=[]
r=request();r['events']=[event('july','credit_revision','2025-07-01',expected={'2026-01-01':'44','2027-01-01':'242/5'},writeoff=dict(fraction='1/5',portion_id='identified-20-percent',no_reasonable_recovery=True,portion_expected_cash='0')),
    event('first','collect','2026-01-01',amount='44',close=False),event('improvement','credit_revision','2026-01-01',expected={'2027-01-01':'55'},writeoff=deepcopy(zero)),event('final','collect','2027-01-01',amount='55',close=True)]
cases.append(dict(id='partial-early-writeoff',request=r,expected=dict(final_cash='299',final_profit='-1',initial_shortfall='20',
    stages={'july':dict(gross=linear(80),allowance=linear(0),net=linear(80),interest=linear(100,-100),impairment=linear(-20),profit=linear(80,-100)),
            'first':dict(gross='44',allowance='0',net='44',profit='-12',cash='244'),
            'improvement':dict(gross='44',allowance='-6',net='50',profit='-6'),
            'final_accrual':dict(gross='242/5',allowance='-33/5',net='55',interest=linear(20,-7),impairment=linear(-20,6),profit='-1')})))
r=request();r['events']=[event('first','collect','2026-01-01',amount='55',close=False),event('final','collect','2027-01-01',amount='121/2',close=True)]
cases.append(dict(id='unchanged-annual',request=r,expected=dict(final_cash='631/2',final_profit='31/2',initial_shortfall='20',stages={'first':dict(gross='55',net='55',allowance='0',interest='10'),'final_accrual':dict(gross='121/2',net='121/2',interest='31/2')})))
r=request();r['events']=[event('july','credit_revision','2025-07-01',expected={'2026-01-01':'44','2027-01-01':'242/5'},writeoff=deepcopy(zero)),event('first','collect','2026-01-01',amount='44',close=False),event('final','collect','2027-01-01',amount='242/5',close=True)]
cases.append(dict(id='adverse-without-no-recovery-finding',request=r,expected=dict(final_cash='1462/5',final_profit='-38/5',initial_shortfall='20',stages={'july':dict(gross=linear(100),allowance=linear(20),net=linear(80)),
    'first':dict(gross='66',allowance='22',net='44'),'final_accrual':dict(gross='363/5',allowance='121/5',net='242/5',profit='-38/5')})))
r=request();r['events']=[event('full','credit_revision','2025-07-01',expected={},writeoff=dict(fraction='1',portion_id='entire-claim',no_reasonable_recovery=True,portion_expected_cash='0'))]
cases.append(dict(id='full-early-writeoff',request=r,expected=dict(final_cash='200',final_profit='-100',initial_shortfall='20',stages={'full':dict(gross='0',allowance='0',net='0',interest=linear(100,-100),impairment=linear(-100))})))
r=request(False);r['events']=[event('prepayment','estimate_revision','2025-07-01',expected={'2026-01-01':'105'}),event('final','collect','2026-01-01',amount='105',close=True)]
cases.append(dict(id='performing-prepayment',request=r,expected=dict(final_cash='305',final_profit='5',initial_shortfall='0',stages={'prepayment':dict(gross=linear(Q(1050,11)),catchup=linear(Q(-50,11)),profit=linear(Q(1050,11),-100)),'final_accrual':dict(gross='105',net='105',profit='5')})))
for name,rate,receipts,profit in [('zero-rate','0',{'2026-01-01':'40','2027-01-01':'60'},'0'),('negative-rate','-1/10',{'2026-01-01':'45','2027-01-01':'81/2'},'-29/2')]:
    r=request(False);r['acquisition'].update(rate=rate,contract=receipts.copy(),expected=receipts.copy())
    r['events']=[event('interim','advance','2025-07-01'),event('first','collect','2026-01-01',amount=receipts['2026-01-01'],close=False),event('final','collect','2027-01-01',amount=receipts['2027-01-01'],close=True)]
    cases.append(dict(id=name,request=r,expected=dict(final_cash=str(300+Q(profit)),final_profit=profit,initial_shortfall='0',stages={})))
r=request(False);r['acquisition'].update(date='2024-02-28',contract={'2025-02-27':'110'},expected={'2025-02-27':'110'})
r['events']=[event('leap','advance','2024-02-29'),event('irregular','advance','2024-09-17'),event('final','collect','2025-02-27',amount='110',close=True)]
cases.append(dict(id='leap-day-irregular',request=r,expected=dict(final_cash='310',final_profit='10',initial_shortfall='0',stages={'final_accrual':dict(net='110',profit='10')})))
r=request(False);r['acquisition'].update(date='2024-02-28',rate='0',contract={'2024-06-01':'20','2024-12-17':'30','2025-03-03':'50'},expected={'2024-06-01':'20','2024-12-17':'30','2025-03-03':'50'})
r['events']=[event('one','collect','2024-06-01',amount='20',close=False),event('two','collect','2024-12-17',amount='30',close=False),event('final','collect','2025-03-03',amount='50',close=True)]
cases.append(dict(id='three-irregular-receipts',request=r,expected=dict(final_cash='300',final_profit='0',initial_shortfall='0',stages={'one':dict(gross='80'),'two':dict(gross='50')})))

def main():
    target=OUT/'authored-cases.json'
    if target.exists():raise SystemExit('Do not overwrite frozen authored cases')
    target.write_text(json.dumps(dict(cases=cases,symbol='f=(11/10)^(181/365); analytic authored targets'),indent=2)+'\n')
    paths=['docs/plans/accounting-dated-credit-schedules-20261016.md',str(target.relative_to(ROOT)),str((OUT/'audit.md').relative_to(ROOT)),
           'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt','data/accounting-master/bank-poci-rollforward-20261016/semantic-contract.md']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_inputs=len(paths))))
if __name__=='__main__':main()
