"""Record support/cure composition after amount-only cure repair."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-02/verification.json').read_text());assert v['status']=='pass' and v['checks']==193
hashes=json.loads((H/'attempt-02/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as fh:json.dump(dict(program=old,dispositions=d),fh,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==43
for ident,comparison in {
 'SIM-F041':'Exact capacity80->64 creates deficiency6; conditional native support2 lets subsidiary repay6 but leaves parent3 unable to pay4. Missing parent effect fails independent shared-history check; actual guarantee accounting/atomic group service unclaimed.',
 'SIM-F044':'Native fee-first6 leaves interest1/principal100; principal-first leaves94/arrears7. Separate timestamp assessment consumes native remaining arrears and explicit exclusive deadline. Amount-only cure defect in attempt01 repaired in attempt02.'}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_scoped_support_priority_cure_discriminator',comparison=comparison,evidence=[rel(H/'attempt-02/verification.json'),rel(H/'result.md')],next_action='Actual support/priority/remedy rights, accounting treatment, linked settlement and intraday facts remain open; native day-level execution is not intraday cure service.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=45;d['scope']='45 original rows individually reviewed;156 outside this continuation. Original criteria/statuses persist; scoped composition is not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 45 original rows reviewed;156 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='45 original failures reviewed;156 outside this pass. Continue quiet rights, query/projection/dependence and information/scenario cases, source dependencies and ordered reading from349.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('43 original rows')]
  t['remaining'].append('45 original rows individually compared;156 outside this pass. Source-backed rights, exact predecessor binding, linked settlement/intraday semantics and complete operations remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Support feedback and allocation-aware cure — 28 October2026

SIM-F041/044 pass193 checks across18 native programs and15 separate timing
assessments. Support2 resolves subsidiary deficiency6 but leaves parent3
against payment4. Payment priority and remaining arrears determine cure.
Attempt01's amount-only cure defect is retained and repaired. Result:
company-state-support-cure-20261028/result.md under data/accounting-master.
Actual rights/accounting, atomic group and native intraday execution stay open.

45 original failures reviewed;156 outside this pass. Main reading348/831,
resume349. Original criteria/statuses/releases persist;E3 deferred.
Continue quiet rights/query/dependence cases, source and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading348/831;resume349. No global continuation veto.

Next: audit original SIM-F045 quiet call rights; SIM-F047 projection x=z+1,
z in[0,2]; SIM-F048 persistent paths(0,10)/(10,0); SIM-F050 linked x-x;
SIM-F051 sample endpoint. Reuse exact solver and retained method evidence,
preserving unknowns and scope. Continue source and ordered review in parallel
only where independent. Do not rerun completed one-shot refresh scripts.
Concurrent research edits remain separately owned; stage only exact changes.
Prior checkpoint: company-state-support-cure-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['support_cure_continuation_20261028']=dict(result=rel(H/'result.md'),checks=193,native_cases=18,timing_cases=15,reviewed_original_failures=45,outside_pass=156,scope='Conditional support and allocation-linked cure; no actual or native intraday admission');dump(p,data)
print(json.dumps(dict(reviewed=45,outside_pass=156,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
