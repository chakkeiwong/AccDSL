"""Bind official discovery paths, source editions and exact technical anchors."""
import hashlib
import json
import re
import time
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
start=time.monotonic();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:' '.join(s.split())
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
requests=[
 ('search108','https://standards.aasb.gov.au/search?keys=AASB%20108','search108.html',4.021051),
 ('search13','https://standards.aasb.gov.au/search?keys=AASB%2013','search13.html',3.598871),
 ('aasb108-page','https://standards.aasb.gov.au/aasb-108-mar-2021','aasb108-page.html',1.264078),
 ('aasb13-page','https://standards.aasb.gov.au/aasb-13-dec-2022','aasb13-page.html',1.205913),
 ('aasb108','https://www.aasb.gov.au/admin/file/content105/c9/AASB108_08-15_COMPmar21_01-23.pdf','aasb108.pdf',5.481099),
 ('search13-2023','https://standards.aasb.gov.au/search?keys=AASB%2013&field_commencing_date=01-01-2023&field_ending_date=31-12-2023','search13-2023.html',3.451427),
 ('aasb13-2023-page','https://standards.aasb.gov.au/aasb-13-mar-2020','aasb13-2023-page.html',1.338271),
 ('aasb13','https://www.aasb.gov.au/admin/file/content105/c9/AASB13_08-15_COMPmar20_07-21.pdf','aasb13.pdf',3.545945),
]
access=[]
for key,url,name,seconds in requests:
    h=OUT/'acquisition'/(key+'.headers');p=OUT/'acquisition'/name
    status=int(re.findall(r'^HTTP/\S+\s+(\d+)',h.read_text(),re.M)[-1]);assert status==200
    access.append({'id':key,'url':url,'status':status,'path':str(p.relative_to(ROOT)),
        'sha256':sha(p),'bytes':p.stat().st_size,'wall_seconds':seconds,
        'command':['curl','--location','--silent','--show-error','--max-time','40',
        '--max-filesize','12000000','--dump-header',str(h.relative_to(ROOT)),
        '--output',str(p.relative_to(ROOT)),'--write-out',
        'http=%{http_code} bytes=%{size_download} seconds=%{time_total} url=%{url_effective}\n',url]})
save('acquisition.json',access)
links=[]
for parent,target in [('search108','aasb108-page'),('search13','aasb13-page'),
                      ('aasb108-page','aasb108'),('search13-2023','aasb13-2023-page'),('aasb13-2023-page','aasb13')]:
    a=next(r for r in access if r['id']==parent);b=next(r for r in access if r['id']==target)
    soup=BeautifulSoup((ROOT/a['path']).read_bytes(),'html.parser')
    found=[x for x in soup.select('a[href]') if x['href']==b['url']];assert found,(parent,target)
    links.append({'parent':parent,'target':target,'url':b['url'],'link_text':found[0].get_text(' ',strip=True)})
save('discovery-links.json',links)

