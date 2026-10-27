"""Freeze the documentary source unit after its bounded author reading."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    assert not (OUT / 'completion.json').exists()
    ledger = json.loads((OUT / 'source-ledger.json').read_text())
    source = json.loads((OUT / 'source-manifest.json').read_text())
    checks = []

    def ck(name, value):
        checks.append({'check': name, 'passed': bool(value)})

    ck('123 checks pass', ledger['passed'] == 123 and ledger['failed'] == 0)
    ck('twenty rows, sixteen spans and fifty reconciliations', len(ledger['rows']) == 20 and len(ledger['spans']) == 16 and len(ledger['calculations']) == 50)
    ck('source identity intact', sha(ROOT / source['source_pdf']) == source['source_pdf_sha256'])
    for page in source['pages']:
        ck('page ' + str(page['pdf_page']) + ' witnesses intact', all(sha(ROOT / page[k]) == page[k + '_sha256'] for k in ['text','reading_text','image']))
    for item in source['pointer_relocations']:
        ck('earlier control preserved: ' + item['historical_path'], sha(ROOT / item['preserved_path']) == item['sha256'])
    for name in ['result.md','method-consequences.md','author-review.md','next-source-frontier.md','harness-repair.md']:
        ck(name + ' present', (OUT / name).is_file())
    ck('V2.32 intact', sha(ROOT / 'docs/design/proposal/manuscript-bidi-dependencies-20261011/accounting-product-proposal.pdf') == '8dc196a4043f382111d5bddfaf8ec0c75f9297f807ed7555d5621f6eb0703623')
    failed = [r['check'] for r in checks if not r['passed']]
    if failed:
        print(json.dumps({'failed':failed})); raise SystemExit(1)
    hashes = {str(p.relative_to(ROOT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in {'run-manifest.json','completion.json','closeout-checks.json'}}
    plan = 'docs/plans/accounting-jpmorgan-commitments-20261011.md'
    hashes[plan] = sha(ROOT / plan)
    manifest = {'started_on':'2026-10-11','completed_on':'2026-10-12','git_commit':'8b6826ccb4a2a86f940f4ca04931d4a4cd901edb','git_state':'main, unrelated dirty work preserved, .git read-only','plan':plan,'result':str((OUT / 'result.md').relative_to(ROOT)),'data_version':{'source_pdf':source['source_pdf'],'sha256':source['source_pdf_sha256'],'as_of':'2025-12-31'},'commands':[source['extraction_command_template'],'PyMuPDF get_text and get_pixmap(scale=1.35) on source-manifest pages','CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-commitments-20261011/check_sources.py','CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-commitments-20261011/closeout.py'],'environment':{'python':platform.python_version(),'cpu_gpu':'CPU-only, GPU intentionally hidden; no ML imports','random_seeds':'N/A deterministic'},'wall_time':{'initial_extraction_seconds':source['wall_seconds'],'source_check_seconds':json.loads((OUT / 'check-run.json').read_text())['wall_seconds'],'closeout_seconds':time.monotonic()-start,'author_reading':'not separately timed'},'source_checks':ledger['passed'],'closeout_checks':len(checks),'pointer_relocations':source['pointer_relocations'],'control_update':'Version 2.33 integration will reconcile live controls; Version 2.32 stays current meanwhile','artifact_hashes':hashes,'readiness':'not_ready','accounting_authority':'issuer policy evidence only; operative ASC remains unverified','independent_acceptance':'pending'}
    (OUT / 'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (OUT / 'closeout-checks.json').write_text(json.dumps({'checks':checks,'passed':len(checks),'failed':0},indent=2)+'\n')
    (OUT / 'completion.json').write_text(json.dumps({'status':'closed_bounded_commitment_source_reading','source_checks':ledger['passed'],'closeout_checks':len(checks),'failed':0,'manifest_sha256':sha(OUT / 'run-manifest.json'),'readiness':'not_ready'},indent=2)+'\n')
    print(json.dumps({'source_checks':ledger['passed'],'closeout_checks':len(checks),'failed':0}))


if __name__ == '__main__':
    main()
