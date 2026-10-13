"""Conditional settlement paths and exact query-specific aggregation tests."""
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (UNIT / name).write_text(json.dumps(value, indent=2) + '\n')

b = json.loads((UNIT / 'baseline.json').read_text())
checks = {}
for path, digest in b['dependencies'].items():
    checks['dependency:' + path] = sha(ROOT / path) == digest
repair = json.loads((ROOT / 'data/accounting-master/apple-coupled-completion-20261013/conditional-repair.json').read_text())
assets = json.loads((ROOT / 'data/accounting-master/apple-assets-20261008/asset-history.json').read_text())
quarter = json.loads((ROOT / 'data/accounting-master/apple-interim-network-20261013/statement-readings.json').read_text())
row = {r['id']: r for r in quarter['rows']}
histories = {}
for h in assets['histories']:
    cap = h['statement_effects']['liabilities']
    expense = repair['hypothetical_accruals'][h['id']]
    histories[h['id']] = {'capital': cap, 'expense': expense}
checks['equal_opening_total'] = sum(histories['H1'].values()) == sum(histories['H2'].values()) == 3082

def path(initial, timing):
    balances = dict(initial)
    periods = []
    for date in [1, 2]:
        journals = []
        paid = {'capital': 0, 'expense': 0}
        for kind in ['capital', 'expense']:
            if timing[kind] != date:
                continue
            paid[kind] = balances[kind]
            journals.append({'period': date, 'event': 'settle_' + kind,
                'postings': [{'account': kind + '_liability', 'debit': paid[kind], 'credit': 0},
                             {'account': 'cash', 'debit': 0, 'credit': paid[kind]}]})
            balances[kind] = 0
        cash = -sum(paid.values())
        effects = {
            'operations': {'net_income': 0},
            'comprehensive': {'net_income': 0, 'oci': 0, 'comprehensive_income': 0},
            'equity': {'profit': 0, 'oci': 0, 'owner_movements': 0, 'change': 0},
            'balance': {'cash_change': cash, 'ppe_change': 0, 'assets_change': cash,
                        'liabilities_change': cash, 'equity_change': 0,
                        'capital_liability_close': balances['capital'],
                        'expense_liability_close': balances['expense'],
                        'liability_close': sum(balances.values())},
            'cash_flow': {'net_income': 0, 'noncash_addback': 0,
                         'operating_liability_adjustment': -paid['expense'],
                         'operating': -paid['expense'], 'investing': -paid['capital'],
                         'financing': 0, 'change': cash}}
        periods.append({'period': date, 'journals': journals, 'effects': effects})
    return periods

scenarios = {'both_first': {'capital': 1, 'expense': 1},
             'capital_first': {'capital': 1, 'expense': 2},
             'expense_first': {'capital': 2, 'expense': 1}}
paths = []
for name, timing in scenarios.items():
    for hid, initial in histories.items():
        periods = path(initial, timing)
        prefix = name + ':' + hid
        for p in periods:
            tag = prefix + ':' + str(p['period'])
            for j in p['journals']:
                checks[tag + ':' + j['event']] = sum(x['debit']-x['credit'] for x in j['postings']) == 0
            e = p['effects'];bs=e['balance'];cf=e['cash_flow']
            checks[tag + ':balance'] = bs['assets_change'] == bs['liabilities_change'] + bs['equity_change']
            checks[tag + ':cash'] = cf['operating'] + cf['investing'] + cf['financing'] == cf['change'] == bs['cash_change']
            checks[tag + ':indirect'] = cf['net_income'] + cf['noncash_addback'] + cf['operating_liability_adjustment'] == cf['operating']
            checks[tag + ':income_equity'] = e['operations']['net_income'] == e['comprehensive']['comprehensive_income'] == e['equity']['change'] == 0
            checks[tag + ':nonnegative_liabilities'] = bs['capital_liability_close'] >= 0 and bs['expense_liability_close'] >= 0
        checks[prefix + ':liability_exhausted_once'] = periods[-1]['effects']['balance']['liability_close'] == 0 and sum(p['effects']['cash_flow']['change'] for p in periods) == -3082
        paths.append({'scenario': name, 'history': hid, 'timing':timing, 'opening':initial, 'periods':periods})

def select(s,h):
    return next(p for p in paths if p['scenario']==s and p['history']==h)

pairs = [(select('both_first',h)['periods'][0]['effects']['cash_flow']['operating'],
          select('both_first',h)['periods'][0]['effects']['cash_flow']['investing']) for h in ['H1','H2']]
