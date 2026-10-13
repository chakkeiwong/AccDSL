"""Verify scoped edits, preserved claims/math and the inspected final PDF."""
import collections,hashlib,json,re
from pathlib import Path
import fitz
U=Path(__file__).resolve().parent;R=U.parents[2]
b=json.loads((U/'baseline.json').read_text());c=json.loads((U/'candidate.json').read_text())
B=R/c['baseline'];C=R/c['candidate'];checks={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in b['candidate_files'].items():checks['baseline:'+p]=sha(R/p)==h
for rel,h in c['source_hashes'].items():
    t=(B/rel).read_text()
    for change in c['changes'].get(rel,[]):
        assert t.count(change['old'])==1
        t=t.replace(change['old'],change['new'])
    checks['scoped_change:'+rel]=(C/rel).read_text()==t
checks['new_section_bound']=sha(C/'sections/certain-answer-semantics.tex')==sha(U/'certain-answer-semantics.tex')
checks['exact_source_file_set']={str(p.relative_to(C)) for p in C.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}==set(c['source_hashes'])|{'sections/certain-answer-semantics.tex'}
def features(folder):
    t='\n'.join(p.read_text() for p in sorted(folder.rglob('*.tex')))
    cites=collections.Counter(k.strip() for m in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',t) for k in m.split(','))
    displays=collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}',t,re.S))
    return cites,displays
oc,od=features(B);nc,nd=features(C)
checks['citations_preserved']=not(oc-nc);checks['displays_preserved']=not(od-nd)
checks['bibliography_unchanged']=sha(C/'references.bib')==sha(B/'references.bib')
checks['expected_display_addition']=sum(od.values())==62 and sum(nd.values())==65
checks['expected_citation_addition']=sum(oc.values())==462 and sum(nc.values())==465
keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',(C/'references.bib').read_text()))
checks['citations_resolve']=set(nc)<=keys
checks['clean_log']=not re.search(r'Warning|Overfull|Underfull|undefined|^!',(C/'accounting-product-proposal.log').read_text(),re.M)
checks['build_success']=json.loads((U/'build-run.json').read_text())['exit_code']==0
checks['source_arithmetic']=not json.loads((U/'source-arithmetic-checks.json').read_text())['failed']
render=json.loads((U/'candidate-renders.json').read_text());review=json.loads((U/'rendered-review.json').read_text());pdf=C/'accounting-product-proposal.pdf'
checks['current_review']=sha(pdf)==render['pdf_sha256']==review['pdf_sha256']
with fitz.open(pdf) as d:
    texts=[' '.join(p.get_text().split()) for p in d]
    body=' '.join(texts[8:])
    checks['version_pages']='Version 2.71' in texts[0] and len(d)==render['pdf_pages']==226
    checks['new_heading_once_in_body']=body.count('A certain liability need not identify its creditor')==1
    checks['new_heading_in_contents']='A certain liability need not identify its creditor' in ' '.join(texts[:8])
    checks['proof_obligation_rendered_once']=body.count('For a decided answer')==1
    checks['scope_qualification_rendered']='sampled answer family cannot be relabelled as the full family' in body
    checks['existential_consequence_rendered']='The uncertainty concerns the creditor, not the existence or total of the payable.' in body
    checks['old_empty_family_guard_preserved']='An empty family returns Infeasible' in body
    checks['old_pending_solver_distinction_preserved']='the response distinguishes those causes' in body
checks['selected_pages_inspected']={p['pdf_page'] for p in review['pages'] if p['inspected']}=={p['pdf_page'] for p in render['pages']}
for p in render['pages']:checks['render:'+str(p['pdf_page'])]=sha(R/p['path'])==p['sha256']
for group in ['dependencies','frozen']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
failed=[k for k,v in checks.items() if not v]
result={'checks':checks,'passed':sum(checks.values()),'failed':failed,'prior_displays':sum(od.values()),'current_displays':sum(nd.values()),'prior_citations':sum(oc.values()),'current_citations':sum(nc.values()),'pdf_sha256':sha(pdf)}
(U/'manuscript-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}));raise SystemExit(bool(failed))
