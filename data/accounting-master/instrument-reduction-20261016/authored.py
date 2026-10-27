"""Hand-derived component-history, reserve, settlement and basis expectations."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
CONTEXT=dict(entity='P',book='P-separate',currency='CU',quantity_unit='unit',price_unit='CU/unit',
    rule='EU2023/1803-original-IFRS9',relationship='hedge-components',designation_date='2025-01-01',maturity_date='2025-12-31')
FINDINGS=dict(eligible_external_nonoption_instruments=True,zero_initial_cost_and_value=True,
    whole_instrument_proportions=True,unchanged_hedged_item=True,no_other_cash_or_earnings=True,pretax_only=True)
MEASURE=dict(complete_values=True,zero_discount_admitted=True,forecast_highly_probable=True,
    economic_relationship=True,credit_risk_not_dominant=True,ratio_eligible=True,reserve_loss_recoverable=True)
REDUCE=dict(objective_unchanged=True,structural_ratio_change=True,documentation_updated=True,
    remaining_ratio_eligible=True,all_instruments_retained=True)
SETTLE=dict(all_forecast_units_received=True,inventory_recognition=True,complete_costs=True,
    nrv_supported=True,no_fees=True,valuation_unchanged=True)

def values(**kw):return {k:str(Q(str(v))) for k,v in kw.items()}

def main():
    base=dict(wire='InstrumentReduction/1',operation='report',context=CONTEXT,opening_cash='2000',findings=FINDINGS,
        item=dict(id='purchase',quantity='100',origin_price='10'),instruments=[dict(id='A',quantity='60'),dict(id='B',quantity='40')],events=[])
    before=values(derivative=140,G=140,U=0,H=-100,reserve=100,profit=40,designated_quantity=100)
    cases=[]
    def add(id,reductions,price,marks,G,U,R,profit,quantity,inventory,cash,equity):
        r=deepcopy(base)
        r['events']=[dict(id='pre',operation='measure',date='2025-03-31',context=CONTEXT,findings=MEASURE,price='11',marks=dict(A='60',B='80'))]
        if reductions:r['events'].append(dict(id='reduce',operation='reduce_instruments',date='2025-03-31',context=CONTEXT,findings=REDUCE,reductions=[dict(instrument=k,quantity=str(v)) for k,v in reductions.items()]))
        r['events'].append(dict(id='final',operation='measure',date='2025-12-31',context=CONTEXT,findings=MEASURE,price=str(price),marks={k:str(v) for k,v in marks.items()}))
        r['events'].append(dict(id='settle',operation='purchase_and_settle',date='2025-12-31',context=CONTEXT,findings=SETTLE,
            quantity='100',unit_price=str(price),supplier_cash=str(Q(100)*Q(str(price))),settlements={k:str(v) for k,v in marks.items()}))
        final=values(derivative=sum(Q(str(v)) for v in marks.values()),G=G,U=U,H=Q(100)*(10-Q(str(price))),reserve=R,profit=profit,designated_quantity=quantity)
        cases.append(dict(id=id,request=r,expected=dict(pre=before,final=final,closing=values(cash=cash,inventory=inventory,equity=equity,profit=profit))))
    add('remove-A',dict(A=30),12,dict(A=120,B=100),190,30,190,30,70,1010,1020,2030)
    add('remove-B-same-nominal',dict(B=30),12,dict(A=120,B=100),205,15,200,20,70,1000,1020,2020)
    add('no-change-after-reduction',dict(A=30),11,dict(A=60,B=80),140,0,100,40,70,1000,1040,2040)
    add('no-reduction',{},12,dict(A=120,B=100),220,0,200,20,100,1000,1020,2020)
    add('proportional-both',dict(A=18,B=12),12,dict(A=120,B=100),196,24,196,24,70,1004,1020,2024)
    add('lower-item-change',dict(A=30),'23/2',dict(A=120,B=100),190,30,150,70,70,1000,1070,2070)
    add('signed-reversal',dict(A=30),9,dict(A=-60,B=-80),-80,-60,-80,-60,70,980,960,1940)
    add('gross-asset-liability',dict(A=30),12,dict(A=120,B=-20),70,30,70,30,70,1130,900,2030)
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=[p,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-instrument-reduction-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/partial-hedge-discontinuation-20261016/semantic-contract.md',
        ROOT/'data/accounting-master/repeated-rebalancing-20261016/semantic-contract.md',
        ROOT/'docs/design/proposal/manuscript-dependent-eps-20261016/sections/added-instruments.tex']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_files=len(paths))))

if __name__=='__main__':main()
