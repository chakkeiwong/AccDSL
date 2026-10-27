from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-bank-options-20261015'
NEW = ROOT / 'docs/design/proposal/manuscript-insurance-branches-20261015'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not NEW.exists()
cases = json.loads((OUT / 'cases.json').read_text())
assert cases['passed']
assert sha(OLD / 'accounting-product-proposal.pdf') == 'd08c6612845a7391d5c7cf51bb154642b99955ac95413e966a7aea638fc5237b'
sources = sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex', '.bib', '.lark'])
for path in sources:
    target = NEW / path.relative_to(OLD)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
(OUT / 'manuscript-baseline.json').write_text(json.dumps({
    'baseline': str(OLD.relative_to(ROOT)), 'pdf_sha256': sha(OLD / 'accounting-product-proposal.pdf'),
    'candidate': str(NEW.relative_to(ROOT)),
    'source_files': [{'path': str(p.relative_to(OLD)), 'sha256': sha(p)} for p in sources],
}, indent=2) + '\n')
path = NEW / 'accounting-product-proposal.tex'
text = path.read_text()
assert text.count('Version 3.12') == 1
path.write_text(text.replace('Version 3.12', 'Version 3.13'))
for name in ['insurance-modification-values', 'insurance-paa-cost-finance',
             'insurance-variable-fee', 'insurance-finance-process']:
    method = ROOT / f'docs/design/proposal/methods/{name}-20261015.tex'
    (NEW / f'sections/{name}.tex').write_bytes(method.read_bytes())
changes = [
    ('sections/insurance-methods.tex', 'Reinsurance has its own group, boundary, recognition time,',
     '\\input{sections/insurance-paa-cost-finance}\n\n\\subsection{Reinsurance and direct participation}\n\n'),
    ('sections/insurance-methods.tex', '\\input{sections/insurance-treaty-changes}',
     '\\input{sections/insurance-variable-fee}\n\n'),
    ('sections/insurance-methods.tex', '\\section{Claims development estimates the remaining payments}',
     '\\input{sections/insurance-finance-process}\n\n'),
    ('sections/insurance-treaty-changes.tex', '\\hypertarget{future-service-consumes-csm-before-creating-a-loss}',
     '\\input{sections/insurance-modification-values}\n\n'),
]
for relative, anchor, addition in changes:
    path = NEW / relative
    text = path.read_text()
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, addition + anchor))
(OUT / 'source-support.json').write_text(json.dumps({
    'sources': cases['sources'], 'reading_record': str((OUT / 'source-reading.md').relative_to(ROOT)),
    'claims': [
        {'topic': 'modification and transfer', 'anchors': ['IFRS17 44 48–50 72–77 91'],
         'support': 'Eligibility, equivalent-premium adjustment, CSM/loss ordering, OCI origin; local bridges'},
        {'topic': 'PAA acquisition and claim finance', 'anchors': ['IFRS17 53–59 81 B72 B126–127 B133'],
         'support': 'Acquisition choices, financing clocks, onerous addition and claim-incurrence-rate OCI allocation'},
        {'topic': 'direct participation and finance', 'anchors': ['IFRS17 45 48–50 81–92 B101–B119 B128–B136'],
         'support': 'Eligibility, variable fee, service/finance separation, mitigation and OCI policies'},
        {'topic': 'joint process laws', 'anchors': ['IFRS17 B37–B41 B49–B55 B65 B74–B78 B86–B89', 'Local exact binary-law derivation'],
         'support': 'Measurement and assumption obligations; exact family, conditional transitions and nonlinear recovery'},
    ],
    'limits': 'Historical source, supplied actual-entity valuations/eligibility/RA, finite synthetic laws; no calibration, runtime or full readiness',
}, indent=2) + '\n')
print(json.dumps({'version': '3.13', 'preserved_sources': len(sources), 'new_sections': 4}))
