"""Record completed structural evidence without advancing the manuscript."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PLAN='docs/plans/accounting-nested-contract-source-20261026.md'
RESULT=str((HERE/'result.md').relative_to(ROOT))
NOTE='''## Current internal work — 26 October 2026

Selected term-state structure and semantics pass 74 complete comparisons,
61 controls and 681 assertions; 121 dependency files remain protected.
The native-valid alternative cost pointer is outside the reviewed selection.
Direct source authoring is next, followed by a separate event/carry audit.
Governing Version 5.14 (744 pages) and standalone Version 5.12 remain unchanged.
S1–S5 partial; S6 held; E3 deferred; no whole requirement closes.
Result: data/accounting-master/term-structural-admission-20261026/result.md.
Active plan: docs/plans/accounting-nested-contract-source-20261026.md.

'''

def main():
    assert not (HERE/'control-refresh.json').exists(),'already_refreshed'
    checks=json.loads((HERE/'checks.json').read_text());assert checks['passed'] and checks['full_comparisons']==74
    for n,h in json.loads((HERE/'source-lock.json').read_text()).items():
        assert sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    for n,h in json.loads((HERE/'run-manifest.json').read_text())['implementation_sha256'].items():
        assert sha256((HERE/n).read_bytes()).hexdigest()==h,n
    old='docs/plans/accounting-term-structural-admission-20261026.md'
    names=['MISSION_CONTROL.md','docs/plans/accounting-master-current.md',
      'docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md',
      'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
      'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md',
      'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json',
      'scripts/accounting_master_catalog.json','data/accounting-master/recovery-current-20261026.md']
    before={n:(ROOT/n).read_bytes() for n in names};after={}
    for n,b in before.items():
        if n.endswith('.json'):
            d=json.loads(b);a=d.get('active_execution',d.get('active_execution_note'))
            assert a['active_work_plan']==old,n
            a.update(active_work_plan=PLAN,latest_internal_result=RESULT,
              next=['Direct source for nested invariants and selected term-state contract',
                    'Separately audit exact event/carry binding, then protected manuscript integration',
                    'Continue full gap program; preserve S6 held and E3 deferred'])
            if 'active_work_plans' in a:a['active_work_plans']=[PLAN if x==old else x for x in a['active_work_plans']]
            if 'latest_results' in a:a['latest_results'].append(RESULT)
            if 'completed_increments' in a:a['completed_increments'].append('Selected term-state structure:74 comparisons;61 controls;681 assertions;121 protected files')
            after[n]=json.dumps(d,indent=2)+chr(10)
        elif n.endswith('recovery-current-20261026.md'):
            after[n]='# Current recovery pointer'+chr(10)*2+NOTE+'''Resume the source plan. Structural prepare.py and verify.py completed;
do not rerun their evidence writers. No process is running. The source plan
has been audited; implementation has not started at this checkpoint.
Main PDF: docs/design/proposal/manuscript-nested-invariants-v514-20261026/accounting-product-proposal.pdf
SHA256: 233f22f891ae2d0ded9c3aa7ef046b8f70c5f5cb6a8d9b3cd43c2a64b1424839
Full remaining work: data/accounting-master/gap-program-20261026/remaining-work.md.
Literature: data/accounting-master/literature-closure-20261026/remaining-work.md.
Preserve 53 obligations, six interactions and 46 operations. No commits,
agents, installs, GPU, outreach or publication. Independent review remains pending.
'''
        else:
            first,rest=b.decode().split(chr(10),1);after[n]=first+chr(10)*2+NOTE+rest.lstrip(chr(10))
    for n,b in before.items():
        p=HERE/'control-before'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    for n,b in before.items():assert (ROOT/n).read_bytes()==b,'concurrent_change:'+n
    for n,v in after.items():(ROOT/n).write_text(v)
    records={n:dict(before=sha256(before[n]).hexdigest(),after=sha256((ROOT/n).read_bytes()).hexdigest()) for n in names}
    (HERE/'control-refresh.json').write_text(json.dumps(dict(files=records,plan=PLAN,result=RESULT,manuscript_advanced=False),indent=2)+chr(10))
    print(json.dumps(dict(refreshed=len(names),active_work_plan=PLAN,governing_version='5.14')))

if __name__=='__main__':main()
