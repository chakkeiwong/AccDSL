"""Record scoped pricing/status cases without endogenous service promotion."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==109
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==35
comparisons={
 'SIM-F025':'Retained S/R example: face80 prices80/40 and leaves equity20/50. At committed equal proceeds80, faces80/160 leave equity20/10. Conditional arithmetic exposes safe-price/risky-policy mismatch; dynamic equilibrium not implemented.',
 'SIM-F028':'Zero-budget endogenous price returnsUnknown with formula/remainder. Explicit offered face100/proceeds80/quote0.8 still executes under two native maps without injected default. Iterative convergence and a general service router remain untested.',
 'SIM-F029':'All nonnegative faces partition into three exact regions with unbounded flat tail100. Need110 infeasible in every region; a false positive tail slope yields face10140 but original payoff still100.'}
for ident,comparison in comparisons.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_scoped_pricing_and_numerical_status_discriminator',comparison=comparison,
  evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Actual offer/policy/asset evidence, equilibrium and service integration remain open; local failed channel or solverUnknown is not company default.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);d['scope']='Thirty-eight original rows individually reviewed;163 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Thirty-eight original rows reviewed;163 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id'] in ['C04','T07']:t['evidence'].append(rel(H/'result.md'))
 if t['id']=='C04':
  t['next_action']='Thirty-eight original failures reviewed;163 outside this pass. Continue measurement/information/scenario failures and ordered reading from337, while T03 source dependencies remain active.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Thirty-five original rows')]
  t['remaining'].append('Thirty-eight original rows individually compared;163 outside this pass. Dynamic endogenous policy/service integration and actual-source/operation completeness remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Pricing policy and numerical outcomes — 28 October 2026

SIM-F025/028/029 pass109 checks across39 solver cases and two native programs.
Exact S/R arithmetic exposes commitment/price mismatch. Whole-domain debt pricing
cannot fund110 from capacity100, including unlimited face. A zero-budget Unknown
does not invalidate an explicit conditional offer or create default. Result:
company-state-pricing-policy-failures-20261028/result.md under data/accounting-master.
Dynamic equilibrium/service integration and actual economic admission remain open.

Thirty-eight original failures reviewed;163 outside this pass. Main reading
336/831, resume337. All original criteria/statuses and releases persist.
E3 deferred. Continue measurement/information failures, source and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;d=json.loads(p.read_text());d[key]['pricing_policy_continuation_20261028']=dict(result=rel(H/'result.md'),checks=109,native_cases=2,solver_cases=39,reviewed_original_failures=38,outside_pass=163,scope='Conditional exact pricing/policy/status examples; no endogenous service or actual admission');dump(p,d)
print(json.dumps(dict(reviewed=38,outside_pass=163,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
