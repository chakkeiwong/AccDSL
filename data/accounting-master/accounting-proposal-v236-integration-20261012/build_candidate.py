"""Create Version 2.36 as a separate candidate from protected Version 2.35."""
import hashlib
import json
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'docs/design/proposal/manuscript-parent-cash-20261012'
CAND = ROOT / 'docs/design/proposal/manuscript-debt-perimeter-20261012'
EXPECTED = '23d1d9da1b599bf5caee7aca7ce6559c0afa1d0ae077504800d97acd8652b7e7'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert sha(BASE / 'accounting-product-proposal.pdf') == EXPECTED
    assert not CAND.exists(), 'Never overwrite an existing candidate'
    sources = [p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}]
    source_hashes = {str(p.relative_to(BASE)): sha(p) for p in sources}
    for p in sources:
        target = CAND / p.relative_to(BASE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    title = CAND / 'accounting-product-proposal.tex'
    old = title.read_text()
    anchor = 'Version 2.35 (proposal candidate)'
    assert old.count(anchor) == 1
    title.write_text(old.replace(anchor, 'Version 2.36 (proposal candidate)'))
    chapter = CAND / 'chapters/15-banking.tex'
    old = chapter.read_text()
    marker = '\\newpage\n\nThe complete Form~10-Ks describe Series~A as the issuer\'s direct, unsecured'
    assert old.count(marker) == 1
    chapter.write_text(old.replace(marker, (OUT / 'addition.tex').read_text() + marker))
    snapshots = []
    (OUT / 'pointers-before').mkdir(exist_ok=True)
    for rel in ['docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-master-current.md', 'docs/plans/accounting-continuation-requirements-20261007.md', 'data/accounting-master/next-plan.md']:
        p = ROOT / rel
        target = OUT / 'pointers-before' / p.name
        assert not target.exists()
        shutil.copyfile(p, target)
        snapshots.append({'live': rel, 'snapshot': str(target.relative_to(ROOT)), 'sha256': sha(target)})
    baseline = {'baseline_pdf': {'path': str((BASE / 'accounting-product-proposal.pdf').relative_to(ROOT)), 'sha256': EXPECTED, 'pages': 174}, 'candidate': str(CAND.relative_to(ROOT)), 'source_hashes': source_hashes, 'pointer_snapshots': snapshots, 'source_unit': 'data/accounting-master/jpmorgan-debt-perimeter-20261012'}
    (OUT / 'baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
    print(json.dumps({'candidate': baseline['candidate'], 'author_sources': len(sources), 'controls_preserved': len(snapshots)}))

if __name__ == '__main__': main()
