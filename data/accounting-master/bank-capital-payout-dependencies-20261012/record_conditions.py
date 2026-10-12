"""Bind selected Part 3 definitions, tables and illustrative arithmetic."""
import json
import hashlib
import re
import time
from fractions import Fraction as F
from pathlib import Path
from lxml import etree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    assert not (OUT / 'source-checks.json').exists()
    start = time.monotonic()
    sections = json.loads((OUT / 'sections.json').read_text())
    by = {(s['section'], s['date']): s for s in sections}
    checks = []
    def ck(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
    for receipt in json.loads((OUT / 'access-receipts.json').read_text()):
        ck('receipt ' + receipt['body'], receipt['http_code'] == 200 and receipt['exit_code'] == 0
           and sha(ROOT / receipt['body']) == receipt['body_sha256']
           and sha(ROOT / receipt['headers']) == receipt['headers_sha256'])
    for section in sections:
        tree = etree.parse(str(ROOT / section['source']))
        nodes = tree.xpath('//DIV8[@N="' + section['section'] + '"]')
        expected = [' '.join(''.join(c.itertext()).split()) for c in nodes[0]]
        ck('section identity ' + section['source'], len(nodes) == 1 and sha(ROOT / section['source']) == section['sha256']
           and expected == [p['text'] for p in section['paragraphs']]
           and sha(ROOT / section['normalized_text']) == section['normalized_text_sha256'])
    conditions = []
    def add(key, section, indexes, interpretation, inputs, unresolved, date='2026-01-01'):
        source = by[section, date]
        conditions.append({'id': key, 'section': section, 'requested_date': date,
                           'source': source['source'], 'source_sha256': source['sha256'],
                           'paragraphs': [source['paragraphs'][i] for i in indexes],
                           'interpretation': interpretation, 'required_inputs': inputs, 'unresolved': unresolved})
    add('bank-scope-and-supervision', '3.1', [1, 2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 18],
        'National-bank/savings-association scope and OCC reserved powers prevent a ratios-only clearance.',
        ['charter and institution category', 'applicable OCC decisions'], 'No bank-specific absence-of-order inference.')
    add('capital-components', '3.2', [2, 91, 494, 496, 497, 499],
        'Tier 1 equals CET1 plus additional Tier 1; total capital adds Tier 2. Component eligibility and leverage exposure refer elsewhere.',
        ['eligible instruments', 'regulatory adjustments', 'leverage exposure'], 'Sections 3.20 and 3.22 not inspected in this unit.')
    add('advanced-approach-dependency', '3.2', [4],
        'Advanced-approach status depends on section 3.100(b)(1).',
        ['institution classification and notices'], 'No classification from size alone or an issuer name.')
    add('category-iii', '3.2', list(range(40, 60)),
        'Parent category, institution category, multi-quarter measures and exit conditions are different routes.',
        ['parent category', 'four-quarter regulatory reports', 'applicable category dates'], 'Referenced 252.5/238.10 and bank facts remain open.')
    add('discretionary-bonus', '3.2', [153, 154, 155, 156, 241],
        'All three bonus conditions and the executive-officer definition matter.',
        ['officer function', 'discretion', 'prior promise', 'contractual rights'], 'Not every employee payment is a discretionary bonus.')
    add('distribution', '3.2', list(range(157, 165)),
        'Covers specified capital reductions, dividend declarations/payments and discretionary Tier 2 payments; replacement exceptions carry their own conditions.',
        ['instrument eligibility and tier', 'declaration/payment/redemption dates', 'same-quarter replacement facts', 'suspension/default rights'],
        'Do not count a declaration and its settlement as independent economic distributions without a reporting treatment; reconciliation remains required.')
    add('risk-weighted-assets', '3.2', list(range(468, 477)),
        'Standardized RWA has category calculations and allowance deductions; it is not total assets.',
        ['exposure classes and deductions'], 'Referenced RWA engines remain outside this source unit.')
    add('minimum-ratios', '3.10', list(range(1, 9)),
        'Minimum ratios have instrument and institution-specific scope, including a separate community-bank exception.',
        ['charter/category', 'community-bank election if applicable'], 'No minimum-ratio-only payout clearance.')
    add('ratio-denominators', '3.10', list(range(9, 18)),
        'Risk-based ratios, ordinary leverage and supplementary leverage use different denominators and averaging clocks.',
        ['eligible capital', 'standardized RWA', 'daily on-balance-sheet assets', 'month-end off-balance-sheet exposures', 'deductions'],
        'Total leverage includes the further transaction-specific provisions of 3.10(c)(2).')
    add('advanced-ratio-choice', '3.10', list(range(65, 77)),
        'The lower-of-standardized-and-advanced comparisons require completed parallel-run approval and an adjusted advanced total-capital numerator.',
        ['parallel-run notification', 'both RWA measures', 'eligible credit reserves and expected losses'], 'Do not choose a favorable ratio or unadjusted numerator.')
    add('capital-adequacy-assessment', '3.10', [78, 79],
        'Capital must reflect risks beyond stated numerical minimums.', ['risk assessment and supervisory facts'], 'A passed threshold alone cannot establish adequacy.')
    add('eligible-retained-income', '3.11', [3, 4, 5],
        'Greater of preceding-four-quarter Call Report net income net of relevant distributions/tax effects, and the average quarterly net income.',
        ['four quarterly net incomes', 'distributions', 'associated tax effects', 'amounts already reflected in income'],
        'Distinct from Part 5 retained net income; Call Report instruction details remain open.', '2026-04-01')
    add('payout-population-and-standard', '3.11', [6, 7, 9],
        'The applicable population selects the payout-ratio route; leverage standard refers to the lesser-of cap and applicable Method 1 surcharge.',
        ['holding-company regulatory reports', 'control relationship', 'Method 1 surcharge and effective date'],
        'Section 217.403(b)/(d) and actual facts remain open.', '2026-04-01')
    add('capital-buffer-and-clock', '3.11', list(range(10, 15)),
        'Capital conservation buffer uses the lowest margin over the three minima at the previous quarter end, with the stated zero rule.',
        ['previous quarter-end CET1/Tier1/total ratios', 'applicable minima'], 'Not a present-day cash balance.', '2026-04-01')
    add('obligation-and-quarter', '3.11', [15, 16],
        'Quarterly aggregate limit includes creation of distribution/bonus obligations; sufficient applicable buffers remove this section-specific amount limit.',
        ['current-quarter distributions, bonuses and obligations', 'both applicable buffers'], 'No-limit-under-this-section does not mean unrestricted capital distribution.', '2026-04-01')
    add('negative-income-and-permission', '3.11', list(range(17, 22)),
        'Negative income rule has its stated buffer conditions; OCC permission is a separate possible route.',
        ['income sign', 'previous quarter buffers', 'OCC permission'], 'Do not silently floor income at zero or treat the example as every negative-income case.', '2026-04-01')
    add('other-rules', '3.11', [23],
        'Other capital, Part 5 and Part 6 restrictions can also apply.', ['other applicable restrictions'], 'Part 3 amount is not total legal capacity.', '2026-04-01')
    add('countercyclical-geography', '3.11', list(range(24, 32)),
        'Jurisdictional exposure weights and protection-provider/securitization location rules determine the applicable countercyclical amount.',
        ['risk-weighted private exposures', 'locations', 'protection providers', 'underlying securitization exposures'],
        'Initial U.S. zero is not verified current global zero.', '2026-04-01')
    add('countercyclical-effective-dates', '3.11', [34, 35, 36, 37, 38, 39],
        'Announcements, delayed increases, decreases and sunset/renewal have distinct dates.',
        ['jurisdictional dated determinations', 'effective dates and renewals'], 'No 2026 level verified from the initial-zero text.', '2026-04-01')
    add('two-ratios-and-leverage-buffer', '3.11', [40, 41, 42, 43],
        'Covered banks use the lower table ratio. Leverage buffer is previous-quarter SLR minus 3 percentage points, with the stated zero condition.',
        ['covered population', 'SLR', 'leverage standard', 'capital conservation buffer', 'countercyclical amount'],
        'An absent table limitation is a state, not a 100% ratio.', '2026-04-01')
    tables = []
    for date in ['2026-01-01', '2026-04-01']:
        section = by['3.11', date]
        tree = etree.parse(str(ROOT / section['source']))
        for index, table in enumerate(tree.xpath('//TABLE'), 1):
            rows = [[' '.join(''.join(cell.itertext()).split()) for cell in row] for row in table.xpath('./TBODY/TR')]
            tables.append({'date': date, 'number': index, 'source': section['source'], 'source_sha256': section['sha256'],
                           'caption': ' '.join(''.join(table.xpath('./CAPTION')[0].itertext()).split()), 'rows': rows})
            ck(f'table structure {date}/{index}', len(rows) == 5 and all(len(row) == 2 for row in rows)
               and [r[1] for r in rows] == ['No payout ratio limitation applies.', '60 percent.', '40 percent.', '20 percent.', '0 percent.'])
    old = by['3.11', '2026-01-01']['paragraphs']; new = by['3.11', '2026-04-01']['paragraphs']
    ck('eligible income unchanged in selected snapshots', [p['text'] for p in old[4:7]] == [p['text'] for p in new[3:6]])
    ck('table 1 unchanged', tables[0]['rows'] == tables[1]['rows'])
    def norm(text):
        return re.sub(r'[^a-z0-9]', '', re.sub(r'-\s*\n\s*', '', text).lower())
    fr_root = ROOT / 'data/accounting-master/national-bank-dividend-authority-20261012/sources'
    fr_text = '\n'.join((fr_root / f'fr-final-rule-page-{i}.txt').read_text() for i in [40, 41])
    for i in [9, 40, 41, 42, 43]:
        ck('FR/amended clause ' + str(i), norm(new[i]['text']) in norm(fr_text))
    for condition in conditions:
        ck('located condition ' + condition['id'], bool(condition['paragraphs']) and
           all(by[condition['section'], condition['requested_date']]['paragraphs'][p['index']] == p for p in condition['paragraphs']))

    # Exact arithmetic for a documentary example, not a product policy engine.
    quarterly = [F(10)] * 4
    annual = sum(quarterly)
    declared = F(38)
    retained = annual - declared
    eligible = max(retained, annual / 4)
    ck('example annual sum', annual == 40)
    ck('example Part 5 retained income', retained == 2)
    ck('example Part 3 eligible income', eligible == 10)
    # With zero countercyclical amount, 1.5% lies in Table 1's 40% interval.
    ck('example table 1 membership', F('1.25') < F('1.5') <= F('1.875'))
    # 0.2 percentage points is below 25% of the stipulated 1-point standard.
    ck('example table 2 membership', F('0.2') <= F('0.25') * F(1))
    ck('example income-branch amount', eligible * F('0.4') == 4)
    ck('example final table maximum', eligible * min(F('0.4'), F(0)) == 0)
    examples = {'units': 'USD millions for money; percentage points for buffers',
                'hypothetical_inputs': {'quarterly_net_income': ['10'] * 4, 'declared_dividends': '38',
                    'other_distributions': '0', 'tax_adjustment_not_already_in_income': '0',
                    'capital_conservation_buffer': '1.5', 'countercyclical_amount': '0',
                    'leverage_buffer_standard': '1', 'leverage_buffer': '0.2',
                    'rule_applicability': 'stipulated covered bank applying amended rule', 'special_OCC_permission': 'absent'},
                'expected': {'part5_retained_income': '2', 'part3_eligible_income': '10',
                    'table1_ratio': '0.4', 'table2_ratio': '0', 'combined_ratio': '0', 'table_maximum': '0'},
                'nonclaim': 'No named-bank inference, input calibration, general engine, legal clearance or full dividend computation.'}
    for value, expected in [('0.25', '0'), ('0.50', '0.20'), ('0.75', '0.40'), ('1.00', '0.60'), ('1.01', 'no_ratio_limit')]:
        # Membership in explicit source rows; outputs are independently stated above.
        x = F(value)
        membership = [x > 1, F('0.75') < x <= 1, F('0.50') < x <= F('0.75'),
                      F('0.25') < x <= F('0.50'), x <= F('0.25')]
        outputs = ['no_ratio_limit', '0.60', '0.40', '0.20', '0']
        ck('table 2 exact boundary ' + value, sum(membership) == 1 and outputs[membership.index(True)] == expected)
    save('condition-ledger.json', {'conditions': conditions, 'tables': tables,
         'reading_scope': '3.1 and both 3.11 responses fully read; selected 3.2 definitions; 3.10 read with transaction dependencies retained, not implemented.',
         'open_dependencies': ['3.20 capital eligibility', '3.22 deductions', '3.100/252.5/238.10 classification',
             '217.403 Method 1 surcharge and dates', 'Call Report instructions and actual four-quarter returns',
             'countercyclical determinations', 'supervisory permissions and conditions',
             'complete amendment/applicability chain', 'duplicate declaration/payment reporting treatment'],
         'nonclaim': 'A dated dependency map, not a complete bank capital or dividend engine.'})
    save('worked-example.json', examples)
    failed = [c['name'] for c in checks if not c['passed']]
    save('source-checks.json', {'checks': checks, 'passed': len(checks) - len(failed), 'failed': failed,
                              'wall_seconds': time.monotonic() - start, 'scope': 'Documentary checks and hypothetical exact arithmetic only.'})
    print(json.dumps({'passed': len(checks) - len(failed), 'failed': failed, 'conditions': len(conditions), 'tables': len(tables)}))
    raise SystemExit(bool(failed))

if __name__ == '__main__':
    main()
