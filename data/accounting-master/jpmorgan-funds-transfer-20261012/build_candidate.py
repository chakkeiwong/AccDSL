"""Create 2.39 from frozen 2.38 with only the stated bank example added."""
import json
import shutil
from prepare import OUT, ROOT, BASE, sha, save

CAND=ROOT/'docs/design/proposal/manuscript-funds-transfer-20261012'
ANCHOR='Debt amounts add a second distinction.'

def main():
    assert not CAND.exists()
    manifest=json.loads((OUT/'source-manifest.json').read_text())
    assert sha(BASE/'accounting-product-proposal.pdf')==manifest['baseline_pdf_sha256']
    for rel,digest in manifest['source_hashes'].items():
        assert sha(BASE/rel)==digest
        dest=CAND/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(BASE/rel,dest)
    title=CAND/'accounting-product-proposal.tex'
    t=title.read_text();assert t.count('Version 2.38 (proposal candidate)')==1
    title.write_text(t.replace('Version 2.38 (proposal candidate)','Version 2.39 (proposal candidate)'))
    chapter=CAND/'chapters/15-banking.tex'
    t=chapter.read_text();assert t.count(ANCHOR)==1
    chapter.write_text(t.replace(ANCHOR,(OUT/'insertion.tex').read_text()+'\n'+ANCHOR))
    save('candidate.json',{'path':str(CAND.relative_to(ROOT)),
        'source_edits':['accounting-product-proposal.tex','chapters/15-banking.tex'],
        'insertion_sha256':sha(OUT/'insertion.tex'),'readiness':'not_ready'})
    print(json.dumps({'candidate':str(CAND.relative_to(ROOT)),'baseline_sources':len(manifest['source_hashes'])}))

if __name__=='__main__':main()
