"""One-shot evidence runner. Each --attempt creates a new preserved directory."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time
import traceback

import financing_control as candidate
import exhaustive_reference as oracle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = 'docs/plans/accounting-two-date-financing-control-20261026.md'
CHECKS, CONTROLS, RECORDS = [], [], {}


def encoded(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: encoded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(v) for v in value]
    return value


def save(path, value):
    path.write_text(json.dumps(encoded(value), indent=2, sort_keys=True) + '\n')


def check(name, actual, expected=True):
    CHECKS.append(dict(id=name, passed=actual == expected, actual=encoded(actual), expected=encoded(expected)))
    if actual != expected:
        raise AssertionError(name)


def rejected(name, model, mutate, code):
    changed = deepcopy(model)
    mutate(changed)
    try:
        candidate.analyze(changed)
    except candidate.InvalidModel as exc:
        actual = str(exc)
    else:
        actual = 'accepted'
    CONTROLS.append(dict(id=name, role='input_admission', actual=actual, expected=code))
    check(name, actual, code)


def compare(name, model, table):
    actual = candidate.analyze(model)
    expected = oracle.enumerate_strategies(table, F(model['investment']))
    check(name + '_full_branches', actual['branches'], expected['branches'])
    check(name + '_strategies', actual['strategies'], expected['strategies'])
    check(name + '_four_strategies', len(expected['all_strategies']), 4)
    for i, row in enumerate(expected['all_strategies']):
        check(f'{name}_pricing_{i}', candidate.price_strategy(model, row['strategy'], actual), row['pricing'])
        check(f'{name}_local_deviations_{i}', row['stable'], row['strategy'] in actual['strategies'])
    RECORDS[name] = dict(candidate=actual, exhaustive=expected)
    return actual, expected


def exercise(model, table):
    result, exhaustive = compare('base', model, table)
    check('unique_current_rights_continuation', result['strategies'], [dict(debt='risky', conversion='safe')])
    for branch, record in result['branches'].items():
        for policy, payoff in record['policies'].items():
            for i, leaf in enumerate(payoff['leaves']):
                cash = leaf['cash']
                prefix = f'cash_{branch}_{policy}_{i}'
                check(prefix + '_conserved', sum(cash.values()), leaf['estate'])
                check(prefix + '_nonnegative', all(v >= 0 for v in cash.values()))
                check(prefix + '_senior', cash['senior'], min(F(40), leaf['estate']))
                check(prefix + '_priority', cash['new'] + cash['old'] == 0 or cash['senior'] == 40)
                if branch == 'debt':
                    check(prefix + '_face_limit', cash['new'] <= 80)
                    check(prefix + '_equity_residual', cash['old'] == 0 or cash['new'] == 80)
                else:
                    check(prefix + '_share_ratio', cash['new'], cash['old'] * 3)
                    check(prefix + '_no_debt', record['rights']['new_debt'], F(0))
    strategy = result['strategies'][0]
    price = candidate.price_strategy(model, strategy, result)
    for key, value in {'quote': F(17000,441), 'required_owner_cash': F(9460,441), 'owner_net_utility': F(3540,441)}.items():
        check(key, price[key], value)
    check('owner_discounted_cash', price['discounted_cash']['old'], F(13000,441))
    threshold = F(9460,441)
    offers = {}
    for label, cash, status in [('cash20',F(20),'rejected'),('cash22',F(22),'accepted'),
                                ('below',threshold-F(1,441),'rejected'),('exact',threshold,'accepted'),('above',threshold+F(1,441),'accepted')]:
        offered = candidate.offer(model, strategy, price['quote'], cash)
        offers[label] = offered
        check('funding_' + label, offered['status'], status)
        check('funding_legs_' + label, sum(x['amount'] for x in offered['cash_legs']), F(0))
        check('funding_dates_' + label, {x['date'] for x in offered['cash_legs']} == {model['dates'][0]})
        if status == 'rejected':
            check('funding_no_execution_' + label, offered['execution'], 'no_funding_executed')
    check('cash20_reason', offers['cash20']['reasons'], ['insufficient_owner_cash'])
    RECORDS['offers'] = offers
    CONTROLS.extend(dict(id='owner_' + key, role='offer_acceptance', result=offers[key]) for key in ('cash20','below','exact','above'))
    higher_outside = deepcopy(model)
    higher_outside['outside_utility_date0'] = '9'
    refusal = candidate.offer(higher_outside, strategy, price['quote'], 22)
    check('participation_separate_from_cash', refusal['reasons'], ['owner_participation'])
    CONTROLS.append(dict(id='participation_refusal', role='offer_acceptance', result=refusal))
    tied_outside = deepcopy(model)
    tied_outside['outside_utility_date0'] = str(price['owner_net_utility'])
    indifferent = candidate.offer(tied_outside, strategy, price['quote'], 22)
    check('participation_tie', indifferent['participation'], 'indifferent')
    check('participation_tie_feasible', indifferent['status'], 'accepted')
    CONTROLS.append(dict(id='participation_tie', role='offer_acceptance', result=indifferent))
    stale_table = deepcopy(table)
    stale_table['controller']['conversion'] = 'old'
    stale = oracle.enumerate_strategies(stale_table)
    check('stale_control_continuation', stale['strategies'], [dict(debt='risky',conversion='risky')])
    stale_strategy = stale['strategies'][0]
    stale_price = candidate.price_strategy(model, stale_strategy, result)
    check('stale_quote', stale_price['quote'], F(15500,441))
    check('stale_owner_cash', stale_price['required_owner_cash'], F(10960,441))
    check('lender_shortfall', price['quote'] - stale_price['quote'], F(1500,441))
    stale_offer = candidate.offer(model, stale_strategy, price['quote'], 22)
    check('stale_control_offer_refusal', stale_offer['reasons'], ['continuation_deviation','quote_payoff_mismatch'])
    consistent_wrong_policy = candidate.offer(model, stale_strategy, stale_price['quote'], 22)
    check('stale_quote_cash_refusal', consistent_wrong_policy['reasons'], ['continuation_deviation','insufficient_owner_cash'])
    RECORDS['stale_control'] = dict(exhaustive=stale, priced=stale_price, offered=stale_offer, own_quote=consistent_wrong_policy)
    CONTROLS.append(dict(id='stale_control',role='offer_acceptance',result=RECORDS['stale_control']))
    zero_model, zero_table = deepcopy(model), deepcopy(table)
    zero_model['conversion_risky_private_benefit'] = '0'
    for leaf in zero_table['branches']['conversion']['risky']:
        leaf['private_benefit'] = '0'
    zero_result, _ = compare('zero_private_benefit',zero_model,zero_table)
    payoffs = zero_result['branches']['conversion']['policies']
    check('zero_benefit_old_prefers_safe', payoffs['safe']['terminal_utility']['old'] > payoffs['risky']['terminal_utility']['old'])
    check('base_old_prefers_risky', result['branches']['conversion']['policies']['risky']['terminal_utility']['old'], F(33,2))
    tied_model, tied_table = deepcopy(model), deepcopy(table)
    tied_model['branches']['conversion']['policies']['safe'] = [['1','90']]
    tied_table['branches']['conversion']['safe'][0].update(estate='90',cash=['40','75/2','25/2'])
    tied, _ = compare('policy_tie',tied_model,tied_table)
    check('retain_all_tied_policies', tied['strategies'], [dict(debt='risky',conversion='safe'),dict(debt='risky',conversion='risky')])
    CONTROLS.append(dict(id='policy_tie',role='tie_preservation',strategies=tied['strategies']))
    governance_tie = deepcopy(model)
    governance_tie['conversion_shares'] = '40'
    unsupported = candidate.analyze(governance_tie)
    check('vote_tie_unresolved', unsupported['status'], 'unsupported_governance')
    check('vote_tie_no_strategies', unsupported['strategies'], [])
    refused_tie = candidate.offer(governance_tie, strategy, 0, 100)
    check('vote_tie_offer_refused', 'unsupported_governance' in refused_tie['reasons'])
    CONTROLS.append(dict(id='unsupported_vote_tie',role='governance',result=unsupported))
    governance_tie['governance']['tie_controller'] = 'new'
    check('explicit_tie_rule', candidate.analyze(governance_tie)['branches']['conversion']['rights']['controller'], 'new')
    CONTROLS.append(dict(id='named_tie_controller',role='governance',controller='new'))
    invalid_controls(model)
    # Fault injection tests oracle sensitivity, not arbitrary-state API admission.
    wrong_rights = deepcopy(result['branches']['conversion']['rights'])
    wrong_rights['new_debt'] = F(80)
    duplicated = candidate.branch_payoffs(model, 'conversion', wrong_rights)
    check('double_debt_recovery_detected', duplicated != exhaustive['branches']['conversion']['policies'])
    CONTROLS.append(dict(id='double_counted_debt',role='oracle_sensitivity',detected=True))
    wrong_discount = deepcopy(model)
    wrong_discount['discount_factors'] = ['1','21/20']
    mismatch = candidate.price_strategy(wrong_discount, strategy)['quote']
    check('wrong_horizon_detected', mismatch != price['quote'])
    CONTROLS.append(dict(id='wrong_horizon',role='oracle_sensitivity',actual=mismatch,expected=price['quote']))
    for name, invalid in [('leaf_conditioned',{'debt':{'low':'safe','high':'risky'},'conversion':'safe'}),
                          ('extra_future_key',dict(strategy,terminal_realization='high'))]:
        try:
            candidate.price_strategy(model, invalid)
        except candidate.InvalidModel as exc:
            reason = str(exc)
        else:
            reason = 'accepted'
        check(name,reason,'nonanticipating_strategy_required')
        CONTROLS.append(dict(id=name,role='information_admission',result=reason))


def invalid_controls(model):
    rejected('negative_signal_mass', model, lambda m:m['branches']['debt'].update(probability='-1/2'), 'signal_mass')
    rejected('unnormalized_signal_mass', model, lambda m:m['branches']['debt'].update(probability='1/3'), 'signal_mass')
    rejected('zero_signal_out_of_scope', model, lambda m:m['branches']['debt'].update(probability='0'), 'signal_mass')
    rejected('unnormalized_leaf_mass', model, lambda m:m['branches']['debt']['policies'].update(risky=[['1/3','20'],['1/3','220']]), 'conditional_mass')
    rejected('negative_estate', model, lambda m:m['branches']['debt']['policies'].update(safe=[['1','-1']]), 'negative_estate')
    rejected('missing_discount_interval', model, lambda m:m.update(discount_factors=['21/20']), 'discount_intervals')
    rejected('nonpositive_discount', model, lambda m:m.update(discount_factors=['0','21/20']), 'discount_intervals')
    rejected('future_signal', model, lambda m:m.update(signal_known_date='2029-01-01'), 'information_timing')
    rejected('premature_terminal_knowledge', model, lambda m:m.update(terminal_known_date='2028-01-01'), 'information_timing')
    rejected('wrong_cash_date', model, lambda m:m.update(terminal_cash_date='2028-01-01'), 'cash_timing')
    rejected('reversed_dates', model, lambda m:m.update(dates=['2027-01-01','2029-01-01','2028-01-01']), 'date_order')
    rejected('unknown_governance', model, lambda m:m['governance'].update(rule='old_always_controls'), 'governance')
    rejected('missing_conversion', model, lambda m:m['branches']['conversion'].update(converts=False), 'conversion_event')
    rejected('inexact_numeric_input', model, lambda m:m.update(investment=60.0), 'exact_rational_required')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'attempt-0[123]', args.attempt):
        raise SystemExit('attempt must be attempt-01, -02 or -03')
    output = HERE / args.attempt
    output.mkdir(exist_ok=False)
    start = time.monotonic()
    baseline = ROOT / 'data/accounting-master/literature-closure-20261026'
    pinned = {baseline/'persistent-financing.py':'e387ac1cfa2d9bbe4282a7e561890ee2c4c3b58cd05bc2c63eba4d448d0efa82',
              baseline/'persistent-financing-results.json':'cd1adb9be85da66cdec5e9d0d1811e4df79786240415c40e2a73bf9db26af2e2'}
    sources = [ROOT/PLAN, HERE/'audit.md', HERE/'model.json', HERE/'independent-payoffs.json',
               HERE/'financing_control.py', HERE/'exhaustive_reference.py', HERE/'verify.py', *pinned]
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    save(output/'source-lock.json',hashes)
    inputs = output/'inputs'
    inputs.mkdir()
    for path in sources:
        if path not in pinned:
            (inputs/path.name).write_bytes(path.read_bytes())
    error, status = None, 'FAIL'
    try:
        check('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1')
        check('bytecode_disabled',os.environ.get('PYTHONDONTWRITEBYTECODE'),'1')
        for path, digest in pinned.items():
            check('protected_' + path.name,hashes[str(path.relative_to(ROOT))],digest)
        model=json.loads((HERE/'model.json').read_text())
        table=json.loads((HERE/'independent-payoffs.json').read_text())
        exercise(model,table)
        for path in sources:
            check('unchanged_' + str(path.relative_to(ROOT)),hashlib.sha256(path.read_bytes()).hexdigest(),hashes[str(path.relative_to(ROOT))])
        status='PASS'
    except Exception:
        error=traceback.format_exc()
        (output/'error.txt').write_text(error)
    elapsed=time.monotonic()-start
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    manifest=dict(status=status,git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
                  command=f'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 {str(HERE.relative_to(ROOT))}/verify.py --attempt {args.attempt}',
                  environment=dict(python=platform.python_version(),executable=os.sys.executable,platform=platform.platform()),
                  cpu_gpu='CPU only; GPU intentionally hidden; standard-library exact arithmetic',
                  seed='N/A exact finite enumeration',data_version='TwoDateFinancingFixture/1; source-lock.json',
                  plan=PLAN,result=str(HERE.relative_to(ROOT)/'result.md'),wall_seconds=elapsed,
                  artifacts=['records.json','checks.json','controls.json','source-lock.json','verification.json'],
                  attempts_budget=3,seconds_budget=300,attempt=args.attempt)
    save(output/'records.json',RECORDS)
    save(output/'checks.json',CHECKS)
    save(output/'controls.json',CONTROLS)
    save(output/'run-manifest.json',manifest)
    summary=dict(status=status,assertions=len(CHECKS),controls=len(CONTROLS),protected_files=len(sources),
                 full_comparison_cases=3,strategies_per_case=4,wall_seconds=elapsed,error=error)
    save(output/'verification.json',summary)
    print(json.dumps(summary))
    return 0 if status=='PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
