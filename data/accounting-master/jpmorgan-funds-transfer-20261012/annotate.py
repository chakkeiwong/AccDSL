"""Locate issuer assertions and check displayed sums without computing capacity."""
import json
import re
import time
from decimal import Decimal
from prepare import OUT, ROOT, PDF, EXPECTED, sha, save

assert not (OUT/'source-checks.json').exists()
start=time.monotonic()
manifest=json.loads((OUT/'source-manifest.json').read_text())
checks=[]
def ck(name,v):checks.append({'name':name,'passed':bool(v)})
ck('source PDF binding',sha(PDF)==EXPECTED)
pages={p['pdf_page']:(ROOT/p['raw']).read_text() for p in manifest['pages']}
normalized={n:' '.join(t.split()) for n,t in pages.items()}
for n,t in normalized.items():
    (OUT/f'sources/page-{n}-normalized.txt').write_text(t+'\n')
spans=[]
def span(key,n,begin,end):
    text=normalized[n]
    assert text.count(begin)==1,(key,begin)
    a=text.index(begin); b=text.index(end,a) if end else len(text)
    value=text[a:b].rstrip()
    b=a+len(value)
    path=OUT/f'sources/page-{n}-normalized.txt'
    item={'id':key,'pdf_page':n,'printed_page':n-2,'text_path':str(path.relative_to(ROOT)),
          'text_sha256':sha(path),'start':a,'end_exclusive':b,'quote':value}
    spans.append(item);ck('exact located quotation '+key,path.read_text()[a:b]==value)
    return value

table=span('restricted-cash-table',294,'The following table presents the components','Also, as of December')
conditions=span('bank-covered-transactions',294,'Restrictions imposed by U.S. federal law','The Parent Company’s two principal subsidiaries')
structure=span('parent-ihc-issuance-proceeds',294,'The Parent Company’s two principal subsidiaries','The principal sources of income')
limits=span('dividend-and-ihc-limits',294,'The principal sources of income','At January')
capacity=span('dated-bank-dividend-capacity',294,'At January','Notes to consolidated financial statements')
other=span('other-restricted-assets',294,'Also, as of December','Intercompany funds transfers')
affiliate=span('item1-affiliate-dependency',6,'Restrictions on transactions with affiliates.','Dividend restrictions.')
dividend=span('item1-dividend-dependency',6,'Dividend restrictions.','Depositor preference.')

rows=[]
rowdefs=[
('customer-segregation','Segregated for the benefit of securities and cleared derivative customers','Cash reserves at non-U.S. central banks', ['19.4','18.7']),
('non-us-reserves-other','Cash reserves at non-U.S. central banks and held for other general purposes','Total restricted cash(a)', ['9.6','8.8']),
('total-restricted-cash','Total restricted cash(a)','(a) Comprises',['29.0','27.5'])]
for key,begin,end,expected in rowdefs:
    text=table[table.index(begin):table.index(end,table.index(begin)+len(begin))]
    vals=re.findall(r'(?<!\d)\d+\.\d+(?!\d)',text)
    ck('displayed row '+key,vals==expected)
    rows.append({'id':key,'perimeter':'consolidated firm','unit':'USD billions','dates':['2025-12-31','2024-12-31'],'values':vals,'source_span':'restricted-cash-table','literal':text.strip()})
additional=[('restricted-deposits','27.8','26.1','deposits with banks','restricted-cash-table'),
    ('restricted-cash-due-banks','1.2','1.4','cash and due from banks','restricted-cash-table'),
    ('clearing-collateral','44.9','40.7','Cash and securities pledged with clearing organizations','other-restricted-assets'),
    ('customer-securities','40.8','26.8','Securities with a fair value','other-restricted-assets')]
for key,a,b,label,anchor in additional:
    text=table if anchor=='restricted-cash-table' else other
    ck('located pair '+key,label in text and '$'+a+' billion and $'+b+' billion' in text)
    rows.append({'id':key,'perimeter':'consolidated firm','unit':'USD billions','dates':['2025-12-31','2024-12-31'],'values':[a,b],'source_span':anchor,'label':label})
