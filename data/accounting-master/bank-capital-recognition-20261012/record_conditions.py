"""Preserve exact clauses, footnotes, scope and remaining facts for capital rules."""
import hashlib
import json
import time
from pathlib import Path
from lxml import etree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    assert not (OUT / 'source-checks.json').exists()
    start = time.monotonic()
    sections = json.loads((OUT / 'sections.json').read_text())
    by = {(s['section'], s['requested_date']): s for s in sections}
    checks = []
    def ck(name, result):
        checks.append({'name': name, 'passed': bool(result)})
    for row in json.loads((OUT / 'access-receipts.json').read_text()):
        stem = ROOT / row['stem']
        ck('official successful transfer ' + row['stem'], row['transfer']['http_code'] == 200
           and row['transfer']['content_type'] == 'text/xml' and row.get('completion', row['result'])['exit_code'] == 0
           and row['args'][-1].startswith('https://www.ecfr.gov/api/versioner/v1/full/'))
        ck('receipt body/header hashes ' + row['stem'], sha(Path(str(stem) + '.xml')) == row['body_sha256']
           and sha(Path(str(stem) + '.headers')) == row['headers_sha256'])
    for s in sections:
        node = etree.parse(str(ROOT / s['body'])).xpath('//DIV8[@N="' + s['section'] + '"]')
        ck('section identity ' + s['body'], len(node) == 1 and sha(ROOT / s['body']) == s['body_sha256'])
        norm = lambda e: ' '.join(''.join(e.itertext()).split())
        ck('all paragraphs and footnotes ' + s['body'], [norm(e) for e in node[0].findall('P')] == [p['text'] for p in s['paragraphs']]
           and [norm(e) for e in node[0].findall('FTNT')] == s['footnotes']
           and [norm(e) for e in node[0].findall('CITA')] == s['amendment_citation'])
    comparisons = []
    for sec in ['3.20', '3.22']:
        a, b = by[sec, '2026-01-01'], by[sec, '2026-04-01']
        equal = all(a[k] == b[k] for k in ['heading', 'paragraphs', 'footnotes', 'amendment_citation', 'tables'])
        ck('normalized complete section equality ' + sec, equal)
        comparisons.append({'section': sec, 'equal_normalized_content': equal,
                            'normalization': 'XML itertext, whitespace collapse; includes heading, P, FTNT and CITA; no tables present.',
                            'limitation': 'Two requested-date responses only; no complete amendment or applicability finding.'})
    conditions = []
    def add(key, section, ordinals, citation, interpretation, inputs, limit, footnotes=()):
        s = by[section, '2026-01-01']
        ps = [s['paragraphs'][i - 1] for i in ordinals]
        ck('located conditions ' + key, all(p['ordinal'] == i for p, i in zip(ps, ordinals)))
        conditions.append({'id': key, 'section': section, 'citation': citation,
                           'requested_date': s['requested_date'], 'source': s['body'], 'source_sha256': s['body_sha256'],
                           'paragraphs': ps, 'footnotes': [f for f in s['footnotes'] if int(f.split()[0]) in footnotes],
                           'interpretation': interpretation, 'required_inputs': inputs, 'unresolved_or_limit': limit})
    add('three-components', '3.20', [1,2,3,4,5,24,49], '3.20(a), (b), (c), (d)',
        'Each regulatory tier has eligible elements and its own adjustments; accounting equity is not the final numerator.',
        ['eligible elements by tier', '3.22 adjustments and deductions'], 'No complete bank numerator computed.')
    add('cet1-instrument', '3.20', list(range(6,20)), '3.20(b)(1)(i)–(xiii)',
        'All listed common-stock criteria apply: issuer, paid-in status, subordination, residual/loss rights, permanence, dividend discretion, GAAP equity, funding, guarantees and reporting.',
        ['contract terms', 'issuance communications and financing', 'issuer and control facts', 'GAAP/regulatory reporting'],
        'GAAP equity classification or a common-stock label satisfies only part of the criteria.')
    add('cet1-other-and-esop', '3.20', [20,21,22,23], '3.20(b)(2)–(5), footnote 1',
        'Retained earnings, AOCI and eligible minority interests have distinct roles; minority limits and specified ESOP exceptions remain conditional.',
        ['retained earnings', 'AOCI and election', 'minority interest', 'ESOP/ERISA facts'], 'Section 3.21 and actual facts remain open.', [1])
    add('at1-instrument-and-calls', '3.20', list(range(25,43)), '3.20(c)(1)(i)–(xiv)',
        'Additional Tier 1 has cumulative instrument criteria, call timing/exceptions, approval, replacement-or-capital demonstration, dividend discretion and issuance restrictions.',
        ['terms and issuance dates', 'OCC approvals', 'replacement or capital adequacy evidence', 'issuer structure'],
        'Five-year call timing does not create an entitlement to redeem.', [2,3])
    add('at1-other-exceptions', '3.20', list(range(43,49)), '3.20(c)(2)–(4)',
        'Minority interest, named government programs, ESOP and pre-2014 rating-event exceptions have their stated populations.',
        ['program and instrument history', 'minority limits'], 'No ordinary instrument is presumed to qualify under a special program.')
    add('tier2-terms-and-amortization', '3.20', list(range(50,65)), '3.20(d)(1)(i)–(xi)',
        'Tier 2 requires the listed terms; original maturity is at least five years, recognized amount reduces by 20% of original amount net of redemptions at the beginning of each final year, and remaining maturity below one year is excluded.',
        ['original issue/redemption amounts', 'maturity and call terms', 'subordination/security/funding', 'approvals'],
        'This is regulatory recognition, not an accounting debt reduction; automatic conversion exception retained.', [7,8,9])
    add('tier2-other', '3.20', list(range(65,71)), '3.20(d)(2)–(6)',
        'Minority interests, limited ALLL/AACL, named program instruments and stated AOCI-opt-out gains have separate conditions.',
        ['3.21 minority limits', 'allowance and standardized RWA', 'program history', 'AOCI election'],
        'Allowance inclusion limit and gain recognition are not generic equity addbacks.')
    add('capital-element-approval', '3.20', list(range(71,76)), '3.20(e)',
        'Prior OCC approval is required unless the stated historical or equivalent-element exception applies; determinations are published.',
        ['element approval or demonstrated exception'], 'No approval inferred from a report label.')
    add('cet1-deductions', '3.22', list(range(1,11)), '3.22(a)(1)–(6)',
        'Goodwill, specified intangibles, loss/credit carryforward DTAs, securitization gains and conditional pension/expected-loss items have different scopes and tax treatment.',
        ['asset classes', 'tax links', 'institution status', 'parallel-run notice', 'eligible reserves'],
        'Insured-depository pension exception and holding-company scope must not be flattened.')
    add('subsidiary-perimeter', '3.22', list(range(11,24)), '3.22(a)(7)–(8)',
        'Financial-subsidiary and savings-association investment deductions alter regulatory consolidation; historical/includable definitions and OCC discretion matter.',
        ['subsidiary activities', 'charter/acquisition history', 'regulatory perimeter'], 'Actual structures and referenced 5.39 remain open.')
    add('aoci-own-credit', '3.22', list(range(24,42)), '3.22(b)',
        'Adjustments are net of associated tax effects. AOCI opt-out is limited by advanced-approach status, election clock, subsidiary consistency and transaction exceptions; own-credit gains/losses are separately adjusted.',
        ['institution category', 'Call Report election and history', 'AOCI components', 'own-credit amounts', 'merger/approval facts'],
        'Neither wholesale AOCI removal nor parent-to-bank transfer of an election is assumed.', [21,22])
    add('own-holdings-and-corresponding-tier', '3.22', list(range(42,58)), '3.22(c)(1)–(2)',
        'Own holdings reduce the specified tier; corresponding deductions follow the underlying instrument with explicit treatment for nonregulated, regulated and nonqualifying issuers.',
        ['instrument classification', 'own holdings', 'issuer regulation/history', 'available tier amounts'],
        'Footnote 23 fixes allowance-inclusion calculation before (c)–(f); cross-reference wording is preserved.', [23])
    add('reciprocal-and-nonadvanced', '3.22', [58,59,60], '3.22(c)(3)–(4)',
        'Reciprocal holdings and the non-advanced 25% investment threshold use different rules; supervisory failed-underwriting/support exceptions are conditional.',
        ['holding arrangement', 'CET1 base after (a)–(c)(3)', 'tax/approval facts'], 'Non-deducted exposures still require appropriate risk weights.', [24,25])
    add('advanced-investments-covered-debt', '3.22', list(range(61,72)), '3.22(c)(5)–(6)',
        'Advanced non-significant investment threshold, allocation by tier, covered-debt exclusions and significant non-common-stock deductions depend on bank status and holding details.',
        ['significance', 'G-SIB subsidiary status', 'gross/net long positions', 'designation and business-day history', 'approvals'],
        'Do not apply 10%/5% thresholds to every bank or all investment categories.', [26,27,28])
    add('nonadvanced-dta-msa', '3.22', list(range(72,77)), '3.22(d)(1)',
        'The 25% individual threshold in (i) governs the specified temporary-difference DTAs and MSAs; carryback realization, parent refund limits and consistent tax exclusions qualify the calculation.',
        ['DTA origin and valuation allowances', 'carryback/refund facts', 'MSAs', 'CET1 threshold base'],
        'Read (ii)/(iii) under (i), not as a free-standing full deduction; remaining items carry 250% risk weight.', [29])
    add('advanced-thresholds', '3.22', list(range(77,84)), '3.22(d)(2)',
        'Individual 10% thresholds precede the aggregate rule expressed as 17.65% of its defined reduced base (called the 15% threshold).',
        ['DTAs/MSAs/significant common stock', 'ordered CET1 base and deductions', 'goodwill overlap', 'tax elections'],
        'Do not replace the operative 17.65% expression with an unreviewed 15% of a different base.', [30,31])
    add('tax-netting', '3.22', list(range(84,93)), '3.22(e)',
        'General associated-DTL netting is permitted, not required, subject to extinguishment on impairment/derecognition; a DTL cannot be reused. DTA offset uses same-authority/eligibility and proportional-allocation rules. Reporting-period consistency and prior approval for changes apply.',
        ['asset-specific DTL links', 'extinguishment conditions', 'tax authority/offset eligibility', 'allocation history', 'policy approval'],
        'Total DTL is not a fungible deduction credit.')
    add('shortfall-and-rwa', '3.22', [93,94], '3.22(f)–(g)',
        'Corresponding-tier shortfalls and the community-bank exception retain their scope; deducted items are excluded from applicable RWA.',
        ['available capital tiers', 'CBLR election', 'deduction inventory', 'applicable RWA engines'],
        'The source paragraph (f) literally refers to (d), while (c)(2) directs shortfalls to (f); no silent textual repair or general engine is made.')
    add('long-short-positions', '3.22', list(range(95,113)), '3.22(h)',
        'Direct, indirect and synthetic holdings use different gross-long measures; hedge recognition requires same instrument, maturity and additional own-capital/index conditions.',
        ['fund contracts/holdings', 'synthetic loss', 'hedge maturity and counterparty risk', 'Call Report classification', 'controls/approval'],
        'Accounting net holdings alone do not establish the regulatory deduction.')
    save('condition-ledger.json', {'conditions': conditions, 'snapshot_comparisons': comparisons,
         'reading_scope': 'All 75 P paragraphs and 12 footnotes of 3.20; all 112 P paragraphs and 11 footnotes of 3.22 in January text. Complete April normalized child-content comparison agrees.',
         'open_dependencies': ['3.21 minority interest', '3.100/252.5/238.10 classification', '3.300 nonqualifying instruments',
          '3.12 CBLR', '3.51 exposure amounts', '3.121 parallel run', '5.39 financial subsidiaries', '217.403 surcharge/date',
          'Call Report instructions and actual reports/elections', 'instrument contracts and issuance/funding facts',
          'tax links and supervisory permissions', 'full amendment/applicability chain'],
         'source_wording_cautions': ['3.22(f) references paragraph (d); 3.22(c)(2) refers shortfalls to (f). Preserve exact wording; full implementation needs resolution.',
          '3.22 footnotes 26/27 retain literal paragraph references and grammar; no unsupported emendation.',
          '3.22(d)(1)(ii)/(iii) must be read with the threshold in (i).'],
         'nonclaim': 'Documentary conditions only; no actual-bank capital or dividend computation.'})
    save('source-checks.json', {'checks': checks, 'passed': sum(c['passed'] for c in checks),
          'failed': [c['name'] for c in checks if not c['passed']], 'wall_seconds': time.monotonic() - start,
          'scope': 'Source integrity and locator checks; no runtime or bank-validity acceptance.'})
    assert all(c['passed'] for c in checks)
    print(json.dumps({'conditions': len(conditions), 'checks': len(checks), 'failed': 0}))

if __name__ == '__main__':
    main()
