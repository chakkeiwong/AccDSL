"""One-shot preparation of a separately locked benefit/tax successor."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
previous=HERE/'corporate-v3';out=HERE/'corporate-v4'
assert not out.exists(), 'Do not rerun preparation'
for pin in json.loads((previous/'run-manifest.json').read_text())['outputs']:
    assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256']
files=json.loads((previous/'predecessor.json').read_text())['files']
for p in sorted(previous.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts:
        files.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out.mkdir()
(out/'predecessor.json').write_text(json.dumps({'profiles':['CorporateComponents/1','CorporateComponents/2','CorporateComponents/3'],'files':files},indent=2)+'\n')
names=['schema_design.py','authored_cases.py','additional_cases.py','additional_checks.py','asset_types.py','asset_cases.py',
    'asset_checks.py','build_exchanges.py','verify_exchanges.py','semantic-contract.md','source-reading.md']
for name in names:
    text=(previous/name).read_text().replace('accdsl.corporate-components-v3.','accdsl.corporate-components-v4.')
    text=text.replace('CorporateComponents/3','CorporateComponents/4')
    (out/name).write_text(text)
print(json.dumps({'prepared':str(out.relative_to(ROOT)),'protected_predecessor_files':len(files)}))
