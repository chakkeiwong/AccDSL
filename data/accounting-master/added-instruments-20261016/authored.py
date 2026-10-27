"""Lock independent acquisition-origin and cumulative reserve targets."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PREV = ROOT/'data/accounting-master/repeated-rebalancing-20261016'


def expected(cash,carrying,gain,item,reserve,profit,basis,assets,liabilities,equity):
    return dict(cash=cash,net_derivative=carrying,D=gain,H=item,reserve=reserve,
                profit=profit,acquisition_basis=basis,derivative_assets=assets,
                derivative_liabilities=liabilities,pretax_equity=equity)


def main():
    prior=json.loads((PREV/'authored-cases.json').read_text())
    seed=dict(wire='RepeatedItemRebalancing/1',operation='report',opening=deepcopy(prior['opening']),
              events=[{k:v for k,v in deepcopy(prior['events'][0]).items() if k!='expected'}])
    context=deepcopy(prior['opening']['context'])
    measure_findings=deepcopy(prior['opening']['findings'])
    add_findings=dict(objective_unchanged=True,changed_relationship=True,
        documentation_updated=True,ratio_eligible=True,eligible_external_whole_nonoption=True,
        purchase_equals_fair_value=True,immediate_purchase_and_designation=True,no_fees=True)
    req=dict(wire='AddedInstrumentLayers/1',operation='report',baseline_hedge=seed,context=context,
             opening_cash='20000',findings=dict(legacy_single_whole_instrument=True,
                 no_other_cash_or_earnings=True,pretax_scope=True),events=[])
    targets={'baseline':expected('20000','1200','1200','-1000','1000','200','0','1200','0','21200')}
    events=[dict(id='a1',operation='add_instrument',date='2024-03-31',context=deepcopy(context),
                 instrument=dict(id='A',nominal='10',acquisition_value='200'),findings=deepcopy(add_findings)),
            dict(id='m2',operation='measure',date='2024-06-30',context=deepcopy(context),price='95',
                 values=dict(original='1400',A='220'),findings=deepcopy(measure_findings)),
            dict(id='a2',operation='add_instrument',date='2024-06-30',context=deepcopy(context),
                 instrument=dict(id='B',nominal='20',acquisition_value='50'),findings=deepcopy(add_findings)),
            dict(id='m3',operation='measure',date='2024-09-30',context=deepcopy(context),price='97',
                 values=dict(original='1900',A='260',B='60'),findings=deepcopy(measure_findings)),
            dict(id='m4',operation='measure',date='2024-10-31',context=deepcopy(context),price='94',
                 values=dict(original='1500',A='190',B='45'),findings=deepcopy(measure_findings)),
            dict(id='m5',operation='measure',date='2024-11-30',context=deepcopy(context),price='79',
                 values=dict(original='-200',A='100',B='20'),findings=deepcopy(measure_findings))]
    # Event dates are independent declared targets; verify first date equals the frozen baseline.
    assert events[0]['date']==seed['events'][0]['date']
    targets.update(a1=expected('19800','1400','1200','-1000','1000','200','200','1400','0','21200'),
        m2=expected('19800','1620','1420','-1500','1420','0','200','1620','0','21420'),
        a2=expected('19750','1670','1420','-1500','1420','0','250','1670','0','21420'),
        m3=expected('19750','2220','1970','-1700','1700','270','250','2220','0','21970'),
        m4=expected('19750','1735','1485','-1400','1400','85','250','1735','0','21485'),
        m5=expected('19750','-80','-330','100','-100','-230','250','120','200','19670'))
    req['events']=events
    cases=[dict(id='two_acquisitions',request=req,targets=targets)]
    for name,idx in [('no_addition',0),('purchase_only',1)]:
        r=deepcopy(req);r['events']=r['events'][:idx]
        cases.append(dict(id=name,request=r,targets={k:targets[k] for k in ['baseline']+['a1'][:idx]}))
    r=deepcopy(req);r['events']=r['events'][:2]
    r['events'][0]['instrument']['acquisition_value']='0';r['events'][1]['values']['A']='20'
    cases.append(dict(id='zero_value_addition',request=r,targets=dict(baseline=targets['baseline'],
        a1=targets['baseline'],m2=expected('20000','1420','1420','-1500','1420','0','0','1420','0','21420'))))
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    files=[OUT/'authored.py',p,OUT/'source-reading.md',ROOT/'docs/plans/accounting-added-instruments-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        PREV/'reference.py',PREV/'authored-cases.json',PREV/'attempt-02/exchanges.json']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),locked_files=len(files))))


if __name__=='__main__':main()
