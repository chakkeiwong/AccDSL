"""Author fixed expectations before implementing the composed calculation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
CONTEXT=dict(entity='synthetic-builder',book='separate',contract='mixed-A',currency='CU',
             unit='currency units',rule='AASB15-compilation8-AU-for-profit')

def snapshot(cash,ar,ca,cl,revenue,expense,profit,equity):
    return dict(zip(('cash','receivable','contract_asset','contract_liability','revenue','expense','profit','equity'),
                    map(str,(cash,ar,ca,cl,revenue,expense,profit,equity))))

def event(id,op,date,**data):
    return dict(id=id,operation=op,date=date,information_date=date,context=deepcopy(CONTEXT),
                findings=dict(zero_impairment_assessed=True,admitted_contract_facts_remain_valid=True),**data)

def advance(id,date,amount):return event(id,'advance',date,advance_id=id,amount=amount)
def perform(id,date,construction,visits,cost):
    e=event(id,'perform',date,construction_cash_cost=construction,visits=visits,visit_cash_cost=cost)
    e['findings'].update(faithful_cost_progress=True,visits_transferred=True,all_costs_expensed_on_performance=True)
    return e
def amend(date='2024-05-01'):
    e=event('amend','amend',date,new_construction_price='140',new_expected_cost='100',new_visits_total='6')
    e['findings'].update(approved_enforceable=True,mixed_modification_not_separate=True,allocations_admitted=True,
                         faithful_cost_progress=True,expected_payment_transfer_interval_leq_year=True)
    return e
def bill(id,date,gross,credits=()):
    e=event(id,'invoice',date,invoice_id=id,gross=gross,credits=[dict(credit_id=k,contract='mixed-A',advance_id=a,amount=v) for k,a,v in credits])
    e['findings']['unconditional_right']=True
    return e
def collect(id,date,invoice,amount):return event(id,'collect',date,settlement_id=id,invoice_id=invoice,amount=amount)

def main():
    base=dict(wire='MixedContractBilling/1',operation='report',context=CONTEXT,annual_start='2024-01-01',as_of='2024-12-31',
        opening_cash='100',terms=dict(construction_price='100',expected_cost='80',visit_price='5',visits_total='4'),
        findings=dict(contract_eligibility_9=True,construction_over_time=True,visits_distinct=True,allocations_admitted=True,
            expected_payment_transfer_interval_leq_year=True,financing_expedient_elected=True,
            no_tax_fx_variable_consideration_refunds_or_onerous_loss=True),events=[])
    events=[advance('a1','2024-01-10','30'),perform('p1','2024-04-01','40','1','2'),
        bill('i1','2024-04-02','80',[('k1','a1','30')]),collect('c1','2024-04-15','i1','20'),amend(),
        advance('a2','2024-05-02','50'),perform('p2','2024-06-01','0','2','4'),
        bill('i2','2024-07-01','90',[('k2','a2','50')]),collect('c2','2024-07-10','i1','30'),
        perform('p3','2024-12-01','60','3','6'),collect('c3','2024-12-15','i2','40')]
    targets=[snapshot(130,0,0,30,0,0,0,100),snapshot(88,0,25,0,55,42,13,113),
        snapshot(88,50,0,25,55,42,13,113),snapshot(108,30,0,25,55,42,13,113),
        snapshot(108,30,0,19,61,42,19,119),snapshot(158,30,0,69,61,42,19,119),
        snapshot(154,30,0,59,71,46,25,125),snapshot(154,70,0,99,71,46,25,125),
        snapshot(184,40,0,99,71,46,25,125),snapshot(118,40,0,0,170,112,58,158),snapshot(158,0,0,0,170,112,58,158)]
    cases=[]
    def add(id,ev,expected,as_of='2024-12-31'):
        r=deepcopy(base);r.update(events=ev,as_of=as_of);cases.append(dict(id=id,request=r,expected={e['id']:s for e,s in zip(ev,expected)}))
    add('partial-billing',events,targets)
    add('before-amendment-cutoff',deepcopy(events[:4]),targets[:4],'2024-04-30')
    add('after-visits-cutoff',deepcopy(events[:7]),targets[:7],'2024-06-30')
    add('before-final-collection',deepcopy(events[:10]),targets[:10],'2024-12-01')
    prepaid=[advance('a1','2024-01-10','120'),deepcopy(events[1]),amend(),advance('a2','2024-05-02','50'),
        deepcopy(events[6]),deepcopy(events[9]),bill('i1','2024-12-02','170',[('k1','a1','120'),('k2','a2','50')])]
    add('fully-prepaid',prepaid,[snapshot(220,0,0,120,0,0,0,100),snapshot(178,0,0,65,55,42,13,113),
        snapshot(178,0,0,59,61,42,19,119),snapshot(228,0,0,109,61,42,19,119),
        snapshot(224,0,0,99,71,46,25,125),snapshot(158,0,0,0,170,112,58,158),snapshot(158,0,0,0,170,112,58,158)])
    early=[bill('i1','2024-01-10','120'),collect('c1','2024-01-11','i1','120'),deepcopy(events[1]),amend(),
        bill('i2','2024-05-02','50'),collect('c2','2024-05-03','i2','50'),deepcopy(events[6]),deepcopy(events[9])]
    add('invoice-before-performance',early,[snapshot(100,120,0,120,0,0,0,100),snapshot(220,0,0,120,0,0,0,100),
        snapshot(178,0,0,65,55,42,13,113),snapshot(178,0,0,59,61,42,19,119),snapshot(178,50,0,109,61,42,19,119),
        snapshot(228,0,0,109,61,42,19,119),snapshot(224,0,0,99,71,46,25,125),snapshot(158,0,0,0,170,112,58,158)])
    split=[advance('a1','2024-01-10','30'),bill('i1','2024-02-01','10',[('k1','a1','10')]),
        bill('i2','2024-03-01','70',[('k2','a1','20')]),perform('p1','2024-04-01','40','1','2'),
        collect('c1','2024-04-15','i2','50'),perform('p2','2024-12-01','40','3','6'),
        bill('i3','2024-12-02','40'),collect('c2','2024-12-15','i3','40')]
    add('no-amendment-split-advance',split,[snapshot(130,0,0,30,0,0,0,100),snapshot(130,0,0,30,0,0,0,100),
        snapshot(130,50,0,80,0,0,0,100),snapshot(88,50,0,25,55,42,13,113),snapshot(138,0,0,25,55,42,13,113),
        snapshot(92,0,40,0,120,88,32,132),snapshot(92,40,0,0,120,88,32,132),snapshot(132,0,0,0,120,88,32,132)])
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=[p,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-mixed-contract-billing-20261016.md',
        ROOT/'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.txt',ROOT/'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf',
        ROOT/'data/accounting-master/extended-method-exchanges-20261015/corporate-v5/semantic-contract.md',
        ROOT/'data/accounting-master/extended-method-exchanges-20261015/corporate-v5/additional_cases.py']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(x.relative_to(ROOT)),sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),locked_files=len(paths))))

if __name__=='__main__':main()
