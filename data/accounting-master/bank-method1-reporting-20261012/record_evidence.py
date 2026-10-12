"""Verify a bounded documentary reading; no bank-score implementation."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import time
import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def norm(s):
    return ' '.join(s.split())

def main():
    assert not (OUT / 'completion.json').exists(), 'Closed unit must not be regenerated'
    started = time.monotonic()
    sources = {}
    for name in ['fr-y15-current-form', 'fr-y15-current-instructions', 'denominators-2024', 'denominators-2025']:
        p = OUT / 'sources' / (name + '.pdf')
        d = fitz.open(p)
        sources[name] = {'path':str(p.relative_to(ROOT)), 'sha256':sha(p),
                         'pages':[{'physical_page':i+1, 'text':page.get_text()} for i,page in enumerate(d)]}
    save('pdf-pages.json', sources)
    def page(name, n):
        return norm(sources[name]['pages'][n-1]['text'])
    conditions = []
    checks = []
    def check(name, ok, detail=None):
        checks.append({'name':name,'passed':bool(ok),'detail':detail})
    def condition(id, source, n, anchors, finding, limit):
        checks_here = [a in page(source,n) for a in anchors]
        check('located_' + id, all(checks_here), {'anchors':anchors,'matches':checks_here})
        conditions.append({'id':id,'source':sources[source]['path'], 'physical_page':n,
                           'source_sha256':sources[source]['sha256'], 'anchors':anchors,
                           'finding':finding,'limit':limit})
    ins='fr-y15-current-instructions'
    condition('mixed_cover',ins,1,['Effective September 2021'],
              'The cover labels the instructions effective September 2021.',
              'GEN-1 is January 2026: the cover does not date every page or establish an update chain.')
    condition('scope_date',ins,5,['January 2026','Schedules A through G','Schedules H through N'],
              'GEN-1 distinguishes domestic holding-company schedules from FBO/IHC schedules.',
              'Reporting population is not identical to a particular bank capital-rule population; no named entity is classified here.')
    condition('perimeter',ins,6,['on a consolidated basis','excluded from the FR Y-15'],
              'The general rules eliminate intragroup transactions and balances, subject to schedule-specific rules.',
              'An issuer consolidated annual report is not automatically the applicable regulatory reporting perimeter.')
    condition('submission',ins,7,['50 calendar days','65 calendar days','5:00 P.M.','first business'],
              'Quarter-end as-of dates differ from receipt deadlines: 50 days for the first three quarters and 65 after December, with weekend/holiday adjustment.',
              'Receipt deadlines do not prove public release or the version available at a historical information date.')
    condition('basis',ins,7,['except as otherwise provided','workpapers'],
              'The report uses US GAAP except as the instructions provide and requires retained workpapers.',
              'GAAP financial statement balances alone need not supply each regulatory input.')
    condition('dollar_precision',ins,7,['Report all dollar amounts in thousands.','nearest million','zeros reported in the thousands column'],
              'General instructions specify thousands with optional nearest-million reporting.',
              'This is a dollar-report rule, not a Method 1 basis-point score-rounding convention.')
    condition('rounded_components',ins,8,['amounts less than $500,000','totals and the sums of their'],
              'Under the option, sub-$500,000 amounts become zero and detail must be adjusted to add to totals.',
              'Independent symmetric intervals for every displayed component would ignore this coupled adjustment rule.')
    condition('availability',ins,8,['confidential treatment','automatically-calculated items','reasonable estimates are permitted'],
              'Confidential treatment can extend to derived fields; first-time filers may use reasonable estimates.',
              'A submission does not guarantee public completeness or exact underlying values.')
    condition('revisions',ins,9,['amended report','resubmit the','same level of consolidation'],
              'Amended reports and resubmission after other source reports require report versions and compatible perimeters.',
              'The latest report cannot silently replace what was available at an earlier information date.')
    condition('payment_scope',ins,25,['last twelve months','Only include outgoing payments','do not include internal'],
              'Schedule C item 1 is a trailing-twelve-month outgoing payment flow with specified exclusions and settlement conventions.',
              'It is not a quarter-end balance or an unrestricted sum of gross cash movements.')
    condition('payment_accuracy',ins,25,['Though payment totals are not rounded','at or above $10 trillion','known overestimates may be reported'],
              'Payment totals have a separate magnitude-dependent accuracy rule and can use known overestimates if precise totals are unavailable.',
              'Do not propagate the general nearest-million rule to every input or treat this as score rounding.')
    condition('form_approval','fr-y15-current-form',1,['Approval expires June 30, 2026','06/2026'],
              'The currently linked form displays June 2026 approval and footer labels.',
              'The labels do not by themselves establish October applicability, expiration consequences, or historical availability.')
    condition('denominator_2024','denominators-2024',2,['year-end 2023','1.105','December 31, 2023','FOR 2024'],
              'The 2024 notice uses year-end-2023 BCBS euro amounts and a 1.105 USD-per-euro rate.',
              'No independent BCBS table or FX recomputation was performed.')
    condition('denominator_2025','denominators-2025',2,['year-end 2024','1.0389','December 31, 2024','FOR 2025'],
              'The 2025 notice uses year-end-2024 BCBS euro amounts and a 1.0389 USD-per-euro rate.',
              'A publication-year label is not the underlying measurement year or capital-requirement effective date.')
    condition('release_2024','denominators-2024',1,['December 18, 2024','OP–1863','ACTION: Notice.'],
              'The notice is published 18 December 2024; its printed filing line on page 2 is 17 December at 8:45 am.',
              'Publication and the printed filing timestamp are separate clocks; no historical downloaded-byte identity is established.')
    condition('release_2025','denominators-2025',1,['December 16, 2025','OP–1875','ACTION: Notice.'],
              'The notice is published 16 December 2025; its printed filing line on page 2 is 15 December at 8:45 am.',
              'This does not establish the earliest availability of another Board or BCBS copy.')
    labels=['Total exposures','Intra-financial system assets','Intra-financial system liabilities',
            'Securities outstanding','Payments activity','Assets under custody',
            'Underwritten transactions in debt and equity markets',
            'Notional amount of over-the-counter (OTC) derivatives',
            'Trading and available-for-sale (AFS) securities','Level 3 assets',
            'Cross-jurisdictional claims','Cross-jurisdictional liabilities']
    # Manually transcribed against the rendered table; verify each label and amount
    # occupies the same PDF row. No positional zip of unrelated text streams.
    values={2024:[115205051188518,11253226663114,11388383441235,19247590871111,3527103136881927,
                  219479268261988,7962804019185,733514990056729,4278831961372,803127442989,28416427492687,23524643383930],
            2025:[115610567459028,11744530471538,11549951568929,20989667733564,3583068096731293,
                  236728086197216,9458987280583,743719670668380,4617580286026,785843290915,27556319815579,22625378519775]}
    tables=[]
    for year, expected in values.items():
        d=fitz.open(OUT/f'sources/denominators-{year}.pdf'); words=d[1].get_text('words')
        numeric=sorted([w for w in words if re.fullmatch(r'\$?\d{1,3}(?:,\d{3}){3,}',w[4])],key=lambda w:w[1])
        check(f'{year}_twelve_numeric_rows',len(numeric)==12)
        for label,amount,w in zip(labels,expected,numeric):
            row=' '.join(x[4] for x in sorted([x for x in words if abs(x[1]-w[1])<1],key=lambda x:x[0]))
            check(f'{year}_{label}',label in row and int(w[4].replace(',','').replace('$',''))==amount,row)
            tables.append({'notice_year':year,'bcbs_reference_year':year-1,'physical_page':2,
                           'printed_page':102909 if year==2024 else 58246,'indicator':label,
                           'amount_usd':str(amount),'row_text':row,'amount_bbox':list(w[:4])})
        check(f'{year}_filing_clock',f'{year}–'+('29981 Filed 12–17–24; 8:45 am' if year==2024 else '22964 Filed 12–15–25; 8:45 am') in page(f'denominators-{year}',2))
    check('different_vintages',values[2024]!=values[2025])
    keyword_hits=[]
    for r in sources[ins]['pages']:
        hits=[l for l in r['text'].splitlines() if re.search(r'round|denominator|aggregate global|score|surcharge',l,re.I)]
        if hits:keyword_hits.append({'physical_page':r['physical_page'],'lines':hits})
    save('instruction-search.json',{'query':'round|denominator|aggregate global|score|surcharge',
         'pages_searched':len(sources[ins]['pages']),'hits':keyword_hits,
         'interpretation':'Search plus selected reading did not identify a score-rounding rule; not proof that no authority supplies one.'})
    exact=json.loads((OUT/'sources/federalregister-exact-search-trusted.json').read_text())
    for num,year in [('2024-29981',2024),('2025-22964',2025)]:
        rows=[r for r in exact['results'] if r['document_number']==num]
        check('search_identity_'+num,len(rows)==1 and rows[0]['type']=='Notice' and rows[0]['publication_date']==f'{year}-12-'+('18' if year==2024 else '16'))
    check('search_proposal_distinct',any(r['document_number']=='2026-05961' and r['type']=='Proposed Rule' for r in exact['results']))
    receipts=json.loads((OUT/'access-receipts.json').read_text())
    for r in receipts:
        check('retained_body_'+r['name'],sha(ROOT/r['body'])==r['body_sha256'])
    for r in json.loads((OUT/'denominator-receipts.json').read_text()):
        check('download_'+r['name'],r['transfer']['http_code']==200 and r['completion']['exit_code']==0)
    baseline=json.loads((OUT/'baseline.json').read_text())
    pdf=ROOT/'docs/design/proposal/manuscript-capital-recognition-20261012/accounting-product-proposal.pdf'
    check('protected_candidate',sha(pdf)==baseline['pdf_sha256'])
    save('condition-ledger.json',{'scope':'Source reading, not a complete current reporting rule or bank calculation',
          'conditions':conditions,'score_rounding':'unresolved','current_2026_denominators':'not acquired',
          'named_bank_score':'not computed','readiness':'not_ready'})
    save('denominator-tables.json',tables)
    save('render-review.json',{'reader':'Codex author review; no independent/human acceptance',
         'read_pdf_pages':{ins:[1,5,6,7,8,9,25],'fr-y15-current-form':[1],
                           'denominators-2024':[1,2],'denominators-2025':[1,2]},
         'boundary':'Both denominator notices fully read, including footnotes and rows; adjacent unrelated notices excluded. Instruction pages selected, not whole-115-page review.',
         'renderer_note':'Form render emitted No common ancestor in structure tree. Visible cover inspected; no structural-validity inference.',
         'inspected_renders':{str(p.relative_to(ROOT)):sha(p) for p in sorted((OUT/'rendered').glob('*.png'))}})
    failed=[r for r in checks if not r['passed']]
    save('source-checks.json',{'passed':len(checks)-len(failed),'failed':failed,'checks':checks,'wall_seconds':time.monotonic()-started})
    print(json.dumps({'conditions':len(conditions),'table_cells':len(tables),'passed':len(checks)-len(failed),'failed':[r['name'] for r in failed]}))
    raise SystemExit(bool(failed))

if __name__=='__main__': main()
