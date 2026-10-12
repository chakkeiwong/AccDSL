"""Verify the exact declared date readings and keep other date roles separate."""
import datetime,hashlib,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sources=json.loads((OUT/'selected-sources.json').read_text())
pages=json.loads((OUT/'selected-pages.json').read_text())
by={(r['document_id'],r['pdf_page']):r for r in pages}
specs=[
(2018,'annual',190,'20 March 2019'),(2018,'interim_h1',49,'8 August 2018'),
(2019,'annual',195,'18 March 2020'),(2019,'interim_h1',49,'7 August 2019'),
(2020,'annual',217,'17 March 2021'),(2020,'interim_h1',53,'6 August 2020'),
(2021,'annual',225,'17 March 2022'),(2021,'interim_h1',55,'10 August 2021'),
(2022,'annual',245,'16 March 2023'),(2022,'interim_h1',62,'9 August 2022'),
(2023,'annual',330,'14 March 2024'),(2023,'interim_h1',79,'10 August 2023'),
(2024,'annual',373,'19 March 2025'),(2024,'interim_h1',61,'8 August 2024'),
(2025,'annual',400,'18 March 2026'),(2025,'interim_h1',65,'8 August 2025')]
checks=[];start=time.monotonic()
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
ck('sixteen selected reports',len(sources)==16 and len(specs)==16)
ck('seventeen candidate pages inspected',len(pages)==17)
rows=[];normalized={}
for key,r in sources.items():
    ck('primary identity '+key,sha(ROOT/r['local_path'])==r['sha256'])
    ck('prior frozen date state '+key,r['source_metadata']['publication_date'] is None and r['source_metadata']['publication_date_status']=='not_verified')
for r in pages:
    ck('text/render identity '+r['document_id']+':'+str(r['pdf_page']),
       sha(ROOT/r['text'])==r['text_sha256'] and sha(ROOT/r['render'])==r['render_sha256'] and r['pdf_sha256']==sources[r['document_id']]['sha256'])
    normalized[(r['document_id'],r['pdf_page'])]=' '.join((ROOT/r['text']).read_text().split())
for year,kind,n,date in specs:
    key=f'munich_re-{year}-{kind}';r=sources[key];p=by[(key,n)];text=normalized[(key,n)]
    online=not (kind=='interim_h1' and year in [2018,2019])
    label='Online publication date' if online else 'Publication date'
    match=re.search(re.escape(label)+r'\s*:\s*'+re.escape(date),text)
    ck('exact label and date '+key,match is not None)
    ck('issuer context '+key,'Münchener Rückversicherungs-Gesellschaft' in text)
    if kind=='annual':ck('report-year footer '+key,f'Munich Re Group Annual Report {year}' in text)
    claim_date=datetime.datetime.strptime(date,'%d %B %Y').date().isoformat()
    rows.append({'document_id':key,'report_year':year,'report_class':kind,'source_url':r['source_url'],
       'pdf':r['local_path'],'pdf_sha256':r['sha256'],'pdf_page':n,
       'printed_page':n-2 if kind=='annual' else None,
       'printed_page_note':'Numbered imprint' if kind=='annual' else 'Unnumbered imprint/board page',
       'source_label':label,'quote':match.group() if match else None,'declared_date':claim_date,
       'date_precision':'day','time_of_day':None,'timezone':None,
       'publication_channel':'online' if online else 'unspecified',
       'evidence_class':'issuer-declared publication statement in exact retained report',
       'historical_unchanged_byte_availability':'not independently established',
       'frozen_corpus_date_status':r['source_metadata']['publication_date_status'],
       'interpretation':'Retain this attributed date assertion; do not replace the source by another report or by its economic period.',
       'text_sha256':p['text_sha256'],'render_sha256':p['render_sha256'],'visual_review':'author inspected'})
ck('every selected report has exactly one primary date',set(r['document_id'] for r in rows)==set(sources) and len(rows)==len(sources))
ck('fourteen online and two unspecified publication channels',sum(r['publication_channel']=='online' for r in rows)==14)
secondary=[]
for key,n,label,date in [
('munich_re-2018-annual',190,'Editorial deadline','1 March 2019'),
('munich_re-2018-annual',190,'Print publication date','3 April 2019'),
('munich_re-2018-interim_h1',49,'Editorial deadline','3 August 2018')]:
    text=normalized[(key,n)];m=re.search(re.escape(label)+r'\s*:\s*'+re.escape(date),text)
    ck('separate date role '+key+' '+label,m is not None)
    secondary.append({'document_id':key,'pdf_page':n,'role':label,'quote':m.group() if m else None,
                      'date':datetime.datetime.strptime(date,'%d %B %Y').date().isoformat(),
                      'disposition':'Preserve separately; not the primary online/general publication date'})
excluded=normalized[('munich_re-2025-annual',87)]
a=excluded.index('On 8 January 2026');z=excluded.index('31 December 2025.',a)+len('31 December 2025.')
quote=excluded[a:z]
ck('extra search hit concerns an EU regulation','EU Commission published' in quote and 'EU Official Journal' in quote)
excluded_row={'document_id':'munich_re-2025-annual','pdf_page':87,'printed_page':85,'quote':quote,
  'disposition':'Excluded as report-publication evidence: date concerns EU Taxonomy Delegated Regulation, not this annual report.'}
save('date-evidence.json',{'primary':rows,'other_date_roles':secondary,'excluded_candidate':excluded_row,
 'scope':'Selected Munich Re 2018–2025 annual/interim reports; source declarations only; no independent historical byte verification.'})
failed=[r['name'] for r in checks if not r['passed']]
result={'checks':checks,'passed':len(checks)-len(failed),'failed':failed,'reports':len(rows),'inspected_pages':len(pages),
 'online_dates':14,'unspecified_channel_dates':2,'other_date_roles':3,'excluded_candidates':1,
 'wall_seconds':time.monotonic()-start,'readiness':'not_ready'}
save('source-checks.json',result)
lines=['# Munich Re declared publication dates','','| Report | Source label | Declared date | PDF page |','| --- | --- | --- | --- |']
lines += [f"| {r['document_id']} | {r['source_label']} | {r['declared_date']} | {r['pdf_page']} |" for r in rows]
(OUT/'date-register.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:result[k] for k in ['passed','failed','reports','inspected_pages','online_dates','unspecified_channel_dates']}))
raise SystemExit(bool(failed))