checks['joint_cash_pairs'] = pairs == [(-2000,-1082),(-1000,-2082)]
bad_max = (max(p[0] for p in pairs), max(p[1] for p in pairs))
bad_min = (min(p[0] for p in pairs), min(p[1] for p in pairs))
checks['independent_maxima_rejected'] = bad_max not in pairs and sum(bad_max) == -2082
checks['independent_minima_rejected'] = bad_min not in pairs and sum(bad_min) == -4082
checks['same_date_total_cash_preserved'] = len({sum(p) for p in pairs}) == 1
checks['same_date_categories_distinguished'] = len(set(pairs)) == 2
for scenario, expected in [('both_first',[0,0]),('capital_first',[-1000,1000]),('expense_first',[1000,-1000])]:
    h1=select(scenario,'H1');h2=select(scenario,'H2')
    difference=[h2['periods'][i]['effects']['cash_flow']['change']-h1['periods'][i]['effects']['cash_flow']['change'] for i in [0,1]]
    checks[scenario + ':time_path_delta'] = difference == expected

# Actual quarterly amounts constrain, but do not explain, the hypothetical remainder.
def amount(k):return int(row[k]['value'])
def movement(k):return amount(k)-int(row[k]['comparison']['value'])
conditions=[]
for hid in ['H1','H2']:
    h=histories[hid];sub=select('both_first',hid)['periods'][0]['effects']
    conditions.append({'history':hid,
        'remaining_ppe_payments':-amount('cash_flow.ppe_payments')-h['capital'],
        'remaining_operating_cash':amount('cash_flow.operating')+h['expense'],
        'remaining_investing_cash':amount('cash_flow.investing')+h['capital'],
        'remaining_financing_cash':amount('cash_flow.financing'),
        'remaining_cash_change':amount('cash_flow.change')+3082,
        'remaining_assets_change':movement('balance.assets')+3082,
        'remaining_liabilities_change':movement('balance.liabilities')+3082,
        'remaining_equity_change':movement('balance.equity')})
for c in conditions:
    checks[c['history']+':quarter_remainder_cash'] = c['remaining_operating_cash']+c['remaining_investing_cash']+c['remaining_financing_cash'] == c['remaining_cash_change'] == 3438
    checks[c['history']+':quarter_remainder_balance'] = c['remaining_assets_change'] == c['remaining_liabilities_change']+c['remaining_equity_change']
checks['quarter_ppe_residuals'] = [c['remaining_ppe_payments'] for c in conditions] == [1858,858]
checks['quarter_CFO_residuals'] = [c['remaining_operating_cash'] for c in conditions] == [31935,30935]
checks['quarter_CFI_residuals'] = [c['remaining_investing_cash'] for c in conditions] == [10874,11874]
save('settlement-paths.json', {'question':'Can equal aggregate annual liabilities be grouped for the specified settlement query?',
    'computed':'Exact conditional settlement journals and their five-statement effects; no company runtime executed',
    'units':'USD millions','initial':histories,'paths':paths,
    'aggregation_verdicts':[
        {'query':'Total cash after both obligations settle, under the fixed no-interest/no-tax scope','verdict':'equal; 3082 paid in both branches'},
        {'query':'Operating and investing cash by category, even on a common date','verdict':'different; retain liability kind and joint branch'},
        {'query':'Cash by date when capital and expense obligations settle on different dates','verdict':'different; retain dates and branch amounts'},
        {'query':'Depreciation, production, impairment or taxable income','verdict':'not established; this settlement scope supplies no required asset/tax state'}],
    'joint_pairs':pairs,'invalid_independent_extrema':{'maximum_pair':bad_max,'minimum_pair':bad_min},
    'quarter_necessary_conditions':conditions,
    'quarter_limit':'Positive residual payment amounts and matching remainder identities do not identify actual transactions, settlements or a feasible remainder.',
    'assumptions':['Condition on an admissible base that is not constructed here.','Inherited q=2000 is illustrative; capital/expense mapping is unadmitted.','Amounts settle at carrying value with sufficient unrestricted cash assumed; no financing event is invented.','Capital payments classified investing; expense settlements operating.','All other activities fixed for the local difference test; taxes/FX/interest/remeasurement have zero incremental effects.','These are ex post scenarios without probability, not historical as-of forecasts.'],
    'actual_history_status':'unresolved; original event, mapping, tax, base and cohort obligations remain'})
failed=[k for k,v in checks.items() if not v]
save('source-arithmetic-checks.json',{'passed':sum(checks.values()),'failed':failed,'checks':checks})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'joint_pairs':pairs,'quarter_conditions':conditions}))
raise SystemExit(bool(failed))
