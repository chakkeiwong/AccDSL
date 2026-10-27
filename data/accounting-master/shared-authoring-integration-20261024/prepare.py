from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
SOURCE = ROOT / 'docs/design/proposal/manuscript-shared-statements-20261024'
TARGET = ROOT / 'docs/design/proposal/manuscript-shared-authoring-20261024'
def sha(p): return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(), 'candidate already prepared'
    assert not (HERE / 'baseline.json').exists(), 'baseline already recorded'
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == 'e3f8aa4996fa9fc8f582930bceb08e199e72476cb19c30ff2ee00b870acc793e'
    edits = {'accounting-product-proposal.tex': [('Version 3.76 (proposal candidate)', 'Version 3.77 (proposal candidate)')],
        'chapters/06-language.tex': [('while preserving unresolved tax assessment and incomplete fiscal coverage.',
            'while preserving unresolved tax assessment and incomplete fiscal coverage.\nSection~\\ref{sec:shared-book-authoring} authors the complete opening and mixed\nevent sequence through matched declarations and typed records.')]}
    changed = {}
    for name, pairs in edits.items():
        value = (SOURCE / name).read_text()
        for old, new in pairs:
            assert value.count(old) == 1, (name, old)
            value = value.replace(old, new)
        changed[name] = value
    name = 'sections/family-outcome-queries.tex'
    changed[name] = (SOURCE / name).read_text() + '\n\\input{sections/shared-book-authoring}\n'
    hashes = {str(p.relative_to(SOURCE)): sha(p) for p in SOURCE.rglob('*')
              if p.is_file() and p.suffix in ['.tex', '.bib', '.lark']}
    assert len(hashes) == 172, len(hashes)
    baseline = {'source_root': str(SOURCE.relative_to(ROOT)), 'candidate_root': str(TARGET.relative_to(ROOT)),
                'source_hashes': hashes, 'pdf_sha256': sha(SOURCE / 'accounting-product-proposal.pdf')}
    (HERE / 'baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
    for name in hashes:
        p = TARGET / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes((SOURCE / name).read_bytes())
    for name, value in changed.items(): (TARGET / name).write_text(value)
    (TARGET / 'sections/shared-book-authoring.tex').write_bytes((HERE / 'manuscript-section.tex').read_bytes())
    print(json.dumps({'protected_sources': len(hashes), 'candidate': str(TARGET.relative_to(ROOT))}))


if __name__ == '__main__': main()
