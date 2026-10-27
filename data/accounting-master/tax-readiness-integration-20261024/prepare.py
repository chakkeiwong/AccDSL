from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
SOURCE = ROOT / 'docs/design/proposal/manuscript-shared-authoring-20261024'
TARGET = ROOT / 'docs/design/proposal/manuscript-tax-information-20261024'
def sha(p): return sha256(p.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(), 'candidate already prepared'
    assert not (HERE / 'baseline.json').exists(), 'baseline already recorded'
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == '53a52b7cd5b0ce30ce3a9eed284d297baf467348a2a9ee82f100f6f44db85702'
    edits = {'accounting-product-proposal.tex': [('Version 3.77 (proposal candidate)', 'Version 3.78 (proposal candidate)')],
        'chapters/06-language.tex': [('event sequence through matched declarations and typed records.',
            'event sequence through matched declarations and typed records.\nSection~\\ref{sec:shared-tax-information} separates supplied tax declarations\nfrom executable tax rules and explains the remaining mixed-book incompatibility.')]}
    changed = {}
    for name, pairs in edits.items():
        value = (SOURCE / name).read_text()
        for old, new in pairs:
            assert value.count(old) == 1, (name, old)
            value = value.replace(old, new)
        changed[name] = value
    name = 'sections/family-outcome-queries.tex'
    changed[name] = (SOURCE / name).read_text() + '\n\\input{sections/shared-tax-information}\n'
    hashes = {str(p.relative_to(SOURCE)): sha(p) for p in SOURCE.rglob('*')
              if p.is_file() and p.suffix in ['.tex', '.bib', '.lark']}
    assert len(hashes) == 173, len(hashes)
    baseline = {'source_root': str(SOURCE.relative_to(ROOT)), 'candidate_root': str(TARGET.relative_to(ROOT)),
                'source_hashes': hashes, 'pdf_sha256': sha(SOURCE / 'accounting-product-proposal.pdf')}
    (HERE / 'baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
    for name in hashes:
        p = TARGET / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes((SOURCE / name).read_bytes())
    for name, value in changed.items(): (TARGET / name).write_text(value)
    (TARGET / 'sections/shared-tax-information.tex').write_bytes((HERE / 'manuscript-section.tex').read_bytes())
    print(json.dumps({'protected_sources': len(hashes), 'candidate': str(TARGET.relative_to(ROOT))}))


if __name__ == '__main__': main()
