"""One-shot customer successor preparation, preserving all frozen profiles."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
previous=HERE/'corporate-v4';out=HERE/'corporate-v5'
assert not out.exists(),'Do not rerun preparation'
for pin in json.loads((previous/'run-manifest.json').read_text())['outputs']:
    assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256']
files=json.loads((previous/'predecessor.json').read_text())['files']
for p in sorted(previous.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts:
        files.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out.mkdir()
(out/'predecessor.json').write_text(json.dumps({'profiles':['CorporateComponents/'+str(i) for i in range(1,5)],'files':files},indent=2)+'\n')
for p in sorted(previous.iterdir()):
    if p.suffix=='.py' or p.name in ['semantic-contract.md','source-reading.md']:
        text=p.read_text().replace('accdsl.corporate-components-v4.','accdsl.corporate-components-v5.')
        text=text.replace('CorporateComponents/4','CorporateComponents/5')
        (out/p.name).write_text(text)
print(json.dumps({'prepared':str(out.relative_to(ROOT)),'protected_predecessor_files':len(files)}))
