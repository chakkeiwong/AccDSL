"""Independent finite arithmetic for a proposal, not product implementation.

Read authored examples and the preserved company fixture. Derive financial
consequences from their inputs; do not treat agreement between frontends or a
specified transaction trace as executed conformance. Write one fresh report.
"""
import hashlib
import json
import platform
import sys
import time
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

START = time.monotonic()
ROOT = Path(__file__).resolve().parents[4]
EXAMPLES = ROOT / 'docs/design/proposal/architecture/platform-contract-examples-v1.json'
used = {Path(__file__).resolve()}
checks = []


def load(path):
    path = Path(path)
    used.add(path.resolve())
    return json.loads(path.read_text())


def check(label, value):
    checks.append({'id': label, 'passed': bool(value)})


def rat(value):
    if isinstance(value, dict):
        assert set(value) == {'n', 'd'}
        n, d = int(value['n']), int(value['d'])
        x = F(n, d)
        assert d > 0 and str(n) == value['n'] and str(d) == value['d']
        assert x.numerator == n and x.denominator == d
        return x
    return F(value)


def pins(value):
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            path = (ROOT / value['path']).resolve()
            check('repository reference ' + value['path'], path.is_relative_to(ROOT))
            used.add(path)
            check('reference bytes ' + value['path'], path.is_file() and
                  hashlib.sha256(path.read_bytes()).hexdigest() == value['sha256'])
        for child in value.values():
            pins(child)
    elif isinstance(value, list):
        for child in value:
            pins(child)


examples = load(EXAMPLES)
pins(examples)
cases = {c['id']: c for c in examples['cases']}
check('unique example IDs', len(cases) == len(examples['cases']))
check('specified-only evidence', examples['evidence_mode'] == 'specification_example'
      and examples['product_implemented'] is False)

for key, stress in [('LX01', F(7, 100)), ('LX02', F(9, 100))]:
    row = cases[key]
    source = cases['LX01']['inputs']['typed_construction']
    if key == 'LX02':
        stress = rat(row['inputs']['replace']['floating_annual_rate'])
    else:
        stress = rat(source['floating_annual_rate'])
    principal, fixed, years = (rat(source[k]) for k in
                               ['principal', 'fixed_annual_rate', 'year_fraction'])
    values = [principal * ((1-x)*fixed+x*stress)*years for x in [F(0), F(1, 2), F(1)]]
    check(key + ' independent interest arithmetic', values == [rat(v) for v in row['expected']['at_x_0_half_1']])
    check(key + ' affine coefficients',
          values[0] == rat(row['expected']['interest_affine']['constant']) and
          values[2]-values[0] == rat(row['expected']['interest_affine']['coefficient_x']))
check('frontend agreement not asserted as executed',
      cases['LX01']['expected']['frontend_agreement'] == 'specified, not measured')

# Accumulate the preserved historical entries independently of their expected table.
ns = load(ROOT / examples['baseline']['path'])
balances = defaultdict(F, {k: F(v) for k, v in ns['opening'].items()})
check('opening balance', sum(balances.values()) == 0)
annual = defaultdict(F)
for period in ['2024H1', '2024H2']:
    movements = defaultdict(F)
    cashflows = defaultdict(F)
    for event in ns['historical_events']:
        if event['period'] != period:
            continue
        lines = [(p['account'], F(p['signed_amount'])) for p in event['postings']]
        check('balanced authored event ' + event['id'], sum(v for _, v in lines) == 0)
        for name, value in lines:
            balances[name] += value
            movements[name] += value
            if name == 'cash' and event['cash_class']:
                cashflows[event['cash_class']] += value
    temporary = [k for k, role in ns['accounts'].items() if role in ['income', 'expense']]
    profit = -sum(movements[k] for k in temporary)
    revenue = -movements['revenue']
    for name in temporary:
        balances['retained'] += balances[name]
        balances[name] = F(0)
    assets = sum(balances[k] for k, role in ns['accounts'].items() if role in ['asset', 'contra_asset'])
    observed = {'cash': balances['cash'], 'receivables': balances['receivables'],
                'inventory': balances['inventory'], 'plant_net': balances['plant_cost']+balances['accum_depreciation'],
                'tax_prepaid': balances['tax_prepaid'], 'assets': assets,
                'payables': -balances['payables'], 'debt': -balances['debt'],
                'equity': -balances['capital']-balances['retained'],
                'revenue': revenue, 'profit': profit,
                **{k+'_cash': cashflows[k] for k in ['operating', 'investing', 'financing']}}
    for name, wanted in ns['expected'][period].items():
        check(period + ' ' + name, observed[name] == F(wanted))
    for name in ['revenue', 'profit', 'operating_cash', 'investing_cash', 'financing_cash']:
        annual[name] += observed[name]
    check(period + ' closed balance', sum(balances.values()) == 0)
annual['cash_change'] = balances['cash']-F(ns['opening']['cash'])
for name, wanted in ns['expected']['2024FY'].items():
    check('2024FY ' + name, annual[name] == F(wanted))

bridges = cases['IX01']['expected']['historical_reconstruction']
check('receivables bridge', F(ns['opening']['receivables'])+annual['revenue']-balances['receivables'] == rat(bridges['collections']))
historical_cogs = sum(F(p['signed_amount']) for e in ns['historical_events'] for p in e['postings'] if p['account'] == 'cost_of_sales')
purchases = balances['inventory']-F(ns['opening']['inventory'])+historical_cogs
check('inventory bridge', purchases == rat(bridges['purchases']))
check('payables bridge', -F(ns['opening']['payables'])+purchases+balances['payables'] == rat(bridges['supplier_payments']))

