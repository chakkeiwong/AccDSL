"""Conditional financial-statement derivations; no bank runtime or model run."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
checks, groups = [], {}


def ck(name, actual, expected):
    checks.append(dict(name=name, actual=str(actual), expected=str(expected),
                       passed=actual == expected))


def journal(name, entries):
    ck(name + '/balance', sum(entries.values()), 0)
    return {k: str(v) for k, v in entries.items()}


def call_position(s, k, time):
    call = max(s-k, F(0)) + time
    return s, min(s, k) - time, call


def put_position(s, k, time):
    put = max(k-s, F(0)) + time
    return min(s, k), k+time, -put


# The correct continuing-involvement branch is an explicit conditional input.
# Each FV case uses FVTPL and gross income/expense presentation.
call_states = []
for name, s, time, want_l, want_net in [
    ('transfer', 80, 5, 75, 5), ('later', 100, 4, 91, 9),
    ('expiry', 110, 0, 95, 15),
]:
    asset, liability, net = call_position(F(s), F(95), F(time))
    ck(f'call/{name}/liability', liability, want_l)
    ck(f'call/{name}/net', asset-liability, want_net)
    ck(f'call/{name}/option-equality', asset-liability, net)
    call_states.append(dict(asset=str(asset), liability=str(liability), net=str(net)))
ck('call/first-remeasurement-profit', (100-80)-(91-75), 4)
ck('call/expiry-remeasurement-profit', (110-100)-(95-91), 6)
ck('call/transfer-balance', 275+80, 75+280)
ck('call/later-balance', 275+100, 91+284)
ck('call/exercise-cash', 275-95, 180)
ck('call/exercise-equity', 180+110, 280+4+6)
ck('call/duplicated-derivative-overstatement', 80-75+5-(80-75), 5)
groups['retained_call'] = {
    'states': call_states,
    'transfer': journal('call/transfer', {'debit-cash': 75, 'credit-associated-liability': -75}),
    'exercise': journal('call/exercise', {'debit-associated-liability': 95, 'credit-cash': -95}),
    'opening': {'cash': 200, 'asset': 80, 'equity': 280},
    'closing': {'cash': 180, 'asset': 110, 'liability': 0, 'equity': 290},
}

put_states = []
for name, s, time, want_a, want_l, want_net in [
    ('transfer', 120, 5, 100, 105, -5),
    ('later', 90, 4, 90, 104, -14), ('expiry', 80, 0, 80, 100, -20),
]:
    asset, liability, net = put_position(F(s), F(100), F(time))
    ck(f'put/{name}/asset-cap', asset, want_a)
    ck(f'put/{name}/liability', liability, want_l)
    ck(f'put/{name}/net', asset-liability, want_net)
    ck(f'put/{name}/option-equality', asset-liability, net)
    put_states.append(dict(asset=str(asset), liability=str(liability), net=str(net)))
ck('put/transfer-balance', 325+100, 105+320)
ck('put/later-change', (90-100)-(104-105), -9)
ck('put/expiry-change', (80-90)-(100-104), -6)
ck('put/exercise-cash', 325-100, 225)
ck('put/closing-equity', 225+80, 320-9-6)
ck('put/wrong-full-fair-value-overstates', 120-100, 20)
groups['written_put'] = {
    'states': put_states,
    'transfer': journal('put/transfer', {'debit-cash': 125, 'credit-asset': -20,
                                       'credit-associated-liability': -105}),
    'exercise': journal('put/exercise', {'debit-associated-liability': 100, 'credit-cash': -100}),
    'opening': {'cash': 200, 'asset': 120, 'equity': 320},
    'closing': {'cash': 225, 'asset': 80, 'liability': 0, 'equity': 305},
}

# A collar combines the retained call and written put. Use full put value,
# not just put time value, once the put is in the money.
collar_states = []
for name, s, tc, tp, want_l, want_net in [
    ('transfer', 100, 5, 1, 96, 4),
    ('up-interim', 130, 2, 1, 119, 11),
    ('down-interim', 70, 1, 2, 81, -11),
    ('up-expiry', 130, 0, 0, 120, 10),
    ('down-expiry', 70, 0, 0, 80, -10),
]:
    s, tc, tp = F(s), F(tc), F(tp)
    c = max(s-120, F(0))+tc
    p = max(80-s, F(0))+tp
    liability = min(s, F(120))+p-tc
    ck(f'collar/{name}/liability', liability, want_l)
    ck(f'collar/{name}/net', s-liability, want_net)
    ck(f'collar/{name}/option-equality', s-liability, c-p)
    collar_states.append(dict(name=name, asset=str(s), liability=str(liability),
                              call=str(c), put=str(p), net=str(c-p)))
ck('collar/initial-balance', 296+100, 96+300)
ck('collar/up-cumulative-income', 10-4, 6)
ck('collar/down-cumulative-income', -10-4, -14)
ck('collar/up-exercise-equity', 296-120+130, 306)
ck('collar/down-exercise-equity', 296-80+70, 286)
ck('collar/wrong-down-put-time-only-liability', 81-(70+2-1), 10)
groups['collar'] = {
    'states': collar_states,
    'transfer': journal('collar/transfer', {'debit-cash': 96, 'credit-associated-liability': -96}),
    'up_exercise': journal('collar/up-exercise', {'debit-associated-liability': 120, 'credit-cash': -120}),
    'down_exercise': journal('collar/down-exercise', {'debit-associated-liability': 80, 'credit-cash': -80}),
    'opening': {'cash': 200, 'asset': 100, 'equity': 300},
    'up_closing': {'cash': 176, 'asset': 130, 'liability': 0, 'equity': 306},
    'down_closing': {'cash': 216, 'asset': 70, 'liability': 0, 'equity': 286},
}

# Gross asset and liability have separate effective rates. No coupons or ECL
# changes, one remaining year; written put exercise price is 102.
asset0, liability0, terminal, strike = F(98), F(95), F(100), F(102)
asset_rate, liability_rate = terminal/asset0-1, terminal/liability0-1
ck('amortised/asset-rate', asset_rate, F(1,49))
ck('amortised/liability-rate', liability_rate, F(1,19))
asset_interest, liability_interest = asset0*asset_rate, liability0*liability_rate
ck('amortised/asset-income', asset_interest, 2)
ck('amortised/liability-expense', liability_interest, 5)
ck('amortised/net-income', asset_interest-liability_interest, -3)
ck('amortised/put-exercise-loss', strike-terminal, 2)
ck('amortised/closing-cash', 200+95-102, 193)
ck('amortised/closing-equity', 193+100, 298-3-2)
groups['amortised_option'] = {
    'asset_rate': str(asset_rate), 'associated_liability_rate': str(liability_rate),
    'accretion_asset': journal('amortised/asset', {'debit-asset': 2, 'credit-interest-income': -2}),
    'accretion_liability': journal('amortised/liability', {'debit-interest-expense': 5, 'credit-liability': -5}),
    'exercise': journal('amortised/exercise', {'debit-liability': 100, 'debit-loss': 2, 'credit-cash': -102}),
    'closing': {'cash': 193, 'asset': 100, 'liability': 0, 'equity': 293},
}

# Same measurement snapshot, different admitted management categories. No
# interval accrual/FX/tax/fees. ECL of 3 is a supplied cumulative measurement.
cost, fair, ecl, cash_after_purchase = F(100), F(98), F(3), F(100)
ac_net = cost-ecl
fvoci_oci = fair-cost+ecl
ck('category/ac-net', ac_net, 97)
ck('category/ac-profit', -ecl, -3)
ck('category/fvoci-carrying', fair, 98)
ck('category/fvoci-profit', -ecl, -3)
ck('category/fvoci-net-oci', fvoci_oci, 1)
ck('category/fvoci-total-comprehensive', -ecl+fvoci_oci, -2)
ck('category/fvtpl-profit', fair-cost, -2)
ck('category/ac-equity', cash_after_purchase+ac_net, 197)
ck('category/fvoci-equity', cash_after_purchase+fair, 200-ecl+fvoci_oci)
ck('category/fvtpl-equity', cash_after_purchase+fair, 198)
ac_sale_gain = fair-ac_net
ck('disposal/ac-gain', ac_sale_gain, 1)
ck('disposal/ac-lifetime-profit', -ecl+ac_sale_gain, -2)
ck('disposal/fvoci-recycle', fvoci_oci, 1)
ck('disposal/fvoci-lifetime-profit', -ecl+fvoci_oci, -2)
ck('disposal/fvtpl-extra-gain', fair-fair, 0)
ck('disposal/all-cash', cash_after_purchase+fair, 198)
groups['debt_measurement_categories'] = {
    'AC': {'carrying': 97, 'profit': -3, 'OCI': 0, 'sale_gain': 1,
           'sale': journal('category/ac-sale', {'debit-cash': 98, 'debit-allowance': 3,
                                              'credit-gross-asset': -100, 'credit-gain': -1})},
    'FVOCI_debt': {'carrying': 98, 'profit': -3, 'OCI': 1, 'sale_recycling': 1,
                  'fair_change': journal('category/fv-change', {'debit-OCI': 2, 'credit-asset': -2}),
                  'impairment': journal('category/fv-impairment', {'debit-impairment': 3, 'credit-OCI': -3}),
                  'recycling': journal('category/recycle', {'debit-OCI': 1, 'credit-gain': -1})},
    'FVTPL': {'carrying': 98, 'profit': -2, 'OCI': 0, 'sale_gain': 0},
    'all_closing_cash_and_equity_after_sale': 198,
    'classification_is_not_free_election': True,
}

# Equity election is a different instrument, not a fourth category elected
# for the same debt. No dividends, trading or business-combination consideration.
ck('equity-election/fair-change', fair-cost, -2)
ck('equity-election/closing-equity', 200+(fair-cost), 198)
ck('equity-election/sale-cash', 100+98, 198)
ck('equity-election/profit', F(0), 0)
ck('equity-election/wrong-recycling-expense', 0-(fair-cost), 2)
groups['equity_election'] = {'profit': 0, 'OCI': -2, 'sale_recycling': 0,
                           'cash_after_sale': 198, 'equity_after_sale': 198,
                           'within_equity_transfer_permitted': True}

# A diagnostic of modified time value, not an invented significance threshold.
# Six monthly interest payments; principal repaid at month six.
principal = F(100)
contract_flows = [principal*F(12,100)/12]*6
benchmark_flows = [principal*F(6,100)/12]*6
ck('time-value/monthly-contract-interest', contract_flows[0], 1)
ck('time-value/monthly-benchmark-interest', benchmark_flows[0], F(1,2))
ck('time-value/period-difference', contract_flows[0]-benchmark_flows[0], F(1,2))
ck('time-value/cumulative-difference', sum(contract_flows)-sum(benchmark_flows), 3)
ck('time-value/contract-total-with-principal', principal+sum(contract_flows), 106)
ck('time-value/benchmark-total-with-principal', principal+sum(benchmark_flows), 103)
groups['modified_time_value_diagnostic'] = {
    'contract': 'Monthly reset to one-year rate; this supplied scenario holds it at 12%',
    'benchmark': 'Otherwise identical; monthly reset to one-month rate, here 6%',
    'period_interest_difference': '1/2', 'cumulative_difference': '3',
    'decision': 'No automatic pass/fail; evaluate reasonably possible scenarios and significance under admitted rule',
}

sources = [ROOT/'docs/design/research/p08-v3-preparation'/name
           for name in ['eu-2023-1803-original.pdf', 'eu-2023-1803-original.txt']]
result = dict(passed=all(c['passed'] for c in checks), count=len(checks),
              group_count=len(groups), groups=groups, checks=checks,
              sources=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                       for p in sources],
              evidence_role='Exact conditional accounting derivations; not empirical option valuation or bank runtime')
(OUT/'cases.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: result[k] for k in ['passed', 'count', 'group_count']}))
assert result['passed'], [c for c in checks if not c['passed']]
