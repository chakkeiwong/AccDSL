"""Create a separate 2.38 candidate; frozen 2.37 stays unchanged."""
import json
import shutil
from prepare import OUT, ROOT, BASE, sha, save

CAND = ROOT / 'docs/design/proposal/manuscript-visible-text-20261012'
BIB = r'''
@misc{hsbc2023annualcover,
  author = {{HSBC Holdings plc}},
  title = {Annual Report and Accounts 2023},
  year = {2023},
  url = {https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2023/annual/pdfs/hsbc-holdings-plc/240226-annual-report-and-accounts-2023.pdf},
  note = {Annual-report year; retained 450-page PDF, cover (physical page 1).
          Local extraction, render and painting-order inspection, 12 October 2026}
}
'''
ANCHOR = 'The inspected Arelle interfaces support native XBRL contexts, dimensions,'

def main():
    assert not CAND.exists(), 'Never overwrite a candidate'
    baseline = json.loads((OUT/'baseline.json').read_text())
    for rel, digest in baseline['source_hashes'].items():
        assert sha(BASE/rel) == digest
        dest = CAND/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(BASE/rel,dest)
    title = CAND/'accounting-product-proposal.tex'
    old = title.read_text()
    assert old.count('Version 2.37 (proposal candidate)') == 1
    title.write_text(old.replace('Version 2.37 (proposal candidate)','Version 2.38 (proposal candidate)'))
    section = CAND/'sections/adapter-methods.tex'
    old = section.read_text()
    assert old.count(ANCHOR) == 1
    section.write_text(old.replace(ANCHOR,(OUT/'insertion.tex').read_text()+'\n'+ANCHOR))
    bib = CAND/'references.bib'
    assert 'hsbc2023annualcover' not in bib.read_text()
    bib.write_text(bib.read_text()+BIB)
    save('candidate.json',{'candidate':str(CAND.relative_to(ROOT)),
        'changed_sources':['accounting-product-proposal.tex','sections/adapter-methods.tex','references.bib'],
        'insertion_sha256':sha(OUT/'insertion.tex'), 'scope':'One observed PDF title failure and proposed exchange; no runtime adapter.'})
    print(json.dumps({'candidate':str(CAND.relative_to(ROOT)),'baseline_source_files':len(baseline['source_hashes'])}))

if __name__ == '__main__':
    main()
