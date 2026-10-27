"""Bind Note 20 debt rows and compare scoped amounts with Note 33."""
import hashlib
import json
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique_span(source, phrase):
    pattern = r'\s+'.join(re.escape(token) for token in phrase.split())
    hits = list(re.finditer(pattern, source))
    if len(hits) != 1:
        raise ValueError(f'{len(hits)} hits: {phrase[:90]}')
    hit = hits[0]
    return {'start': hit.start(), 'end': hit.end(), 'quote': hit.group(), 'span_sha256': hashlib.sha256(hit.group().encode()).hexdigest()}

def main():
    assert not (OUT / 'source-ledger.json').exists(), 'Preserve completed source ledger'
    manifest = json.loads((OUT / 'source-manifest.json').read_text())
    checks = []
    def ck(name, value): checks.append({'check': name, 'passed': bool(value)})
    ck('source PDF', sha(ROOT / manifest['source_pdf']) == manifest['source_pdf_sha256'])
    ck('Note 33 comparator', sha(ROOT / manifest['comparator']) == manifest['comparator_sha256'])
    ck('Version 2.35 candidate', sha(ROOT / manifest['candidate_pdf']) == manifest['candidate_pdf_sha256'])
    pages = {}
    for row in manifest['pages']:
        n = row['pdf_page']
        for field in ['reading', 'layout', 'render']:
            ck(f'{field} page {n}', sha(ROOT / row[field]) == row[field + '_sha256'])
        pages[n] = (ROOT / row['reading']).read_text()
    ck('two-page note boundary', 'Note 20 – Long-term debt' in pages[283] and 'guaranteed certain long-' in pages[284])
    ck('carrying-value definition', 'carrying values (including' in pages[283] and 'remaining contractual maturity' in pages[283])
    ck('parent and subsidiary headings', 'Parent company' in pages[283] and 'Subsidiaries' in pages[283])

    specs = [
        ('parent.senior.fixed', 283, 'Fixed rate $ 11,761 $ 91,867 $ 122,443 $ 226,071 $ 214,911', {'2025_total': 226071, '2024_total': 214911}),
        ('parent.senior.variable', 283, 'Variable rate 48 6,795 1,618 8,461 8,655', {'2025_total': 8461, '2024_total': 8655}),
        ('parent.subordinated.fixed', 283, 'Fixed rate $ 2,489 $ 3,099 $ 12,919 $ 18,507 $ 14,457', {'2025_total': 18507, '2024_total': 14457}),
        ('parent.subtotal', 283, 'Subtotal $ 14,298 $ 101,761 $ 136,980 $ 253,039 $ 238,023', {'2025_under_1': 14298, '2025_1_to_5': 101761, '2025_after_5': 136980, '2025_total': 253039, '2024_total': 238023}),
        ('subsidiary.fhlb.fixed', 283, 'Fixed rate $ 1,236 $ 405 $ 18 $ 1,659 $ 9,257', {'2025_total': 1659, '2024_total': 9257}),
        ('subsidiary.fhlb.variable', 283, 'Variable rate — 16,500 — 16,500 20,000', {'2025_total': 16500, '2024_total': 20000}),
        ('subsidiary.purchase_money', 283, 'Fixed rate $ — $ 49,435 $ — $ 49,435 $ 49,208', {'2025_total': 49435, '2024_total': 49208}),
        ('subsidiary.senior.fixed', 283, 'Fixed rate $ 5,896 $ 19,908 $ 11,973 $ 37,777 $ 26,545', {'2025_total': 37777, '2024_total': 26545}),
        ('subsidiary.senior.variable', 283, 'Variable rate 21,159 43,393 10,650 75,202 56,782', {'2025_total': 75202, '2024_total': 56782}),
        ('subsidiary.junior.fixed', 283, 'Fixed rate $ — $ 495 $ — $ 495 $ 488', {'2025_total': 495, '2024_total': 488}),
        ('subsidiary.junior.variable', 283, 'Variable rate — 421 678 1,099 1,115', {'2025_total': 1099, '2024_total': 1115}),
        ('subsidiary.junior.subtotal', 283, 'Subtotal $ — $ 916 $ 678 $ 1,594 $ 1,603', {'2025_1_to_5': 916, '2025_after_5': 678, '2025_total': 1594, '2024_total': 1603}),
        ('consolidated.long_term_debt', 283, 'Total long-term debt(b)(c)(d) $ 42,589 $ 232,318 $ 160,299 $ 435,206 (g)(h) $ 401,418', {'2025_under_1': 42589, '2025_1_to_5': 232318, '2025_after_5': 160299, '2025_total': 435206, '2024_total': 401418}),
        ('consolidated.beneficial_interests', 283, 'Total long-term beneficial interests(e) $ 1,156 $ 4,741 $ 120 $ 6,017 $ 5,478', {'2025_total': 6017, '2024_total': 5478}),
    ]
    rows = []
    for key, page, phrase, amounts in specs:
        span = unique_span(pages[page], phrase)
        rows.append({'id': key, 'pdf_page': page, 'printed_page': page - 2, 'source_text': next(r['reading'] for r in manifest['pages'] if r['pdf_page'] == page), 'amounts_usd_millions': amounts, **span})
        ck('source row ' + key, pages[page][span['start']:span['end']] == span['quote'])
    qualifiers = [
        ('carrying measurement', 283, 'long-term debt carrying values (including unamortized premiums and discounts, issuance costs, valuation adjustments and fair value adjustments, where applicable) by remaining contractual maturity'),
        ('fair value share', 283, 'Included $134.6 billion and $100.8 billion of long-term debt accounted for at fair value at December 31, 2025 and 2024, respectively'),
        ('zero coupon principal difference', 283, 'Included $18.1 billion and $13.5 billion of outstanding zero-coupon notes at December 31, 2025 and 2024, respectively. The aggregate principal amount of these notes at their respective maturities is $57.6 billion and $50.2 billion'),
        ('consolidated five-year carrying values', 283, 'aggregate carrying values of debt that matures in each of the five years subsequent to 2025 is $42.6 billion in 2026, $55.8 billion in 2027, $105.4 billion in 2028, $31.4 billion in 2029 and $39.8 billion in 2030'),
        ('beneficial interests separate', 283, 'Included on the Consolidated balance sheets in beneficial interests issued by consolidated VIEs'),
        ('guaranteed subsidiary debt', 284, 'JPMorgan Chase & Co. has guaranteed certain long- term debt of its subsidiaries, including structured notes'),
        ('guaranteed debt amount', 284, 'such guaranteed long- term debt and structured notes was $47.6 billion and $41.2 billion at December 31, 2025 and 2024'),
        ('rate hedge boundary', 284, 'modified weighted-average interest rates for total long-term debt, including the effects of related derivative instruments, were 4.75% and 5.15%'),
    ]
    notes = []
    for key, page, phrase in qualifiers:
        span = unique_span(pages[page], phrase)
        notes.append({'id': key, 'pdf_page': page, 'printed_page': page - 2, 'source_text': next(r['reading'] for r in manifest['pages'] if r['pdf_page'] == page), **span})
        ck('source qualifier ' + key, pages[page][span['start']:span['end']] == span['quote'])

    V = {r['id']: r['amounts_usd_millions'] for r in rows}
    parent = V['parent.subtotal']; junior = V['subsidiary.junior.subtotal']; total = V['consolidated.long_term_debt']
    old = json.loads((ROOT / manifest['comparator']).read_text())
    note33 = next(r['values_usd_millions'] for r in old['selected_rows'] if r['id'] == 'balance.long_term_debt')
    maturity_quote = next(r['quote'] for r in old['qualifiers'] if r['id'] == 'maturity schedule')
    ck('parent subtotal rows 2025', sum(V[k]['2025_total'] for k in ['parent.senior.fixed', 'parent.senior.variable', 'parent.subordinated.fixed']) == parent['2025_total'])
    ck('parent subtotal rows 2024', sum(V[k]['2024_total'] for k in ['parent.senior.fixed', 'parent.senior.variable', 'parent.subordinated.fixed']) == parent['2024_total'])
    ck('parent maturity buckets sum', sum(parent[k] for k in ['2025_under_1', '2025_1_to_5', '2025_after_5']) == parent['2025_total'])
    ck('junior subsidiary subtotal 2025', V['subsidiary.junior.fixed']['2025_total'] + V['subsidiary.junior.variable']['2025_total'] == junior['2025_total'])
    ck('junior subsidiary subtotal 2024', V['subsidiary.junior.fixed']['2024_total'] + V['subsidiary.junior.variable']['2024_total'] == junior['2024_total'])
    ck('consolidated 2025 category bridge', parent['2025_total'] + V['subsidiary.fhlb.fixed']['2025_total'] + V['subsidiary.fhlb.variable']['2025_total'] + V['subsidiary.purchase_money']['2025_total'] + V['subsidiary.senior.fixed']['2025_total'] + V['subsidiary.senior.variable']['2025_total'] + junior['2025_total'] == total['2025_total'])
    ck('consolidated 2024 category bridge', parent['2024_total'] + V['subsidiary.fhlb.fixed']['2024_total'] + V['subsidiary.fhlb.variable']['2024_total'] + V['subsidiary.purchase_money']['2024_total'] + V['subsidiary.senior.fixed']['2024_total'] + V['subsidiary.senior.variable']['2024_total'] + junior['2024_total'] == total['2024_total'])
    ck('consolidated maturity buckets sum', sum(total[k] for k in ['2025_under_1', '2025_1_to_5', '2025_after_5']) == total['2025_total'])
    ck('2025 Note 33 residual equals junior row', note33['2025'] - parent['2025_total'] == junior['2025_total'] == 1594)
    ck('2024 Note 33 residual equals junior row', note33['2024'] - parent['2024_total'] == junior['2024_total'] == 1603)
    ck('five-year parent footnote preserved', all(v in maturity_quote for v in ['$14.3 billion', '$20.3 billion', '$36.4 billion', '$22.4 billion', '$23.6 billion']))
    ck('2026 parent displayed residual is two million', 14300 - parent['2025_under_1'] == 2)
    ck('2027-2030 parent displayed residual is 23 million', (20300+36400+22400+23600) - (parent['2025_1_to_5'] + junior['2025_1_to_5']) == 23)
    ck('consolidated five-year displayed residual is 93 million', (42600+55800+105400+31400+39800) - (total['2025_under_1'] + total['2025_1_to_5']) == 93)
    ck('2025 parent versus consolidated are distinct', note33['2025'] != total['2025_total'])
    ck('guarantee amount separate', '47.6 billion' in notes[6]['quote'] and total['2025_total'] != 47600)
    failed = [r['check'] for r in checks if not r['passed']]
    if failed:
        print(json.dumps({'failures': failed}))
        raise SystemExit(1)
    ledger = {'source_manifest': str((OUT / 'source-manifest.json').relative_to(ROOT)), 'rows': rows, 'qualifiers': notes, 'comparator': manifest['comparator'], 'calculated': {'note33_minus_note20_parent_2025_usd_millions': note33['2025']-parent['2025_total'], 'note33_minus_note20_parent_2024_usd_millions': note33['2024']-parent['2024_total'], 'matching_note20_subsidiary_junior_2025_usd_millions': junior['2025_total'], 'matching_note20_subsidiary_junior_2024_usd_millions': junior['2024_total'], 'parent_2027_to_2030_contractual_rounded_usd_millions': 102700, 'note20_parent_plus_junior_1_to_5_carrying_usd_millions': 102677}, 'boundary': 'Numerical bridge is exact in displayed totals for both years, but accounting/legal mapping of the subsidiary junior row into parent-only debt is not established.'}
    (OUT / 'source-ledger.json').write_text(json.dumps(ledger, indent=2) + '\n')
    (OUT / 'checks.json').write_text(json.dumps({'checks': checks, 'passed': len(checks), 'failed': 0, 'wall_seconds': time.monotonic()-START}, indent=2) + '\n')
    print(json.dumps({'rows': len(rows), 'qualifiers': len(notes), 'checks': len(checks), 'failed': 0}))

if __name__ == '__main__':
    main()
