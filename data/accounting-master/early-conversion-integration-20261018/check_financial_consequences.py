"""Independent documentary arithmetic; no accounting engine or tax-law inference."""
from datetime import date, datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    checks = []

    def equal(name, actual, expected):
        assert actual == expected, (name, actual, expected)
        checks.append(dict(check=name, actual=str(actual), expected=str(expected), passed=True))

    issue, conversion, end = date(2025, 7, 1), date(2025, 10, 1), date(2026, 1, 1)
    first, second = (conversion - issue).days, (end - conversion).days
    equal('preconversion days', first, 92)
    equal('actual-share days', second, 92)
    equal('nonoverlapping half-open intervals', first + second, (end - issue).days)
    rate, coupon, principal, proceeds, equity = F(1, 23), F(400), F(9200), F(10000), F(800)
    discount = coupon / (1 + rate) + (principal + coupon) / (1 + rate) ** 2
    equal('issue debt present value', discount, principal)
    equal('issue components', principal + equity, proceeds)
    interest = principal * rate
    equal('first effective interest', interest, coupon)
    before_coupon = principal + interest
    equal('before October coupon', before_coupon, F(9600))
    after_coupon = before_coupon - coupon
    equal('after October coupon / early transfer', after_coupon, F(9200))
    equal('redemption-world second interest', after_coupon * rate, F(400))
    equal('redemption-world closing debt', after_coupon * (1 + rate), F(9600))

    def entry(event, debits, credits):
        equal(event + ': balanced', sum(debits.values(), F()), sum(credits.values(), F()))
        return dict(event=event, debits={k: str(v) for k, v in debits.items()},
                    credits={k: str(v) for k, v in credits.items()})

    common = [
        entry('1 July issue', {'cash': proceeds}, {'debt': principal, 'conversion_equity': equity}),
        entry('July-September accrual', {'interest_expense': interest}, {'debt': interest}),
        entry('1 October coupon', {'debt': coupon}, {'cash': coupon}),
    ]
    early = common + [entry('1 October unchanged original-right conversion', {'debt': after_coupon}, {'ordinary_equity': after_coupon})]
    redemption = common + [
        entry('October-December accrual', {'interest_expense': F(400)}, {'debt': F(400)}),
        entry('1 January 2026 cash settlement', {'debt': F(9600)}, {'cash': F(9600)}),
    ]
    early_transfer = early[-1]
    equal('no acceleration in early transfer', F(early_transfer['debits']['debt']), principal)
    equal('original conversion equity remains', equity, F(800))
    equal('total equity components following conversion', equity + after_coupon, proceeds)
    conversion_profit_accounts = {'gain_on_conversion', 'loss_on_conversion'}
    assert not conversion_profit_accounts.intersection(early_transfer['debits'])
    assert not conversion_profit_accounts.intersection(early_transfer['credits'])
    checks.append(dict(check='conversion entry contains no gain/loss account under selected policy', passed=True))

    # These are supplied earnings effects, not inferred deductibility, tax bases,
    # current/deferred-tax postings or a universal fiscal treatment.
    full_tax_benefit, early_tax_benefit, conversion_tax_effect = F(200), F(100), F()
    full_net_expense = 2 * interest - full_tax_benefit
    early_net_expense = interest - early_tax_benefit
    equal('full net expense', full_net_expense, F(600))
    equal('preconversion net expense', early_net_expense, F(300))
    equal('avoided later net expense', full_net_expense - early_net_expense, F(300))

    day_counts = [(date(2025, 1, 1), date(2025, 4, 1), 2000),
                  (date(2025, 4, 1), issue, 2400),
                  (issue, conversion, 2400), (conversion, end, 2100)]
    denominator = sum((F((b - a).days * shares, 365) for a, b, shares in day_counts), F())
    equal('base denominator', denominator, F(162480, 73))
    potential = F(600 * first, 365)
    actual = F(600 * second, 365)
    full_increment = F(600 * (end - issue).days, 365)
    equal('potential plus actual share weights', potential + actual, full_increment)
    equal('full debt diluted increment', full_increment, F(22080, 73))
    ordinary, total, options = F(12000), F(15000), F(240)
    early_ordinary = ordinary + full_net_expense - early_net_expense - conversion_tax_effect
    early_total = total + full_net_expense - early_net_expense - conversion_tax_effect
    equal('early basic continuing earnings', early_ordinary, F(12300))
    equal('early basic total earnings', early_total, F(15300))
    equal('early basic denominator', denominator + actual, F(173520, 73))
    diluted = denominator + options + full_increment
    equal('fully diluted denominator', diluted, F(202080, 73))
    equal('fully diluted continuing numerator preserved', early_ordinary + early_net_expense, ordinary + full_net_expense)
    equal('fully diluted total numerator preserved', early_total + early_net_expense, total + full_net_expense)
    equal('fully diluted continuing EPS', (early_ordinary + early_net_expense) / diluted, F(7665, 1684))
    equal('fully diluted total EPS', (early_total + early_net_expense) / diluted, F(4745, 842))
    equal('fully diluted discontinued EPS', F(3000) / diluted, F(1825, 1684))
    equal('EPS reconciliation', F(7665, 1684) + F(1825, 1684), F(4745, 842))
    assert ordinary / (denominator + options) > (ordinary + full_net_expense) / diluted
    assert early_ordinary / (denominator + actual + options) > (early_ordinary + early_net_expense) / diluted
    assert F(5) > (early_ordinary + early_net_expense) / diluted
    checks.append(dict(check='options and debt dilute; preference increment 5 remains excluded in both worlds', passed=True))

    source_paths = [
        'docs/design/proposal/manuscript-navigation-20261018/sections/eps-lifecycle.tex',
        'data/accounting-master/early-conversion-source-20261018/sources/bdo-convertible-june-2026.pdf',
        'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
    ]
    result = dict(
        status='passed_documentary_arithmetic', checks=checks, checks_passed=len(checks),
        exact_journals=dict(early_conversion=early, no_early_conversion_counterfactual=redemption),
        tax=dict(full_year_earnings_benefit='200', preconversion_earnings_benefit='100',
                 additional_conversion_earnings_effect='0', provenance='supplied synthetic facts',
                 tax_law_or_tax_base_inference=False, tax_postings_not_specified=True),
        eps=dict(early_basic_continuing=str(early_ordinary / (denominator + actual)),
                 early_basic_total=str(early_total / (denominator + actual)),
                 potential_share_weight=str(potential), actual_share_weight=str(actual)),
        sources=[dict(path=p, sha256=sha(ROOT / p)) for p in source_paths],
        manifest=dict(git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                      command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/early-conversion-integration-20261018/check_financial_consequences.py',
                      environment=dict(python=sys.version, executable=sys.executable, platform=platform.platform()),
                      cpu_gpu='CPU only; GPU devices intentionally hidden; no numerical framework imported',
                      cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'), data_version='bound synthetic Version 3.43 facts',
                      random_seeds='N/A: exact deterministic arithmetic',
                      completed_utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic() - started,
                      plan='docs/plans/accounting-early-conversion-integration-20261018.md',
                      result='data/accounting-master/early-conversion-integration-20261018/financial-consequences.json',
                      script_sha256=sha(Path(__file__))),
        nonclaims=['No actual issuer admission', 'No tax-law conclusion', 'No universal early-conversion rule',
                   'No accounting-engine implementation', 'No independent domain acceptance'])
    (OUT / 'financial-consequences.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], checks_passed=len(checks), result=result['manifest']['result'])))


if __name__ == '__main__':
    main()
