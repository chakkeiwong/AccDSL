"""Verify an additive performance-award section and its inspected PDF."""
import collections,hashlib,json,re
from pathlib import Path
import fitz
U=Path(__file__).resolve().parent;R=U.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((U/'baseline.json').read_text());c=json.loads((U/'candidate.json').read_text())
B=R/c['baseline'];C=R/c['candidate'];checks={}
for p,h in b['candidate_files'].items():checks['baseline:'+p]=sha(R/p)==h
for rel in c['source_hashes']:
    t=(B/rel).read_text()
    if rel=='accounting-product-proposal.tex':t=t.replace('Version 2.65','Version 2.66')
    if rel=='chapters/14-financing-groups.tex':
        t=t.replace(r'\input{sections/apple-stock-plan}',r'\input{sections/apple-stock-plan}'+'\n'+r'\input{sections/apple-performance-award}')
    checks['additive:'+rel]=(C/rel).read_text()==t
checks['section_bound']=sha(C/'sections/apple-performance-award.tex')==sha(U/'apple-performance-award.tex')
def features(folder):
    t='\n'.join(p.read_text() for p in sorted(folder.rglob('*.tex')))
    cites=collections.Counter(k.strip() for m in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',t) for k in m.split(','))
    displays=collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}',t,re.S))
    return cites,displays
oc,od=features(B);nc,nd=features(C)
checks['citations_preserved']=not(oc-nc);checks['displays_preserved']=not(od-nd)
checks['bibliography_preserved']=sha(B/'references.bib')==sha(C/'references.bib')
keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',(C/'references.bib').read_text()))
checks['citations_resolve']=set(nc)<=keys
checks['clean_log']=not re.search(r'Warning|Overfull|Underfull|undefined|^!',(C/'accounting-product-proposal.log').read_text(),re.M)
checks['build_success']=json.loads((U/'build-run.json').read_text())['exit_code']==0
checks['source_arithmetic']=not json.loads((U/'source-arithmetic-checks.json').read_text())['failed']
render=json.loads((U/'candidate-renders.json').read_text());review=json.loads((U/'rendered-review.json').read_text());pdf=C/'accounting-product-proposal.pdf'
checks['current_review']=sha(pdf)==render['pdf_sha256']==review['pdf_sha256']
with fitz.open(pdf) as d:
    t=' '.join(' '.join(p.get_text().split()) for p in d)
    checks['version_pages']='Version 2.66' in t and len(d)==render['pdf_pages']==219
    checks['consequences_rendered']=all(s in t for s in ['Performance conditions determine','1,500','375','225','150','severance'])
checks['five_pages_inspected']={p['pdf_page'] for p in review['pages'] if p['inspected']}=={1,5,123,124,125}
for p in render['pages']:checks['render:'+str(p['pdf_page'])]=sha(R/p['path'])==p['sha256']
for p,h in b['dependencies'].items():checks['dependency:'+p]=sha(R/p)==h
for p,h in b['frozen'].items():checks['frozen:'+p]=sha(R/p)==h
failed=[k for k,x in checks.items() if not x]
r={'checks':checks,'passed':sum(checks.values()),'failed':failed,'prior_displays':sum(od.values()),'current_displays':sum(nd.values()),'prior_citations':sum(oc.values()),'current_citations':sum(nc.values()),'pdf_sha256':sha(pdf)}
(U/'manuscript-checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='checks'}));raise SystemExit(bool(failed))