# Derive forecast flows from demand, collection, purchase and payment assumptions.
# Three x values check connected identities; the algebra is affine by construction.
f = {k: F(v) for k, v in ns['forecast'].items() if k not in ['start', 'end_exclusive']}


def company(x, floating_rate):
    revenue = f['demand_units']*f['price']
    cogs = f['demand_units']*f['unit_cost']
    ending_inventory = f['target_inventory_units']*f['unit_cost']
    purchases = ending_inventory-balances['inventory']+cogs
    collections = f['current_sales_collection_fraction']*revenue+f['legacy_receivable_collections']
    supplier_payment = f['old_payables_paid']+f['new_purchases_paid']
    # Existing plant and two additions: 10 + 10/5 + 12/12.
    depreciation = F(10)+F(10, 5)+F(12, 12)
    interest = -balances['debt']*((1-x)*F(1, 20)+x*floating_rate)
    pbt = revenue-cogs-f['payroll']-depreciation-interest
    tax = f['tax_rate']*max(F(0), pbt)
    profit = pbt-tax
    ocf = collections-supplier_payment-f['payroll']-interest-tax
    cash = balances['cash']+ocf-f['capex_at_period_end']-f['dividend']
    ar = balances['receivables']+revenue-collections
    ap = -balances['payables']+purchases-supplier_payment
    plant = balances['plant_cost']+balances['accum_depreciation']+f['capex_at_period_end']-depreciation
    equity = -balances['capital']-balances['retained']+profit-f['dividend']
    assets = cash+ar+ending_inventory+plant
    check('scenario balance ' + str((x, floating_rate)), assets == ap-balances['debt']+equity)
    return {'interest':interest,'profit_before_tax':pbt,'tax':tax,'profit':profit,
            'operating_cash':ocf,'cash':cash,'equity':equity,'assets':assets,
            'receivables':ar,'inventory':ending_inventory,'payables':ap,
            'debt':-balances['debt'],'plant_net':plant}


for x in [F(0), F(1, 2), F(1)]:
    result = company(x, F(7, 100))
    for name, coefficients in cases['IX01']['expected']['joint_affine'].items():
        check('joint forecast ' + str(x) + ' ' + name,
              result[name] == rat(coefficients['constant'])+x*rat(coefficients['coefficient_x']))
    for name, value in cases['IX01']['expected']['constant_balances'].items():
        check('constant balance ' + str(x) + ' ' + name, result[name] == rat(value))
    if x in [F(0), F(1)]:
        old = ns['expected']['2025_fixed' if x == 0 else '2025_floating']
        for name in result.keys() & old.keys():
            check('protected endpoint ' + str(x) + ' ' + name, result[name] == F(old[name]))
    else:
        for name, value in cases['IX01']['expected']['midpoint'].items():
            check('midpoint ' + name, result[name] == rat(value))
changed = company(F(1), F(9, 100))
for name, wanted in cases['IX02']['expected']['all_floating'].items():
    check('changed rate ' + name, changed[name] == rat(wanted))

partial = cases['FX01']
mass = [rat(x) for x in partial['inputs']['masses']]
known = rat(partial['inputs']['cash'][0])
check('partial mass conserved', sum(mass) == 1)
derived_bounds = [mass[0]*known+mass[1]*rat(b) for b in partial['inputs']['independent_unresolved_bounds']]
check('unconditional mean bounds', derived_bounds == [rat(v) for v in partial['expected']['mean_bounds']])
check('no invented mean', partial['expected']['unconditional_mean'] is None)
check('zero conditioning mass', sum(rat(v) for i,v in enumerate(cases['FX02']['inputs']['prior']) if i in cases['FX02']['inputs']['event_members']) == 0)
check('economic shortfall', rat(cases['FX04']['inputs']['due'])-rat(cases['FX04']['inputs']['available_cash']) == rat(cases['FX04']['expected']['shortfall']))
check('overlapping classifications', sum(rat(x) for x in cases['IX05']['inputs']['revenue_by_product']) == sum(rat(x) for x in cases['IX05']['inputs']['revenue_by_region']) == rat(cases['IX05']['expected']['revenue']))
check('migration exact decimal', F(cases['PX08']['inputs']['original_value']) == rat(cases['PX08']['inputs']['candidate_exact']) != rat(cases['PX08']['inputs']['adversarial_candidate']))
check('specified replay has no second post', cases['PX01']['expected']['event_posting_count'] == 1 and not cases['PX02']['expected']['additional_commit'])
check('counterpart traces explicitly unexecuted', all('no database' in c['evidence_limit'] for c in cases.values() if c['id'].startswith('PX')))

out = Path(sys.argv[1]).resolve()
failed = [c for c in checks if not c['passed']]
report = {'passed':not failed,'checks':checks,'failures':failed,
          'input_hashes':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)},
          'manifest':{'command':'python3 docs/design/proposal/architecture/platform-contract-calculation-v1.py '+str(out),
                      'git_commit':'N/A: historical repository marker is unusable',
                      'environment':platform.python_version()+' standard library',
                      'cpu_gpu':'CPU only; no accelerator framework imported',
                      'seeds':'N/A: deterministic exact arithmetic',
                      'data_version':examples['baseline'],
                      'wall_seconds':round(time.monotonic()-START,4),
                      'plan':'docs/plans/accounting-p16-direct-execution-20261006.md','result':str(out)},
          'limits':'Exact finite document calculations and pins only. No compiler, runtime, solver, storage/recovery, accounting-authority or empirical-forecast acceptance.'}
with out.open('x') as stream:
    json.dump(report,stream,indent=2)
    stream.write('\n')
print(json.dumps({'passed':not failed,'checks':len(checks),'failures':failed,'result':str(out)}))
sys.exit(1 if failed else 0)
