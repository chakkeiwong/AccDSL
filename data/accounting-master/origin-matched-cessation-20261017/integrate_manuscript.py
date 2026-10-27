"""Create a protected successor once; preserve every predecessor source body."""
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'docs/design/proposal/manuscript-zero-cost-collar-20261017'
NEXT = ROOT / 'docs/design/proposal/manuscript-origin-matched-cessation-20261017'
ADDITION = '\n' + r'\input{sections/origin-matched-cessation}' + '\n'


def main():
    assert not NEXT.exists(), 'Preserve existing successor'
    files = sorted(p for p in BASE.rglob('*')
                   if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'})
    assert len(files) == 141
    assert not (OUT / 'baseline-source-lock.json').exists()
    records = []
    for path in files:
        relative = path.relative_to(BASE)
        for target in (OUT / 'baseline-sources' / relative, NEXT / relative):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        records.append(dict(path=str(relative), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (OUT / 'baseline-source-lock.json').write_text(json.dumps(
        dict(baseline=str(BASE.relative_to(ROOT)), files=records), indent=2) + '\n')
    title = NEXT / 'accounting-product-proposal.tex'
    text = title.read_text()
    assert text.count('Version 3.40 (proposal candidate)') == 1
    title.write_text(text.replace('Version 3.40 (proposal candidate)', 'Version 3.41 (proposal candidate)'))
    section = NEXT / 'sections/partial-hedge-discontinuation.tex'
    section.write_text(section.read_text() + ADDITION)
    shutil.copy2(OUT / 'cessation.tex', NEXT / 'sections/origin-matched-cessation.tex')
    print(json.dumps(dict(version='3.41', protected_sources=len(files), new_sections=1)))


if __name__ == '__main__':
    main()
