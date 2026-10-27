from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-corporate-cohorts-20261015'
NEW = ROOT / 'docs/design/proposal/manuscript-financing-modifications-20261015'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not NEW.exists()
cases = json.loads((OUT / 'cases.json').read_text())
assert cases['passed']
assert sha(OLD / 'accounting-product-proposal.pdf') == 'c359d606ff4e30481fb64b57acd261729c949e2d46d820c8065d3af017558c53'
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
assert text.count('Version 3.10') == 1
path.write_text(text.replace('Version 3.10', 'Version 3.11'))
for name in ['financing-amendment-dates', 'award-modifications', 'net-hedge-timing']:
    method = ROOT / f'docs/design/proposal/methods/{name}-20261015.tex'
    (NEW / f'sections/{name}.tex').write_bytes(method.read_bytes())
changes = [
    ('sections/financing-changes.tex', '\\section{A hedge reserve is neither cash nor a second gain}',
     '\\input{sections/financing-amendment-dates}\n\n'),
    ('sections/awards-participation.tex', '\\hypertarget{participation-allocates-the-numerator-before-division}',
     '\\input{sections/award-modifications}\n\n'),
    ('chapters/14-financing-groups.tex', '\\input{sections/awards-participation}',
     '\\input{sections/net-hedge-timing}\n\n'),
]
for relative, anchor, addition in changes:
    path = NEW / relative
    text = path.read_text()
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, addition + anchor))
repair = json.loads((OUT / 'transition-repair.json').read_text())
path = NEW / repair['path']
text = path.read_text()
assert text.count(repair['before']) == 1
path.write_text(text.replace(repair['before'], repair['after']))
(OUT / 'source-support.json').write_text(json.dumps({
    'sources': cases['sources'],
    'reading_record': str((OUT / 'source-reading.md').relative_to(ROOT)),
    'claims': [
        {'topic': 'amendment dates and discharge',
         'anchors': ['IAS32 13 15–27 AG32–35', 'IFRS9 3.3.1–4 B3.3.1–6', 'IAS7 6 16–17 43–44'],
         'support': 'Historical rules plus supplied legal facts and local journal derivation'},
        {'topic': 'award modifications', 'anchors': ['IFRS2 27 B42–B44C'],
         'support': 'Original/incremental service and cash-to-equity rules; supplied valuations'},
        {'topic': 'groups and net hedges',
         'anchors': ['IFRS9 6.2.3–6.4.1 6.5.8–12 6.6.1–6 B6.6.1–16'],
         'support': 'Eligibility, gross effects, timing and presentation; exact conditional examples'},
    ],
    'limits': 'No actual entity admission, option valuation model, current-rule completeness or runtime conformance',
}, indent=2) + '\n')
print(json.dumps({'version': '3.11', 'preserved_sources': len(sources), 'new_sections': 3}))
