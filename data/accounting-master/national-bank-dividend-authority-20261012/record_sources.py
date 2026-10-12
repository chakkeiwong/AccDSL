"""Bind retained responses and located conditions; do not apply a bank rule."""
import datetime
import hashlib
import json
import re
import time
from pathlib import Path
from lxml import etree

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
S=OUT/'sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
assert not (OUT/'source-ledger.json').exists()
start=time.monotonic()
ecfr='https://www.ecfr.gov/'
gov='https://www.govinfo.gov/'
api=ecfr+'api/versioner/v1/full/2026-01-01/title-12.xml'
usc='https://uscode.house.gov/'
attempts=[
('ecfr-5-64','body',ecfr+'current/title-12/chapter-I/part-5/subpart-E/section-5.64',200,10596,5.114085,'https://unblock.federalregister.gov/','access page; no rule text',False),
('uscode-60-trusted','body',usc+'view.xhtml?req=granuleid:USC-prelim-title12-section60&num=0&edition=prelim',500,75,1.065336,None,'internal server error after required trusted DNS retry',False),
('ecfr-api-docs','body',ecfr+'developers/documentation/api/v1',200,10596,1.848947,'https://unblock.federalregister.gov/','access page; no API documentation',False),
('govinfo-usc2025-60','pdf',gov+'content/pkg/USCODE-2025-title12/pdf/USCODE-2025-title12-chap2-subchapIV-sec60.pdf',200,44172,1.884926,gov+'error','HTML Page Not Found; initial subchapter guess wrong',False),
('ecfr-20260101-part5E','xml',api+'?part=5&subpart=E',406,171,0.840536,None,'API explicitly requires response compression',False),
('govinfo-usc2024-60','pdf',gov+'content/pkg/USCODE-2024-title12/pdf/USCODE-2024-title12-chap2-subchapIV-sec60.pdf',200,44172,1.743087,gov+'error','HTML Page Not Found; same wrong subchapter guess, different edition',False),
('ecfr-20260101-part5E-compressed','xml',api+'?part=5&subpart=E',200,2627,2.142779,None,'complete Subpart E XML; requested-date response',True),
('ecfr-20260101-5-46','xml',api+'?part=5&section=5.46',200,3027,0.689944,None,'complete referenced section XML',True),
('ecfr-20260101-part6','xml',api+'?part=6',200,9224,1.139286,None,'complete Part 6 XML; selected dependency reading only',True),
('uscode-title12-index','body',usc+'browse/prelim@title12&edition=prelim',500,75,6.528399,None,'internal server error; no hierarchy confirmation',True),
('govinfo-usc2024-60-corrected','pdf',gov+'content/pkg/USCODE-2024-title12/pdf/USCODE-2024-title12-chap2-subchapII-sec60.pdf',200,147991,2.347780,None,'official 2024 edition PDF; sections 59 and 60 inspected',True),
('govinfo-cfr2025-5-64','pdf',gov+'content/pkg/CFR-2025-title12-vol1/pdf/CFR-2025-title12-vol1-sec5-64.pdf',200,155174,2.480548,None,'official 1-1-25 CFR edition; sections 5.60 through 5.66 inspected',True),
('govinfo-usc2024-56','pdf',gov+'content/pkg/USCODE-2024-title12/pdf/USCODE-2024-title12-chap2-subchapII-sec56.pdf',200,147650,4.208426,None,'official 2024 edition PDF; section 56 and its amendment note inspected',True),
('fr-20251201-toc','body',gov+'content/pkg/FR-2025-12-01/html/FR-2025-12-01.htm',200,9032,2.027889,gov+'error','guessed issue index returned Page Not Found',True),
('fr90-55288','pdf',gov+'link/fr/90/55288?link-type=pdf',200,1027245,6.260087,gov+'content/pkg/FR-2025-12-01/pdf/2025-21626.pdf#page=41','complete 45-page final rule; effective-date and OCC amendment passages inspected',True)]
receipts=[json.loads((S/'uscode-60-receipt.json').read_text())]
for key,ext,url,http,size,seconds,final,disposition,compressed in attempts:
    body=S/f'{key}.{ext}';head=S/f'{key}.headers'
    assert body.exists() and head.exists()
    receipts.append({'id':key,'url':url,'final_url':final or url,'http_code':http,'exit_code':0,
        'transfer_bytes_from_curl':size,'decompressed_body_bytes':body.stat().st_size,
        'elapsed_seconds_from_curl':seconds,'body':str(body.relative_to(ROOT)),'body_sha256':sha(body),
        'headers':str(head.relative_to(ROOT)),'headers_sha256':sha(head),
        'compression_requested':compressed,
        'body_mtime_utc':datetime.datetime.fromtimestamp(body.stat().st_mtime,datetime.timezone.utc).isoformat(),
        'time_scope':'Local file modification time and retained response headers; not a legal effective or publication timestamp.',
        'execution':'trusted except initial eCFR page; initial House sandbox failure retained separately',
        'disposition':disposition})
