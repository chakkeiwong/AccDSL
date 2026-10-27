#!/usr/bin/env python3
"""Verify the exact V2.31 correction/insertion without rewriting prior evidence."""
import hashlib,json,re,time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-jpmorgan-defaults-20261011'
CAND=ROOT/'docs/design/proposal/manuscript-jpmorgan-succession-20261011'
SOURCE=ROOT/'data/accounting-master/jpmorgan-succession-20261011'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    start=time.monotonic();checks=[]
    def ck(k,v):checks.append({'check':k,'passed':bool(v)})
    def files(p):return {q.relative_to(p) for q in p.rglob('*') if q.is_file() and q.suffix in {'.tex','.bib','.lark'}}
    ck('V2.30 protected',sha(BASE/'accounting-product-proposal.pdf')=='253563e012fc77a9043caf518ac684f9de511b1a534c0983094601ee20244c80')
    old,new=files(BASE),files(CAND);ck('source inventory preserved',old==new)
    changed=[];delta=''
    correction_before='''voting populations, not a generic creditor vote. The 2022 summary lacks a
trustee-conflict paragraph present in 2023--2025; that disclosure difference
alone does not establish a contract amendment. The original Indenture and'''
    correction_after='''voting populations, not a generic creditor vote. The 2022 default-and-waiver
subsection omits the trustee-conflict paragraph that the 2023--2025 versions
place there. The 2022 filing discusses a potential default, trustee conflict
and possible resignation later under its trustee heading. This change in
placement does not establish a contract amendment. The original Indenture and'''
    for rel in sorted(old):
        a=(BASE/rel).read_text();b=(CAND/rel).read_text()
        if a!=b:changed.append(str(rel))
        if str(rel)=='accounting-product-proposal.tex':
            ck('title change only',b==a.replace('Version 2.30','Version 2.31'))
        elif str(rel)=='chapters/15-banking.tex':
            s=b.index('Reported succession terms');e=b.index('Loan origination can debit loans',s);delta=b[s:e]
            ck('exact corrected source-context passage',correction_before in a and correction_after in b and correction_before not in b)
            reconstructed=(b[:s].removesuffix('\\newpage\n')+b[e:]).replace(correction_after,correction_before)
            ck('all remaining bank source preserved',reconstructed==a)
            ck('substantive succession insertion',len(delta)>1000)
        else:ck('unchanged '+str(rel),a==b)
    ck('only title and bank chapter changed',set(changed)=={'accounting-product-proposal.tex','chapters/15-banking.tex'})
    for term in ['general Series~A summary','corporation or limited liability company','full guarantee','continuing issuer or guarantor','no default','notice or time','immediately after','material assets','do not define a numeric percentage','supplement may provide','Succession itself does not prove repayment','accounting derecognition','reported terms that may apply']:
        ck('required insertion qualification '+term,term in delta)
    before='\n'.join((BASE/p).read_text() for p in sorted(old) if p.suffix=='.tex')
    after='\n'.join((CAND/p).read_text() for p in sorted(new) if p.suffix=='.tex')
    pattern=re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
    displays=lambda t:[m.group() for m in pattern.finditer(t)]
    ck('48 displayed equations preserved',displays(before)==displays(after) and len(displays(after))==48)
    labels=re.findall(r'\\label\{([^{}]+)\}',after);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}',after)
    ck('unique labels',len(labels)==len(set(labels)));ck('references resolve',set(refs)<=set(labels))
    bib=(CAND/'references.bib').read_text();keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib))
    cited={k.strip() for g in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}',after) for k in g.split(',')}
    ck('71 bibliography entries preserved',len(keys)==71 and bib==(BASE/'references.bib').read_text());ck('citations resolve',cited<=keys)
    pdf=CAND/'accounting-product-proposal.pdf'
    with fitz.open(pdf) as d:
        count=len(d);p117=' '.join(d[116].get_text().split());p118=' '.join(d[117].get_text().split())
        ck('correction on page 117',all(x in p117 for x in ['2022 default-and-waiver','later under its trustee heading']))
        ck('new passage on page 118',all(x in p118 for x in ['Reported succession terms','limited liability company','accounting derecognition','terms that may apply']))
        ck('171-page layout diagnostic',count==171)
    log=(CAND/'accounting-product-proposal.log').read_text()
    bad=[l for l in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning',l,re.I) and 'Package: infwarerr' not in l]
    ck('clean final TeX log',not bad);ck('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(CAND/'accounting-product-proposal.blg').read_text(),re.I))
    sr=json.loads((SOURCE/'run-manifest.json').read_text());sl=json.loads((SOURCE/'source-ledger.json').read_text())
    ck('84/0 source checks and 20 spans',sl['passed']==84 and sl['failed']==0 and sum(len(x['spans']) for x in sl['records'])==20)
    ck('source manifest hashes intact',all(sha(ROOT/p)==h for p,h in sr['artifact_hashes'].items()))
    ck('four source PDFs/texts intact',all(sha(ROOT/x['source_pdf'])==x['source_pdf_sha256'] and sha(ROOT/x['source_text'])==x['source_text_sha256'] for x in sl['records']))
    browser=json.loads((SOURCE/'browser-inspection.json').read_text());ck('unsupported original clause claims excluded',browser['verification_status']=='UNSUPPORTED_ORIGINAL_TEXT_READING' and not browser['admitted_original_findings'])
    rm=json.loads((OUT/'render-manifest.json').read_text());ck('final render PDF identity',rm['pdf_sha256']==sha(pdf))
    ck('eleven ordered render pages',[x['pdf_page_index'] for x in rm['rendered_pages']]==list(range(114,125)))
    ck('render image hashes intact',all(sha(ROOT/x['image'])==x['sha256'] for x in rm['rendered_pages']))
    baseline=json.loads((OUT/'baseline.json').read_text());ck('four prior controls preserved',len(baseline['pointer_relocations'])==4 and all(sha(ROOT/x['preserved_path'])==x['sha256'] for x in baseline['pointer_relocations']))
    report={'recorded_at':'2026-10-11','plan':'docs/plans/accounting-jpmorgan-succession-integration-20261011.md','baseline_pdf':baseline['baseline_pdf'],'candidate_pdf':{'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'pages':count},'changed_sources':changed,'documented_correction':{'before':correction_before,'after':correction_after,'source':'2022 10-K PDF page 330'},'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'readiness':'not_ready'}
    (OUT/'manuscript-checks.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'check-run.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 python3 '+str(Path(__file__).relative_to(ROOT)),'wall_seconds':time.monotonic()-start},indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'failed':report['failed'],'failures':[x['check'] for x in checks if not x['passed']],'pages':count}));raise SystemExit(bool(report['failed']))
if __name__=='__main__':main()