for year,a,b,total in [('2025','19.4','9.6','29.0'),('2024','18.7','8.8','27.5'),('2025 footnote','27.8','1.2','29.0'),('2024 footnote','26.1','1.4','27.5')]:
    ck('exact displayed sum '+year,Decimal(a)+Decimal(b)==Decimal(total))
ck('table dates and billions explicit','December 31, (in billions) 2025 2024' in table)
ck('bank and affiliate transaction qualifications retained',all(s in conditions for s in ['secured in specified amounts','safe and sound banking practices','unless collateralized with cash or US Government debt obligations','10%','20%']))
ck('substantially all issuance proceeds qualification retained','substantially all the net proceeds' in structure and 'preferred and common stock' in structure)
ck('regulatory and IHC conditions retained',all(s in limits for s in ['unsafe or unsound practice','capital or liquidity','management or Board of Directors']))
ck('dated approximate dividend capacity retained',all(s in capacity for s in ['January 1, 2026','approximately $30.1 billion','without the prior approval','earnings during the year']))
ck('Item 1 locates Note 26 and discretionary restriction',all(s in dividend for s in ['Refer to Note 26','January 1, 2026','unsafe or unsound practice']))
ck('Item 1 broad affiliate scope retained','derivatives, securities lending' in affiliate and 'comply with certain other requirements' in affiliate)
for page in manifest['pages']:
    for key in ['raw','layout','render']:ck('preserved '+key+' '+str(page['pdf_page']),sha(ROOT/page[key])==page[key+'_sha256'])
facts={'source_pdf':str(PDF.relative_to(ROOT)),'source_sha256':EXPECTED,'evidence_class':'issuer-reported assertions; operative law not independently checked',
    'rows':rows,'spans':spans,'dividend_capacity':{'date':'2026-01-01','payer':'JPMorgan Chase Bank, N.A.','recipient':'JPMorgan Chase & Co.',
        'value':'30.1','unit':'USD billions','precision':'approximately','condition':'without prior approval of relevant banking regulators',
        'additional_conditions':['regulatory unsafe/unsound intervention retained','2026 earnings may supplement capacity; no amount estimated'],
        'source_span':'dated-bank-dividend-capacity'},
    'query_dispositions':[
        {'query':'Unrestricted parent cash from consolidated restricted cash and Note 33 parent cash','status':'invalid context subtraction','missing':'parent-specific restricted balances and deposit terms'},
        {'query':'Cash dividend actually paid by the bank on 1 January 2026','status':'unresolved','missing':'dated transfer event; capacity is not payment'},
        {'query':'Unconditional future parent funding of 30.1 billion','status':'unsupported','missing':'actual decisions, applicable restrictions and future bank earnings'},
        {'query':'Sum restricted cash with both other restricted-asset disclosures','status':'unresolved overlap','missing':'disjointness and category membership; no total computed'},
        {'query':'Apply issuer 10%/20% summary as executable law','status':'unverified legal rule','missing':'operative editions, defined capital, covered transactions, exemptions and actual exposures'},
        {'query':'Treat the 2025 50.0 billion subsidiary dividends in Note 33 as the same quantity as 30.1 billion capacity','status':'different payer scope, dates and quantity','missing':'bank-specific paid-dividend reconciliation'}],
    'scope':'No general claim that all restricted resources or legal conditions have been enumerated.'}
save('source-ledger.json',facts)
failed=[r['name'] for r in checks if not r['passed']]
save('source-checks.json',{'checks':checks,'passed':len(checks)-len(failed),'failed':failed,'wall_seconds':time.monotonic()-start})
print(json.dumps({'passed':len(checks)-len(failed),'failed':failed,'paired_rows':len(rows),'located_spans':len(spans)}))
raise SystemExit(bool(failed))
