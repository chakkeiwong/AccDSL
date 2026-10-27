# P08 and master repair execution

Authorised by the user's request to review, refresh and execute the repair.
Requirements: MC15, MC17, MC19, MC25, MC30 and MC33–MC35. The stopped run
`20261003T075910-81c6e8bb` and the root-cause investigation are the baseline.
P00–P07 and P11 acceptance and P12's checked pending review must survive.

## Skeptical review of the proposed repair

The diagnosis supports the repairs, but its proposed multi-file publication
framework and general subtask scheduler are larger than necessary. Use the P08
JSON as the single canonical commit: assemble in memory, validate, preserve the
previous bytes, and atomically replace it. The existing narrative is supplementary
and cannot confer acceptance. A failure before replacement leaves the previous
bundle; the checker must reject a stale bundle after source edits.

Keep the existing phase scheduler. Add an explicit partial-work verdict, checks
after editable timeout/failure, a durable checked continuation, and fresh reviewed
planning before another partial-work attempt. Select a bounded P08 task from
current checker findings and the finite task descriptions in its catalog. A
partial outcome never becomes acceptance. Repeated unchanged failure must defer
that phase until relevant inputs change or the operator explicitly retries it.

The original broad plan wrongly assumed authority closure and complete regime
implementation would fit one 900-second worker. The new stages are: coherent
bundle; exact source disposition; admitted authority and lifecycle implementation;
matched comparison and final verification. Source disposition remains separate
from admission. No second regime may pass by relabelling AASB claims. Treat a
failed retrieval as evidence about that route, with a precise remaining claim.

The exact original economic facts and all four phase criteria remain fixed.
Tests, quotation presence and source counts cannot establish accounting validity.
An explicit incomplete completion field vetoes acceptance even if a reviewer
returns AGREE. The master must use the standalone P08 checker once, including
its unit suite, instead of a weaker test-only substitute.

Audit decision: proceed with the reduced implementation above. No unfair method
comparison, new environment dependency or expanded permission is necessary.
Retain v3–v5 as historical evidence and validate actual inputs before promotion.

## Evidence contract and bounded execution

Question: do these repairs preserve verified progress, prevent false phase
acceptance, and enable the real second-regime work? Comparator: diagnosed code
and preserved partial results. Engineering pass requires the focused controller
fault tests, P08 replay, reproducible validated publication, explicit criterion
veto, fresh review of changed control paths, and an actual master invocation.
P08 completion additionally requires admitted same-fact lifecycles for both
settlement outcomes and independent review of the exact checked candidate.

Continuation vetoes: live unidentified writer, protected-byte changes, invalid
controller/approval boundary, or unrecoverable checker records. Candidate failures
trigger narrower repair; missing authority blocks only dependent admission.
Counts/timings are explanatory. A bounded AASB/EU agreement cannot close the
wider MC19 differing-treatments requirement, professional validity or any G1–G18.

Defaults: existing Python/standard library; deterministic CPU checks; 900-second
worker limit, two repairs and 7,200-second invocation retained. Reserve 300 seconds
of invocation time for supervisor checks before launching editable work (the
current P08 checker takes about 28 seconds; the existing check cap is 300).
This is an operational limit, not an accounting criterion. No new worker starts
without this reserve. Stop or exhausted time preserves the checked continuation.

Validation commands: `python3 -m unittest discover -s tests -p test_accounting_master.py`;
`python3 -B scripts/build_accounting_p08.py`; `python3 -B scripts/check_accounting_p08.py --check`.
Record outputs and pre-edit hashes under
`data/accounting-master/p08-execution-repair-20261003/`. Controller review is
bound to the resulting code/test/plan hashes; old verdicts cannot be copied onto
new bytes. Source disposition and product repair use the existing authorised
sequential workers and their independent plan/result reviews.

Run after verification and review:
`python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py run`.
Check that exact command against the installed narrow rule. Update checkpoint
and next plan from observed state; preserve the pending P12 review.

## Live execution correction and source-preparation completion

Run `20261003T115045-50f3dc47` demonstrated timeout cleanup, passing supervisor
checks and fresh reviewed replanning after the draft source dossier was written.
Monitoring then exposed a missing status transition: replanning left needs_repair
persisted during the next work window, while the real internal checker requires
running/repairing. The supervisor requested an orderly stop before that check,
verified no child survivors and repaired the transition. A new regression uses
the actual locked helper subprocess after partial work, rather than an injected
checker. The full controller suite now passes 115 tests. A stop request also
defers verification without launching another child.

The stopped repair worker had made no file changes. The supervisor therefore
executes its already reviewed source-integrity plan directly. Its independent
AGREE is retained in P08/replan-1/review_plan-0.response.json of that run.
This work validates typed RDF relationships, anchors, pins, coverage and honest
pending dispositions, and integrates them with the builder/checker. It does not
decide legal applicability or enable the EU lifecycle. The draft is preserved
as p08-v6/pre-validation-source-disposition.json. Mutation checks must reject
wrong-subject predicates, citation/amendment confusion, omitted corrections,
stale pins, invalid assumptions and premature admission. The AASB cases and
common economics must equal the preserved baseline. This reduced plan passes
the audit because its artifacts answer integrity/integration questions without
promoting them into accounting conclusions.
