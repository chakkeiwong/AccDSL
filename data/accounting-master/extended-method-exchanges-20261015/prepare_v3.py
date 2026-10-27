"""One-shot preparation of a separate, reviewable asset-exchange successor."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
previous = HERE / 'corporate-v2'
out = HERE / 'corporate-v3'
assert not out.exists(), 'Do not rerun successor preparation'
for pin in json.loads((previous / 'run-manifest.json').read_text())['outputs']:
    assert hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256']
files = []
for directory in [HERE / 'corporate', previous]:
    for p in sorted(directory.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            files.append({'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
out.mkdir()
(out / 'predecessor.json').write_text(json.dumps({'profiles': ['CorporateComponents/1', 'CorporateComponents/2'], 'files': files}, indent=2) + '\n')
for name in ['schema_design.py', 'authored_cases.py', 'additional_cases.py', 'additional_checks.py',
             'build_exchanges.py', 'verify_exchanges.py', 'semantic-contract.md', 'source-reading.md']:
    text = (previous / name).read_text().replace('accdsl.corporate-components-v2.', 'accdsl.corporate-components-v3.')
    text = text.replace('CorporateComponents/2', 'CorporateComponents/3')
    (out / name).write_text(text)
print(json.dumps({'prepared': str(out.relative_to(ROOT)), 'protected_predecessor_files': len(files)}))
