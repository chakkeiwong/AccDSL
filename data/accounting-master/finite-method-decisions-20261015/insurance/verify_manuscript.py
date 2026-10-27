"""Compare the protected predecessor with the rendered insurance successor."""
from collections import Counter
from pathlib import Path
import hashlib,json,re,subprocess,time

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    started=time.perf_counter();checks=[]
    def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
    baseline=json.loads((OUT/'manuscript-baseline.json').read_text())
    old=(ROOT/baseline['baseline_pdf']).parent;new=ROOT/baseline['candidate']
    check('protected_pdf',sha(ROOT/baseline['baseline_pdf'])==baseline['baseline_pdf_sha256'])
    changed=[]
    for item in baseline['source_files']:
        name=item['path'];check('protected:'+name,sha(old/name)==item['sha256'])
        if (old/name).read_bytes()!=(new/name).read_bytes():changed.append(name)
    check('only_intended_changes',set(changed)=={'accounting-product-proposal.tex','sections/insurance-methods.tex'},changed)
    additions={str(p.relative_to(new)) for p in new.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}-{x['path'] for x in baseline['source_files']}
    check('only_intended_additions',additions=={'sections/insurance-priced-guarantee.tex','sections/insurance-acquisition-treaty.tex'},sorted(additions))
    for chapter in ['insurance-methods']:
        a=(old/'sections'/f'{chapter}.tex').read_text();b=(new/'sections'/f'{chapter}.tex').read_text()
        for entry in ['insurance-priced-guarantee','insurance-acquisition-treaty']:b=b.replace('\\input{sections/'+entry+'}\n\n','')
        b=b.replace(r'Section~\ref{sec:insurance-acquisition-incorporation} supplied the acquisition assets and the net inflows','The preceding example supplied the acquisition assets and the net inflows')
        check('prior_chapter_preserved_except_explicit_navigation_repair:'+chapter,a==b)
    texts=['\n'.join(p.read_text() for p in sorted(folder.rglob('*.tex'))) for folder in [old,new]]
    counts={}
    for label,pattern in {'displays':r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?)\}','labels':r'\\label\{[^}]+\}','citations':r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}'}.items():
        a,b=[Counter(re.findall(pattern,t,re.S)) for t in texts]
        counts[label]={'before':sum(a.values()),'after':sum(b.values()),'removed':list((a-b).elements())}
        check('preserved:'+label,not(a-b),counts[label])
    check('bibliography',(old/'references.bib').read_bytes()==(new/'references.bib').read_bytes())
    build=json.loads((OUT/'build-run.json').read_text());render=json.loads((OUT/'verified-render/render-manifest.json').read_text());review=json.loads((OUT/'render-review.json').read_text())
    check('build',build['exit_code']==0 and not build['diagnostics'],build['diagnostics'])
    pdf=new/'accounting-product-proposal.pdf';check('pdf_hash',sha(pdf)==build['pdf_sha256']==render['pdf_sha256']==review['pdf_sha256'])
    for page in review['physical_pages']:
        row=render['pages'][str(page)];check('render:'+str(page),sha(ROOT/row['path'])==row['sha256'])
    fls=(new/'accounting-product-proposal.fls').read_text().splitlines();cwd=Path(next(x[4:] for x in fls if x.startswith('PWD ')))
    paths={(cwd/x[6:]).resolve() for x in fls if x.startswith('INPUT ')}
    external=[str(p) for p in paths if p.is_relative_to(ROOT) and not p.is_relative_to(new)]
    check('all_project_inputs_frozen_in_candidate',not external,external)
    independent=json.loads((OUT/'independent-checks.json').read_text());check('independent_specification_checks',independent['passed'] and all(x['passed'] for x in independent['checks']))
    check('unrelated_index',(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()==subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT))
    result={'passed':all(x['passed'] for x in checks),'check_count':len(checks),'checks':checks,'counts':counts,'wall_seconds':time.perf_counter()-started,'candidate_pdf_sha256':sha(pdf),'source_inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(paths) if p.is_relative_to(new) and p.is_file()]}
    (OUT/'manuscript-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'checks':len(checks),'counts':counts,'failed':[x['name'] for x in checks if not x['passed']]}))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
