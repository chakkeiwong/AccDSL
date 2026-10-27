"""Independently freeze POCI finance and signed allowance targets."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def row(G,L,N,interest,impairment,cash,profit):
    return dict(gross=G,allowance=L,net=N,interest=interest,impairment_gain=impairment,cash=cash,profit=profit)


def main():
    context=dict(entity='synthetic-bank',book='separate',currency='CU',unit='currency units',
        rule='EU2023/1803-original-POCI',contract='terminal-claim-A',calendar='annual-anniversary')
    flags=dict(poci_at_initial_recognition=True,amortised_cost_classification=True,price_equals_fair_value=True,
        no_integral_fees_or_costs=True,complete_initial_expected_cash=True,contract_terms_admitted=True,
        no_modification_fx_tax_or_other_cash=True)
    base=dict(wire='POCIAnnualTerminal/1',operation='report',context=context,opening_cash='200',
        acquisition=dict(date='2024-01-01',price='50',contractual_receipt='121',expected_receipt='121/2',
            credit_adjusted_rate='1/10',term_years=2,findings=flags),events=[])
    def advance(id,year):return dict(id=id,operation='advance',date=str(year)+'-01-01',context=deepcopy(context),
        findings=dict(information_view_admitted=True,credit_assessment_unchanged=True,no_interim_cash_or_modification=True))
    def revise(id,year,receipt,improved):return dict(id=id,operation='revise_credit',date=str(year)+'-01-01',
        information_date=str(year)+'-01-01',context=deepcopy(context),expected_receipt=receipt,credit_improved=improved,
        findings=dict(credit_cash_forecast_admitted=True,contract_terms_unchanged=True))
    def close(year,cash):return dict(id='close',operation='collect_close',date=str(year)+'-01-01',information_date=str(year)+'-01-01',
        context=deepcopy(context),cash=cash,findings=dict(receipt_confirmed=True,no_reasonable_further_recovery=True,contractual_population_complete=True))
    initial=row('50','0','50','0','0','150','0')
    y1=row('55','0','55','5','0','150','5')
    cases=[]
    def add(id,events,expected,uncollected,request=None):
        r=deepcopy(request or base);r['events']=events
        cases.append(dict(id=id,request=r,expected=expected,uncollected_contractual=uncollected))
    add('unchanged',[advance('y1',2025),advance('y2',2026),close(2026,'121/2')],dict(acquisition=initial,y1=y1,
        y2=row('121/2','0','121/2','21/2','0','150','21/2'),
        close_measure=row('121/2','0','121/2','21/2','0','150','21/2'),
        close=row('0','0','0','21/2','0','421/2','21/2')),'121/2')
    add('improve-then-adverse-collection',[advance('y1',2025),revise('better',2025,'88',True),advance('y2',2026),close(2026,'70')],
        dict(acquisition=initial,y1=y1,better=row('55','-25','80','5','25','150','30'),
            y2=row('121/2','-55/2','88','13','25','150','38'),
            close_measure=row('121/2','-19/2','70','13','7','150','20'),
            close=row('0','0','0','13','7','220','20')),'51')
    add('deteriorate',[advance('y1',2025),revise('worse',2025,'44',False),advance('y2',2026),close(2026,'44')],
        dict(acquisition=initial,y1=y1,worse=row('55','15','40','5','-15','150','-10'),
            y2=row('121/2','33/2','44','9','-15','150','-6'),
            close_measure=row('121/2','33/2','44','9','-15','150','-6'),
            close=row('0','0','0','9','-15','194','-6')),'77')
    add('deteriorate-then-full-recovery',[advance('y1',2025),revise('worse',2025,'44',False),advance('y2',2026),close(2026,'121')],
        dict(acquisition=initial,y1=y1,worse=row('55','15','40','5','-15','150','-10'),
            y2=row('121/2','33/2','44','9','-15','150','-6'),
            close_measure=row('121/2','-121/2','121','9','62','150','71'),
            close=row('0','0','0','9','62','271','71')),'0')
    add('zero-final-recovery',[advance('y1',2025),advance('y2',2026),close(2026,'0')],dict(acquisition=initial,y1=y1,
        y2=row('121/2','0','121/2','21/2','0','150','21/2'),
        close_measure=row('121/2','121/2','0','21/2','-121/2','150','-50'),
        close=row('0','0','0','21/2','-121/2','150','-50')),'121')
    r=deepcopy(base);r['acquisition'].update(price='60',contractual_receipt='100',expected_receipt='72',credit_adjusted_rate='1/5',term_years=1)
    add('A07-rate-base-limit',[advance('y1',2025),close(2025,'72')],dict(acquisition=row('60','0','60','0','0','140','0'),
        y1=row('72','0','72','12','0','140','12'),close_measure=row('72','0','72','12','0','140','12'),
        close=row('0','0','0','12','0','212','12')),'28',r)
    r=deepcopy(r);r['acquisition'].update(expected_receipt='54',credit_adjusted_rate='-1/10')
    add('negative-original-rate',[advance('y1',2025),close(2025,'54')],dict(acquisition=row('60','0','60','0','0','140','0'),
        y1=row('54','0','54','-6','0','140','-6'),close_measure=row('54','0','54','-6','0','140','-6'),
        close=row('0','0','0','-6','0','194','-6')),'46',r)
    r=deepcopy(r);r['acquisition'].update(expected_receipt='60',credit_adjusted_rate='0')
    add('zero-original-rate',[advance('y1',2025),close(2025,'60')],dict(acquisition=row('60','0','60','0','0','140','0'),
        y1=row('60','0','60','0','0','140','0'),close_measure=row('60','0','60','0','0','140','0'),
        close=row('0','0','0','0','0','200','0')),'40',r)
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    files=[Path(__file__).resolve(),p,OUT/'source-reading.md',ROOT/'docs/plans/accounting-bank-poci-rollforward-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'docs/design/proposal/methods/standards-mapping-v1.md',ROOT/'docs/design/proposal/methods/standards-fixtures-v1.json',
        ROOT/'data/accounting-master/r03-bank-residual-audit-20261016/result.md',ROOT/'data/accounting-master/deliverables/P17/methods.json']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),locked_files=len(files))))


if __name__=='__main__':main()
