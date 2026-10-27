#!/usr/bin/env python3
"""Exact author-source preservation and bounded historical-source integration."""
import hashlib
import json
import re
import time
from pathlib import Path
import fitz

start=time.monotonic()
out=Path(__file__).resolve().parent
repo=out.parents[2]
base=repo/'docs/design/proposal/manuscript-jpmorgan-commitments-20261012'
cand=repo/'docs/design/proposal/manuscript-historical-credit-loss-20261012'
baseline=json.loads((out/'baseline.json').read_text())
checks=[]
def ck(name,ok):
    checks.append({'name':name,'pass':bool(ok)})
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
ck('protected baseline PDF',sha(base/'accounting-product-proposal.pdf')==baseline['baseline_pdf']['sha256'])
files=baseline['source_hashes']
ck('author-source inventory',set(files)=={str(p.relative_to(cand)) for p in cand.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}})
addition=(out/'addition.tex').read_text()
bib_add=(out/'bib-addition.bib').read_text()
marker='A commitment to acquire loans makes the time distinction especially clear.'
changed=[]
for rel,digest in sorted(files.items()):
    a,b=base/rel,cand/rel
    ck('baseline source '+rel,sha(a)==digest)
    old,new=a.read_text(),b.read_text()
    if old!=new:changed.append(rel)
    if rel=='accounting-product-proposal.tex':
        expected=old.replace('Version 2.33 (proposal candidate) \\quad 11 October 2026',
                             'Version 2.34 (proposal candidate) \\quad 12 October 2026')
    elif rel=='chapters/15-banking.tex':
        ck('single insertion anchor',old.count(marker)==1)
        expected=old.replace(marker,addition+marker)
    elif rel=='references.bib':
        expected=old.rstrip()+'\n\n'+bib_add
    elif rel=='sections/bank-methods.tex':
        anchor='At year-one accrual the loan has survived'
        ck('single layout-repair anchor',old.count(anchor)==1)
        expected=old.replace(anchor,'\\enlargethispage{\\baselineskip}\n'+anchor)
        section='\\hypertarget{funding-capital-and-decision-policies}{%'
        ck('single section-break anchor',old.count(section)==1)
        expected=expected.replace(section,'\\newpage\n'+section)
    else:
        expected=old
    ck('exact candidate source '+rel,new==expected)
ck('only title bank bibliography and layout changed',set(changed)=={'accounting-product-proposal.tex','chapters/15-banking.tex','references.bib','sections/bank-methods.tex'})
before='\n'.join((base/p).read_text() for p in sorted(files) if p.endswith('.tex'))
after='\n'.join((cand/p).read_text() for p in sorted(files) if p.endswith('.tex'))
pattern=re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
displays=lambda t:[m.group() for m in pattern.finditer(t)]
ck('48 unchanged displays',displays(before)==displays(after) and len(displays(after))==48)
labels=re.findall(r'\\label\{([^{}]+)\}',after)
refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}',after)
ck('unique labels',len(labels)==len(set(labels)))
ck('references resolve',set(refs)<=set(labels))
bib=(cand/'references.bib').read_text()
keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
cited={k.strip() for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}',after) for k in group.split(',')}
ck('75 unique bibliography entries',len(keys)==len(set(keys))==75)
ck('74 inherited bibliography entries retained',(base/'references.bib').read_text().strip() in bib)
ck('citations resolve',cited<=set(keys))
for term in ['historical FASB amendment','present obligation','cancel unconditionally','contingent','noncontingent','not verified current Codification','later rule history']:
    ck('source boundary '+term,term in ' '.join(addition.split()))
for unit in baseline['source_units']:
    path=repo/unit
    m=json.loads((path/'run-manifest.json').read_text())
    c=json.loads((path/'completion.json').read_text())
    ck('frozen source unit '+unit,all(sha(repo/p)==h for p,h in m['artifact_hashes'].items()) and c['manifest_sha256']==sha(path/'run-manifest.json') and c['failed']==0)
for item in baseline['pointer_snapshots']:
    ck('pre-update control '+item['live'],sha(repo/item['snapshot'])==item['sha256'])
pdf=cand/'accounting-product-proposal.pdf'
with fitz.open(pdf) as doc:
    count=len(doc)
    p119=' '.join(doc[118].get_text().split())
    p120=' '.join(doc[119].get_text().split())
    ck('historical explanation and boundary together',all(x in p119 for x in ['historical FASB amendment','2016-13','not verified current Codification']))
    ck('issuer four quantities retained',all(x in p119 for x in ['1,817,307','603,947','5,071','6,278']))
    ck('forward acquisition remains subsequent',all(x in p120 for x in ['30 December','7 January','not loans already owned']))
log=(cand/'accounting-product-proposal.log').read_text(errors='replace')
warnings=[line for line in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning',line,re.I) and 'Package: infwarerr' not in line]
ck('clean final TeX log',not warnings)
blg=(cand/'accounting-product-proposal.blg').read_text(errors='replace')
ck('clean bibliography log','Warning--' not in blg and "I didn't find" not in blg)
failed=[x['name'] for x in checks if not x['pass']]
result={'checks':len(checks),'failed':failed,'pages':count,'pdf_sha256':sha(pdf),'wall_seconds':time.monotonic()-start,'warnings':warnings,'results':checks}
(out/'check-run.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['checks','failed','pages','pdf_sha256']}))
raise SystemExit(bool(failed))
