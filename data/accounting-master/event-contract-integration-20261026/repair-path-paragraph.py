from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10);BS=chr(92)
target=ROOT/'docs/design/proposal/manuscript-event-contract-20261026';archive=HERE/'attempt-02'
assert not archive.exists();archive.mkdir()
for name in ['build.json','build.log','verification.json','baseline.json','authored-event-contract.tex']:(archive/name).write_bytes((HERE/name).read_bytes())
for name in ['accounting-product-proposal.pdf','accounting-product-proposal.log']:(archive/name).write_bytes((target/name).read_bytes())
p=HERE/'authored-event-contract.tex';text=p.read_text()
old='remain unresolved. The source boundary, counterexamples and selected-contract'+NL+'evidence are retained under'+NL+BS+'path{data/accounting-master/authored-event-prerequisite-audit-20261026/} and'+NL+BS+'path{data/accounting-master/authored-event-contract-20261026/}.'
new='remain unresolved.'+NL*2+'The source boundary and counterexamples are retained under'+NL+BS+'path{data/accounting-master/authored-event-prerequisite-audit-20261026/}.'+NL+'The selected-contract evidence is retained under'+NL+BS+'path{data/accounting-master/authored-event-contract-20261026/}.'
assert old in text;text=text.replace(old,new);p.write_text(text);(target/'sections/authored-event-contract.tex').write_text(text)
baseline=json.loads((HERE/'baseline.json').read_text());baseline['added']['authored-event-contract']=sha256(p.read_bytes()).hexdigest()
(HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+NL);(HERE/'build.json').unlink()
with (HERE/'layout-repair.md').open('a') as f:f.write(NL+'Explicit paragraph termination alone did not remove the warnings. Attempt 2 is'+NL+
 'preserved. Separate the two long source paths from the scientific limitation'+NL+
 'and give each path its own sentence, preserving all content and source targets.'+NL)
print('Archived attempt 2 and separated source-path sentences')
