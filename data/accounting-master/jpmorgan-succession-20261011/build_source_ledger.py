#!/usr/bin/env python3
"""Bind succession summaries and repair the scope of the trustee comparison."""
import hashlib,json,re,time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
SOURCES=ROOT/'data/accounting-master/jpmorgan-complete-filings-20261011/sources'
PRIOR=ROOT/'data/accounting-master/jpmorgan-default-remedies-20261011/source-ledger.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def norm(s): return ' '.join(s.split())
def tight(s): return re.sub(r'\s+','',s).replace('’',"'").replace('“','"').replace('”','"')
def span(text,a,b):
    while text[a].isspace(): a+=1
    while text[b-1].isspace(): b-=1
    q=text[a:b]
    return {'start_char':a,'end_char_exclusive':b,'start_line':text.count('\n',0,a)+1,'end_line':text.count('\n',0,b-1)+1,'first_pdf_page':text.count('\f',0,a)+1,'last_pdf_page':text.count('\f',0,b-1)+1,'quote':q,'quote_sha256':digest(q)}
def main():
    started=time.monotonic(); old=json.loads(PRIOR.read_text()); records=[];checks=[]
    def ck(label,ok):checks.append({'check':label,'passed':bool(ok)})
    for y in range(2022,2026):
        pdf=SOURCES/f'jpmorgan-{y}-10k.pdf';txt=SOURCES/f'jpmorgan-{y}-10k.txt';t=txt.read_text()
        p=next(r for r in old['records'] if r['filing_year']==y)
        ck(f'{y}: inherited source bytes',sha(pdf)==p['source_pdf_sha256'] and sha(txt)==p['source_text_sha256'])
        default=t.rfind('Events of Default and Waivers');a=t.find('Consolidations, Mergers, Sales and Transfers of Assets',default)
        transfer=t.find('Any transfer of material assets of the Guarantor',a)
        protection=t.find('There are no covenants or other provisions',transfer)
        e=min(v for v in [t.find(k,protection) for k in ['JPMorgan Chase Guarantee','JPMorganChase Guarantee']] if v>=0)
        tail=t.find('Concerning the Trustee, Paying Agent, Registrar and Transfer Agent',e);tail_end=t.find('Governing Law and Judgments',tail)
        ck(f'{y}: section order',default<a<transfer<protection<e<tail<tail_end)
        spans={'conditions':span(t,a,transfer),'resolution_transfer':span(t,transfer,protection),'change_control_limits':span(t,protection,e),'trustee_tail':span(t,tail,tail_end)}
        scope=p['spans']['series_scope'];spans['series_scope']=scope
        full=span(t,a,e)
        with fitz.open(pdf) as d:
            for key,s in spans.items():
                ck(f'{y}/{key}: exact quote bytes',t[s['start_char']:s['end_char_exclusive']]==s['quote'] and digest(s['quote'])==s['quote_sha256'])
                pages=tight(' '.join(d[i-1].get_text() for i in range(s['first_pdf_page'],s['last_pdf_page']+1)))
                ck(f'{y}/{key}: complete PDF span witness',tight(s['quote']) in pages)
        n={k:norm(s['quote']) for k,s in spans.items()}
        c=n['conditions']
        issuer=c[c.index('with respect to the Issuer:'):c.index('with respect to the Guarantor:')]
        guarantor=c[c.index('with respect to the Guarantor:'):]
        ck(f'{y}: issuer successor conditions',all(s in issuer for s in ['continuing company','United States corporation or limited liability company','expressly assumes','payment of the principal','covenants and conditions','no Event of Default','notice or lapse of time or both','immediately after']))
        ck(f'{y}: guarantor successor conditions',all(s in guarantor for s in ['continuing corporation','United States corporation','full and unconditional guarantee','covenants and conditions','no Event of Default','notice or lapse of time or both','immediately after']) and 'limited liability company' not in guarantor)
        ck(f'{y}: no invented substantial-all threshold','all or substantially all' in c)
        ck(f'{y}: specified resolution transfer',all(s in n['resolution_transfer'] for s in ['material assets','directly or indirectly','Title 11','Title II','other applicable federal or state','will be deemed','all or substantially all']))
        ck(f'{y}: change-control protection qualified',all(s in n['change_control_limits'] for s in ['no covenants or other provisions','additional protection','recapitalization','change of control','highly leveraged','would apply only if','specific protections','put right or increased interest','applicable prospectus supplement']))
        ck(f'{y}: general terms only may apply','may apply' in n['series_scope'])
        ck(f'{y}: conflict paragraph location','conflicting interest' in n['trustee_tail'] if y==2022 else 'conflicting interest' not in n['trustee_tail'])
        ck(f'{y}: corresponding earlier default-section location',('trustee_conflict' in p['spans'])==(y!=2022))
        if y==2022:
            ck('2022: later trustee paragraph substance',all(s in n['trustee_tail'] for s in ['actual or potential event of default','may be required to resign','successor trustee','notice','specific period of time']))
        cleaned=norm(re.sub(r'(?m)^\s*(?:a|b|i|ii)\.\s+','',full['quote']))
        records.append({'filing_year':y,'source_pdf':str(pdf.relative_to(ROOT)),'source_pdf_sha256':sha(pdf),'source_text':str(txt.relative_to(ROOT)),'source_text_sha256':sha(txt),'source_role':'10-K reported general-terms summary, original/supplements uninspected','spans':spans,'complete_succession_body':full,'list_label_normalized_sha256':digest(cleaned),'list_label_normalized_body':cleaned,'trustee_conflict_location':'later trustee section' if y==2022 else 'earlier default/waiver section','previous_default_record':{'ledger':str(PRIOR.relative_to(ROOT)),'filing_year':y,'trustee_span_sha256':p['spans'].get('trustee_conflict',{}).get('quote_sha256')}})
    ck('four succession bodies match after specified label/whitespace normalization',len({r['list_label_normalized_sha256'] for r in records})==1)
    browser=json.loads((OUT/'browser-inspection.json').read_text())
    ck('unsupported original-exhibit hypothesis excluded',browser['verification_status']=='UNSUPPORTED_ORIGINAL_TEXT_READING' and browser['admitted_original_findings']==[])
    pdf=ROOT/'docs/design/proposal/manuscript-jpmorgan-defaults-20261011/accounting-product-proposal.pdf'
    ck('Version 2.30 remains frozen',sha(pdf)=='253563e012fc77a9043caf518ac684f9de511b1a534c0983094601ee20244c80')
    result={'recorded_at':'2026-10-11','plan':'docs/plans/accounting-jpmorgan-succession-20261011.md','records':records,'normalization':'Remove only line-leading a./b./i./ii. list markers and collapse whitespace; preserve full original bodies separately.','context_repair':'2022 trustee-conflict wording is present under the later trustee heading, despite absence from the previously selected default/modification body. Later filings place related wording earlier; exact full text is retained.','original_source_status':'Not verified from inspectable returned original text; local ordinary/trusted routes are denial pages; no original clauses admitted.','checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'readiness':'not_ready'}
    (OUT/'source-ledger.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'check-run.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-succession-20261011/build_source_ledger.py','wall_seconds':time.monotonic()-started},indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'failed':result['failed'],'spans':sum(len(r['spans']) for r in records),'failures':[x['check'] for x in checks if not x['passed']]}))
    raise SystemExit(bool(result['failed']))
if __name__=='__main__':main()
