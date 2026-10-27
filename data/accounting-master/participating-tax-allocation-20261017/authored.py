"""Freeze source numerators and independent local expectations before implementation."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
FINDINGS=['equity_classification','fixed_proportional_rights','ordinary_only_tax_benefit',
    'tax_deduction_supported','actual_benefit_recognition_supported','full_actual_benefit_distributed',
    'complete_dividends','no_other_entitlements','denominator_complete','base_balance_supported',
    'same_rights_on_residual_allocation']


def request(p, opening, ratio, tax, dp, do, h, reported, year=2025, location='profit', n=100):
    vals=dict(profit_before_benefit=p,opening_base_balance=opening,participating_ratio=ratio,
        tax_rate=tax,weighted_average_ordinary=n,participating_dividend=dp,ordinary_base_dividend=do,
        ordinary_tax_dividend=h,actual_tax_benefit=h,reported_profit=reported)
    return dict(wire='ParticipatingTaxEPS/1',operation='basic',
        context=dict(entity='synthetic-Y',book='group',currency='CU',ordinary_class='O',
            participating_class='P',start=f'{year}-01-01',end_exclusive=f'{year+1}-01-01',
            information_date=f'{year+1}-03-01',facts_available_on=f'{year+1}-02-01',
            rule='IFRS-IC-2017-IAS33-participating-tax'),
        amounts={k:str(Q(str(v))) for k,v in vals.items()},benefit_location=location,
        findings={k:True for k in FINDINGS})


def main():
    cases=[]
    def add(id,r,ordinary,participating,residual,residual_tax,closing):
        cases.append(dict(id=id,request=r,expected={k:str(Q(str(v))) for k,v in
            dict(ordinary_earnings=ordinary,participating_earnings=participating,
                residual_base=residual,residual_tax=residual_tax,closing_base_balance=closing,
                basic_eps=Q(str(ordinary))/Q(r['amounts']['weighted_average_ordinary'])).items()}))
    add('source-year1',request(330,0,10,'3/10',0,0,0,330,2023),120,300,330,90,330)
    add('source-year2',request(550,330,10,'3/10',300,30,90,640,2024),200,500,220,60,550)
    add('source-year3',request(110,550,10,'3/10',600,60,180,290,2025),40,100,-550,-150,0)
    for original in list(cases):
        r=deepcopy(original['request']);r['benefit_location']='equity'
        r['amounts']['reported_profit']=r['amounts']['profit_before_benefit']
        cases.append(dict(id=original['id']+'-equity',request=r,expected=original['expected']))
    add('full-current-payout',request(330,0,10,'3/10',300,30,90,420),120,300,0,0,0)
    add('equal-base-rights',request(80,0,1,'1/4',0,0,0,80),50,40,80,10,80)
    add('no-tax',request(100,0,3,0,0,0,0,100),25,75,100,0,100)
    add('no-participation',request(50,100,0,'3/10',0,80,0,50),50,0,-30,0,70)
    add('zero-current-prior-payout',request(0,100,3,'1/5',75,25,15,15),0,0,-100,-15,0)
    add('zero-everything',request(0,0,10,'3/10',0,0,0,0),0,0,0,0,0)
    add('weighted-denominator',request(80,0,1,'1/4',0,0,0,80,n='125/2'),50,40,80,10,80)
    target=OUT/'authored-cases.json'
    assert not target.exists()
    target.write_text(json.dumps(dict(source_denominator_note='100 is locally supplied; source gives numerator only',cases=cases),indent=2)+'\n')
    sources=ROOT/'data/accounting-master/dependent-eps-source-selection-20261017'
    paths=[target,Path(__file__).resolve(),OUT/'derivation.md',OUT/'semantic-contract.md',
        ROOT/'docs/plans/accounting-participating-tax-allocation-20261017.md',
        sources/'ias33-tax-agenda.pdf',sources/'ias33-tax-example.pdf',sources/'aasb133-2020.pdf',
        sources/'source-reading.md',ROOT/'data/accounting-master/capped-participation-20261016/semantic-contract.md']
    lock=dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])
    (OUT/'input-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_inputs=len(paths))))


if __name__=='__main__':main()
