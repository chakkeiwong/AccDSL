"""Verify the declared addition and the protected source/manuscript evidence."""
import json
import re
import time
import fitz
from prepare import OUT, ROOT, PDF, BASE, sha, save
from build_candidate import CAND, ANCHOR

assert not (OUT/'completion.json').exists()
start=time.monotonic()
m=json.loads((OUT/'source-manifest.json').read_text())
sourcechecks=json.loads((OUT/'source-checks.json').read_text())
checks=[]
def ck(name,value):checks.append({'name':name,'passed':bool(value)})
ck('33 source checks pass',sourcechecks['passed']==33 and not sourcechecks['failed'])
ck('issuer source preserved',sha(PDF)==m['sha256'])
doc=fitz.open(PDF)
for x in m['pages']:
    ck('raw source reproduced '+str(x['pdf_page']),doc[x['pdf_page']-1].get_text('text',sort=False)==(ROOT/x['raw']).read_text())
    for k in ['raw','layout','render']:ck(k+' binding '+str(x['pdf_page']),sha(ROOT/x[k])==x[k+'_sha256'])
facts=json.loads((OUT/'source-ledger.json').read_text())
for s in facts['spans']:
    p=ROOT/s['text_path']
    ck('located span '+s['id'],sha(p)==s['text_sha256'] and p.read_text()[s['start']:s['end_exclusive']]==s['quote'])
ck('baseline PDF preserved',sha(BASE/'accounting-product-proposal.pdf')==m['baseline_pdf_sha256'])
files=m['source_hashes']
ck('source inventory preserved',set(files)=={str(p.relative_to(CAND)) for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}})
insertion=(OUT/'insertion.tex').read_text()
for rel,digest in files.items():
    ck('protected baseline '+rel,sha(BASE/rel)==digest)
    old=(BASE/rel).read_text();expected=old
    if rel=='accounting-product-proposal.tex':expected=expected.replace('Version 2.38 (proposal candidate)','Version 2.39 (proposal candidate)')
    elif rel=='chapters/15-banking.tex':expected=expected.replace(ANCHOR,insertion+'\n'+ANCHOR)
    ck('exact candidate '+rel,(CAND/rel).read_text()==expected)
before='\n'.join((BASE/p).read_text() for p in sorted(files) if p.endswith('.tex'))
after='\n'.join((CAND/p).read_text() for p in sorted(files) if p.endswith('.tex'))
pattern=re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
displays=lambda t:[x.group() for x in pattern.finditer(t)]
ck('48 displays preserved',displays(before)==displays(after) and len(displays(after))==48)
bib=(CAND/'references.bib').read_text()
keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
citations={k.strip() for g in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}',after) for k in g.split(',')}
ck('76 bibliography entries preserved',len(keys)==len(set(keys))==76 and bib==(BASE/'references.bib').read_text())
ck('citations resolve',citations<=set(keys))
labels=re.findall(r'\\label\{([^{}]+)\}',after)
refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}',after)
ck('labels unique and references resolve',len(labels)==len(set(labels)) and set(refs)<=set(labels))
ck('insertion hash',sha(OUT/'insertion.tex')==json.loads((OUT/'candidate.json').read_text())['insertion_sha256'])
pdf=CAND/'accounting-product-proposal.pdf';d=fitz.open(pdf)
t=' '.join(' '.join(p.get_text().split()) for p in d)
ck('new dated capacity and approval condition rendered',all(s in t for s in ['1 January 2026','US$30.1bn','without prior approval','future cash receipt','dividend decision']))
ck('new restricted-cash distinction rendered',all(s in t for s in ['US$29.0bn','US$19.4bn','US$9.6bn','US$27.8bn','US$1.2bn','consolidated and parent-only','category overlap']))
ck('prior visibility repair retained','A PDF can preserve characters' in t and 'unresolved availability condition' in t)
log=(CAND/'accounting-product-proposal.log').read_text(errors='replace')
warnings=[s for s in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning',s)]
ck('final TeX log clean',not warnings)
blg=(CAND/'accounting-product-proposal.blg').read_text(errors='replace')
ck('bibliography log clean','Warning--' not in blg and "I didn't find" not in blg)
for x in m['pointer_snapshots']:ck('before pointer '+x['live'],sha(ROOT/x['snapshot'])==x['sha256'])
for x in json.loads((OUT/'final-renders.json').read_text()):
    ck('final render '+str(x['pdf_page']),sha(ROOT/x['render'])==x['sha256'] and sha(pdf)==x['pdf_sha256'])
failed=[x['name'] for x in checks if not x['passed']]
result={'checks':checks,'passed':len(checks)-len(failed),'failed':failed,'pages':len(d),
    'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),'warnings':warnings,'wall_seconds':time.monotonic()-start,
    'readiness':'not_ready','scope':'Bounded documentary preservation and integration; author review remains a separate ledger.'}
save('integration-checks.json',result)
print(json.dumps({k:result[k] for k in ['passed','failed','pages','pdf_sha256','warnings']}))
raise SystemExit(bool(failed))
