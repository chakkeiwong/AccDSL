from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
target=ROOT/'docs/design/proposal/manuscript-event-contract-20261026'
archive=HERE/'attempt-01';assert not archive.exists();archive.mkdir()
for name in ['build.json','build.log','verification.json','baseline.json','authored-event-contract.tex']:
    p=HERE/name;(archive/name).write_bytes(p.read_bytes())
for name in ['accounting-product-proposal.pdf','accounting-product-proposal.log']:
    (archive/name).write_bytes((target/name).read_bytes())
p=HERE/'authored-event-contract.tex';text=p.read_text();text+=NL+chr(92)+'par'+NL
p.write_text(text);(target/'sections/authored-event-contract.tex').write_text(text)
baseline=json.loads((HERE/'baseline.json').read_text());baseline['added']['authored-event-contract']=sha256(p.read_bytes()).hexdigest()
(HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+NL)
(HERE/'build.json').unlink()
(HERE/'layout-repair.md').write_text('# Explicit paragraph termination'+NL*2+
 'Attempt 1 built 544 pages but added four underfull warnings in the final paragraph.'+NL+
 'Rendered pages 510–511 show stretched lines before the following section. The'+NL+
 'included subsection ended without an explicit paragraph break before closing'+NL+
 'nested inputs. Add only a final paragraph terminator; preserve every word,'+NL+
 'equation and evidence path. Initial PDF/log/hash/section retained in attempt-01.'+NL+
 'Rebuild and compare warnings before accepting this repair.'+NL)
print('Archived initial layout and added explicit paragraph terminator')
