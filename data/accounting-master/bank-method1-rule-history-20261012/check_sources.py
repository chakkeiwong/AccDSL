"""Check located rule-history evidence without implementing a bank score."""
from pathlib import Path
import hashlib
import json
import re
import time
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,o):(OUT/n).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def norm(s):return ' '.join(s.split())

def main():
    assert not (OUT/'completion.json').exists()
    start=time.monotonic();checks=[];conditions=[]
    def ck(n,v,detail=None):checks.append({'name':n,'passed':bool(v),'detail':detail})
    docs={n:fitz.open(OUT/f'sources/{n}.pdf') for n in ['proposal-2026-05961','final-2015-18702']}
    save('pdf-pages.json',{n:[{'physical_page':i+1,'text':p.get_text()} for i,p in enumerate(d)] for n,d in docs.items()})
    def cond(id,name,page,anchors,finding,limit):
        text=norm(docs[name][page-1].get_text());matched=[x in text for x in anchors];ck(id,all(matched),dict(zip(anchors,matched)))
        conditions.append({'id':id,'source':str((OUT/f'sources/{name}.pdf').relative_to(ROOT)),
                           'physical_page':page,'printed_page':14907+page if name.startswith('proposal') else 49081+page,
                           'anchors':anchors,'finding':finding,'limit':limit})
    prop='proposal-2026-05961';final='final-2015-18702'
    cond('proposal_status',prop,1,['ACTION: Notice of proposed rulemaking.','June 18, 2026'],
         '27 March 2026 proposal with a comment deadline, not a final effective amendment.',
         'A passed comment deadline does not establish adoption.')
    cond('existing_rounding_description',prop,2,['Scores are rounded to the nearest basis point','at or above one-half are rounded to one'],
         'Footnote 9 in the background describes existing score rounding to nearest basis point, with half up.',
         'This is the Board preamble description, not proposed Method 2 ceiling arithmetic or a full current-law determination.')
    cond('proposal_dates',prop,10,['December 31 of the previous','as averages of daily or monthly values'],
         'The proposal distinguishes then-current point-in-time inputs from proposed averaging.',
         'Empirical benefits and cited papers are not independently assessed.')
    cond('valuation_frequency',prop,13,['would not change the frequency of valuation','only to GSIBs identified'],
         'Footnote 63 distinguishes averaging of carrying values from changing GAAP valuation frequency; entity scopes differ.',
         'Proposed requirements do not establish actual reporting obligations.')
    cond('proposed_fx',prop,14,['proposing to update its internal methodology','annual average exchange rates'],
         'The proposal would use annual-average rather than year-end spot FX for global denominators.',
         'The two retained annual notices use stated year-end rates; do not replace them with this proposal.')
    cond('ceiling_is_method2',prop,14,['20- basis point ranges','Where ceiling means to round'],
         'The proposed Method 2 band formula uses a ceiling; this is a different operation from rounding the score.',
         'Image formula inspected; no Method 2 implementation or adoption inference.')
    cond('method1_bands',prop,15,['would not amend the score band ranges for method 1'],
         'The proposed narrower bands concern Method 2, while the proposal says Method 1 bands would remain.',
         'Other proposed Method 1 inputs and weights can change.')
    cond('proposed_amendatory_text',prop,41,['Revise paragraphs (c) and (d).','Trading volume—fixed income','Trading volume—equity and other'],
         'The amendatory text proposes a revised effective-date rule and a 14-indicator Method 1 table.',
         'The source is proposed text; no change to the retained 12-indicator rule is made.')
    cond('final_identity',final,1,['ACTION: Final rule.','December 1, 2015','January 1, 2018'],
         'The original final rule has general and specified-exception effective dates.',
         'These dates do not establish the current rule or its complete amendment chain.')
    cond('historical_rounding',final,3,['Scores would be rounded to the nearest basis','or above one-half would be rounded to one'],
         'Printed 49084 footnote 22 contains the earlier nearest-basis-point description.',
         'The surrounding passage recaps the proposal in the final-rule preamble; retain the conditional tense and context.')
    cond('adopted_method1_structure',final,4,['The final rule adopts the proposed weights for method 1.','retains the relative approach for method 1'],
         'Printed 49085 explains the adopted weights and relative approach.',
         'This does not turn every sentence in the preceding proposal recap into operative text.')
    cond('historical_final_clauses',final,25,['equals or exceeds 130 basis points','most recent FR Y– 15'],
         'Final §§217.402–404 show the threshold and the original most-recent-report wording.',
         'The retained January 2026 §217.404 instead specifies previous-calendar-year December 31; no unchanged-history claim.')
    cond('cap_and_weights',final,26,['will not exceed 100 basis points','6.67 percent.'],
         'The final clause states the substitutability cap and literal decimal indicator weights.',
         'No normalization of literal weights or independent rounding of each component follows.')
    soup=BeautifulSoup((OUT/'sources/denominator-index.html').read_bytes(),'html.parser');body=soup.find(id='content')
    table=body.find('table');trs=table.find_all('tr');headers=[norm(x.get_text(' ',strip=True)) for x in trs[0].find_all(['th','td'])]
    ck('index_date', 'December 12, 2025' in norm(body.get_text(' ',strip=True)))
    ck('index_measurement_headers',headers[2:4]==['Denominators in USD (end-2024)','Denominators in USD (end-2023)'])
    old=json.loads((ROOT/'data/accounting-master/bank-method1-reporting-20261012/denominator-tables.json').read_text())
    comparisons=[]
    for row in trs[1:]:
        cells=[norm(x.get_text(' ',strip=True)) for x in row.find_all(['th','td'])]
        nums=[x for x in cells if re.fullmatch(r'\d{1,3}(,\d{3})+',x)]
        names=[x for x in cells if x not in nums]
        if not nums:continue
        label=names[-1];ck('index_width_'+label,len(nums)==11)
        for idx,notice_year in [(0,2025),(1,2024)]:
            matches=[r for r in old if r['notice_year']==notice_year and r['indicator'].lower()==label.lower()]
            ok=len(matches)==1 and nums[idx].replace(',','')==matches[0]['amount_usd']
            ck(f'notice_match_{notice_year}_{label}',ok)
            comparisons.append({'indicator':label,'index_header':headers[idx+2],
                                'index_usd':nums[idx].replace(',',''),'notice_year':notice_year,
                                'notice_usd':matches[0]['amount_usd'] if len(matches)==1 else None,'matches':ok})
    ck('all_24_mapped',len(comparisons)==24)
    save('denominator-comparison.json',{'headers':headers,'checked_columns':headers[2:4],
         'rows':comparisons,'other_columns':'retained, not independently compared',
         'availability':'The page update label is not proof of selected bytes on that date or earliest availability.'})
    search=json.loads((OUT/'sources/rule-status-search.json').read_text())
    ck('bounded_search',search['count']==1 and len(search['results'])==1)
    ck('search_identifies_proposal',search['results'][0]['document_number']=='2026-05961' and search['results'][0]['type']=='Proposed Rule')
    ck('historical_locator', 'Scores would be rounded' in docs[final][2].get_text() and 'Scores would be rounded' not in docs[final][6].get_text())
    save('citation-location.json',{'proposal':{'physical_page':2,'printed_page':14909,'footnote':9,'see_also':'80 FR 49088'},
         'located_rounding':{'source':'final-2015-18702.pdf','physical_page':3,'printed_page':49084,'footnote':22},
         'interpretation':'The precise older rounding locator is 49084 n22. The proposal also cites 49088, whose inspected page concerns Method 2 coefficients; no silent relocation of the source citation.'})
    for n,d in docs.items():ck('pdf_identity_'+n,len(d)==(42 if n==prop else 35))
    receipts=json.loads((OUT/'access-receipts.json').read_text())+[json.loads((OUT/n).read_text()) for n in ['status-search-receipt.json','release-receipt.json','final-rule-receipt.json']]
    for r in receipts:ck('transport_'+r['name'],r['transfer']['http_code']==200 and r['transfer']['exitcode']==0)
    pdf=ROOT/'docs/design/proposal/manuscript-reporting-inputs-20261012/accounting-product-proposal.pdf'
    ck('protected_v243',sha(pdf)==json.loads((OUT/'baseline.json').read_text())['pdf_sha256'])
    save('condition-ledger.json',{'conditions':conditions,'rounding_status':'Official existing-practice description located; current complete rule history unverified',
         'proposed_policy':'not adopted by this inquiry','named_bank_score':'not computed','readiness':'not_ready'})
    save('reading-review.json',{'reader':'Codex author; no independent/human acceptance',
         'proposal_pages':{'full_selected_text':[2,10,12,13,14,41,42],'selected_passages':[1,15],
                           'image_table':[11,12],'image_formula':[14]},
         'final_2015_pages':{'full_selected_text':[3,4,7,25,26],'identity_dates':[1]},
         'scope':'Neither full publication or economic analysis is claimed read. Proposed table changes and source boundaries only.',
         'renders':{str(p.relative_to(ROOT)):sha(p) for p in (OUT/'rendered').glob('*.png')}})
    fail=[r for r in checks if not r['passed']];save('source-checks.json',{'passed':len(checks)-len(fail),'failed':fail,'checks':checks,'wall_seconds':time.monotonic()-start})
    print(json.dumps({'conditions':len(conditions),'matched_denominators':len(comparisons),'passed':len(checks)-len(fail),'failed':[r['name'] for r in fail]}));raise SystemExit(bool(fail))

if __name__=='__main__':main()
