"""One-shot information-case reconciliation; preserve original acceptance."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['passed'] and v['checks']==165
hashes=json.loads((H/'attempt-01/source-hashes.json').read_text())
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text());assert len(d['rows'])==79
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
comparisons={'LIT-F010': ('Saved quiet-coupon histories share current cash but contract rights change actions; cash-only merge refuses and augmented-state full-path equality remains.', 'Issuer-specific sufficient state and general Markov justification remain open.'), 'LIT-F011': ('Twelve equal-likelihood updates preserve three priors and both persistent types; expected coupon26/5 replaces neither coupon5 nor7.', 'Actual observation model identification remains open.'), 'LIT-F012': ('Zero evidence retains a structured conflict. Separately identified repair proposals retain the original; revised likelihood may resolve or retain conflict without automatic admission.', 'Real source/model diagnosis and general repair integration remain open.'), 'LIT-F013': ('Exact(.99)^100 extinction remains positive; conditional strata keep common/distress types with supplied masses and explicit finite scope.', 'Within-type approximation, SMC integration and actual rare-type evidence remain open.'), 'LIT-F014': ('Retained replacement and full-history evidence selects6 before correction,5 at publication,6 in original view; independent conflicting aliases survive.', 'Corpus-wide source meaning, lineage and correction authority remain open.'), 'LIT-F015': ('Hypothetical fixed/floating branches preserve the actual unavailable view. Later supplied receipt resolves floating; conflicting fixed assumption refuses overwrite.', 'General actor/context integration, actual access and source admission remain open.')}
for ident,(comparison,next_action) in comparisons.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_literature_information_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action=next_action,original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=85
d['scope']='85 original rows individually reviewed;116 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 85 original rows reviewed;116 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='85 original failures reviewed;116 outside this pass. Inspect LIT-F016 onward against retained finance and runtime evidence; continue connected sources and ordered reading367.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('79 original rows')]
  t['remaining'].append('85 original rows individually compared;116 outside this pass. Actual information/source/likelihood premises, remaining literature cases, source-backed construction and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='\n## Persistent types and information contexts — 28 October2026\n\nLIT-F010–015 pass165 exact checks with16 result groups,12 refusal controls\nand four retained evidence units. Equal likelihood preserves uncertainty;\nzero evidence retains conflict through proposed repair; hypothetical branches\nleave actual dated views unchanged. Real source and inference premises stay open.\nResult: company-state-information-reconciliation-20261028/result.md under data/accounting-master.\n\n85 original failures reviewed;116 outside this pass. Main reading366/831,\nresume367. Original criteria/statuses/releases persist;E3 deferred.\nContinue finance literature cases, connected sources and ordered review.\n\n'
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
No global continuation veto. Main review366/831;next367.

Next: inspect LIT-F016 onward, separating face/proceeds/yield/carrying amount,
market-access refusal, dilution, recovery allocation and conversion effects.
Reuse complete retained results only when they match original requirements.
Continue source research and ordered reading367. READ-0358-0360-01 stays open.
Do not rerun one-shot scripts. Concurrent edits stay separate; the prior
checkpoint is retained in this unit/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['information_reconciliation_continuation_20261028']=dict(result=rel(H/'result.md'),checks=165,result_groups=16,refusal_controls=12,reused_units=4,reviewed_original_failures=85,outside_pass=116,scope='Finite conflict/repair and actual/hypothetical separation; no calibrated inference or source admission');dump(p,data)
print(json.dumps(dict(reviewed=85,outside_pass=116,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
