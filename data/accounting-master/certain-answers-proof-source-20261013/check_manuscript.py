"""Verify exact scoped 2.72 change and inspected rendered manuscript."""
import collections,hashlib,json,re
from pathlib import Path
import fitz
U=Path(__file__).resolve().parent;R=U.parents[2]
b=json.loads((U/'baseline.json').read_text());c=json.loads((U/'candidate.json').read_text())
B=R/c['baseline'];C=R/c['candidate'];checks={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in b['candidate_files'].items():checks['baseline:'+p]=sha(R/p)==h
for rel in c['source_hashes']:
    old=(B/rel).read_text();new=old
    if rel=='accounting-product-proposal.tex':new=old.replace('Version 2.71','Version 2.72')
    if rel=='sections/certain-answer-semantics.tex':
        start=c['old_qualification_start'];end=c['old_qualification_end']
        assert old.count(start)==old.count(end)==1
        left,rest=old.split(start);_,right=rest.split(end,1)
        new=left+(U/'theorem-qualification.tex').read_text().rstrip()+right
    if rel=='references.bib':new=old+(U/'bibliography-addition.bib').read_text()
    checks['scoped:'+rel]=(C/rel).read_text()==new
checks['exact_source_file_set']={str(p.relative_to(C)) for p in C.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}==set(c['source_hashes'])
def features(folder):
    t='\n'.join(p.read_text() for p in sorted(folder.rglob('*.tex')))
    cites=collections.Counter(k.strip() for m in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',t) for k in m.split(','))
    displays=collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}',t,re.S))
    return cites,displays
oc,od=features(B);nc,nd=features(C)
checks['prior_citations_preserved']=not(oc-nc)
checks['prior_displays_preserved']=not(od-nd)
checks['display_count_unchanged']=sum(od.values())==sum(nd.values())==65
checks['citation_count_expanded']=sum(oc.values())==465 and sum(nc.values())==468
keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',(C/'references.bib').read_text()))
checks['citations_resolve']=set(nc)<=keys
checks['bibliography_prefix_preserved']=(C/'references.bib').read_bytes().startswith((B/'references.bib').read_bytes())
checks['archived_source_sha']=sha(R/'docs/papers/Certain answers as objects and knowledge Libkin (2016).pdf')=='ed3a343607504a2a83c709760d994052e963e56c474e500cab1d81fe9fa6db01'
checks['clean_log']=not re.search(r'Warning|Overfull|Underfull|undefined|^!',(C/'accounting-product-proposal.log').read_text(),re.M)
checks['build_success']=json.loads((U/'build-run.json').read_text())['exit_code']==0
render=json.loads((U/'candidate-renders.json').read_text());review=json.loads((U/'rendered-review.json').read_text());pdf=C/'accounting-product-proposal.pdf'
checks['current_review']=sha(pdf)==render['pdf_sha256']==review['pdf_sha256']
with fitz.open(pdf) as d:
    body=' '.join(' '.join(p.get_text().split()) for p in d)
    checks['version_pages']='Version 2.72' in d[0].get_text() and len(d)==render['pdf_pages']==226
    checks['one_new_proof_discussion']=body.count('primary proof compares information by reverse inclusion')==1
    checks['input_output_asymmetry_rendered']='closed-world inputs and open-world answers' in body
    checks['transfer_limit_rendered']='for every financial output' in body
    checks['versioned_bibliography_rendered']='Final publisher bytes and exact KR version were not compared' in body
    checks['example_heading_once_in_body']=body.count('A certain liability need not identify its creditor')==2
checks['pages_inspected']={r['pdf_page'] for r in render['pages']}=={r['pdf_page'] for r in review['pages'] if r['inspected']}
for r in render['pages']:checks['render:'+str(r['pdf_page'])]=sha(R/r['path'])==r['sha256']
for group in ['frozen']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
failed=[k for k,v in checks.items() if not v]
out={'checks':checks,'passed':sum(checks.values()),'failed':failed,'prior_displays':sum(od.values()),'current_displays':sum(nd.values()),'prior_citations':sum(oc.values()),'current_citations':sum(nc.values()),'pdf_sha256':sha(pdf)}
(U/'manuscript-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='checks'}));raise SystemExit(bool(failed))
