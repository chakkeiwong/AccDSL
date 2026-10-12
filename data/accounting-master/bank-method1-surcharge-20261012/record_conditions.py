"""Preserve distinct scores, surcharges, timing rules and source limitations."""
import hashlib
import json
import time
from pathlib import Path
from lxml import etree
import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
    (OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def main():
    assert not (OUT/'source-checks.json').exists()
    start=time.monotonic();checks=[]
    def ck(n,b):checks.append({'name':n,'passed':bool(b)})
    norm=lambda e:' '.join(''.join(e.itertext()).split())
    receipts=json.loads((OUT/'access-receipts.json').read_text())
    for r in receipts:
        ck('response hashes '+r['stem'],sha(ROOT/r['body'])==r['body_sha256'] and sha(ROOT/(r['stem']+'.headers'))==r['headers_sha256'])
        if r['section']=='217.401':
            ck('429 excluded from authority',r['transfer']['http_code']==429 and not r['admitted_as_authority']
               and 'Too Many Requests' in (ROOT/r['body']).read_text())
        else:
            ck('successful official XML '+r['stem'],r['transfer']['http_code']==200 and r['transfer']['content_type']=='text/xml'
               and r['admitted_as_authority'] and r['args'][-1].startswith('https://www.ecfr.gov/api/'))
    sections=json.loads((OUT/'sections.json').read_text());by={(r['section'],r['requested_date']):r for r in sections}
    for s in sections:
        ns=etree.parse(str(ROOT/s['body'])).xpath('//DIV8[@N="'+s['section']+'"]')
        ck('section identity '+s['body'],len(ns)==1 and sha(ROOT/s['body'])==s['body_sha256'])
        ck('complete P/footnote/CITA '+s['body'],[norm(e) for e in ns[0].findall('P')]==[p['text'] for p in s['paragraphs']]
           and [norm(e) for e in ns[0].findall('FTNT')]==s['footnotes'] and [norm(e) for e in ns[0].findall('CITA')]==s['amendment_citation'])
        expected=[{'caption':norm(t.find('CAPTION')),'headers':[norm(e) for e in t.xpath('./THEAD/TR/TH')],
                   'rows':[[norm(e) for e in row.findall('TD')] for row in t.xpath('./TBODY/TR')]} for t in ns[0].xpath('.//TABLE')]
        ck('nested table inventory '+s['body'],expected==s['tables'])
    a,b=by['217.403','2026-01-01'],by['217.403','2026-04-01']
    ck('January/April operative paragraphs equal',all(a[k]==b[k] for k in ['heading','paragraphs','footnotes','amendment_citation']))
    ck('January/April table headers and cells equal',len(a['tables'])==len(b['tables'])==2
       and all(x['headers']==y['headers'] and x['rows']==y['rows'] for x,y in zip(a['tables'],b['tables'])))
    ck('exact caption punctuation difference preserved',a['tables'][0]==b['tables'][0]
       and a['tables'][1]['caption']=='Table 2 to § 217.403: Method 2 Surcharge'
       and b['tables'][1]['caption']=='Table 2 to § 217.403—Method 2 Surcharge'
       and a['other_children'][1][1].replace('217.403: Method','217.403—Method',1)==b['other_children'][1][1])
    ck('Method 1 six rows',a['tables'][0]['rows']==[['Below 130','0.0 percent.'],['130—229','1.0 percent.'],['230—329','1.5 percent.'],['330—429','2.0 percent.'],['430—529','2.5 percent.'],['530—629','3.5 percent.']])
    ck('distinct Method 2 band',a['tables'][1]['rows'][5]==['530—629','3.0 percent.'])
    weights=by['217.404','2026-01-01']['tables'][0]['rows']
    ck('twelve indicators and literal weights',len(weights)==12 and [r[2] for r in weights].count('6.67 percent.')==9
       and [r[2] for r in weights].count('10 percent.')==2 and weights[0][2]=='20 percent.')
    comparison=json.loads((OUT/'definition-comparison.json').read_text())
    for y,name in [(2025,'archive-receipt.json'),(2026,'archive-2026-receipt.json')]:
        r=json.loads((OUT/name).read_text());p=ROOT/(r['stem']+'.pdf');d=fitz.open(p)
        ck('annual edition identity '+str(y),r['transfer']['http_code']==200 and len(d)==2
           and f'1–1–{str(y)[2:]} Edition' in d[0].get_text() and 'Definitions.' in d[0].get_text())
        ck('annual receipt hashes '+str(y),sha(p)==r['body_sha256'] and sha(ROOT/(r['stem']+'.headers'))==r['headers_sha256'])
    ck('annual complete definition equality',comparison['complete_normalized_definition_equal']
       and comparison['editions'][0]['normalized_body']==comparison['editions'][1]['normalized_body'])
    for name in ['archive-renders.json','archive-2026-renders.json']:
        for row in json.loads((OUT/name).read_text()):
            ck('archive render '+row['render'],sha(ROOT/row['render'])==row['sha256'] and sha(ROOT/row['source'])==row['source_sha256'])
    conditions=[]
    def add(key,sec,ns,citation,meaning,inputs,limit):
        s=by[sec,'2026-01-01'];ps=[s['paragraphs'][i-1] for i in ns]
        ck('located condition '+key,all(p['ordinal']==i for p,i in zip(ps,ns)))
        conditions.append({'id':key,'citation':citation,'source':s['body'],'source_sha256':s['body_sha256'],
            'paragraphs':ps,'interpretation':meaning,'required_inputs':inputs,'unresolved_or_limit':limit})
    add('scope','217.400',[1,2,3,4,5],'217.400(a), (b)(1)',
        'The stated advanced-approach/Category III and consolidated-parent exclusions delimit BHC scope.',
        ['institution category','entity/control hierarchy'],'Reservation of authority is separate; not every large bank is the covered BHC.')
    add('initial-clocks','217.400',[6,7],'217.400(b)(2)',
        'Initial identification deadline, surcharge calculation deadline and first payout application are distinct.',
        ['date entering relevant category','identification year','applicable supervisory decisions'],'Do not assume first application equals calculation date.')
    add('board-authority','217.400',[8,9],'217.400(c)',
        'The Board may extend scope, adjust a surcharge or change compliance dates subject to stated procedures.',
        ['applicable orders/decisions'],'Public silence does not establish absence of a decision.')
    add('identification','217.402',[1],'217.402',
        'Method 1 score at least 130 basis points identifies a G-SIB BHC, subject to initial timing and annual calculation by December 31.',
        ['supported Method 1 score','annual determination and scope'],'No bank-specific identification performed.')
    add('overall-versus-method1','217.403',[1,2,3,4],'217.403(a), (b)(1)',
        'Overall surcharge is greater of Methods 1 and 2; Method 1 uses its own score and Table 1.',
        ['both methods for overall comparison','specific Method 1 result for cross-reference'],'An overall surcharge cannot automatically substitute for Method 1.')
    add('method1-tail','217.403',[5,6,7],'217.403(b)(2)',
        'The above-table rule at score 630 or more uses the stated 4.5% base and additional amount per 100 basis points.',
        ['score and applicable interval/rounding conventions'],'No fractional-score interpolation, rounding or high-tail implementation supplied.')
    add('method2-reference','217.403',[8,9,10,11],'217.403(c)',
        'Method 2 has a separate table and high-score rule, referring to 217.405.',
        ['Method 2 inputs and score'],'217.405 calculation not inspected; do not infer it from Method 1.')
    add('adjustment-dates','217.403',[12,13],'217.403(d)',
        'The stated increase rule takes effect January 1 after one full calendar year; decrease takes effect the immediately following January 1.',
        ['calculation year','prior and new applicable requirement','supervisory adjustments'],'Retain the GSIB wording and the bank rule cross-reference; no mixed Method 1/overall change case implemented.')
    add('method1-score','217.404',list(range(1,9)),'217.404(a), (b), Table 1',
        'Twelve indicator scores use reported amounts, Board-published global denominators, 10000 scaling and literal weights, with a 100-basis-point cap on the substitutability sum.',
        ['prior December 31 reported indicators','correct year-specific global denominators','reporting/rounding conventions'],
        'Do not normalize the published 6.67% weights to sum to exactly 100%, substitute local denominators, or infer the denominator year from an unexamined file label.')
    retained=ROOT/'data/accounting-master/bank-capital-payout-dependencies-20261012/sources/ecfr-2026-04-01-3.11.xml'
    ps=etree.parse(str(retained)).xpath('//DIV8[@N="3.11"]/P');texts=[norm(p) for p in ps]
    selected=[(i+1,t) for i,t in enumerate(texts) if t.startswith('(v) Leverage buffer standard.')]
    ck('retained bank Method 1 cross-reference',len(selected)==1 and '§ 217.403(b)' in selected[0][1] and '§ 217.403(d)' in selected[0][1])
    conditions.append({'id':'bank-leverage-reference','citation':'3.11(a)(1)(v), requested 1 April 2026',
        'source':str(retained.relative_to(ROOT)),'source_sha256':sha(retained),'ordinal':selected[0][0],'text':selected[0][1],
        'interpretation':'Covered bank leverage standard is the stated lesser-of 1% and, if applicable, half the controlling G-SIB BHC Method 1 surcharge, subject to the referenced effective-date provisions.',
        'required_inputs':['exact parent/bank scope','most recent required Method 1 calculation and effective date','actual reports'],
        'unresolved_or_limit':'No substitution of the overall surcharge, named-bank computation or full applicability finding.'})
    save('condition-ledger.json',{'conditions':conditions,'tables':a['tables']+by['217.404','2026-01-01']['tables'],
         'annual_definitions':{'comparison_file':'definition-comparison.json','edition':'1 January 2026',
          'source':'sources/cfr-2026-217-401.pdf','printed_pages':[630,631],
          'meaning':'Global sample definitions and report-based indicator meanings retained in full; API 429 remains excluded.'},
         'reading_scope':'Full 217.400/.402/.403/.404 including three distinct tables; full 217.401 in annual 2025/2026 editions; retained bank cross-reference. April 403 operative paragraphs/table cells agree; Method 2 caption colon/em dash difference retained in snapshot-comparison.json.',
         'open_dependencies':['FR Y-15 instructions and actual reports','annual Board global-denominator data and publication clocks',
          'score rounding/interval conventions','mixed Method 1/overall surcharge transition application','217.405 if overall surcharge is computed',
          'actual scope/control/election and supervisory facts','complete amendment/applicability chain'],
         'nonclaim':'No actual bank score, surcharge, leverage buffer, payout or complete regulatory engine.'})
    save('source-checks.json',{'checks':checks,'passed':sum(c['passed'] for c in checks),
         'failed':[c['name'] for c in checks if not c['passed']],'wall_seconds':time.monotonic()-start,
         'scope':'Documentary source, exact table, locator and rendering checks only.'})
    assert all(c['passed'] for c in checks)
    print(json.dumps({'source_checks':len(checks),'conditions':len(conditions),'failed':0}))

if __name__=='__main__':main()
