"""Create a separate, exactly delimited Version 2.40 manuscript."""
import json
import shutil
from complete_sources import OUT, ROOT, sha, save

BASE = ROOT / 'docs/design/proposal/manuscript-funds-transfer-20261012'
CAND = ROOT / 'docs/design/proposal/manuscript-dividend-timing-20261012'
ANCHOR = 'Debt amounts add a second distinction.'

def main():
    assert not CAND.exists()
    baseline = json.loads((OUT / 'baseline.json').read_text())
    assert sha(BASE / 'accounting-product-proposal.pdf') == baseline['inputs'][str((BASE / 'accounting-product-proposal.pdf').relative_to(ROOT))]
    source_files = sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'})
    hashes = {str(p.relative_to(BASE)): sha(p) for p in source_files}
    for source in source_files:
        dest = CAND / source.relative_to(BASE)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    title = CAND / 'accounting-product-proposal.tex'
    old = title.read_text()
    assert old.count('Version 2.39 (proposal candidate)') == 1
    title.write_text(old.replace('Version 2.39 (proposal candidate)', 'Version 2.40 (proposal candidate)'))
    chapter = CAND / 'chapters/15-banking.tex'
    old = chapter.read_text()
    assert old.count(ANCHOR) == 1
    chapter.write_text(old.replace(ANCHOR, (OUT / 'insertion.tex').read_text() + '\n' + ANCHOR))
    bib = CAND / 'references.bib'
    bib.write_text(bib.read_text() + '\n' + (OUT / 'new-references.bib').read_text())
    save('candidate.json', {'path': str(CAND.relative_to(ROOT)), 'baseline': str(BASE.relative_to(ROOT)),
         'baseline_pdf_sha256': sha(BASE / 'accounting-product-proposal.pdf'), 'source_hashes': hashes,
         'insertion_sha256': sha(OUT / 'insertion.tex'), 'new_references_sha256': sha(OUT / 'new-references.bib'),
         'source_plan_original': baseline['inputs']['docs/plans/accounting-national-bank-dividend-authority-20261012.md'],
         'source_plan_adapted': sha(ROOT / 'docs/plans/accounting-national-bank-dividend-authority-20261012.md'),
         'integration_plan': sha(ROOT / 'docs/plans/accounting-dividend-timing-integration-20261012.md'),
         'readiness': 'not_ready'})
    print(json.dumps({'candidate': str(CAND.relative_to(ROOT)), 'baseline_sources': len(hashes)}))

if __name__ == '__main__':
    main()
