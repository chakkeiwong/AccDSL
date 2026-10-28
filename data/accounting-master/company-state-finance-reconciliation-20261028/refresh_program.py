"""One-shot finance-case reconciliation; preserve original acceptance."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['passed'] and v['checks']==219
hashes=json.loads((H/'attempt-01/source-hashes.json').read_text())
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text());assert len(d['rows'])==85
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
comparisons={'LIT-F016': ('Original law gives face100, proceeds1880/21, yield11/94 and mixed-law lender gap-44/101. Retained native cash/carrying and face memory are distinct.', 'Source edition/erratum correspondence and actual pricing/recognition remain open.'), 'LIT-F017': ('Need95 leaves115/21 gap: full-payment request refuses, explicit payment89 replans, partial-payment policy retains arrears115/21.', 'Actual market access, legal priority and distress choices remain open.'), 'LIT-F018': ('Retained S/R exact conditional stress distinguishes safe price80/equity20 from risky price40/equity50; committed risky face160 raises80/equity10.', 'General coupled pricing/policy solver and actual commitment remain open.'), 'LIT-F019': ('Estate70 allocates60/10 under supplied senior priority; estate130 gives60/50/20. Unknown rank retains alternatives; independent recovery overdraws.', 'Actual collateral/claim population and legal priority remain open.'), 'LIT-F020': ('Junior claim extinguishes before original estate100 allocation60/16/24. Stale debt and duplicate conversion refuse; separate native160/16 evidence retains full books.', 'Rich security rights and source-backed accounting remain open.')}
for ident,(comparison,next_action) in comparisons.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_literature_finance_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action=next_action,original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=90
d['scope']='90 original rows individually reviewed;111 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 90 original rows reviewed;111 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='90 original failures reviewed;111 outside this pass. Inspect LIT-F021 onward against original equity/control requirements and retained evidence; continue connected sources and ordered reading367.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('85 original rows')]
  t['remaining'].append('90 original rows individually compared;111 outside this pass. Actual financing/rights/source premises, remaining literature cases, source-backed construction and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='\n## Finance identities and exclusive claims — 28 October2026\n\nLIT-F016–020 pass219 exact checks with12 result groups,11 refusal controls\nand four retained evidence units. Need95 preserves its115/21 shortfall;\nexplicit conversion extinguishes junior debt before allocation60/16/24.\nActual prices, access, priorities and accounting remain unverified.\nResult: company-state-finance-reconciliation-20261028/result.md under data/accounting-master.\n\n90 original failures reviewed;111 outside this pass. Main reading366/831,\nresume367. Original criteria/statuses/releases persist;E3 deferred.\nContinue equity/control literature cases, connected sources and ordered review.\n\n'
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
No global continuation veto. Main review366/831;next367.

Next: inspect LIT-F021 onward and exact equity/control evidence requirements.
Reuse full saved records where appropriate; do not infer whole-case coverage
from matching names or arithmetic. Continue source research and reading367.
READ-0358-0360-01 remains for successor repair after diagnosis. Do not rerun
one-shot scripts. Concurrent work stays separate; prior checkpoint retained.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['finance_reconciliation_continuation_20261028']=dict(result=rel(H/'result.md'),checks=219,result_groups=12,refusal_controls=11,reused_units=4,reviewed_original_failures=90,outside_pass=111,scope='Finite funding and exclusive-claim examples; no actual pricing, rights or accounting admission');dump(p,data)
print(json.dumps(dict(reviewed=90,outside_pass=111,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
