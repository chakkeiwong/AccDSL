"""One-shot master refresh after successful W05 financing evidence."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
v=read(HERE/'attempt-02/checks.json');assert v['passed'] and (v['comparisons'],v['controls'],v['assertions'])==(20,34,283)
for n,h in read(HERE/'attempt-02/source-lock.json').items():assert sha(ROOT/n)==h,n
manifest=read(HERE.parent/'term-execution-integration-20261026/verification.json')
assert sha(ROOT/'docs/AccDSL-latest.pdf')==manifest['pdf_sha256']
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')=='63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5'
names=[n for n in read(HERE.parent/'term-execution-integration-20261026/control-input-hashes.json')
       if n not in ['docs/README.md','docs/design/README.md']]
before={n:(ROOT/n).read_bytes() for n in names};backup=HERE/'control-before'
assert not backup.exists() and not (HERE/'control-refresh.json').exists(),'already_refreshed'
plan='docs/plans/accounting-financing-remedy-binding-20261026.md'
result='data/accounting-master/financing-opening-invariants-20261026/result.md'
remaining='data/accounting-master/financing-opening-invariants-20261026/remaining-work.md'
assert (ROOT/plan).is_file() and (ROOT/result).is_file()
note=f'''## Current internal work — financing invariants — 26 October 2026

W05 selected claim/share/missed-history invariants and opening admission pass
20 full comparisons, 24 snapshots, 34 controls and 283 assertions; 36 dependency
files remain protected. Memory-omitting methods and plausible history rewrites
are refused while accepted prefixes survive. Fiscal openings remain distinct
from intermediate snapshots; the first verifier error and repair are preserved.
Governing Version 5.15 (747 pages), standalone Version 5.12 and all broad
obligations remain unchanged. This result awaits manuscript integration.
Next: selected E03 conditional remedy binding under {plan}.
Result: {result}.
Remaining work: {remaining}.
S1–S5 partial; S6 held; E3 forecasting deferred. No whole requirement closes.

'''
proposed={}
for n,b in before.items():
    if n.endswith('.json'):
        data=json.loads(b);key='active_execution_note' if n.startswith('scripts/') else 'active_execution'
        a=data[key];protected={k:deepcopy(value) for k,value in a.items() if k.startswith(('full_gap','gap_program','literature'))}
        a.update(active_work_plan=plan,latest_internal_result=result,remaining_work=remaining,
                 next=['Bind E03 selected event/default/acceleration/rescission distinctions to typed execution',
                       'Protected manuscript integration for W05/E01/E02/E03 companions',
                       'Continue full gap/literature queues; S6 held and E3 deferred'])
        if 'active_work_plans' in a:
            a['active_work_plans']=[plan]+[p for p in a['active_work_plans'] if p not in [plan,'docs/plans/accounting-financing-opening-invariants-20261026.md']]
        if 'completed_increments' in a and result not in a['completed_increments']:a['completed_increments'].append(result)
        assert all(a[k]==value for k,value in protected.items())
        proposed[n]=json.dumps(data,indent=2,ensure_ascii=False)+chr(10)
    elif n.endswith('recovery-current-20261026.md'):
        proposed[n]='# Current recovery pointer'+chr(10)*2+note+f'''Stable main links select Version 5.15, 747 pages, not_ready.
PDF SHA256: {manifest['pdf_sha256']}.
Term integration and financing attempt-02 are complete and frozen. Do not rerun
successful writers. No process is running. Continue the selected remedy plan.
Preserve all 53 obligations, six interactions, 46 operations, 18 broad packages,
full gap-program and literature residuals. Independent reader acceptance remains
pending and does not block feasible internal work.
'''
    else:
        first,rest=b.decode().split(chr(10),1)
        value=first+chr(10)*2+note+rest.lstrip(chr(10))
        lines=[]
        for line in value.splitlines():
            if line.startswith('Current question:'):line='Current question: how do selected conditional remedies enter typed execution without erasing economic history?'
            elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
            elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
            lines.append(line)
        proposed[n]=chr(10).join(lines)+chr(10)
for n,b in before.items():
    q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
for n,b in before.items():assert (ROOT/n).read_bytes()==b,'concurrent_change:'+n
for n,value in proposed.items():(ROOT/n).write_text(value)
for n in names:assert plan in (ROOT/n).read_text() and result in (ROOT/n).read_text()
assert sha(ROOT/'docs/AccDSL-latest.pdf')==manifest['pdf_sha256']
(HERE/'control-refresh.json').write_text(json.dumps(dict(updated_files={n:dict(before=sha256(before[n]).hexdigest(),after=sha(ROOT/n)) for n in names},
 next_plan=plan,latest_result=result,governing_unchanged=True,whole_requirements_closed=0),indent=2)+chr(10))
print(json.dumps(dict(updated=len(names),candidate='5.15',next_plan=plan)))
