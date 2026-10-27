"""Create a separate candidate with one exact prose insertion and citations."""
import hashlib
import json
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT/'docs/design/proposal/manuscript-jpmorgan-succession-20261011'
CAND = ROOT/'docs/design/proposal/manuscript-bidi-dependencies-20261011'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert sha(BASE/'accounting-product-proposal.pdf') == 'fb10b6363e8a31d7b53c72e945ee348ef09e41cbb37aa9bb51366632c2957c33'
    assert not CAND.exists(), 'Preserve existing candidate'
    assert not (OUT/'baseline.json').exists()
    inputs = [p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark','.md','.json'}]
    for src in inputs:
        dest=CAND/src.relative_to(BASE)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest)
    title=CAND/'accounting-product-proposal.tex'
    text=title.read_text(); assert text.count('Version 2.31') == 1
    title.write_text(text.replace('Version 2.31','Version 2.32'))
    adapter=CAND/'sections/adapter-methods.tex'
    text=adapter.read_text(); marker='The actual taxonomy notices show why that distinction changes the design.'
    assert text.count(marker) == 1
    adapter.write_text(text.replace(marker,(OUT/'addition.tex').read_text()+marker))
    bib=CAND/'references.bib'
    bib.write_text(bib.read_text()+(OUT/'bibliography-addition.bib').read_text())
    relocations=[]
    for path in ['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md','docs/plans/accounting-continuation-requirements-20261007.md','data/accounting-master/next-plan.md']:
        src=ROOT/path;dest=OUT/'pointers-before'/src.name
        dest.parent.mkdir(exist_ok=True)
        assert not dest.exists()
        shutil.copyfile(src,dest)
        relocations.append({'historical_path':path,'preserved_path':str(dest.relative_to(ROOT)),'sha256':sha(src)})
    baseline={'baseline_pdf':{'path':str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),'sha256':sha(BASE/'accounting-product-proposal.pdf'),'pages':171},'source_hashes':{str(p.relative_to(BASE)):sha(p) for p in inputs},'pointer_relocations':relocations,'baseline_reading':'PDF pages 141–144 viewed in order; concrete imported-dependency and terms example added to existing generic rule; no inherited prose deletion needed'}
    (OUT/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    print(json.dumps({'candidate':str(CAND.relative_to(ROOT)),'copied_sources':len(inputs),'preserved_controls':len(relocations)}))

if __name__=='__main__':main()