save('access-receipts.json',{'attempts':receipts,'attempt_count':len(receipts),
    'distinct_urls':len({r['url'] for r in receipts}),
    'curl_options':'--location --connect-timeout 10 --max-time 25; later requests --compressed; bodies/headers preserved.',
    'provenance':'HTTP/transfer/elapsed values transcribed from bounded tool outputs; no invented request start timestamps.'})

sections=[]
for filename,nums in [('ecfr-20260101-part5E-compressed.xml',None),('ecfr-20260101-5-46.xml',None),('ecfr-20260101-part6.xml',['6.1','6.2','6.3','6.4'])]:
    file=S/filename;tree=etree.parse(str(file))
    nodes=tree.xpath('self::DIV8|//DIV8')
    for node in nodes:
        n=node.get('N')
        if nums and n not in nums:continue
        paragraphs=[{'element':c.tag,'attributes':dict(c.attrib),'text':' '.join(''.join(c.itertext()).split())} for c in node]
        text='\n'.join(x['text'] for x in paragraphs)+'\n'
        p=S/f'ecfr-section-{n}.txt';p.write_text(text)
        sections.append({'section':n,'source':str(file.relative_to(ROOT)),'source_sha256':sha(file),
            'xpath':f'//DIV8[@N="{n}"]','requested_date':'2026-01-01','normalized_text':str(p.relative_to(ROOT)),
            'normalized_text_sha256':sha(p),'paragraphs':paragraphs})
by={s['section']:s for s in sections}
conditions=[]
def condition(key,section,needle,meaning,inputs,unresolved):
    paras=by[section]['paragraphs'];found=[(i,p['text']) for i,p in enumerate(paras) if needle in p['text']]
    assert len(found)==1,(key,found)
    i,quote=found[0]
    conditions.append({'id':key,'section':section,'paragraph_index':i,'quote':quote,
        'interpretation':meaning,'required_inputs':inputs,'unresolved':unresolved})
condition('stock-dividend-scope','5.60','do not apply to dividends paid in stock',
    'The earnings restriction excludes dividends paid in bank stock; the subpart otherwise addresses all national-bank dividends.',
    ['dividend form','bank charter'],'Do not remove other restrictions merely because the earnings section has an exception.')
condition('retained-net-income','5.61','Retained net income means',
    'Net income less all dividends declared in the specified period. Cash payments alone do not define this amount.',
    ['bank-specific net income','all dividends declared by period'],'Accounting/regulatory input reconciliation not supplied by parent Note 33.')
condition('declaration-clock','5.62','date a dividend is declared',
    'Compliance under this subpart uses declaration date.', ['declaration date','payment date separately'],
    'A payment date or annual filing date cannot silently replace this clock.')
condition('capital-and-undivided-profits','5.63','General limitation.',
    'Permanent capital withdrawal and undivided-profit restrictions apply subject to the stated capital-reduction exception.',
    ['permanent capital','undivided profits','approved reduction when applicable'],'Section 59 and 5.46 procedures apply to the exception; no bank-specific approval inspected.')
condition('preferred-stock-capital','5.63','Preferred stock.',
    'Preferred dividends have the stated section-56 exception; insufficient undivided profits makes the proposal a capital reduction.',
    ['stock class','undivided profits','capital-reduction approval'],'Not an unrestricted preferred-dividend exemption.')
condition('current-calendar-year','5.64','(a) Definitions.',
    'The current year is the calendar year of actual or proposed declaration.', ['declaration calendar year'],'Bank fiscal-period labels do not replace the definition.')
