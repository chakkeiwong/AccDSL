"""Capture audit provenance once; never refresh a protected baseline in place."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = ROOT / 'docs/design/proposal/manuscript-fiscal-timeline-20261025'
ORIGINAL = ROOT / 'data/accounting-master/simulator-gap-reassessment-20261025/original-obligations.json'
EXPECTED_PDF = '2c9e72249cbc28aadcb6ded520165b6ee86bcbff88adc634afc05740ee9ac8f9'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = OUT / 'baseline.json'
    if target.exists():
        raise SystemExit('Baseline already exists; verify it rather than overwriting it.')
    original = json.loads(ORIGINAL.read_text())
    groups = original['groups']
    counts = {k: len(v) for k, v in groups.items()}
    assert counts == {'obligations': 53, 'interactions': 6, 'operations': 46}, counts
    for rows in groups.values():
        assert len({r['id'] for r in rows}) == len(rows)
    pdf = DOC / 'accounting-product-proposal.pdf'
    assert digest(pdf) == EXPECTED_PDF
    files = [ORIGINAL, pdf, ROOT / 'docs/plans/accounting-current-design-reconciliation-20261025.md']
    files += sorted(p for p in DOC.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.sty', '.cls'})
    inventory = []
    for path in files:
        row = {'path': str(path.relative_to(ROOT)), 'sha256': digest(path), 'bytes': path.stat().st_size}
        if path.suffix == '.tex':
            row['headings'] = [{'line': i, 'text': line.strip()} for i, line in enumerate(path.read_text().splitlines(), 1)
                               if line.lstrip().startswith(('\\chapter', '\\section', '\\subsection', '\\input'))]
        inventory.append(row)
    (OUT / 'original-obligations.json').write_bytes(ORIGINAL.read_bytes())
    target.write_text(json.dumps({'date': '2026-10-26', 'version': '4.39', 'status': 'not_ready',
                                 'counts': counts, 'files': inventory}, indent=2) + '\n')
    (OUT / 'audit-status.json').write_text(json.dumps({
        'baseline': 'baseline.json', 'judgment': 'in_progress',
        'groups': {key: [{'id': r['id'], 'review_status': 'uninspected'} for r in rows]
                   for key, rows in groups.items()}}, indent=2) + '\n')
    print(json.dumps({'baseline_files': len(inventory), 'counts': counts, 'pdf_verified': True}))


if __name__ == '__main__':
    main()
