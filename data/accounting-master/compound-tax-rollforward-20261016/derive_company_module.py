"""Preserved company replay with explicit, reviewable tax-lifecycle changes."""
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def main():
    text = (ROOT/'data/accounting-master/company-eps-join-20261016/reference_join.py').read_text()
    replacements = [
        ('"""Exact documentary company replay and EPS projection; no book writes."""',
         '"""Par compound-tax company replay, derived from preserved CompanyEPSJoin/1."""'),
        ('from copy import deepcopy', 'from copy import deepcopy\nfrom reference_tax import calculate as tax_schedule, FINDINGS'),
        ('    need(debt == principal, "different_maturity_schedule", "unsupported")',
         '    need(principal == proceeds, "nonpar_maturity_schedule", "unsupported")\n'
         '    tax = instrument["tax"]\n'
         '    tax_request = dict(proceeds=str(proceeds), liability=str(debt), coupon=str(coupon),\n'
         '        period_rate=str(rate), tax_rate=tax["rate"], fiscal=dict(initial_base=tax["initial_liability_tax_base"],\n'
         '        accrued_base=str(proceeds+coupon), after_coupon_base=str(proceeds), deduction=str(coupon),\n'
         '        settlement_taxable_income="0", **{k:tax[k] for k in FINDINGS}))\n'
         '    schedule_result = tax_schedule(tax_request)\n'
         '    need(schedule_result["status"] == "conditional_complete", "fiscal_schedule_not_admitted", "unsupported")\n'
         '    tax_amounts = {k:Q(v) for k,v in schedule_result["amounts"].items()}'),
        ('keys = [*base_oracle.ACCOUNTS, "new_debt", "new_conversion_equity"]',
         'keys = [*base_oracle.ACCOUNTS, "new_debt", "new_conversion_equity", "compound_dtl"]'),
        ('        dict(id="new.accrue", date=instrument["maturity_date"], order=1,',
         '        dict(id="new.issue_tax", date=instrument["issue_date"], order=2,\n'
         '             journal={"P": dict(new_conversion_equity=tax_amounts["initial_dtl"], compound_dtl=-tax_amounts["initial_dtl"])}, flows=[]),\n'
         '        dict(id="new.accrue", date=instrument["maturity_date"], order=1,'),
        ('        dict(id="new.coupon", date=instrument["maturity_date"], order=2,',
         '        dict(id="new.accrue_tax", date=instrument["maturity_date"], order=2,\n'
         '             journal={"P": dict(compound_dtl=-tax_amounts["deferred_tax_expense_delta"],\n'
         '                  deferred_tax=tax_amounts["deferred_tax_expense_delta"])}, flows=[]),\n'
         '        dict(id="new.coupon", date=instrument["maturity_date"], order=3,'),
        ('date=instrument["maturity_date"], order=3,\n            journal=',
         'date=instrument["maturity_date"], order=4,\n            journal='),
        ('            taxable = base_oracle.pretax(books["P"])+return_timing',
         '            # Fiscal deduction is coupon only; book interest includes discount accretion.\n'
         '            taxable = base_oracle.pretax(books["P"])+return_timing+interest-coupon'),
        ('        if event["id"] == "new.conversion":\n            equity_changes += before_settle',
         '        if event["id"] == "new.issue_tax":\n            equity_changes -= tax_amounts["initial_dtl"]\n'
         '        if event["id"] == "new.conversion":\n            equity_changes += before_settle'),
        ('[*base_oracle.LIABS, "new_debt"]', '[*base_oracle.LIABS, "new_debt", "compound_dtl"]'),
        ('potential_numerator_increment=interest*(1-Q(instrument["tax"]["rate"]))',
         'potential_numerator_increment=tax_amounts["after_tax_cost"]'),
        ('flows=flows, daily_shares=trace, issue_debt=debt, issue_equity=original_equity,',
         'flows=flows, daily_shares=trace, issue_debt=debt, issue_equity=original_equity, tax_schedule=schedule_result,')]
    for before,after in replacements:
        wanted = 2 if before.startswith('date=instrument') else 1
        assert text.count(before) == wanted, before
        text = text.replace(before,after)
    target = OUT/'reference_company.py'
    assert not target.exists()
    target.write_text(text)
    print('Created separate company replay with 12 bounded lifecycle changes; original unchanged.')


if __name__ == '__main__':
    main()
