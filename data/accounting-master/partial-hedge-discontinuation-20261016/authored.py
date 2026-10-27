"""Freeze independently derived partial-discontinuation stages before calculation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PRIOR=ROOT/'data/accounting-master/repeated-rebalancing-20261016'


def target(D,R,P,continuing_R,stopped_R,released,cash='20000',inventory='0'):
    return dict(derivative=D,reserve=R,profit=P,continuing_reserve=continuing_R,
                stopped_reserve=stopped_R,released=released,cash=cash,inventory=inventory)


def main():
    prior=json.loads((PRIOR/'authored-cases.json').read_text())
    seed=dict(wire='RepeatedItemRebalancing/1',operation='report',opening=deepcopy(prior['opening']),
              events=[{k:v for k,v in deepcopy(prior['events'][0]).items() if k!='expected'}])
    context=deepcopy(seed['opening']['context'])
    finding=dict(single_external_nonoption_derivative=True,original_zero_cost=True,
        homogeneous_paired_portions=True,proportional_entire_instrument=True,
        no_other_cash_or_earnings=True,pretax_scope=True)
    stop=dict(id='stop',date='2024-03-31',quantity='20',expected=True,
        unrecoverable_loss='0',highly_probable=False,
        findings=dict(remaining_qualifies=True,documentation_updated=True,identified_matching_portions=True))
    measure=dict(id='mark',operation='measure',date='2024-06-30',context=deepcopy(context),
        price='95',derivative='1400',findings=dict(continuing_qualifies=True,
            complete_valuation_effects=True,zero_discount_admitted=True,
            continuing_reserve_recoverable=True,stopped_expectation_unchanged=True,
            stopped_loss_assessment_unchanged=True))
    close=dict(id='close',operation='purchase_and_settle',date='2024-06-30',context=deepcopy(context),
        quantity='100',unit_price='95',supplier_cash='9500',settlement_cash='1400',
        findings=dict(all_expected_units_received=True,inventory_recognition_satisfied=True,
            costs_complete=True,nrv_supports_adjusted_cost=True,no_further_value_movement=True,
            early_settlement_permitted=True,settlement_at_carrying_no_fees=True))
    base=dict(wire='PartialHedgeDiscontinuation/1',operation='report',baseline_hedge=seed,
        context=context,opening_cash='20000',findings=finding,discontinuation=stop,events=[measure,close])
    cases=[]
    gain=dict(baseline=target('1200','1000','200','1000','0','0'),
        stop=target('1200','1000','200','800','200','0'),
        mark=target('1400','1320','80','1120','200','0'),
        close=target('0','0','80','0','0','0','11900','8180'))
    cases.append(dict(id='gain-still-expected',request=deepcopy(base),expected=gain,
        close_expected=dict(quantity='100',supplier_cost='9500',basis_transferred='1320',net_cash='-8100',equity='20080')))
    r=deepcopy(base);r['discontinuation']['expected']=False
    r['events'][-1].update(quantity='80',supplier_cash='7600')
    cancelled=dict(baseline=gain['baseline'],stop=target('1200','800','400','800','0','200'),
        mark=target('1400','1120','280','1120','0','200'),
        close=target('0','0','280','0','0','200','13800','6480'))
    cash_cancel=dict(quantity='80',supplier_cost='7600',basis_transferred='1120',net_cash='-6200',equity='20280')
    cases.append(dict(id='gain-cancel-at-stop',request=r,expected=cancelled,close_expected=cash_cancel))
    r=deepcopy(base)
    assess=dict(id='assessment',operation='assess_stopped',date='2024-06-30',context=deepcopy(context),
        expected=False,unrecoverable_loss='0',findings=dict(facts_admitted=True))
    r['events'].insert(1,deepcopy(assess));r['events'][-1].update(quantity='80',supplier_cash='7600')
    cases.append(dict(id='gain-cancel-later',request=r,expected=dict(baseline=gain['baseline'],stop=gain['stop'],
        mark=gain['mark'],assessment=cancelled['mark'],close=cancelled['close']),close_expected=cash_cancel))
    loss=deepcopy(base);loss['baseline_hedge']['events'][0].update(price='70',derivative='-1200')
    loss['events'][0].update(price='65',derivative='-1400')
    loss['events'][-1].update(unit_price='65',supplier_cash='6500',settlement_cash='-1400')
    losses=dict(baseline=target('-1200','-1000','-200','-1000','0','0'),
        stop=target('-1200','-1000','-200','-800','-200','0'),
        mark=target('-1400','-1320','-80','-1120','-200','0'),
        close=target('0','0','-80','0','0','0','12100','7820'))
    cases.append(dict(id='loss-still-expected',request=deepcopy(loss),expected=losses,
        close_expected=dict(quantity='100',supplier_cost='6500',basis_transferred='-1320',net_cash='-7900',equity='19920')))
    r=deepcopy(loss);a=deepcopy(assess);a.update(expected=True,unrecoverable_loss='60');r['events'].insert(1,a)
    partial=target('-1400','-1260','-140','-1120','-140','-60')
    cases.append(dict(id='loss-partly-unrecoverable',request=r,expected=dict(baseline=losses['baseline'],stop=losses['stop'],mark=losses['mark'],assessment=partial,
        close=target('0','0','-140','0','0','-60','12100','7760')),
        close_expected=dict(quantity='100',supplier_cost='6500',basis_transferred='-1260',net_cash='-7900',equity='19860')))
    r=deepcopy(r);a=deepcopy(assess);a['id']='cancel';r['events'].insert(2,a)
    r['events'][-1].update(quantity='80',supplier_cash='5200')
    cases.append(dict(id='loss-unrecoverable-then-cancel',request=r,
        expected=dict(baseline=losses['baseline'],stop=losses['stop'],mark=losses['mark'],assessment=partial,
            cancel=target('-1400','-1120','-280','-1120','0','-200'),
            close=target('0','0','-280','0','0','-200','13400','6320')),
        close_expected=dict(quantity='80',supplier_cost='5200',basis_transferred='-1120',net_cash='-6600',equity='19720')))
    r=deepcopy(base);r['discontinuation']['quantity']='25/2'
    cases.append(dict(id='fractional-portion',request=r,expected=dict(baseline=gain['baseline'],
        stop=target('1200','1000','200','875','125','0'),mark=target('1400','1350','50','1225','125','0'),
        close=target('0','0','50','0','0','0','11900','8150')),
        close_expected=dict(quantity='100',supplier_cost='9500',basis_transferred='1350',net_cash='-8100',equity='20050')))
    r=deepcopy(base);same=deepcopy(r['events'][0]);same.update(id='same',date='2024-03-31',price='90',derivative='1200');r['events'].insert(0,same)
    cases.append(dict(id='same-mark-after-split',request=r,expected=dict(gain,same=gain['stop']),
        close_expected=cases[0]['close_expected']))
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    files=[OUT/'authored.py',p,OUT/'source-reading.md',ROOT/'docs/plans/accounting-partial-hedge-discontinuation-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        PRIOR/'reference.py',PRIOR/'authored-cases.json',PRIOR/'attempt-02/exchanges.json']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),locked_files=len(files))))


if __name__=='__main__':main()
