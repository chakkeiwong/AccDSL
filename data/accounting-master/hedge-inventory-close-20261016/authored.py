"""Independent purchase, reserve-origin and cash results before close code."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PREV=ROOT/'data/accounting-master/repeated-rebalancing-20261016'


def main():
    original=json.loads((PREV/'authored-cases.json').read_text())
    cases=[]
    for name,last,price,supplier,D,R,I,date,sale,pre_cash,profit,closing,receipts,payments in [
        ('gain','m3','97','12610','1900','1810','90','2024-09-30','2024-10-15','9290','3790','23790','16400','12610'),
        ('loss','m6','80','10400','-500','-400','-100','2024-12-31','2025-01-02','9100','3600','23600','14500','10900')]:
        events=[]
        for event in original['events']:
            events.append({k:v for k,v in deepcopy(event).items() if k!='expected'})
            if event['id']==last:break
        hedge=dict(wire='RepeatedItemRebalancing/1',operation='report',opening=deepcopy(original['opening']),events=events)
        findings=dict(all_designated_units_received=True,inventory_recognition_satisfied=True,
            acquisition_costs_complete=True,nrv_supports_adjusted_cost=True,hedge_settlement_complete=True,
            settlement_at_carrying_no_fees=True,early_settlement_permitted=True,no_further_valuation_movement=True,
            all_units_sold=True,sale_recognition_satisfied=True,no_other_cash_or_earnings=True,pretax_scope=True)
        request=dict(wire='HedgeInventoryClose/1',operation='report',hedge=hedge,context=deepcopy(original['opening']['context']),
            opening_cash='20000',purchase=dict(date=date,quantity='130',unit_price=price,supplier_cash=supplier),
            settlement=dict(date=date,cash=D),sale=dict(date=sale,quantity='130',cash='14500'),findings=findings)
        expected=dict(quantity='130',supplier_cost=supplier,derivative_settlement=D,original_reserve=R,
            original_ineffectiveness=I,inventory_after_basis='10800',cash_before_sale=pre_cash,
            profit_before_sale=I,equity_before_sale='20090' if name=='gain' else '19900',
            cost_of_sales='10800',sale_revenue='14500',closing_cash=closing,closing_inventory='0',
            closing_derivative='0',closing_reserve='0',cumulative_pretax_profit=profit,closing_pretax_equity=closing,
            operating_receipts=receipts,operating_payments=payments,net_cash=profit,oci_reclassification='0',
            direct_basis_reserve_change='-1810' if name=='gain' else '400',basis_profit='0',tax='not_calculated')
        journals=dict(purchase={'inventory':supplier,'cash':'-12610' if name=='gain' else '-10400'},
            settle={'cash':D,'derivative':'-1900' if name=='gain' else '500'},
            basis={'cf_reserve':R,'inventory':'-1810' if name=='gain' else '400'},
            sale={'cash':'14500','revenue':'-14500','cogs':'10800','inventory':'-10800'})
        cases.append(dict(id=name,request=request,expected=expected,journal_targets=journals))
    path=OUT/'authored-cases.json';assert not path.exists();path.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    files=[OUT/'authored.py',path,OUT/'source-reading.md',ROOT/'docs/plans/accounting-hedge-inventory-close-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',PREV/'reference.py',PREV/'authored-cases.json',PREV/'attempt-02/exchanges.json']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2)+'\n')
    print(json.dumps(dict(worlds=len(cases),locked_files=len(files))))


if __name__=='__main__':main()
