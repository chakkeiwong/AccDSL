"""Bind the dated PAA increment to unchanged original acceptance clauses."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'data/accounting-master/release-plan-execution-20261027'
read=lambda p:json.loads(p.read_text());digest=lambda p:sha256(p.read_bytes()).hexdigest()
clauses={r['id']:r for r in read(BASE/'acceptance-clauses.json')['rows']}
originals={r['id']:r for r in read(BASE/'release-acceptance.json')['rows']}
baselines={str((BASE/p).relative_to(ROOT)):digest(BASE/p) for p in ['release-acceptance.json','acceptance-clauses.json']}
support={
 'MC05.03':('The supplied coverage interval and observation boundary give exactly 183/366 elapsed days; changed calendar/event dates refuse.','Actual economic/publication/system clocks and general calendar policies remain separate.'),
 'MC13.03':('Eight native dated transitions preserve full journals, memory, gross cash origins and complete failed prefixes.','No durable commit, actual event admission or general transactional recovery is claimed.'),
 'MC13.05':('Balanced conditional reports retain false source/accounting/posting and fiscal/notes-completeness flags.','Accounting applicability and real company facts require separate evidence.'),
 'MC15.05':('The finite selected example has exact requests, outputs, refusal rules and explicit exclusions in contract.md.','This does not supply every corporate or sector operation.'),
 'MC16.01':('Every opening/closing mapped account and balance/income report field matches independently authored expectations.','Full statutory presentation and complete notes are not supplied.'),
 'MC16.02':('Gross receipts135 and payments54 remain separate; cash movement81 and profit/equity reconcile under the supplied classification.','Actual cash-flow-policy applicability and indirect classification remain unresolved.'),
 'MC16.04':('The eight-event conditional history produces the complete declared interim report through unchanged native interfaces.','The second half-year and full disclosure package are outside this finite example.'),
 'MC22.01':('Separate issued/held groups retain opening, dated movements, typed group memory and closing balances.','Actual cohorts, actuarial calibration and broader group changes remain required.'),
 'MC22.02':('PAA eligibility, service allocation, short claims settlement, transferred risk and non-performance premises are explicit; contradicted or unknown findings refuse appropriately.','General measurement, variable fees, transition, loss recovery and source applicability are not promoted.'),
 'MC22.03':('Issued and held IDs are distinct and linked; event bindings reject substitution and balances/cash remain gross.','No actual group identity has been recovered and more complex treaties remain unsupported.'),
 'MC22.04':('The original selected PAA roll-forward now reaches a dated group/profile/company-book/interim-report interface with complete independent outcomes.','The bounded interface connection is supplied; independent domain/implementation acceptance and broader actuarial/accounting support remain open.'),
 'MC22.05':('The new reference preserves explicit obligations for broader insurer methods and the separate undated recovery-change join.','Those obligations are not discharged by this example.'),
 'MC24.03':('InsurancePAADatedBook/1 names its unchanged program/book/report versions, typed payloads and supported finite domain.','Full grammar/IR coverage, other interfaces and independent implementability remain separate.'),
 'MC24.04':('Independent serialized requests, journals, stages and financial reports predate and agree with native execution for both charts.','This is adapter-to-program conformance, not a general source-to-IR compiler.'),
 'MC25.01':('contract.md defines complete arguments/result variants and preserves stopped native results without a fabricated report.','Other API families and migrations are outside this addition.'),
 'MC25.03':('Source, payload, program, method, state and flow identities are checked; duplicate commands stop on the exact prior state.','General identity/migration and durable idempotency obligations remain.'),
 'MC26.04':('Missing risk or eligibility returns unresolved; outside assumptions return unsupported; malformed identities return invalid.','This finite refusal contract does not establish general solver infeasibility or completeness.'),
 'MC33.01':('Seven complete cases and 21 controls agree with independent expectations; 70 extra checks establish exact cash identities and failed prefixes.','Author conformance is not independent professional or implementation acceptance.'),
 'MC33.04':('Engineering conformance and conditional arithmetic pass; source/accounting/scientific/reader acceptance remain distinct.','No forecast or broad release promotion follows.'),
 'MC34.01':('The result addresses the original MC22 selected-example gap rather than substituting the newer recovery extension.','Other original acceptance conditions are retained verbatim and remain required.'),
 'MC35.02':('Source paragraphs, independent calculations, native compatibility and failure controls were investigated internally.','Broader internal work and focused independent acceptance still remain.')}
rows=[]
for identifier,(increment,residual) in support.items():
    clause=clauses[identifier];acceptance=originals[clause['parent']]['original_condition']['acceptance']
    assert acceptance==clause['original_acceptance'] and sha256(acceptance.encode()).hexdigest()==clause['original_acceptance_sha256']
    rows.append(dict(id=identifier,condition=clause['condition'],original_acceptance=acceptance,
        original_acceptance_sha256=clause['original_acceptance_sha256'],supported_increment=increment,remaining_condition=residual,
        full_requirement_closed=False,scope_waiver=False,disposition='bounded_interface_evidence_added_acceptance_partial'))
names=['contract.md','source-note.md','result.md','preservation.json','source-lock.json','authored-expectations.json',
       'attempt-01/verification.json','attempt-01/run-manifest.json','complete-record-checks.json']
record=dict(date=datetime.now(timezone.utc).isoformat(),baseline_records=baselines,rows=rows,
    evidence={str((HERE/p).relative_to(ROOT)):digest(HERE/p) for p in names},
    MC22_next_action='Integrate this exact interface in the protected specification and seek distinct implementation/domain acceptance after remaining feasible internal work; preserve broader insurer obligations.',
    full_release_closure=False)
with (HERE/'acceptance-supplement.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
lines=['# Dated PAA acceptance increment','','The original selected-example interface gap now has bounded implementation and',
       'complete conformance evidence. Original acceptance wording is unchanged;',
       'broad MC22 and independent acceptance remain open.','','| Clause | Added evidence | Remaining condition |','| --- | --- | --- |']
for row in rows:lines.append(f"| {row['id']} | {row['supported_increment']} | {row['remaining_condition']} |")
lines+=['','See contract.md for the proposed interface and acceptance-supplement.json for',
        'the exact original wording, hashes and evidence identities.','']
with (HERE/'acceptance-supplement.md').open('x') as stream:stream.write('\n'.join(lines))
assert all(digest(ROOT/p)==h for p,h in baselines.items())
print(json.dumps(dict(clauses=len(rows),frozen_records_preserved=True,broad_closures=0)))
