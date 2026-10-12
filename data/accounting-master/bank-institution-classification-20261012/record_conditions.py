"""Bind classification routes, measurement windows and missing institution facts."""
import hashlib
import json
import time
from pathlib import Path
from lxml import etree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, v):
    (OUT / n).write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')

def main():
    assert not (OUT / 'source-checks.json').exists()
    start = time.monotonic()
    sections = json.loads((OUT / 'sections.json').read_text())
    by = {(s['section'], s['requested_date']): s for s in sections}
    checks = []
    def ck(n, b):
        checks.append({'name': n, 'passed': bool(b)})
    norm = lambda e: ' '.join(''.join(e.itertext()).split())
    for r in json.loads((OUT / 'access-receipts.json').read_text()):
        ck('official successful response ' + r['stem'], r['transfer']['http_code'] == 200
           and r['transfer']['content_type'] == 'text/xml' and r.get('completion', r['result'])['exit_code'] == 0
           and r['args'][-1].startswith('https://www.ecfr.gov/api/versioner/v1/full/'))
        ck('response hashes ' + r['stem'], sha(ROOT / r['body']) == r['body_sha256']
           and sha(ROOT / (r['stem'] + '.headers')) == r['headers_sha256'])
    for s in sections:
        nodes = etree.parse(str(ROOT / s['body'])).xpath('//DIV8[@N="' + s['section'] + '"]')
        ck('section identity ' + s['body'], len(nodes) == 1 and sha(ROOT / s['body']) == s['body_sha256'])
        ck('complete paragraph inventory ' + s['body'], [norm(e) for e in nodes[0].findall('P')] == [p['text'] for p in s['paragraphs']]
           and [norm(e) for e in nodes[0].findall('FTNT')] == s['footnotes']
           and [norm(e) for e in nodes[0].findall('CITA')] == s['amendment_citation'] and not s['other_children'])
    equalities = []
    for sec in ['3.100', '252.5', '238.10']:
        a, b = by[sec, '2026-01-01'], by[sec, '2026-04-01']
        equal = all(a[k] == b[k] for k in ['heading', 'paragraphs', 'footnotes', 'amendment_citation', 'other_children'])
        ck('full normalized January/April comparison ' + sec, equal)
        equalities.append({'section': sec, 'normalized_content_equal': equal, 'scope': 'Two requested snapshots only; no full amendment history.'})
    retained = ROOT / 'data/accounting-master/bank-capital-payout-dependencies-20261012/sources/ecfr-2026-01-01-3.2.xml'
    ps = etree.parse(str(retained)).xpath('//DIV8[@N="3.2"]/P')
    bank_ps = [{'ordinal': i + 1, 'text': norm(e)} for i, e in enumerate(ps)]
    ck('retained bank Category II/III boundaries', bank_ps[27]['text'].startswith('Category II national bank')
       and bank_ps[39]['text'].startswith('Category III national bank') and bank_ps[58]['text'].startswith('(C) Is a Category II'))
    by['3.2', '2026-01-01'] = {'section': '3.2', 'body': str(retained.relative_to(ROOT)), 'body_sha256': sha(retained), 'paragraphs': bank_ps}
    conditions = []
    def add(key, sec, ns, citation, interpretation, required, limit):
        s = by[sec, '2026-01-01'];p = [s['paragraphs'][n - 1] for n in ns]
        ck('located condition ' + key, all(x['ordinal'] == n for x,n in zip(p, ns)))
        conditions.append({'id': key, 'citation': citation, 'section': sec, 'requested_date': '2026-01-01',
                           'source': s['body'], 'source_sha256': s['body_sha256'], 'paragraphs': p,
                           'interpretation': interpretation, 'required_inputs': required, 'unresolved_or_limit': limit})
    add('advanced-approach-routes', '3.100', list(range(1,10)), '3.100(a), (b)(1)',
        'G-SIB-BHC subsidiary, Category II bank, specified advanced-approach depository/holding-company parent, or own election are alternative applicability routes.',
        ['control chain', '217.402 identity', 'parent method use', 'bank category', 'election'], 'An institution name or one size measure does not settle the routes.')
    add('market-risk-and-conservatism', '3.100', list(range(10,16)), '3.100(b)(2), (c)',
        'Covered positions have stated exceptions; conservatism requires demonstrably greater requirements, management, prior notice and immaterial aggregate exposures.',
        ['exposure classes', 'OCC notice and demonstration'], 'No arbitrary conservative scalar may substitute for these requirements.')
    add('parent-population-frequency', '252.5', [1,2,3,4], '252.5(a), (b)',
        'The U.S. BHC, U.S. intermediate holding company and foreign banking organization populations have distinct asset scopes; category is determined at least quarterly.',
        ['252.2 population and average assets', '217.402 identity'], 'Foreign worldwide assets and combined U.S. assets are not interchangeable.')
    add('parent-category-ii', '252.5', list(range(5,22)), '252.5(c)',
        'Entry uses the specified average size or cross-jurisdictional route and G-SIB exclusion. Continued status has explicit exit alternatives using four individual quarters or G-SIB entry.',
        ['average assets/activity', 'each recent quarter', 'G-SIB status', 'prior category'], 'An average below threshold is not automatically a completed four-quarter exit.')
    add('parent-category-iii', '252.5', list(range(22,46)), '252.5(d)',
        'Category III combines size or size-plus-activity thresholds with exclusions; exits require the stated conjunctions, a smaller-size route or movement to a higher category.',
        ['four-quarter measures and prior category', 'nonbank assets', 'wholesale funding', 'off-balance exposures'], 'Preserve AND/OR hierarchy; do not reduce all tests to size.')
    add('parent-category-iv', '252.5', list(range(46,60)), '252.5(e)',
        'Category IV has the defined average size and exclusion conditions, with four-quarter lower-size exit or higher-category routes.',
        ['scope-specific assets', 'higher-category status', 'quarterly history'], 'No all-purpose compliance transition date is supplied by this section.')
    add('slhc-categories', '238.10', list(range(1,33)), '238.10(a)–(d)',
        'The covered savings-and-loan holding-company population has its own Category II/III/IV conditions and continued-status/exit rules.',
        ['238.2 covered population', 'averages and individual quarters', 'prior category'], 'Do not import the BHC G-SIB route into this different scope.')
    add('parent-average-definitions', '252.2', list(range(4,11)) + [70,71,72], '252.2: average measures and total consolidated assets',
        'Four-quarter averages allow the stated shorter reporting history. U.S. BHC/IHC quarterly total assets themselves use daily or Wednesday averages on FR Y-9C; foreign organizations and state member banks use their specified reports.',
        ['correct reporting series', 'available history', 'institution scope'], 'Quarter-end accounting balances do not automatically supply the quarterly measure.')
    add('parent-scope-and-reports', '252.2', [11,12,13,14,15,26,31,34,37,38,39,40,41,42,45,53,54,55,56,57,58,73,74,75,76,77,78,80,81,82,87,90],
        '252.2: institution, control, exposure and report definitions',
        'Top-tier U.S. scope, foreign controls and report-specific exposures determine the relevant population and metrics.',
        ['entity/control facts', 'FR Y-9C/Y-9LP/Y-15/Y-7Q', 'underlying instructions'], 'Cross-referenced control law and actual forms remain unverified.')
    add('slhc-scope-and-measures', '238.2', list(range(57,76)) + [77,78,79,81,82,83,85,86,89], '238.2(w)–(ss), selected definitions',
        'Covered top-tier U.S. scope excludes specified commercial/insurance holding companies; dated June 30 tests matter. Average and report-specific measures have explicit histories and sources.',
        ['covered-status facts', 'prior-June assets/revenue', 'regulatory reports and history'], 'Savings-and-loan holding-company status alone does not establish the covered population.')
    add('bank-category-ii', '3.2', list(range(28,40)), '3.2: Category II national bank or Federal savings association',
        'A Category II parent is one route; the independent bank route requires no depository-institution holding-company parent, specified Call Report/activity averages, and continued-status/exit conditions.',
        ['parent relation/category', 'bank reporting history', 'FR Y-15 or equivalent'], 'Retained January definition only; no actual bank category assigned.')
    add('bank-category-iii', '3.2', list(range(40,60)), '3.2: Category III national bank or Federal savings association',
        'Routes include Category III parent, qualifying depository parent, or the stated independent-bank tests. Activity thresholds and category/exit history matter.',
        ['parent categories/metrics', 'bank averages and each quarter', 'higher-category status'], 'Not a simple copy of any parent label; retained exact text controls.')
    save('condition-ledger.json', {'conditions': conditions, 'snapshot_comparisons': equalities,
         'reading_scope': 'All 106 P paragraphs of January 3.100/252.5/238.10 and full normalized April comparison. Selected January 252.2/238.2 definitions and retained 3.2 Category II/III definitions read; complete definition sections were not reviewed.',
         'dependencies': ['217.400–404 scope/definitions/G-SIB identification/surcharge/Method 1 score',
          'actual dated entity/control facts and elections', 'FR Y-9C/Y-9LP/Y-15/Y-7Q/Call Report instructions and returns',
          'provision-specific compliance transitions and supervisory decisions', 'full amendment/applicability chain'],
         'nonclaim': 'No actual institution classification, ratio, dividend capacity or general classification engine.'})
    save('source-checks.json', {'checks': checks, 'passed': sum(c['passed'] for c in checks),
         'failed': [c['name'] for c in checks if not c['passed']], 'wall_seconds': time.monotonic()-start,
         'scope': 'Documentary integrity, normalization and exact locators only.'})
    assert all(c['passed'] for c in checks)
    print(json.dumps({'source_checks':len(checks),'conditions':len(conditions),'failed':0}))

if __name__ == '__main__':
    main()
