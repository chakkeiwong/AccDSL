"""Attach bank conformance to unchanged original conditions; close no broad row."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'data/accounting-master/release-plan-execution-20261027'
read=lambda p:json.loads(p.read_text());digest=lambda p:sha256(p.read_bytes()).hexdigest()
clauses={r['id']:r for r in read(BASE/'acceptance-clauses.json')['rows']}
originals={r['id']:r for r in read(BASE/'release-acceptance.json')['rows']}
baseline={str((BASE/n).relative_to(ROOT)):digest(BASE/n) for n in ['acceptance-clauses.json','release-acceptance.json']}
support={
 'MC21.01':('The compatibility map identifies exact closed asset/liability/deposit/collateral/credit/capital records and their complete retained cases. Copied record, source and state checks pass.',
             'A composite same-basis whole-bank state, wider instruments and independent implementation/domain acceptance remain open.'),
 'MC21.02':('Existing credit, funding and liquidity methods and capital/query operations are collected with exact contracts, profiles, version boundaries and refusal behavior. All selected complete exchanges replay.',
             'No automatic /1-to-/2 migration or AU-to-US accounting conversion is admitted. Broader methods and actual source/applicability facts remain separate.'),
 'MC21.03':('The already connected US worked case independently reconstructs its dated book before capital; allowance expense is not deducted twice, cap ordering is retained, and missing averages leave leverage unresolved. Unchanged ratios coexist with nine unpaid deposits in the stress case.',
             'Historical conditional rules, supplied CECL, eligibility and average assets do not establish actual-bank applicability, regulatory compliance, permissible payout or calibrated risk.'),
 'MC21.04':('The selected US opening/final/two-runoff/missing-average cases, AU credit/transfer methods and exact-time successor reproduce with complete reports or query results. Explicit later-operation scope is consolidated instead of inventing another isolated example.',
             'The map and reproduction supplement still need integration into the protected specification. Broader sector composition, actual facts and distinct independent acceptance remain required; positive recovery stays a separate dependent operation.')
}
rows=[]
for key,(increment,residual) in support.items():
    c=clauses[key];original=originals[c['parent']]['original_condition']['acceptance']
    assert c['original_acceptance']==original and sha256(original.encode()).hexdigest()==c['original_acceptance_sha256']
    rows.append(dict(id=key,condition=c['condition'],original_acceptance=original,
        original_acceptance_sha256=c['original_acceptance_sha256'],supported_increment=increment,
        remaining_condition=residual,disposition='bounded_original_condition_evidence_consolidated_acceptance_partial',
        full_requirement_closed=False,scope_waiver=False))
names=['result.md','compatibility-map.md','execution-audit.md','preservation.json',
       'preparation-02/bundle-manifest.json','attempt-01/checks.json','attempt-01/run-manifest.json',
       'worked-case-extract.json','bank-interface-bundle.tar.gz']
record=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),baseline_records=baseline,rows=rows,
    evidence={str((HERE/p).relative_to(ROOT)):digest(HERE/p) for p in names},full_release_closure=False,
    MC21_next_action='Integrate exact profile boundaries and reproduction references into the protected specification; preserve wider composition, applicability and independent-acceptance obligations.')
with (HERE/'acceptance-supplement.json').open('x') as f:json.dump(record,f,indent=2);f.write(chr(10))
lines=['# Bank acceptance evidence consolidated','','The four original MC21 subconditions have specific retained evidence and',
       'remaining work. No original wording or broad acceptance status changes.','',
       '| Clause | Supported evidence | Remaining condition |','| --- | --- | --- |']
for row in rows:lines.append('| '+row['id']+' | '+row['supported_increment']+' | '+row['remaining_condition']+' |')
with (HERE/'acceptance-supplement.md').open('x') as f:f.write(chr(10).join(lines)+chr(10))
assert all(digest(ROOT/p)==h for p,h in baseline.items())
print(json.dumps(dict(clauses=len(rows),frozen_acceptance_preserved=True,broad_closures=0)))
