"""Preserve the provisional first build before repairing its inherited date."""
from hashlib import sha256
from pathlib import Path
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = ROOT / 'docs/design/proposal/manuscript-authoring-scope-20261026'
SAVED = HERE / 'rejected-date-build'
assert not SAVED.exists()
SAVED.mkdir()
for name in ['integrate.py', 'baseline.json', 'build.json', 'build.log', 'verification.json',
             'page-1.png', 'page-102.png', 'page-103.png', 'page-104.png']:
    shutil.copy2(HERE / name, SAVED / name)
for name in ['accounting-product-proposal.tex', 'accounting-product-proposal.pdf', 'accounting-product-proposal.log']:
    shutil.copy2(TARGET / name, SAVED / name)
path = HERE / 'integrate.py'
text = path.read_text()
old = "return text.replace('Version 4.39 (proposal candidate)', 'Version 4.40 (proposal candidate)')"
new = "return text.replace('Version 4.39 (proposal candidate)', 'Version 4.40 (proposal candidate)').replace('25 October 2026', '26 October 2026')"
assert text.count(old) == 1
path.write_text(text.replace(old, new))
source = TARGET / 'accounting-product-proposal.tex'
assert source.read_text().count('25 October 2026') == 1
source.write_text(source.read_text().replace('25 October 2026', '26 October 2026'))
baseline = json.loads((HERE / 'baseline.json').read_text())
baseline['writer_sha256'] = sha256(path.read_bytes()).hexdigest()
(HERE / 'baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
for name in ['build.json', 'build.log', 'verification.json', 'page-1.png', 'page-102.png', 'page-103.png', 'page-104.png']:
    (HERE / name).unlink()
print(json.dumps({'date_repaired': True, 'first_build_preserved': str(SAVED.relative_to(ROOT))}))
