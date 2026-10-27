"""Freeze independent collar cash targets and signed interim amounts."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
FINDINGS=['external_contracts','not_net_written','eligible_designation','highly_probable_purchase',
    'combined_risk_alignment','complete_valuation','zero_discount_no_carry','credit_not_dominant',
    'continuing_qualification','recoverable_reserves','inventory_recognition','pretax_no_other_flows']


def main():
    context=dict(entity='synthetic-collar-buyer',book='legal',currency='CU',underlying='commodity-X',
        start='2025-01-01',expiry='2025-12-31',information_date='2026-02-01',
        rule='EU2023/1803-original-IFRS9')
    base=dict(wire='AlignedZeroCostCollar/1',operation='report',context=context,
        opening_cash='300',quantity='10',opening_spot='10',
        call=dict(id='actual-call',quantity='10',strike='11',expiry=context['expiry'],underlying=context['underlying'],premium='6'),
        put=dict(id='actual-put',quantity='10',strike='9',expiry=context['expiry'],underlying=context['underlying'],premium='6'),
        findings={k:True for k in FINDINGS},quotes=[],closing={})
    pos=dict(date='2025-04-01',spot='117/10',call_time='8',put_time='3',call_value='15',put_value='3',item_change='-7',
        call_id='actual-call',put_id='actual-put',facts_available_on='2025-04-01')
    neg=dict(date='2025-08-01',spot='83/10',call_time='3',put_time='8',call_value='3',put_value='15',item_change='7',
        call_id='actual-call',put_id='actual-put',facts_available_on='2025-08-01')
    cases=[]
    for spot,cash,basis,call,put in [(6,210,90,0,30),(9,210,90,0,0),(10,200,100,0,0),(11,190,110,0,0),(14,190,110,30,0)]:
        r=deepcopy(base);r['quotes']=[deepcopy(pos),deepcopy(neg),
            dict(date=context['expiry'],spot=str(spot),call_time='0',put_time='0',call_value=str(call),put_value=str(put),
                item_change=str(put-call),call_id='actual-call',put_id='actual-put',facts_available_on=context['expiry'])]
        r['closing']=dict(date=context['expiry'],quantity='10',supplier_cash=str(10*spot),call_receipt=str(call),put_payment=str(put))
        cases.append(dict(id='terminal-'+str(spot),request=r,expected=dict(cash=str(cash),inventory=str(basis),
            profit='0',capital='300',intrinsic_reserve='0',time_reserve='0',call_asset='0',put_liability='0'),
            interim_expected=[dict(intrinsic='7',time='5',call='15',put='3'),dict(intrinsic='-7',time='-5',call='3',put='15')]))
    r=deepcopy(cases[4]);r['id']='opposite-reversal'
    first=deepcopy(neg);first['date']=first['facts_available_on']='2025-04-01'
    second=deepcopy(pos);second['date']=second['facts_available_on']='2025-08-01'
    r['request']['quotes'][:2]=[first,second];r['interim_expected'].reverse();cases.append(r)
    r=deepcopy(cases[0]);r['id']='expiry-only';r['request']['quotes']=r['request']['quotes'][-1:];r['interim_expected']=[];cases.append(r)
    r=deepcopy(cases[4]);r['id']='five-units';r['request']['quantity']='5'
    for leg in ('call','put'):r['request'][leg].update(quantity='5',premium='3')
    for quote in r['request']['quotes']:
        for key in ('call_time','put_time','call_value','put_value','item_change'):quote[key]=str(Q(quote[key])/2)
    r['request']['closing'].update(quantity='5',supplier_cash='70',call_receipt='15')
    r['expected'].update(cash='245',inventory='55')
    for row in r['interim_expected']:
        for key in row:row[key]=str(Q(row[key])/2)
    cases.append(r)
    p=OUT/'authored-cases.json';assert not p.exists()
    p.write_text(json.dumps(dict(cases=cases,mark_witness=dict(terminal_prices=['6','9','10','11','14'],
        inception_weights=['1/5']*5,positive_weights=['1/10','1/10','1/10','1/5','1/2'],
        negative_weights=['1/2','1/5','1/10','1/10','1/10'],
        role='per-date synthetic valuation consistency only; no inferred/joint forecast measure')),indent=2)+'\n')
    paths=[p,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-zero-cost-collar-20261017.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/aligned-option-components-20261016/semantic-contract.md']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_inputs=len(paths))))


if __name__=='__main__':main()
