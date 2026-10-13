"""Verify the additive source-preserving proposal candidate."""
import collections
import hashlib
import json
import re
from pathlib import Path
import fitz
U=Path(__file__).resolve().parent;R=U.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((U/'baseline.json').read_text());c=json.loads((U/'candidate.json').read_text())
B=R/c['baseline'];C=R/c['candidate'];checks={}
for p,h in b['candidate_files'].items():checks['baseline:'+p]=sha(R/p)==h
for rel in c['source_hashes']:
    t=(B/rel).read_text()
    if rel=='accounting-product-proposal.tex':t=t.replace('Version 2.67','Version 2.68')
    if rel=='sections/adapter-methods.tex':
        anchor='Each adapter therefore pins code, dependency, model and taxonomy versions,'
        t=t.replace(anchor,r'\input{sections/arelle-fact-identity}'+'\n\n'+anchor)
    if rel=='references.bib':t+=(U/'bibliography-additions.bib').read_text()
    checks['additive:'+rel]=(C/rel).read_text()==t
checks['section_bound']=sha(C/'sections/arelle-fact-identity.tex')==sha(U/'arelle-fact-identity.tex')
def features(folder):
    t='\n'.join(p.read_text() for p in sorted(folder.rglob('*.tex')))
    cites=collections.Counter(k.strip() for m in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',t) for k in m.split(','))
    displays=collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}',t,re.S))
    return cites,displays
oc,od=features(B);nc,nd=features(C)
checks['citations_preserved']=not(oc-nc);checks['displays_preserved']=not(od-nd)
checks['bibliography_preserved']=(C/'references.bib').read_bytes().startswith((B/'references.bib').read_bytes())
keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',(C/'references.bib').read_text()))
checks['citations_resolve']=set(nc)<=keys
checks['clean_log']=not re.search(r'Warning|Overfull|Underfull|undefined|^!',(C/'accounting-product-proposal.log').read_text(),re.M)
checks['build_success']=json.loads((U/'build-run.json').read_text())['exit_code']==0
checks['source_arithmetic']=not json.loads((U/'source-arithmetic-checks.json').read_text())['failed']
render=json.loads((U/'candidate-renders.json').read_text());review=json.loads((U/'rendered-review.json').read_text());pdf=C/'accounting-product-proposal.pdf'
checks['current_review']=sha(pdf)==render['pdf_sha256']==review['pdf_sha256']
with fitz.open(pdf) as d:
    t=' '.join(' '.join(p.get_text().split()) for p in d)
    checks['version_pages']='Version 2.68' in t and len(d)==render['pdf_pages']==222
    checks['consequences_rendered']=all(s in t for s in ['Equal amounts still have separate source occurrences','complete-subset reduction','consistent-pairs reduction','underlying tree'])
checks['reviewed_all_selected_pages']={p['pdf_page'] for p in review['pages'] if p['inspected']}=={1,5,187,188,189,212}
for p in render['pages']:checks['render:'+str(p['pdf_page'])]=sha(R/p['path'])==p['sha256']
for group in ['dependencies','frozen']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
failed=[k for k,x in checks.items() if not x]
r={'checks':checks,'passed':sum(checks.values()),'failed':failed,'prior_displays':sum(od.values()),'current_displays':sum(nd.values()),'prior_citations':sum(oc.values()),'current_citations':sum(nc.values()),'pdf_sha256':sha(pdf)}
(U/'manuscript-checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='checks'}));raise SystemExit(bool(failed))
