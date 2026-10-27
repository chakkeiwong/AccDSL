"""Freeze exact contract-loss expectations before the reference calculation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def state(cash,asset,provision,asset_loss,provision_expense,settlement,admin,profit,equity):
    return dict(cash=cash,asset=asset,provision=provision,asset_loss=asset_loss,
        provision_expense=provision_expense,settlement_result=settlement,
        admin_expense=admin,profit=profit,equity=equity)


def main():
    context=dict(entity='synthetic-service-company',book='separate',currency='CU',unit='currency units',
        rule='EU2023/1803-original-IFRS15-IAS37',contract='service-A')
    shared=dict(eligible_original_cost=True,one_remaining_point_in_time_service=True,
        no_prior_service_or_amortisation=True,no_advance_receivable_tax_fx_or_reimbursement=True,
        time_value_immaterial=True,contract_enforceable=True)
    def assess(id,date,incremental,allocated,penalty):
        return dict(id=id,operation='assess',date=date,information_date=date,context=deepcopy(context),
            consideration='100',incremental_cash=incremental,allocated_direct_cash=allocated,exit_compensation=penalty,
            findings=dict(other_standard_impairment_completed=True,no_additional_cgu_loss=True,
                complete_disjoint_direct_costs=True,no_future_noncash_costs=True,
                reliable_best_estimates=True,collectible_fixed_consideration=True,
                available_enforceable_exit=True,no_other_exit_benefits_or_costs=True))
    def finish(op,incremental='100',allocated='30',penalty='50',admin='0'):
        return dict(id='settlement',operation=op,date='2025-12-31',context=deepcopy(context),
            receipt='100' if op=='fulfil' else '0',incremental_cash=incremental if op=='fulfil' else '0',
            allocated_direct_cash=allocated if op=='fulfil' else '0',exit_compensation='0' if op=='fulfil' else penalty,
            unrelated_admin_cash=admin,findings=dict(confirmed_same_contract_cash=True,
                complete_performance_or_termination=True,no_other_rights_or_obligations=True,
                no_alternative_use_of_remaining_cost_asset=True,admin_unrelated_to_contract=True))
    base=dict(wire='OnerousContractSequence/1',operation='report',context=context,opening_date='2025-01-01',
        opening_cash='200',original_unamortized_cost='20',findings=shared,events=[])
    assessed=state('200','0','30','20','30','0','0','-50','170')
    complete=state('170','0','0','20','30','0','0','-50','170')
    cases=[]
    def add(id,events,expected):
        req=deepcopy(base);req['events']=events;cases.append(dict(id=id,request=req,expected=expected))
    add('fulfil-least-cost',[assess('assessment','2025-01-01','100','30','50'),finish('fulfil')],dict(assessment=assessed,settlement=complete))
    a20=state('200','0','20','20','20','0','0','-40','180')
    add('cancel-cheaper-exit',[assess('assessment','2025-01-01','100','30','20'),finish('cancel',penalty='20')],
        dict(assessment=a20,settlement=state('180','0','0','20','20','0','0','-40','180')))
    add('fulfil-despite-cheaper-exit',[assess('assessment','2025-01-01','100','30','20'),finish('fulfil',penalty='20')],
        dict(assessment=a20,settlement=state('170','0','0','20','20','-10','0','-50','170')))
    add('free-cancellation',[assess('assessment','2025-01-01','100','30','0'),finish('cancel',penalty='0')],
        dict(assessment=state('200','0','0','20','0','0','0','-20','200'),settlement=state('200','0','0','20','0','0','0','-20','200')))
    add('no-loss-contract',[assess('assessment','2025-01-01','60','20','50'),finish('fulfil','60','20')],
        dict(assessment=state('200','20','0','0','0','0','0','0','220'),settlement=state('220','0','0','0','0','0','0','0','220')))
    partial=state('200','10','0','10','0','0','0','-10','210')
    add('asset-loss-only',[assess('assessment','2025-01-01','70','20','50'),finish('fulfil','70','20')],
        dict(assessment=partial,settlement=state('210','0','0','10','0','0','0','-10','210')))
    add('estimate-improves',[assess('assessment','2025-01-01','100','30','50'),assess('review','2025-07-01','70','20','50'),finish('fulfil','70','20')],
        dict(assessment=assessed,review=partial,settlement=state('210','0','0','10','0','0','0','-10','210')))
    worse=state('200','0','40','20','40','0','0','-60','160')
    add('estimate-worsens',[assess('assessment','2025-01-01','100','30','50'),assess('review','2025-07-01','100','40','50'),finish('fulfil','100','40')],
        dict(assessment=assessed,review=worse,settlement=state('160','0','0','20','40','0','0','-60','160')))
    add('unrelated-admin-expense',[assess('assessment','2025-01-01','100','30','50'),finish('fulfil',admin='15')],
        dict(assessment=assessed,settlement=state('155','0','0','20','30','0','15','-65','155')))
    add('equal-exit-and-fulfil-loss',[assess('assessment','2025-01-01','100','30','30'),finish('fulfil',penalty='30')],
        dict(assessment=assessed,settlement=complete))
    path=OUT/'authored-cases.json';assert not path.exists();path.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=[path,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-onerous-contract-sequence-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/extended-method-exchanges-20261015/corporate-residuals/semantic-contract.md']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_inputs=len(paths))))


if __name__=='__main__':main()
