"""Read exact source rows, verify documentary sums, preserve qualified spans."""
import hashlib
import json
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    manifest = json.loads((OUT / 'source-manifest.json').read_text())
    checks, records, spans, calculations = [], {}, [], []

    def ck(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})

    ck('exact retained PDF', sha(ROOT / manifest['source_pdf']) == manifest['source_pdf_sha256'])
    for item in manifest['pages']:
        for field in ['text', 'reading_text', 'image']:
            ck(f"page {item['pdf_page']} {field}", sha(ROOT / item[field]) == item[field + '_sha256'])

    def row(key, page, label, values, occurrence=1, line_count=1):
        lines = (OUT / 'sources' / f'page-{page}.txt').read_text().splitlines()
        candidates = [i for i, line in enumerate(lines) if line.strip().startswith(label)]
        index = candidates[occurrence - 1]
        raw = '\n'.join(lines[index:index + line_count])
        body = raw[raw.index(label) + len(label):]
        body = re.sub(r'\([a-z]\)', '', body)
        tokens = re.findall(r'(?<![\w.])\(?\d[\d,]*\)?|—', body)
        parsed = [None if t == '—' else int(t.replace(',', '').replace('(', '-').replace(')', '')) for t in tokens]
        ck('source row ' + key, parsed == values)
        records[key] = {'source_pdf_page': page, 'printed_page': page - 2, 'layout_line': index + 1, 'raw_text': raw, 'parsed_values': parsed, 'source_dash': 'retained as null; zero arithmetic contribution only where the source subtotal supports it', 'units': 'USD millions as displayed', 'source_precision': 'rounded reported millions; no underlying exactness claim'}
        return parsed

    columns = ['2025 <=1 year', '2025 >1 through 3 years', '2025 >3 through 5 years', '2025 >5 years', '2025 contractual total', '2024 contractual total', '2025 carrying value', '2024 carrying value']
    consumer = row('consumer_ex_card', 298, 'Total consumer, excluding credit card', [24280,5666,3458,10183,43587,44844,337,571])
    card = row('credit_card', 298, 'Credit card(b)', [1073537,104229,None,None,1177766,1001311,2200,None], line_count=3)
    all_consumer = row('total_consumer', 298, 'Total consumer(c)', [1097817,109895,3458,10183,1221353,1046155,2537,571])
    wholesale = row('wholesale', 298, 'Total wholesale(c)', [155797,187773,224821,27563,595954,531467,3741,3118])
    total = row('total_lending', 298, 'Total lending-related', [1253614,297668,228279,37746,1817307,1577622,6278,3689])
    for key in ['consumer_ex_card','credit_card','total_consumer','wholesale','total_lending']:
        records[key]['columns'] = columns

    begin = row('allowance_beginning_2025', 262, 'Beginning balance at January 1,', [82,None,2019,2101], occurrence=2)
    provision = row('commitment_provision_2025', 262, 'Provision for lending-related commitments', [1,2200,768,2969])
    other = row('commitment_other_2025', 262, 'Other', [None,None,1,1], occurrence=2)
    end = row('allowance_ending_2025', 262, 'Ending balance at December 31,', [83,2200,2788,5071], occurrence=2)
    asset_allow = row('asset_specific_allowance', 262, 'Asset-specific', [None,None,119,119], occurrence=3)
    portfolio_allow = row('portfolio_allowance', 262, 'Portfolio-based', [83,2200,2669,4952], occurrence=3)
    asset_exposure = row('asset_specific_commitments', 262, 'Asset-specific', [None,None,925,925], occurrence=4)
    portfolio_exposure = row('portfolio_commitments', 262, 'Portfolio-based', [24358,23617,555047,603022], occurrence=4, line_count=2)
    covered = row('allowance_scope_commitments', 262, 'Total lending-related commitments', [24358,23617,555972,603947])
    for key in list(records)[5:]:
        records[key]['columns'] = ['consumer excluding card', 'credit card', 'wholesale', 'total']

    ratings_ig = row('guarantees_investment_grade', 299, 'Investment-grade(a)', [20535,3187,20443,3380])
    ratings_other = row('guarantees_noninvestment_grade', 299, 'Noninvestment-grade(a)', [9384,1342,8233,974])
    guarantees = row('guarantees_contractual', 299, 'Total contractual amount', [29919,4529,28676,4354])
    gar_allow = row('guarantees_allowance', 299, 'Allowance for lending-related commitments', [175,13,94,37])
    gar_liability = row('guarantee_liability', 299, 'Guarantee liability', [441,None,379,None])
    gar_carry = row('guarantees_carrying', 299, 'Total carrying value', [616,13,473,37])
    for key in list(records)[14:]:
        records[key]['columns'] = ['2025 standby letters/other financial guarantees', '2025 other letters of credit', '2024 standby letters/other financial guarantees', '2024 other letters of credit']

    def calc(name, observed, expected, role='documentary reconciliation'):
        calculations.append({'name':name, 'observed':observed, 'expected':expected, 'role':role})
        ck(name, observed == expected)

    zero = lambda x: 0 if x is None else x
    for i in range(8):
        calc('consumer subtotal column ' + str(i), zero(consumer[i]) + zero(card[i]), all_consumer[i])
        calc('total lending column ' + str(i), all_consumer[i] + wholesale[i], total[i])
    for name, values in [('consumer',all_consumer),('wholesale',wholesale),('total',total)]:
        calc(name + ' maturity buckets',sum(values[:4]),values[4])
    for i in range(4):
        calc('allowance roll-forward column ' + str(i), zero(begin[i]) + provision[i] + zero(other[i]), end[i])
        calc('allowance methods column ' + str(i), zero(asset_allow[i]) + portfolio_allow[i], end[i])
        calc('exposure methods column ' + str(i), zero(asset_exposure[i]) + portfolio_exposure[i], covered[i])
        calc('guarantee rating subtotal column ' + str(i),ratings_ig[i]+ratings_other[i],guarantees[i])
        calc('guarantee carrying components column ' + str(i),gar_allow[i]+zero(gar_liability[i]),gar_carry[i])
    for key in list(records)[5:14]:
        values = records[key]['parsed_values']
        calc(key+' segment total',sum(zero(x) for x in values[:3]),values[3])
    calc('contractual versus allowance population difference', total[4]-covered[3], 1213360, 'difference of reported populations; not exact composition of rounded footnote exclusions')
    calc('carrying value versus allowance difference',total[6]-end[3],1207,'unallocated measurement difference; not a second allowance or cash flow')

    def span(key, page, first, last, meaning):
        text = ' '.join((OUT/'sources'/f'page-{page}-reading.txt').read_text().split())
        s = text.index(first); e = text.index(last,s)+len(last)
        quote = text[s:e]
        ck('source span '+key,first in quote and last in quote and e>s)
        spans.append({'id':key,'source_pdf_page':page,'printed_page':page-2,'text':quote,'text_sha256':hashlib.sha256(quote.encode()).hexdigest(),'interpretation':meaning,'evidence_class':'issuer disclosure; not independently verified law or contract enforceability'})

    span('maximum_vs_expected',297,'The contractual amount of these financial instruments','representative of its expected future credit exposure or funding requirements.','Maximum contractual exposure has draw/performance conditions; issuer explicitly rejects using total as expected funding or credit exposure.')
    span('conditional_cancellation',297,'The amounts in the table below for credit card','significant decrease in the value of underlying property.','Total available lines for specified products; generally reducible/cancellable only under contract or law. No universal cancellation rule.')
    span('allowance_liability_and_provision',260,'The Firm’s allowance for credit losses represents','recognized in the provision for credit losses.','Commitment allowance is presented in accounts payable and other liabilities; distinguish loan contra-asset and provision expense.')
    span('cancellable_draw_exclusion',260,'The allowance for loan losses and allowance for lending-related commitments represent','cancellable lending-related commitments (e.g., credit cards).','No allowance for future draws on unconditionally cancellable commitments in the reported policy. This is not zero possible draw or zero liquidity demand.')
    span('expected_life',260,'The expected life of each instrument','generally paying down the highest interest rate balances first.','Contract terms, prepayments, cancellation and selected options affect expected life; funded card repayment allocation is separate.')
    span('company_scenario_protocol',261,'The credit loss factors incorporate','are updated by the Firm’s central forecasting team.','Five scenarios, eight-quarter forecast and one-year reversion are issuer choices. AccDSL must retain their provenance, not adopt these as universal defaults.')
    span('qualitative_adjustments',261,'The quantitative calculation is adjusted','could affect the estimate of the allowance for loan losses and the allowance for lending-related commitments.','Model and qualitative uncertainty remain; central macro variables alone do not reproduce allowance.')
    span('allowance_scope_and_transaction',262,'(d) The allowance for lending-related commitments','approximately $23 billion.','Footnotes distinguish liability presentation, rounded excluded populations, Apple transaction allowance and expected drawn loans at closing.')
    span('risk_participation_basis',298,'(d) As of December 31, 2025 and 2024','shown gross of risk participations.','Wholesale contractual figures net specified risk participations; regulator gross reporting has a different basis.')
    span('apple_and_carrying_value',298,'(h) Includes estimated total credit exposure','related to the Apple Card transaction.','Expected-close exposure includes estimated drawn loans; carrying value combines allowance, guarantee, fair-value and deferred components as applicable.')
    span('apple_event_clocks',49,'Apple Card transaction: On January 7, 2026,','(the “Apple Card transaction”).','Commitment date 2025-12-30, announcement 2026-01-07 and approximate future close are distinct. Do not book future acquired loans as 2025 owned loans.')
    span('other_unfunded_purposes',299,'Other unfunded commitments to extend credit generally','including the issuance of a standby letter of credit.','Working-capital, bond/CP backstops, clearing liquidity and multipurpose facilities have distinct draw mechanisms.')
    span('contingent_noncontingent',299,'The lending-related contingent obligation','any non-contingent obligation.','Reported guarantee policy keeps expected credit-loss obligation separate from non-contingent guarantee obligation.')
    span('standby_guarantee_conditions',299,'Standby letters of credit and other financial guarantees are conditional','trade financings and similar transactions.','Performance undertaking to a third party has conditions; contractual amount is not an already-funded loan.')
    span('outside_lending_population',300,'The Firm transacts in certain derivative contracts','substantially lower percentage of the notional amount.','Other guarantee/notional populations remain outside the lending subtotal; notional can exceed contractual maximum for certain stable-value products.')
    span('group_guarantee_exclusion',302,'The Parent Company has guaranteed certain long- term debt','Refer to Note 20 for additional information.','Issuer describes JPMFC as 100%-owned and excludes these parent guarantees from the Note 28 table. Not a complete guarantee inventory or independent legal ownership verification.')

    report = {'started_on':'2026-10-11','date':'2026-10-12','plan':'docs/plans/accounting-jpmorgan-commitments-20261011.md','source_manifest':'source-manifest.json','as_of':'2025-12-31','rows':records,'spans':spans,'calculations':calculations,'missing_inputs':['contract-level unconditional versus conditional cancellation rights and actual exercise','draw paths and dependence with borrower distress','borrower/default and recovery inputs with support','future acquired portfolio identity, balances and closing conditions','complete allowance, fair-value, fee and guarantee bridge','cash settlement mechanism, collateral calls and available funding','operative ASC and prudential requirements applicable to each instrument'], 'checks':checks,'passed':sum(r['passed'] for r in checks),'failed':sum(not r['passed'] for r in checks),'readiness':'not_ready','claims_excluded':['full package semantics','loss or liquidity forecast','legally verified cancellation','operative US GAAP verification','historical byte availability','genuine same-context E05 conflict']}
    (OUT/'source-ledger.json').write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'check-run.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-commitments-20261011/check_sources.py','wall_seconds':time.monotonic()-start},indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'failed':report['failed'],'rows':len(records),'spans':len(spans),'calculations':len(calculations),'failures':[r['check'] for r in checks if not r['passed']]}))
    raise SystemExit(bool(report['failed']))


if __name__ == '__main__':
    main()