specs=[
 ('108-5-effort','aasb108',6,'Applying a requirement is impracticable when the entity cannot apply it after making every reasonable effort to do so.'),
 ('108-5-intent','aasb108',6,'requires assumptions about what management’s intent would have been in that period'),
 ('108-5-information','aasb108',6,'would have been available when the financial statements for that prior period were authorised for issue from other information.'),
 ('108-19-priority','aasb108',8,'in accordance with the specific transitional provisions, if any, in that Australian Accounting Standard;'),
 ('108-34-estimates','aasb108',10,'By its nature, a change in an accounting estimate does not relate to prior periods and is not the correction of an error.'),
 ('108-51-later-estimates','aasb108',12,'Estimation is inherently subjective, and estimates may be developed after the reporting period.'),
 ('108-52-information','aasb108',12,'would have been available when the financial statements for that prior period were authorised for issue'),
 ('108-53-hindsight','aasb108',12,'Hindsight should not be used when applying a new accounting policy to, or correcting amounts for, a prior period'),
 ('108-53-continuation','aasb108',13,'does not prevent reliable adjustment or correction of the comparative information.'),
 ('13-2-target','aasb13',6,'Fair value is a market-based measurement, not an entity-specific measurement.'),
 ('13-9-definition','aasb13',7,'the price that would be received to sell an asset or paid to transfer a liability in an orderly transaction between market participants at the measurement date.'),
 ('13-14-unit','aasb13',7,'The unit of account for the asset or liability shall be determined in accordance with the Standard that requires or permits the fair value measurement'),
 ('13-19-market','aasb13',7,'The entity must have access to the principal (or most advantageous) market at the measurement date.'),
 ('13-22-participants','aasb13',8,'using the assumptions that market participants would use when pricing the asset or liability'),
 ('13-34-transfer','aasb13',9,'A liability would remain outstanding and the market participant transferee would be required to fulfil the obligation.'),
 ('13-42-risk','aasb13',11,'Non-performance risk is assumed to be the same before and after the transfer of the liability.'),
 ('13-47-demand','aasb13',11,'not less than the amount payable on demand, discounted from the first date that the amount could be required to be paid.'),
 ('13-52-scope','aasb13',12,'The exception in paragraph 48 applies only to financial assets, financial liabilities and other contracts within the scope of AASB 9'),
 ('13-61-technique','aasb13',13,'valuation techniques that are appropriate in the circumstances and for which sufficient data are available to measure fair value'),
 ('13-74-hierarchy','aasb13',14,'the fair value hierarchy prioritises the inputs to valuation techniques, not the valuation techniques used to measure fair value.'),
 ('13-87-unobservable','aasb13',16,'unobservable inputs shall reflect the assumptions that market participants would use when pricing the asset or liability, including assumptions about risk.'),
 ('13-89-own-data','aasb13',16,'an entity may begin with its own data, but it shall adjust those data if reasonably available information indicates that other market participants would use different data'),
 ('13-B14-risk','aasb13',24,'To avoid double-counting or omitting the effects of risk factors, discount rates should reflect assumptions that are consistent with those inherent in the cash flows.'),
 ('13-B16-difficulty','aasb13',25,'the degree of difficulty alone is not a sufficient reason to exclude a risk premium.'),
 ('13-B31-compensation','aasb13',27,'the compensation that a market participant would require for taking on the obligation.'),
 ('13-B33-liability','aasb13',28,'by adjusting the rate used to discount the future cash flows to their present values (ie as a reduction in the discount rate).'),
 ('13-B33-once','aasb13',28,'An entity shall ensure that it does not double-count or omit adjustments for risk.'),
 ('13-B43-orderly','aasb13',31,'it is not appropriate to conclude that all transactions in that market are not orderly'),
 ('17-31-FCF','aasb17',10,'the fulfilment cash flows shall not reflect the non-performance risk of that entity'),
]
anchors=[]
for label,name,page,excerpt in specs:
    p=OUT/'text'/f'{name}-{page}.txt';s=norm(p.read_text());e=norm(excerpt)
    assert s.count(e)==1,(label,s.count(e))
    anchors.append({'id':label,'source':name,'pdf_page':page,'text_path':str(p.relative_to(ROOT)),
                    'normalized_start':s.index(e),'exact_normalized_excerpt':e})
save('source-anchors.json',anchors)
inspected={'aasb108':[1,6,12,13],'aasb13':[1,9,11,16,27,28]}
sources={}
for name in ['aasb108','aasb13','aasb17']:
    pdf=OUT/'acquisition'/(name+'.pdf') if name!='aasb17' else ROOT/'docs/design/research/standards/aasb17.pdf'
    pages=sorted(int(p.stem.split('-')[-1]) for p in (OUT/'text').glob(name+'-*.txt'))
    sources[name]={'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'read_pages':pages,
                   'inspected_renders':inspected.get(name,[])}
save('source-evidence.json',{'sources':sources,'read_page_count':sum(len(v['read_pages']) for v in sources.values()),
    'source_anchors':len(anchors),'requests':len(access),
    'text_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted((OUT/'text').glob('*.txt'))},
    'renders':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),
                'author_inspected':int(p.stem.split('-')[-1]) in inspected[p.stem.split('-')[0]],
                'pdf_sha256':sources[p.stem.split('-')[0]]['sha256']} for p in sorted((OUT/'rendered').glob('*.png'))],
    'selected_editions':{'aasb108':'Compilation 3, 31 December 2022; period starts from 1 January 2023',
                        'aasb13':'Compilation 2, 30 June 2021; period starts from 1 July 2021; official 2023 search selection'},
    'excluded_edition':'aasb13-page.html: compilation 3, 31 December 2023; period starts from 1 January 2024',
    'wall_seconds':time.monotonic()-start,'scope':'Selected method dependencies; no actual group or current amendment-chain conclusion'})
print(json.dumps({'requests':len(access),'anchors':len(anchors),'read_pages':sum(len(v['read_pages']) for v in sources.values()),'inspected_renders':10}))
