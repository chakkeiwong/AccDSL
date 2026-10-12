"""Verify all preserved source and equations, plus citations and build identity."""
import json
import re
import time
import fitz
from build_candidate import OUT, ROOT, BASE, CAND, sha, save, expected_text

assert not (OUT/'completion.json').exists()
start=time.monotonic();checks=[]
def ck(n,v): checks.append({'name':n,'passed':bool(v)})
c=json.loads((OUT/'candidate.json').read_text())
unit=ROOT/'data/accounting-master/insurance-vfa-source-20261012'
closed=json.loads((unit/'completion.json').read_text())
ck('source closure binding',sha(unit/'run-manifest.json')==closed['manifest_sha256'])
ck('30 source and 15 finite checks pass',closed['source_checks']==30 and closed['finite_checks']==15 and closed['failed']==0)
manifest=json.loads((unit/'run-manifest.json').read_text())
ck('all source artifact and input hashes',all(sha(ROOT/p)==h for p,h in (manifest['input_hashes']|manifest['artifact_hashes']).items()))
ck('protected 2.46 PDF',sha(BASE/'accounting-product-proposal.pdf')==c['baseline_pdf_sha256'])
files=c['source_hashes']
ck('same source inventory',set(files)=={str(p.relative_to(CAND)) for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}})
for rel,digest in files.items():
    ck('baseline '+rel,sha(BASE/rel)==sha(OUT/'baseline-source'/rel)==digest)
    ck('exact delta '+rel,(CAND/rel).read_text()==expected_text(rel))
rel='sections/insurance-methods.tex'
extra=(OUT/'insurance-addition.tex').read_text()+'\n'
s=(CAND/rel).read_text()
ck('all old insurance prose preserved',s.count(extra)==1 and s.replace(extra,'',1)==(BASE/rel).read_text())
before='\n'.join((BASE/p).read_text() for p in sorted(files) if p.endswith('.tex'))
after='\n'.join((CAND/p).read_text() for p in sorted(files) if p.endswith('.tex'))
pattern=re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
displays=lambda s:[m.group() for m in pattern.finditer(s)]
ck('48 displays preserved exactly',displays(before)==displays(after) and len(displays(after))==48)
oldbib=(BASE/'references.bib').read_text();bib=(CAND/'references.bib').read_text()
keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib);oldkeys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',oldbib)
ck('all 93 references preserved exactly',len(oldkeys)==len(keys)==len(set(keys))==93 and bib==oldbib)
cites={k.strip() for g in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}',after) for k in g.split(',')}
ck('all citations resolve',cites<=set(keys))
labels=re.findall(r'\\label\{([^{}]+)\}',after);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}',after)
ck('labels unique and references resolve',len(labels)==len(set(labels)) and set(refs)<=set(labels))
for n,h in c['passage_hashes'].items():ck('delta binding '+n,sha(OUT/n)==h)
pdf=CAND/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
text=' '.join(' '.join(p.get_text().split()) for p in doc)
for phrase in ['Version 2.47','Eligibility depends on the contract',
               'A small settlement example shows why the guarantee matters',
               'Moving from 80 to 100 leaves 20 more after payment',
               'The accounting calculation therefore needs more than this payoff schedule',
               'the complete CSM movement needs these additional']:
    ck('rendered meaning '+phrase,phrase in text)
log=(CAND/'accounting-product-proposal.log').read_text(errors='replace')
warnings=[s for s in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning',s)]
ck('TeX log clean',not warnings)
blg=(CAND/'accounting-product-proposal.blg').read_text(errors='replace')
ck('bibliography log clean','Warning--' not in blg and "I didn't find" not in blg)
for r in json.loads((OUT/'final-renders.json').read_text()):ck('render binding '+str(r['pdf_page']),sha(ROOT/r['render'])==r['sha256'] and sha(pdf)==r['pdf_sha256'])
failure=[r['name'] for r in checks if not r['passed']]
result={'checks':checks,'passed':len(checks)-len(failure),'failed':failure,'pages':len(doc),
        'pdf_sha256':sha(pdf),'warnings':warnings,'wall_seconds':time.monotonic()-start,
        'readiness':'not_ready','scope':'Preservation and build evidence; independent/human acceptance pending'}
save('integration-checks.json',result)
print(json.dumps({k:result[k] for k in ['passed','failed','pages','pdf_sha256','warnings']}))
raise SystemExit(bool(failure))
