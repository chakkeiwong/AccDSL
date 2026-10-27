"""Freeze hand-derived outcomes before the lifecycle/company implementations."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREV = ROOT / 'data/accounting-master/company-eps-join-20261016'


def main():
    premises = json.loads((PREV / 'premises.json').read_text())
    inst = premises['new_instrument']
    inst.update(id='new-par-July-compound', principal='100', period_rate='3/23')
    inst['tax'] = dict(rate='1/4', initial_liability_tax_base='100',
        coupon_deductible_at_accrual=True, discount_not_separately_deductible=True,
        fiscal_proceeds_are_debt=True, settlement_no_additional_tax=True,
        sufficient_taxable_income=True, no_other_counterfactual_earnings_tax=True,
        complete_consequences=True)
    expected = deepcopy(json.loads((PREV / 'authored_expectations.json').read_text()))
    expected['kind'] = 'Independent hand derivation; unchanged baseline copied, lifecycle deltas authored before calculator'
    for world in ('conversion', 'redemption'):
        expected[world].update(group_profit='93', parent_profit='1713/20', basic_numerator='1713/20',
            deferred_tax='4', pretax='124', parent_legal_profit='81/2', potential_numerator_increment='9')
    expected['conversion']['basic_eps'] = '125049/16808'
    expected['redemption'].update(cash='641', assets='721', equity='721', parent_equity='2823/4',
        parent_legal_cash='977/2', parent_legal_equity='1337/2', financing_payments='210',
        net_cash='41', basic_eps='1713/200')
    expected['journal_targets'].update(
        accrue={'finance_expense':'12','new_debt':'-12'},
        issue_tax={'new_conversion_equity':'2','compound_dtl':'-2'},
        accrue_tax={'compound_dtl':'2','deferred_tax':'-2'},
        conversion={'new_debt':'100','capital':'-100'},
        redemption={'new_debt':'100','cash':'-100'})
    cases = [
        dict(id='coupon', values=['100','92','4','3/23','1/4'], expected=['8','12','2','6','-1','-2','9']),
        dict(id='zero-coupon', values=['100','92','0','2/23','1/4'], expected=['8','8','2','6','0','-2','6']),
        dict(id='no-equity', values=['100','100','4','1/25','1/4'], expected=['0','4','0','0','-1','0','3']),
        dict(id='zero-tax', values=['100','92','4','3/23','0'], expected=['8','12','0','8','0','0','12']),
        dict(id='other-split-rate', values=['60','50','5','3/10','1/5'], expected=['10','15','2','8','-1','-2','12'])]
    schedule = dict(input_fields=['proceeds','liability','coupon','period_rate','tax_rate'],
        expected_fields=['gross_equity','finance_expense','initial_dtl','net_issue_equity',
                         'current_tax_expense_delta','deferred_tax_expense_delta','after_tax_cost'], cases=cases)
    for name, value in [('premises.json',premises),('authored-expectations.json',expected),('authored-schedules.json',schedule)]:
        p = OUT / name
        assert not p.exists()
        p.write_text(json.dumps(value, indent=2)+'\n')
    files = [OUT / n for n in ('authored.py','premises.json','authored-expectations.json','authored-schedules.json','source-reading.md')]
    files += [ROOT / p for p in (
        'docs/plans/accounting-compound-tax-rollforward-20261016.md',
        'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        'data/accounting-master/company-eps-join-20261016/reference_join.py',
        'data/accounting-master/company-eps-join-20261016/base-packet-lock.json',
        'data/accounting-master/company-eps-join-20261016/authored_expectations.json',
        'data/accounting-master/company-composition-20261016/authored_cases.py',
        'data/accounting-master/company-composition-20261016/financial_checks.py',
        'data/accounting-master/company-composition-20261016/attempt-03/portable-exchanges.json',
        'data/accounting-master/continuation-integrity-eps-20261016/ordered-eps/reference_selector.py',
        'data/accounting-master/continuation-integrity-eps-20261016/ordered-eps/schema_design.py')]
    records = [dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
    (OUT / 'input-lock.json').write_text(json.dumps(dict(files=records), indent=2)+'\n')
    print(json.dumps(dict(locked_files=len(records), schedule_cases=len(cases), company_worlds=2)))


if __name__ == '__main__':
    main()