condition('earnings-general-rule','5.64','(c) Earnings limitations',
    'Without the specified OCC approval, all current-year declared common/preferred dividends including the proposal face the stated income/retained-income/transfer restriction.',
    ['current-year net income to date','current-year total declared dividends','prior two retained net incomes','OCC-required transfers','preferred-retirement-fund transfers'],
    'The prior-loss adjustments and other subpart restrictions remain required; no amount computed.')
condition('older-year-offset-order','5.64','(2) Excess dividends in prior periods.',
    'The specified excess-dividend cases can need years minus three and minus four and the stated offset order.',
    ['net incomes and declarations for four preceding years','origin of retained loss','offset allocation'],
    'A three-year-only formula or zero-floor substitution is not established by the rule.')
condition('unoffset-reduction','5.64','(ii) If the bank',
    'Uncovered excess reduces current available retained net income under the stated calculation.', ['remaining unoffset excess'],
    'Do not reuse the same retained-income capacity twice across allocations.')
condition('loss-origin-limit','5.64','(iii) The calculation',
    'The adjustment only addresses retained losses caused by dividends exceeding one year income; it excludes other current earnings deficits.',
    ['cause of retained loss'],'A generic negative retained-income adjustment is unsupported.')
condition('occ-prior-approval','5.64','(3) Prior approval required.',
    'Amounts beyond the stated earnings limitation require the specified OCC approval and request.',
    ['proposed amount','approval evidence'],'Approval under this section does not erase other restrictions.')
condition('post-dividend-capital','5.65','Notwithstanding any other provision',
    'The bank may not declare or pay a dividend that would make it undercapitalized under Part 6.',
    ['post-dividend capital measures','Part 6 classification inputs'],'Part 3 definitions, institution-specific application and supervisory actions are not closed.')
condition('property-dividends','5.66','In addition to cash dividends',
    'Property dividends need OCC approval and use actual current property value with the stated book adjustment.',
    ['property current value','book value','approval','declaration event'],'Book value alone is not the dividend amount specified here.')
condition('permanent-capital-definition','5.46','(4) Permanent capital means',
    'Permanent capital equals capital stock plus capital surplus as defined in the same section.',
    ['capital stock','capital surplus components'],'This is not an automatic synonym for reported common equity or Tier 1 capital.')
condition('other-supervisory-authority','6.1','(d) Other supervisory authority.',
    'Prompt-corrective-action classifications do not limit other OCC supervisory authority.',
    ['applicable supervisory orders and conditions'],'No absence-of-order evidence established.')
save('source-ledger.json',{'sections':sections,'conditions':conditions,
    'temporal_case':{'api_requested_date':'2026-01-01','annual_cfr_edition':'1-1-25','uscode_edition':'2024',
        'fr_publication':'2025-12-01','fr_start_page':55248,'fr_amending_page':55288,
        'fr_effective_date':'2026-04-01','fr_optional_adoption_date':'2026-01-01',
        'issuer_report':'2025 Form 10-K printed 91/physical 93 reports Firm elected early adoption effective 1 January 2026',
        'source_boundary':'Issuer report is later evidence of the election; it is not proof the election was publicly known on 1 January.',
        'counterexample':'A date-only lookup retaining the pre-effective 6% well-capitalized SLR criterion does not resolve the reported early-adoption case.',
        'nonclaim':'Neither the issuer-reported 30.1 billion capacity nor a capital classification is recomputed.'},
    'open_dependencies':['complete relevant amendment and applicability chain','Part 3 regulatory capital definitions and distribution limits',
        'statutory dependencies beyond inspected 56/59/60','institution-specific approvals, orders and input data',
        'reported group election versus entity-specific implementation evidence','historical public availability of election evidence',
        'complete offset allocation design before numerical implementation'],
    'scope':'Selected primary legal texts and exact input requirements; not legal compliance, current-through-2026 certification or a bank capacity engine.'})
save('preparation-run.json',{'command':['python3',str(Path(__file__).relative_to(ROOT))],'wall_seconds':time.monotonic()-start,
    'environment':'system Python; lxml; CPU document parsing; no stochastic process or GPU',
    'notes':'Full PDFs preserved even where selected sections/pages only are inspected; sort=True PDF text is retained as an interleaving diagnostic, not quotation authority.'})
print(json.dumps({'attempts':len(receipts),'distinct_urls':len({r['url'] for r in receipts}),'selected_sections':len(sections),'condition_records':len(conditions)}))
