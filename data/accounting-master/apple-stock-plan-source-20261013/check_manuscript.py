"""Check preservation, source support and the inspected V2.65 candidate."""
import collections
import hashlib
import json
import re
from pathlib import Path
import fitz

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((UNIT/'baseline.json').read_text())
c=json.loads((UNIT/'candidate.json').read_text())
base,cand=ROOT/c['baseline'],ROOT/c['candidate']
checks={}
for p,h in b['candidate_files'].items(): checks['protected:'+p]=sha(ROOT/p)==h
for rel in c['source_hashes']:
    expected=(base/rel).read_text()
    if rel=='accounting-product-proposal.tex':
        expected=expected.replace('Version 2.64','Version 2.65')
    if rel=='chapters/14-financing-groups.tex':
        expected=expected.replace(r'\input{sections/apple-eps-ownership}',
            r'\input{sections/apple-eps-ownership}'+'\n'+r'\input{sections/apple-stock-plan}')
    if rel=='sections/apple-eps-ownership.tex':
        expected=expected.replace('The 2022 employee plan permits several award types. Its RSUs generally vest',
            'The annual report describes several award types under the 2022 employee\n'
            'plan and the usual terms of its RSUs. In that reported practice, RSUs generally vest')
    if rel=='references.bib': expected+=(UNIT/'bibliography-additions.bib').read_text()
    checks['preserved_or_declared_edit:'+rel]=(cand/rel).read_text()==expected
checks['new_section_bound']=sha(cand/'sections/apple-stock-plan.tex')==sha(UNIT/'apple-stock-plan.tex')
def features(folder):
    text='\n'.join(p.read_text() for p in sorted(folder.rglob('*.tex')))
    citations=collections.Counter(k.strip() for m in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',text) for k in m.split(','))
    displays=collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}',text,re.S))
    return citations,displays
oc,od=features(base);nc,nd=features(cand)
checks['prior_citations_preserved']=not(oc-nc)
checks['prior_displays_preserved']=not(od-nd)
keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',(cand/'references.bib').read_text()))
checks['citations_resolve']=set(nc)<=keys
checks['bibliography_additive']=(cand/'references.bib').read_bytes().startswith((base/'references.bib').read_bytes())
checks['clean_log']=not re.search(r'Warning|Overfull|Underfull|undefined|^!',(cand/'accounting-product-proposal.log').read_text(),re.M)
checks['build_success']=json.loads((UNIT/'build-run.json').read_text())['exit_code']==0
checks['source_checks_pass']=not json.loads((UNIT/'source-arithmetic-checks.json').read_text())['failed']
renders=json.loads((UNIT/'candidate-renders.json').read_text())
review=json.loads((UNIT/'rendered-review.json').read_text())
pdf=cand/'accounting-product-proposal.pdf'
checks['current_pdf_review']=sha(pdf)==renders['pdf_sha256']==review['pdf_sha256']
with fitz.open(pdf) as d:
    text=' '.join(' '.join(p.get_text().split()) for p in d)
    checks['version_pages']='Version 2.65' in text and len(d)==renders['pdf_pages']==217
    checks['new_section_rendered']=all(s in text for s in ['1,274,374,682','163,331,226','1,093,463,078','net reserve shares used','Cook'])
checks['six_pages_inspected']={p['pdf_page'] for p in review['pages'] if p['inspected']}=={1,5,121,122,123,207}
for p in renders['pages']: checks['render:'+str(p['pdf_page'])]=sha(ROOT/p['path'])==p['sha256']
for p,h in b['dependencies'].items(): checks['dependency:'+p]=sha(ROOT/p)==h
for p,h in b['frozen'].items(): checks['frozen:'+p]=sha(ROOT/p)==h
failed=[k for k,v in checks.items() if not v]
r={'checks':checks,'passed':sum(checks.values()),'failed':failed,
   'prior_displays':sum(od.values()),'current_displays':sum(nd.values()),
   'prior_citations':sum(oc.values()),'current_citations':sum(nc.values()),
   'pdf_sha256':sha(pdf)}
(UNIT/'manuscript-checks.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='checks'}))
raise SystemExit(bool(failed))
