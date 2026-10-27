"""Exact Version 2.33 manuscript and source preservation checks."""
import hashlib
import json
import re
import time
from pathlib import Path

import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=ROOT/'docs/design/proposal/manuscript-bidi-dependencies-20261011'
CAND=ROOT/'docs/design/proposal/manuscript-jpmorgan-commitments-20261012'
SOURCE=ROOT/'data/accounting-master/jpmorgan-commitments-20261011'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start=time.monotonic();checks=[]
    def ck(name,ok):checks.append({'check':name,'passed':bool(ok)})
    baseline=json.loads((OUT/'baseline.json').read_text())
    ck('protected baseline PDF',sha(ROOT/baseline['baseline_pdf']['path'])==baseline['baseline_pdf']['sha256'])
    files=baseline['source_hashes'];extensions={'.tex','.bib','.lark','.md','.json'}
    ck('source inventory unchanged',set(files)=={str(p.relative_to(CAND)) for p in CAND.rglob('*') if p.is_file() and p.suffix in extensions})
    addition=(OUT/'addition.tex').read_text()
    marker='Regulatory capital is computed in a separate prudential layer with its own'
    changed=[]
    for rel,digest in sorted(files.items()):
        a=BASE/rel;b=CAND/rel;ck('baseline source intact '+rel,sha(a)==digest)
        old=a.read_text();new=b.read_text()
        if old!=new:changed.append(rel)
        if rel=='accounting-product-proposal.tex':expected=old.replace('Version 2.32','Version 2.33')
        elif rel=='chapters/15-banking.tex':
            ck('single insertion anchor',old.count(marker)==1)
            expected=old.replace(marker,addition+marker)
        else:expected=old
        ck('exact candidate content '+rel,new==expected)
    ck('only title and bank chapter changed',set(changed)=={'accounting-product-proposal.tex','chapters/15-banking.tex'})
    before='\n'.join((BASE/p).read_text() for p in sorted(files) if p.endswith('.tex'))
    after='\n'.join((CAND/p).read_text() for p in sorted(files) if p.endswith('.tex'))
    pattern=re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
    displays=lambda t:[m.group() for m in pattern.finditer(t)]
    ck('48 exact displays preserved',displays(before)==displays(after) and len(displays(after))==48)
    labels=re.findall(r'\\label\{([^{}]+)\}',after)
    refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}',after)
    ck('unique labels',len(labels)==len(set(labels)))
    ck('references resolve',set(refs)<=set(labels))
    bib=(CAND/'references.bib').read_text();keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
    cited={k.strip() for g in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}',after) for k in g.split(',')}
    ck('74 exact bibliography entries preserved',len(keys)==len(set(keys))==74 and bib==(BASE/'references.bib').read_text())
    ck('citations resolve',cited<=set(keys))
    ck('specific 2025 source citation',addition.count('jpmorgan2025tenk')>=3)
    for term in ['1,817,307','603,947','5,071','6,278','US\\$175m','US\\$441m','US\\$616m','30 December','7 January','US\\$104bn','US\\$23bn','US\\$2.2bn','not loans already owned','cannot be recovered from a commitment total','net of risk participations','operative accounting rules']:
        ck('qualified example '+term,term in ' '.join(addition.split()))
    ledger=json.loads((SOURCE/'source-ledger.json').read_text());manifest=json.loads((SOURCE/'run-manifest.json').read_text())
    ck('source unit complete',ledger['passed']==123 and ledger['failed']==0 and len(ledger['rows'])==20 and len(ledger['spans'])==16 and len(ledger['calculations'])==50)
    ck('source artifacts intact',all(sha(ROOT/p)==d for p,d in manifest['artifact_hashes'].items()))
    ck('source completion intact',json.loads((SOURCE/'completion.json').read_text())['failed']==0)
    ck('four prior controls preserved',len(baseline['pointer_relocations'])==4 and all(sha(ROOT/r['preserved_path'])==r['sha256'] for r in baseline['pointer_relocations']))
    pdf=CAND/'accounting-product-proposal.pdf'
    with fitz.open(pdf) as doc:
        pages=len(doc);insert=' '.join(doc[118].get_text().split());continued=' '.join(doc[119].get_text().split())
        ck('new table and chronology together on PDF page 119',all(s in insert for s in ['1,817,307','603,947','5,071','6,278','30 December 2025','US$104bn']))
        ck('bank method continues next page',all(s in continued for s in ['Regulatory capital','A bank’s cash','State and event order']))
        ck('173-page layout diagnostic',pages==173)
    texlog=(CAND/'accounting-product-proposal.log').read_text()
    warnings=[line for line in texlog.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning',line,re.I) and 'Package: infwarerr' not in line]
    ck('clean TeX log',not warnings)
    ck('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(CAND/'accounting-product-proposal.blg').read_text(),re.I))
    render=json.loads((OUT/'render-manifest.json').read_text())
    ck('render binds PDF',render['pdf_sha256']==sha(pdf))
    ck('eight ordered pages',[r['pdf_page_index'] for r in render['rendered_pages']]==list(range(118,126)))
    ck('render image hashes intact',all(sha(ROOT/r['image'])==r['sha256'] for r in render['rendered_pages']))
    audit=json.loads((OUT/'surface-audit.json').read_text())
    ck('surface audit targets bank chapter',audit['tex_path']==str((CAND/'chapters/15-banking.tex').resolve()))
    result={'recorded_at':'2026-10-12','plan':'docs/plans/accounting-jpmorgan-commitment-integration-20261012.md','baseline_pdf':baseline['baseline_pdf'],'candidate_pdf':{'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'pages':pages},'changed_sources':changed,'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'readiness':'not_ready','review_scope':'bounded bank chapter and adjacent transition; author review only'}
    (OUT/'manuscript-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'check-run.json').write_text(json.dumps({'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v233-integration-20261012/check_integration.py','wall_seconds':time.monotonic()-start},indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'failed':result['failed'],'failures':[r['check'] for r in checks if not r['passed']],'pages':pages}))
    raise SystemExit(bool(result['failed']))


if __name__=='__main__':main()
