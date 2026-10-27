"""Create one separate candidate; preserve the exact earlier candidate."""
import hashlib
import json
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'docs/design/proposal/manuscript-bidi-dependencies-20261011'
CAND = ROOT / 'docs/design/proposal/manuscript-jpmorgan-commitments-20261012'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(BASE/'accounting-product-proposal.pdf') == '8dc196a4043f382111d5bddfaf8ec0c75f9297f807ed7555d5621f6eb0703623'
assert not CAND.exists()
inputs = [p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark','.md','.json'}]
for source in inputs:
    target = CAND/source.relative_to(BASE)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
title = CAND/'accounting-product-proposal.tex'
old = title.read_text(); assert old.count('Version 2.32') == 1
title.write_text(old.replace('Version 2.32','Version 2.33'))
chapter = CAND/'chapters/15-banking.tex'
old = chapter.read_text()
marker = 'Regulatory capital is computed in a separate prudential layer with its own'
assert old.count(marker) == 1
chapter.write_text(old.replace(marker,(OUT/'addition.tex').read_text()+marker))
relocations=[]
for relative in ['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md','docs/plans/accounting-continuation-requirements-20261007.md','data/accounting-master/next-plan.md']:
    source=ROOT/relative; target=OUT/'pointers-before'/source.name
    target.parent.mkdir(exist_ok=True); shutil.copyfile(source,target)
    relocations.append({'historical_path':relative,'preserved_path':str(target.relative_to(ROOT)),'sha256':sha(source)})
(OUT/'baseline.json').write_text(json.dumps({'baseline_pdf':{'path':str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),'sha256':sha(BASE/'accounting-product-proposal.pdf'),'pages':172},'source_hashes':{str(p.relative_to(BASE)):sha(p) for p in inputs},'pointer_relocations':relocations,'baseline_reading':'PDF pages 118–121 read in order; new real commitment example follows the simple allowance calculation and precedes regulatory capital and synthetic bank path'},indent=2)+'\n')
print(json.dumps({'candidate':str(CAND.relative_to(ROOT)),'sources':len(inputs),'controls':len(relocations)}))
