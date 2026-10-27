from pathlib import Path
import hashlib,json,shutil

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
BASE=ROOT/'docs/design/proposal/manuscript-participating-tax-allocation-20261017'
NEXT=ROOT/'docs/design/proposal/manuscript-zero-cost-collar-20261017'
ADDITION='\n'+r'\input{sections/zero-cost-collar}'+'\n'


def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==140
    records=[]
    for p in files:
        rel=p.relative_to(BASE)
        for target in (OUT/'baseline-sources'/rel,NEXT/rel):
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    p=NEXT/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.39 (proposal candidate)')==1
    p.write_text(s.replace('Version 3.39 (proposal candidate)','Version 3.40 (proposal candidate)'))
    p=NEXT/'sections/aligned-option-components.tex';p.write_text(p.read_text()+ADDITION)
    shutil.copy2(OUT/'collar.tex',NEXT/'sections/zero-cost-collar.tex')
    print(json.dumps(dict(version='3.40',protected_sources=len(files),new_sections=1)))


if __name__=='__main__':main()
