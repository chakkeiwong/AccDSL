"""Preserve the first build and repair the new run-in heading spacing."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
TARGET=ROOT/'docs/design/proposal/manuscript-credit-linked-book-20261025'
SOURCE=ROOT/'docs/design/proposal/manuscript-credit-linked-20261025'
attempt=HERE/'attempt-01-layout';attempt.mkdir()
for name in ['accounting-product-proposal.pdf','accounting-product-proposal.log']:
    shutil.copyfile(TARGET/name,attempt/name)
shutil.copyfile(TARGET/'sections/company-family-language.tex',attempt/'company-family-language.tex')
shutil.copyfile('/tmp/accdsl-credit-book-integration-verify.log',attempt/'verify.log')
old='Map the shared expressions into a separate proposed book.'
new='A separate book retains exact credit amounts.'
addition=(HERE/'book-addition.tex').read_text();assert addition.count(old)==1
(HERE/'book-addition-v2.tex').write_text(addition.replace(old,new))
text=(HERE/'integrate.py').read_text()
text=text.replace('book-addition.tex','book-addition-v2.tex').replace(old,new)
text=text.replace('build.json','build-v2.json').replace('build.log','build-v2.log')
needle="    baseline = json.loads((HERE / 'integration-baseline.json').read_text())"
check="    for name, h in json.loads((HERE / 'layout-repair-lock.json').read_text()).items():\n        assert sha(HERE / name) == h, 'repair_changed:' + name\n"
assert text.count(needle)==1;text=text.replace(needle,check+needle)
compile(text,'integrate_v2.py','exec');(HERE/'integrate_v2.py').write_text(text)
anchor=r"\paragraph{A member's balances can depend on state held by the group.}"
base=(SOURCE/'sections/company-family-language.tex').read_text();assert base.count(anchor)==1
(TARGET/'sections/company-family-language.tex').write_text(base.replace(anchor,(HERE/'book-addition-v2.tex').read_text()+chr(10)*2+anchor))
names=['book-addition-v2.tex','integrate_v2.py','repair_layout.py']
(HERE/'layout-repair-lock.json').write_text(json.dumps({n:sha256((HERE/n).read_bytes()).hexdigest() for n in names},indent=2)+chr(10))
print(json.dumps({'layout_repaired':True,'first_build_preserved':True}))
