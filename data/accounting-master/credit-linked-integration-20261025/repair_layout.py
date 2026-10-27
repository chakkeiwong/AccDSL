"""Preserve the first build and shorten the provenance line without deletion."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
TARGET=ROOT/'docs/design/proposal/manuscript-credit-linked-20261025'
SOURCE=ROOT/'docs/design/proposal/manuscript-insurance-statement-20261025'
attempt=HERE/'attempt-01-layout'; attempt.mkdir()
for name in ['accounting-product-proposal.pdf','accounting-product-proposal.log']:
    shutil.copyfile(TARGET/name,attempt/name)
shutil.copyfile(TARGET/'sections/company-family-language.tex',attempt/'company-family-language.tex')
shutil.copyfile('/tmp/accdsl-credit-linked-integration-verify.log',attempt/'verify.log')
old=(HERE/'credit-addition.tex').read_text()
needle='Complete exchanges and refusal evidence are retained in\n\\path{data/accounting-master/credit-linked-measurements-20261025/}. Three'
replacement='Complete exchanges and refusal evidence are retained under\n+{\\small\\path{data/accounting-master/}} in the directory\n+{\\small\\path{credit-linked-measurements-20261025/}}. Three'
replacement=replacement.replace('\n+','\n')
assert old.count(needle)==1
(HERE/'credit-addition-v2.tex').write_text(old.replace(needle,replacement))
text=(HERE/'integrate.py').read_text()
text=text.replace('credit-addition.tex','credit-addition-v2.tex').replace('build.json','build-v2.json').replace('build.log','build-v2.log')
needle2="    baseline = json.loads((HERE / 'integration-baseline.json').read_text())"
addition="    for name, h in json.loads((HERE / 'layout-repair-lock.json').read_text()).items():\n        assert sha(HERE / name) == h, 'repair_changed:' + name\n"
assert text.count(needle2)==1; text=text.replace(needle2,addition+needle2)
compile(text,'integrate_v2.py','exec'); (HERE/'integrate_v2.py').write_text(text)
anchor=r"\paragraph{A member's balances can depend on state held by the group.}"
base=(SOURCE/'sections/company-family-language.tex').read_text(); assert base.count(anchor)==1
(TARGET/'sections/company-family-language.tex').write_text(base.replace(anchor,(HERE/'credit-addition-v2.tex').read_text()+'\n\n'+anchor))
names=['credit-addition-v2.tex','integrate_v2.py','repair_layout.py']
(HERE/'layout-repair-lock.json').write_text(json.dumps({n:sha256((HERE/n).read_bytes()).hexdigest() for n in names},indent=2)+'\n')
print(json.dumps({'layout_repaired':True,'first_build_preserved':True}))
