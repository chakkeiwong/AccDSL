from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-inventory-persistence-20261025'
TARGET=ROOT/'docs/design/proposal/manuscript-functions-20261025'
ADDITIONS={
 'chapters/03-literature.tex':('literature-addition.tex','These methods suggest a common division of work.'),
 'sections/company-family-language.tex':('functions-addition.tex',r'\paragraph{Available inputs do not establish a saved past calculation.}'),
 'chapters/12-research.tex':('research-addition.tex','OpenAlex retraction flags and available Crossref correction/version relations')}

def sha(p):return sha256(p.read_bytes()).hexdigest()
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        assert text.count('Version 3.99 (proposal candidate)')==1
        return text.replace('Version 3.99 (proposal candidate)','Version 4.00 (proposal candidate)')
    if name=='references.bib':return text+'\n'+(HERE/'bibliography-addition.bib').read_text()
    if name in ADDITIONS:
        addition,anchor=ADDITIONS[name]; assert text.count(anchor)==1,(name,anchor)
        return text.replace(anchor,(HERE/addition).read_text()+'\n'+anchor)
    return text

def main():
    assert not TARGET.exists(),'candidate already prepared'
    assert not (HERE/'baseline.json').exists(),'baseline already recorded'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='6cb611a97dd3d1479c8a010bd65e3de724950a67c9e0284de1ce24ee939f6a06'
    hashes={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert len(hashes)==174
    evidence={}
    for package in ['simulator-survey-source-recovery-20261025','company-functions-20261025']:
        folder=HERE.parent/package
        assert (folder/'manifest.json').exists() and (folder/'control-refresh.json').exists()
        for name,h in json.loads((folder/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
        for p in folder.iterdir():
            if p.is_file():evidence[p.relative_to(ROOT).as_posix()]=sha(p)
    for name in ['scripts/company_functions_v1.py','tests/test_company_functions_v1.py','docs/design/research/simulator-equations-and-events-20261025.md']:
        evidence[name]=sha(ROOT/name)
    (HERE/'evidence-check.json').write_text(json.dumps({'passed':True,'protected_evidence':evidence},indent=2)+'\n')
    (HERE/'baseline.json').write_text(json.dumps({'source_root':SOURCE.relative_to(ROOT).as_posix(),
        'candidate_root':TARGET.relative_to(ROOT).as_posix(),'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(expected(name,(SOURCE/name).read_text()))
    print(json.dumps({'protected_sources':len(hashes),'evidence_files':len(evidence),'candidate':TARGET.relative_to(ROOT).as_posix()}))

if __name__=='__main__':main()
