#!/usr/bin/env python3
"""Verify the bounded Version 2.30 delta and retained source evidence."""
import hashlib, json, re, time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/design/proposal/manuscript-jpmorgan-balance-20261011'
CAND=ROOT/'docs/design/proposal/manuscript-jpmorgan-defaults-20261011'
SOURCE=ROOT/'data/accounting-master/jpmorgan-default-remedies-20261011'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    began=time.monotonic(); checks=[]; slash=chr(92)
    def ck(label,yes): checks.append({'check':label,'passed':bool(yes)})
    def files(p): return {q.relative_to(p) for q in p.rglob('*') if q.is_file() and q.suffix in {'.tex','.bib','.lark'}}
    ck('protected Version 2.29 PDF',sha(BASE/'accounting-product-proposal.pdf')=='aebe128cada22e57907e9651a43cc37b4031f2af34d951cc0bcf48dc64aa406b')
    old,new=files(BASE),files(CAND)
    ck('same source inventory',old==new)
    changed=[]; addition=''
    for rel in sorted(old):
        a=(BASE/rel).read_text(); b=(CAND/rel).read_text()
        if a!=b: changed.append(str(rel))
        if str(rel)=='accounting-product-proposal.tex':
            ck('main TeX changes title only',b==a.replace('Version 2.29','Version 2.30'))
        elif str(rel)=='chapters/15-banking.tex':
            s=b.index('The filings then describe general Series~A terms'); e=b.index('Loan origination can debit loans',s)
            addition=b[s:e]
            rebuilt=b[:s].removesuffix(slash+'newpage'+chr(10))+b[e:]
            ck('complete old bank prose retained',rebuilt==a)
            ck('substantive explanatory delta',len(addition)>1000)
        else: ck('unchanged source '+str(rel),a==b)
    ck('only title and banking change',set(changed)=={'accounting-product-proposal.tex','chapters/15-banking.tex'})
    for term in ['may apply','In their summary','30 days','when due','90-day','aggregate principal','by written notice','continuing','automatically','Guarantor insolvency','payment default by the guarantor','60 days','indemnity','inconsistent majority','each holder','without holder consent','Section~8.01','Section~8.02','each affected outstanding series','repurchase rights','voting populations','does not establish a contract amendment','remain uninspected']:
        ck('new qualification '+term,term in addition)
    a=chr(10).join((BASE/p).read_text() for p in sorted(old) if p.suffix=='.tex')
    b=chr(10).join((CAND/p).read_text() for p in sorted(new) if p.suffix=='.tex')
    pattern=re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
    before=[m.group() for m in pattern.finditer(a)]; after=[m.group() for m in pattern.finditer(b)]
    ck('48 unchanged displayed equations',before==after and len(after)==48)
    labels=re.findall(r'\\label\{([^{}]+)\}',b)
    refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}',b)
    ck('unique labels',len(labels)==len(set(labels)))
    ck('references resolve',set(refs)<=set(labels))
    bibliography=(CAND/'references.bib').read_text()
    keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',bibliography))
    cited={k.strip() for g in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}',b) for k in g.split(',')}
    ck('71-entry bibliography unchanged',bibliography==(BASE/'references.bib').read_text() and len(keys)==71)
    ck('citations resolve',cited<=keys)
    pdf=CAND/'accounting-product-proposal.pdf'
    with fitz.open(pdf) as doc:
        pages=len(doc); passage=' '.join(doc[116].get_text().split())
        ck('new passage stays on PDF page 117',all(x in passage for x in ['30 days','Guarantor insolvency','Section 8.01','remain uninspected']))
        ck('170 page diagnostic',pages==170)
    log=(CAND/'accounting-product-proposal.log').read_text()
    bad=[l for l in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning|undefined citation|undefined reference',l,re.I) and 'Package: infwarerr' not in l]
    ck('clean TeX log',not bad)
    ck('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(CAND/'accounting-product-proposal.blg').read_text(),re.I))
    source=json.loads((SOURCE/'source-ledger.json').read_text())
    ck('175 source checks and 51 spans',source['passed']==175 and source['failed']==0 and sum(len(r['spans']) for r in source['records'])==51)
    run=json.loads((SOURCE/'run-manifest.json').read_text())
    ck('source artifacts intact',all(sha(ROOT/p)==h for p,h in run['artifact_hashes'].items()))
    ck('all source PDF and text bytes intact',all(sha(ROOT/r['source_pdf'])==r['source_pdf_sha256'] and sha(ROOT/r['source_text'])==r['source_text_sha256'] for r in source['records']))
    render=json.loads((OUT/'render-manifest.json').read_text())
    ck('final PDF render identity',render['pdf_sha256']==sha(pdf))
    ck('ten ordered render indices',[x['pdf_page_index'] for x in render['rendered_pages']]==list(range(114,124)))
    ck('render bytes intact',all(sha(ROOT/x['image'])==x['sha256'] for x in render['rendered_pages']))
    baseline=json.loads((OUT/'baseline.json').read_text())
    ck('four prior controls retained',len(baseline['pointer_relocations'])==4 and all(sha(ROOT/x['preserved_path'])==x['sha256'] for x in baseline['pointer_relocations']))
    report={'recorded_at':'2026-10-11','plan':'docs/plans/accounting-jpmorgan-default-remedy-integration-20261011.md','baseline_pdf':baseline['baseline_pdf'],'candidate_pdf':{'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'pages':pages},'changed_sources':changed,'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'readiness':'not_ready'}
    (OUT/'manuscript-checks.json').write_text(json.dumps(report,indent=2)+chr(10))
    (OUT/'check-run.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 python3 '+str(Path(__file__).relative_to(ROOT)),'wall_seconds':time.monotonic()-began},indent=2)+chr(10))
    print(json.dumps({'passed':report['passed'],'failed':report['failed'],'failures':[x['check'] for x in checks if not x['passed']],'candidate_pdf':report['candidate_pdf']}))
    raise SystemExit(bool(report['failed']))
if __name__=='__main__': main()
