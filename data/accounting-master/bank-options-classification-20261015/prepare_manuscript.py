from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-financing-modifications-20261015'
NEW = ROOT / 'docs/design/proposal/manuscript-bank-options-20261015'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not NEW.exists()
cases = json.loads((OUT / 'cases.json').read_text())
assert cases['passed']
assert sha(OLD / 'accounting-product-proposal.pdf') == 'cc009f7d98a34039c4ad61d1a3dd36e8ed65f4f731c555a26f03c78bd003ee3a'
sources = sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex', '.bib', '.lark'])
for path in sources:
    target = NEW / path.relative_to(OLD)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
(OUT / 'manuscript-baseline.json').write_text(json.dumps({
    'baseline': str(OLD.relative_to(ROOT)),
    'pdf_sha256': sha(OLD / 'accounting-product-proposal.pdf'),
    'candidate': str(NEW.relative_to(ROOT)),
    'source_files': [{'path': str(p.relative_to(OLD)), 'sha256': sha(p)} for p in sources],
}, indent=2) + '\n')
path = NEW / 'accounting-product-proposal.tex'
text = path.read_text()
assert text.count('Version 3.11') == 1
path.write_text(text.replace('Version 3.11', 'Version 3.12'))
for name in ['bank-asset-classification', 'bank-option-transfers']:
    method = ROOT / f'docs/design/proposal/methods/{name}-20261015.tex'
    (NEW / f'sections/{name}.tex').write_bytes(method.read_bytes())
changes = [
    ('chapters/15-banking.tex', '\\input{sections/bank-methods}',
     '\\input{sections/bank-asset-classification}\n\n', 'before'),
    ('sections/bank-methods.tex', '\\input{sections/bank-transfer-fees}',
     '\n\n\\input{sections/bank-option-transfers}', 'after'),
]
for relative, anchor, addition, direction in changes:
    path = NEW / relative
    text = path.read_text()
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, addition + anchor if direction == 'before' else anchor + addition))
repair = json.loads((OUT / 'presentation-repair.json').read_text())
path = NEW / repair['path']
text = path.read_text()
assert text.count(repair['before']) == 1
path.write_text(text.replace(repair['before'], repair['after']))
(OUT / 'source-support.json').write_text(json.dumps({
    'sources': cases['sources'],
    'reading_record': str((OUT / 'source-reading.md').relative_to(ROOT)),
    'claims': [
        {'topic': 'retained options and collars',
         'anchors': ['IFRS9 3.2.2–23 B3.2.4–17'],
         'support': 'Prior risk/control findings, conditional measurement and non-duplication; local cash/equity derivations'},
        {'topic': 'asset classification and measurement',
         'anchors': ['IFRS9 4.1.1–5 4.3.2 4.4.1 B4.1.1–26 5.5.1–2 5.7.5–11 B5.7.1–1A'],
         'support': 'Business model, cash flows and distinct debt/equity reporting routes; conditional comparisons'},
    ],
    'limits': 'Historical authority, supplied pricing/ECL and conditional legal facts; no current bank admission or runtime conformance',
}, indent=2) + '\n')
print(json.dumps({'version': '3.12', 'preserved_sources': len(sources), 'new_sections': 2}))
