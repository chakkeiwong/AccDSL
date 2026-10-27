"""Retain reading-order text of the already downloaded filing ranges."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'extractions.json').exists()
    tick = time.monotonic()
    base = read(OUT / 'baseline.json')
    previous = ROOT / base['prior_manifest']
    assert sha(previous) == base['prior_manifest_sha256']
    assert read(previous.with_name('completion.json'))['manifest_sha256'] == sha(previous)
    reloc = {r['historical_path']: r['preserved_path'] for r in base['pointer_relocations']}
    inherited = {reloc.get(p, p): h for p, h in read(previous)['artifact_hashes'].items()}
    assert len(inherited) == base['prior_references'] == 1982
    bad = [p for p, h in inherited.items() if not (ROOT / p).is_file() or sha(ROOT / p) != h]
    assert not bad, bad[:5]
    ledger = read(ROOT / 'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json')
    bounds = {2022: (44, 306), 2023: (46, 324), 2024: (50, 336), 2025: (44, 330)}
    receipts = []
    (OUT / 'reading-order').mkdir(exist_ok=True)
    for row in ledger['records']:
        year = row['period_year']
        pdf = ROOT / row['roles']['complete_issuer_10k']['path']
        assert sha(pdf) == row['roles']['complete_issuer_10k']['sha256']
        end, signature = bounds[year]
        for name, first, last in [('front', 3, end), ('signatures', signature, signature)]:
            target = OUT / 'reading-order' / f'{year}-{name}.txt'
            assert not target.exists()
            cmd = ['pdftotext', '-f', str(first), '-l', str(last), rel(pdf), rel(target)]
            started, t = datetime.now(timezone.utc).isoformat(), time.monotonic()
            p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
            body = target.read_text()
            pages = body.split('\f')
            assert pages[-1] == '' and len(pages) - 1 == last - first + 1
            receipts.append(dict(year=year, role=name, source_pdf=rel(pdf), source_sha256=sha(pdf),
                text=rel(target), sha256=sha(target), pdf_first_page=first, pdf_last_page=last,
                printed_first_page=first - 2, printed_last_page=last - 2,
                page_count=len(pages)-1, command=cmd, exit_code=p.returncode, stderr=p.stderr,
                started_at=started, wall_seconds=time.monotonic()-t))
    report = dict(recorded_at=datetime.now(timezone.utc).isoformat(), prior_references=len(inherited),
        tool_version=subprocess.run(['pdftotext','-v'],capture_output=True,text=True).stderr,
        receipts=receipts, wall_seconds=time.monotonic()-tick,
        cpu_gpu_status='CPU only; GPU devices intentionally hidden; no model imports',
        full_semantic_reading=False)
    (OUT / 'extractions.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(prior_verified=len(inherited), extractions=len(receipts),
                         retained_pages=sum(r['page_count'] for r in receipts))))


if __name__ == '__main__':
    main()
