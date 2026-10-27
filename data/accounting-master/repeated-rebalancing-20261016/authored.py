"""Hand-authored cumulative reversal targets, frozen before implementation."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    context=dict(entity='P',book='P-separate-USD',currency='USD',quantity_unit='tonne',price_unit='USD/tonne',
        risk='one-common-forward-price',relationship='hedge-A',rule='EU2023/1803-original-IFRS9',
        maturity_date='2025-01-01',designation_date='2024-01-01')
    findings=dict(zero_discount_admitted=True,complete_valuation_effects=True,forecast_highly_probable=True,
                  economic_relationship=True,credit_risk_not_dominant=True,ratio_eligible=True)
    opening=dict(context=context,findings=findings,layer=dict(id='initial',quantity='100',price='80',date='2024-01-01'))
    events=[
        dict(id='m1',operation='measure',date='2024-03-31',price='90',derivative='1200',expected=dict(H='-1000',reserve='1000',profit='200',journal=['1200','-1000','-200'])),
        dict(id='r1',operation='add_item',date='2024-03-31',layer=dict(id='added1',quantity='10',price='90',date='2024-03-31')),
        dict(id='m2',operation='measure',date='2024-06-30',price='95',derivative='1400',expected=dict(H='-1550',reserve='1400',profit='0',journal=['200','-400','200'])),
        dict(id='r2',operation='add_item',date='2024-06-30',layer=dict(id='added2',quantity='20',price='95',date='2024-06-30')),
        dict(id='m3',operation='measure',date='2024-09-30',price='97',derivative='1900',expected=dict(H='-1810',reserve='1810',profit='90',journal=['500','-410','-90'])),
        dict(id='m4',operation='measure',date='2024-10-31',price='94',derivative='1500',expected=dict(H='-1420',reserve='1420',profit='80',journal=['-400','390','10'])),
        dict(id='m5',operation='measure',date='2024-11-30',price='79',derivative='-200',expected=dict(H='530',reserve='-200',profit='0',journal=['-1700','1620','80'])),
        dict(id='m6',operation='measure',date='2024-12-31',price='80',derivative='-500',expected=dict(H='400',reserve='-400',profit='-100',journal=['-300','200','100']))]
    rebalance_findings=dict(objective_unchanged=True,changed_relationship=True,documentation_updated=True,ratio_eligible=True)
    for event in events:
        event['context']=context
        event['findings']=findings if event['operation']=='measure' else rebalance_findings
    value=dict(kind='exact authored diagnostic; no market data or eligibility inference',opening=opening,events=events,
               wrong_reset_expected=dict(reserve_at_m2='1200',profit_at_m2='200'),journal_fields=['derivative','cf_reserve','gains'])
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(value,indent=2)+'\n')
    files=[OUT/'authored.py',p,OUT/'source-reading.md',ROOT/'docs/plans/accounting-repeated-rebalancing-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/extended-method-exchanges-20261015/financing-v2/authored_cases.py',
        ROOT/'data/accounting-master/extended-method-exchanges-20261015/financing-v2/financial_checks.py']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(x.relative_to(ROOT)),sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in files]),indent=2)+'\n')
    print(json.dumps(dict(observations=6,additions=2,locked_files=len(files))))


if __name__=='__main__':main()
