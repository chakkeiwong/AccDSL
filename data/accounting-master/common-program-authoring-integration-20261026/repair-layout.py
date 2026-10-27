"""Preserve the first build and repair only stretched provenance lines."""
from pathlib import Path
from hashlib import sha256
import json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10);BS=chr(92)
TARGET=ROOT/'docs/design/proposal/manuscript-common-program-20261026'
archive=HERE/'attempt-01';archive.mkdir()
for name in ['build.json','build.log','verification.json','baseline.json','common-program-authoring.tex']:
 shutil.copy2(HERE/name,archive/name)
for suffix in ['pdf','log']:shutil.copy2(TARGET/('accounting-product-proposal.'+suffix),archive/('accounting-product-proposal.'+suffix))
p=HERE/'common-program-authoring.tex';before=p.read_text();marker='The field inventory and grammar design are retained under'
assert before.count(marker)==1
after=before.replace(marker,BS+'begingroup'+BS+'raggedright'+NL+marker)
after=after.replace('20261026/}; the'+NL+'implementation and checks are under','20261026/}.'+NL+'The implementation and checks are under')
assert after.endswith(BS+'par'+NL)
after+=BS+'endgroup'+NL
p.write_text(after);(TARGET/'sections'/p.name).write_text(after)
b=json.loads((HERE/'baseline.json').read_text());b['added']['common-program-authoring']=sha256(p.read_bytes()).hexdigest()
(HERE/'baseline.json').write_text(json.dumps(b,indent=2)+NL)
(HERE/'build.json').rename(archive/'build-original.json')
print(json.dumps({'previous_attempt_preserved':True,'repair':'Ragged-right provenance paragraph; two sentences; no substantive change'}))
