"""One-shot S09 advancement and explicit next-phase refresh."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
NOTE='docs/design/research/company-state-program-20261028/software-and-company-state.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
assert json.loads((H/'attempt-01/verification.json').read_text())['status']=='pass'
assert json.loads((H/'ledger-update.json').read_text())['existing_rows_unchanged']
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
with (H/'program-before.json').open('x') as out:json.dump(old,out,indent=2)
for t in program['tasks']:
 if t['id']=='S09':
  assert t['status']=='planned';t['status']='in_progress'
  t['evidence'] += [NOTE,rel(H/'result.md'),rel(H/'attempt-01/verification.json')]
  t['next_action']='Use connected source/code comparison and concrete follow-on cases: matched Arelle occurrence preservation, QuantLib commit/index/pricer/calendar, ACTUS explicit horizon/observer and matched core, and solver encoding/dependency provenance. Do not repeat fixture arithmetic as external runtime evidence; continue independent ready work while source matching remains open.'
  t['remaining']=['Matched runtime/version/dependency and terms admission; wider software competitors and source-specific omissions. Four inspected component paths do not satisfy the complete S09 survey criterion.']
for a,b in zip(old['tasks'],program['tasks']):
 for k in ['id','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
 if a['id']!='S09':assert a['status']==b['status']
dump(p,program)
entry='''
## Connected software comparison — 28 October 2026

S09 is in_progress after a primary-code comparison of Arelle, QuantLib,
ACTUS service and the local Z3 wrapper. Forty source-identity checks pass;
four source records and nine claims extend all six survey ledgers while
preserving prior rows. Context/value/occurrence, reset/pricer, observer/horizon
and joint-family limits now have concrete follow-on tests. Result:
company-state-software-reuse-20261028/result.md under data/accounting-master.

No external runtime, latest-version or software adoption claim. Wider reuse,
source/dependency matching and other surveys remain incomplete. Twenty-five
original failures reviewed;176 outside this pass. Main reading312/831, resume313.
Only S09 status advances; all criteria/dependencies and frozen releases persist.
E3 deferred. Continue ordered review and independent ready construction/research.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['software_reuse_continuation_20261028']=dict(result=rel(H/'result.md'),source_checks=40,source_records=4,claims=9,all_six_ledgers_updated=True,status='S09 in_progress; external runtime and wider survey incomplete');dump(p,d)
print(json.dumps(dict(status='pass',only_status_changed='S09 planned to in_progress',criteria_preserved=True,source_hashes_verified=len(hashes))))

