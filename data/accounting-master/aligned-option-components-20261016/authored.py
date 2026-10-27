"""Freeze component, reserve, earnings and gross-cash expectations."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
CONTEXT=dict(entity='P',book='P-separate',currency='CU',quantity_unit='unit',rule='EU2023/1803-original-IFRS9',
    designation_date='2025-01-01',expiry='2025-12-31')
FINDINGS=dict(actual_terms_admitted=True,aligned_terms_match_item=True,complete_component_values=True,
    intrinsic_hedge_qualifies=True,forecast_highly_probable=True,transaction_related_inventory=True,
    reserve_recoverable=True,zero_discount_admitted=True,no_other_cash_or_earnings=True,no_fees=True,pretax_only=True)

def vals(seq):
    keys=('actual_intrinsic','aligned_intrinsic','actual_value','intrinsic_reserve','cost_reserve','intrinsic_profit','time_profit','profit')
    return {k:str(Q(str(v))) for k,v in zip(keys,seq)}

def main():
    cases=[]
    def add(id,actual_strike,aligned_strike,initial_actual,initial_aligned,observations,expected,closing,quantity=1,capital=200):
        r=dict(wire='AlignedOptionComponents/1',operation='report',context=CONTEXT,opening_cash=str(capital),opening_price='90',premium_cash=str(initial_actual),findings=FINDINGS,
            item=dict(id='purchase',quantity=str(quantity),hedged_price=str(aligned_strike)),
            actual=dict(id='actual-call',kind='purchased_call',quantity=str(quantity),strike=str(actual_strike),initial_time_value=str(initial_actual),expiry='2025-12-31'),
            aligned=dict(id='aligned-call',kind='hypothetical_call',quantity=str(quantity),strike=str(aligned_strike),initial_time_value=str(initial_aligned),expiry='2025-12-31'),quotes=[])
        for i,row in enumerate(observations):
            price,at,ht,av,hv=row
            r['quotes'].append(dict(id='q'+str(i+1),date=['2025-06-30','2025-09-30','2025-12-31'][i],context=CONTEXT,
                actual_id='actual-call',aligned_id='aligned-call',price=str(price),actual_time_value=str(at),aligned_time_value=str(ht),actual_option_value=str(av),aligned_option_value=str(hv)))
        last=observations[-1]
        r['closing']=dict(date='2025-12-31',quantity=str(quantity),unit_price=str(last[0]),supplier_cash=str(Q(str(last[0]))*quantity),
            actual_settlement=str(last[3]),findings=dict(all_units_received=True,inventory_recognition=True,nrv_supported=True,complete_costs=True))
        cases.append(dict(id=id,request=deepcopy(r),expected=dict(quotes=[vals(x) for x in expected],closing={k:str(Q(str(v))) for k,v in zip(('cash','inventory','profit','equity'),closing)})))
    add('higher-actual',100,110,6,4,[(115,3,3,18,8),(117,2,1,19,8),(130,0,0,30,20)],
        [(15,5,18,5,-1,10,-2,8),(17,7,19,7,-3,10,-1,9),(30,20,30,20,-4,10,-2,8)],(94,114,8,208))
    add('lower-actual',110,100,2,3,[(105,1,'5/2',1,'15/2'),(115,'1/2',1,'11/2',16),(120,0,0,10,20)],
        [(0,5,1,0,'-1/2',0,'-1/2','-1/2'),(5,15,'11/2',5,'-3/2',0,0,0),(10,20,10,10,-2,0,0,0)],(88,112,0,200))
    add('matched-terms',100,100,4,4,[(105,2,2,7,7),(110,1,1,11,11),(120,0,0,20,20)],
        [(5,5,7,5,-2,0,0,0),(10,10,11,10,-3,0,0,0),(20,20,20,20,-4,0,0,0)],(96,104,0,200))
    add('higher-out-of-money',100,110,6,4,[(95,3,3,3,3),(97,2,1,2,1),(95,0,0,0,0)],
        [(0,0,3,0,-1,0,-2,-2),(0,0,2,0,-3,0,-1,-1),(0,0,0,0,-4,0,-2,-2)],(99,99,-2,198))
    add('lower-out-of-money',110,100,2,3,[(95,1,'5/2',1,'5/2'),(97,'1/2',1,'1/2',1),(95,0,0,0,0)],
        [(0,0,1,0,'-1/2',0,'-1/2','-1/2'),(0,0,'1/2',0,'-3/2',0,0,0),(0,0,0,0,-2,0,0,0)],(103,97,0,200))
    add('double-quantity',100,110,12,8,[(115,6,6,36,16),(117,4,2,38,16),(130,0,0,60,40)],
        [(30,10,36,10,-2,20,-4,16),(34,14,38,14,-6,20,-2,18),(60,40,60,40,-8,20,-4,16)],(188,228,16,416),quantity=2,capital=400)
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=[p,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-aligned-option-components-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'docs/design/proposal/manuscript-instrument-reduction-20261016/sections/financing-components.tex']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),quotes=18,protected_files=len(paths))))

if __name__=='__main__':main()
