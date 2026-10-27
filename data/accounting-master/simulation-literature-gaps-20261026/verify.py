"""Check this assessment's integrity; not a scientific method validation."""
from pathlib import Path
from urllib.parse import unquote, urlparse
import hashlib
import json
import fitz

base = Path(__file__).resolve().parent
root = base.parents[2]
recovery = json.loads((base / 'source-recovery.json').read_text())
gaps = json.loads((base / 'gaps.json').read_text())
checks = []

def check(name, passed, **details):
    checks.append(dict(check=name, passed=bool(passed), **details))

for source in recovery['sources']:
    local = root / source['local_path']
    download = root / source['download_path']
    digest = hashlib.sha256(local.read_bytes()).hexdigest()
    with fitz.open(local) as doc:
        pages = len(doc)
    check('Retained PDF identity, original bytes and pages',
          digest == source['sha256'] and local.read_bytes() == download.read_bytes()
          and pages == source['pages'], id=source['id'], pages=pages, sha256=digest)

check('Nine unique gap families with closure evidence and proposed-only checks',
      len(gaps['records']) == 9 and len({g['id'] for g in gaps['records']}) == 9
      and all(g['closure_evidence'] and all(c['status'].startswith('proposed')
              for c in g['proposed_checks']) for g in gaps['records']))
for gap in gaps['records']:
    for anchor in gap['existing_anchors']:
        check('Existing gap anchor file', (root / anchor['path']).is_file(),
              id=gap['id'], path=anchor['path'])

for name in ['source-support.json', 'omissions.json']:
    ledger = json.loads((root / 'docs/design/research' / name).read_text())
    record = next(r for r in ledger['records'] if r.get('id') == 'mccarthy1982')
    check('Live McCarthy access status is repaired', record['status'].startswith('RECOVERED')
          and any(s.get('dossier') == str(base.relative_to(root))
                  for s in ledger['supplement_updates']), ledger=name)
    check('Original blocked record preserved in recovery evidence',
          recovery['historical_mccarthy_records'][name]['status'].startswith('SOURCE_BLOCKED'),
          ledger=name)

# These authored files contain ordinary inline links without nested parentheses.
# Split the exact delimiter to avoid the escaped-regex error in the first check.
for name in ['result.md', 'source-reading.md']:
    path = base / name
    for part in path.read_text().split('](')[1:]:
        target_text = part.split(')', 1)[0].split('#', 1)[0]
        if urlparse(target_text).scheme:
            continue
        target = (path.parent / unquote(target_text)).resolve()
        check('Assessment local link resolves', target.exists(), source=name,
              target=str(target.relative_to(root)))

pdf = root / 'docs/design/proposal/manuscript-insurance-identity-20261026/accounting-product-proposal.pdf'
digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
check('Governing baseline PDF unchanged',
      digest == '1f83ca1205813a28cc3cbe4576653531ecd6c4b8d80c6ef70e88684110cf5e63',
      sha256=digest)
for name in ['docs/plans/accounting-mission-requirements.md',
             'docs/plans/accounting-product-design-checkpoint.md']:
    check('Dated assessment supplement recorded',
          '## Simulation literature assessment — 26 October 2026' in (root / name).read_text(),
          path=name)

manifest = []
for path in sorted((base / 'sources').iterdir()):
    if path.is_file():
        manifest.append(dict(path=str(path.relative_to(root)),
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                             bytes=path.stat().st_size))
(base / 'source-manifest.json').write_text(json.dumps(dict(
    date='2026-10-26', files=manifest,
    scope='Retained sources, metadata and derived page images; failed-response bodies not retained'),
    indent=2) + chr(10))

result = dict(date='2026-10-26', status='PASS' if all(c['passed'] for c in checks) else 'FAIL',
              check_count=len(checks), source_file_count=len(manifest), checks=checks,
              command='python3 data/accounting-master/simulation-literature-gaps-20261026/verify.py',
              earlier_check_repair='The initial link regex included an opening parenthesis in paths; this checker parses the exact inline-link delimiter. No manuscript link change was needed.',
              limits=['Assessment/source integrity only; no method-transfer, solver or empirical validation.',
                      'No independent human reader or domain acceptance.',
                      'No manuscript, current execution queue or solver default changed.'])
(base / 'verification.json').write_text(json.dumps(result, indent=2) + chr(10))
print(json.dumps(dict(status=result['status'], checks=len(checks),
                      source_files=len(manifest), failures=[c for c in checks if not c['passed']]), indent=2))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
