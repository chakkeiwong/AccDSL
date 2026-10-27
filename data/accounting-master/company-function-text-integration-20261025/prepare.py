from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-functions-20261025'
TARGET=ROOT/'docs/design/proposal/manuscript-function-text-20261025'
ADDITIONS={
 'sections/company-family-language.tex':('text-addition.tex',r'\paragraph{Available inputs do not establish a saved past calculation.}')}

def sha(p):return sha256(p.read_bytes()).hexdigest()
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        assert text.count('Version 4.00 (proposal candidate)')==1
        return text.replace('Version 4.00 (proposal candidate)','Version 4.01 (proposal candidate)')
    if name in ADDITIONS:
        addition,anchor=ADDITIONS[name]; assert text.count(anchor)==1,(name,anchor)
        return text.replace(anchor,(HERE/addition).read_text()+'\n'+anchor)
    return text

def main():
    assert not TARGET.exists(),'candidate already prepared'
    assert not (HERE/'baseline.json').exists(),'baseline already recorded'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='187d64d0c6df510938417574b8170d9d7124cb5c9ffa643b49003a7e6a01b329'
    hashes={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert len(hashes)==174
    evidence={}
    for package in ['company-functions-20261025','company-function-text-20261025']:
        folder=HERE.parent/package
        assert (folder/'manifest.json').exists() and (folder/'control-refresh.json').exists()
        for name,h in json.loads((folder/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
        for p in folder.iterdir():
            if p.is_file():evidence[p.relative_to(ROOT).as_posix()]=sha(p)
    for name in ['scripts/company_functions_v1.py','scripts/company_function_text_v1.py','tests/test_company_function_text_v1.py']:
        evidence[name]=sha(ROOT/name)
    comparison=json.loads((HERE.parent/'company-function-text-20261025/comparison.json').read_text())
    source_text=comparison['cases']['ordinary']['source']
    addition=(HERE/'text-addition.tex').read_text()
    block=addition.split('function complement;',1)[1].split('end_function;',1)[0]
    exact='function complement;'+block+'end_function;'
    assert exact in source_text,'manuscript function differs from checked source'
    assert 'call regular complement discount;' in source_text
    (HERE/'example-check.json').write_text(json.dumps({'passed':True,'source_sha256':comparison['cases']['ordinary']['parsed']['source_sha256'],'function_block':exact,'call':'call regular complement discount;'},indent=2)+chr(10))
    (HERE/'evidence-check.json').write_text(json.dumps({'passed':True,'protected_evidence':evidence},indent=2)+'\n')
    (HERE/'baseline.json').write_text(json.dumps({'source_root':SOURCE.relative_to(ROOT).as_posix(),
        'candidate_root':TARGET.relative_to(ROOT).as_posix(),'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(expected(name,(SOURCE/name).read_text()))
    print(json.dumps({'protected_sources':len(hashes),'evidence_files':len(evidence),'candidate':TARGET.relative_to(ROOT).as_posix()}))

if __name__=='__main__':main()
