from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-native-company-sale-20261025'
TARGET=ROOT/'docs/design/proposal/manuscript-company-reports-20261025'
ADDITIONS={'sections/company-family-language.tex':('reports-addition.tex',r'\paragraph{A payment can change the decision that follows it.}')}
def sha(p):return sha256(p.read_bytes()).hexdigest()
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        assert text.count('Version 4.07 (proposal candidate)')==1
        return text.replace('Version 4.07 (proposal candidate)','Version 4.08 (proposal candidate)')
    if name in ADDITIONS:
        addition,anchor=ADDITIONS[name];assert text.count(anchor)==1
        return text.replace(anchor,(HERE/addition).read_text()+'\n'+anchor)
    return text
def main():
    assert not TARGET.exists() and not (HERE/'baseline.json').exists(),'already prepared'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='23d26d2e8897e9329056bee4aec09516a041f476fd4ec5af5d1cb18089250f18'
    hashes={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert len(hashes)==174
    folder=HERE.parent/'company-book-reports-20261025';assert (folder/'control-refresh.json').exists()
    for name,h in json.loads((folder/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
    evidence={p.relative_to(ROOT).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'control-before' not in p.parts}
    for name in ['scripts/company_book_reports_v1.py','tests/test_company_book_reports_v1.py']:evidence[name]=sha(ROOT/name)
    comparison=json.loads((folder/'comparison.json').read_text());assert all(x['passed'] for x in comparison['checks'])
    (HERE/'evidence-check.json').write_text(json.dumps({'passed':True,'protected_evidence':evidence},indent=2)+'\n')
    (HERE/'baseline.json').write_text(json.dumps({'source_root':SOURCE.relative_to(ROOT).as_posix(),'candidate_root':TARGET.relative_to(ROOT).as_posix(),'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
    print(json.dumps({'protected_sources':len(hashes),'evidence_files':len(evidence),'candidate':str(TARGET.relative_to(ROOT))}))
if __name__=='__main__':main()
