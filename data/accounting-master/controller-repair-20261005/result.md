# Controller repair result before campaign restart

5 October 2026. Scope: MC25, MC27, MC33 and MC34; the proposal-first campaign
continues to preserve MC01–MC35 and G1–G18. Product implementation is disabled.

The nine findings in the preserved controller review have been repaired.
Launch refusal now occurs before Popen and refunds an unused editable attempt;
ordinary invocations cannot exceed 7,200 seconds; failed atomic JSON publication
cleans its own temporary file. Campaign invocations have durable identities,
baselines captured under the runner lock and bound terminal results consumed
exactly once. Partial reviews record absent final files without accepting the
phase. Preservation traversal fails closed. Final proposal checks require
explicit dispositions of upstream blockers and matching PDF/render/review evidence.

The retained test logs report 190 controller tests passing in 45.224 seconds
and 20 current proposal tests passing in 2.279 seconds. The original 17 proposal
test bodies are retained in the current suite; accepted historical test and
format files remain unchanged. The last source-only correction adds the
7,200-second constant to modular review packets. The campaign startup reruns
the current suites and records the exact command and outcome before review.

| Decision | Primary criterion | Veto checks | Main uncertainty | Next action | Limit |
| --- | --- | --- | --- | --- | --- |
| Proceed to startup verification and independent controller review | Targeted fault tests and both current suites passed before the packet correction | Preserved accepted/corpus/source hashes match; pending P16 review remains valid | Fresh independent review has not yet accepted the changed controller | Run the existing approved campaign command; inspect every startup verdict | No P16 acceptance or accounting/forecast validity follows |

Final skeptical inspection verified that campaign accounting consumes a
run-specific manifest rather than a later mutable plan, and a lost update after
a second no-progress run cannot authorize a third run. Incomplete terminal
evidence remains a supervisor stop. The original deadline, retry allowance and
no-progress counter were not reset. Fault tests cover ordinary interruption and
serialized run interleaving; they do not prove arbitrary power-loss behavior or
contain malicious detached workers. A substantive independent objection triggers
repair before further proposal authoring.

P16 is still incomplete: four proposed contracts exist; five contracts, the
initial profile and fourteen decisions remain unfinished. The saved uncertainty
review is next after controller acceptance. The four imported preparation packets
remain candidate inputs. P17–P19 are pending. The executable command is:

```text
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py campaign --max-seconds 172800
```

The stored deadline is `2026-10-06T16:29:46.450619+00:00`, with monotonic deadline
`1940875.230219879` on boot `ffea3b13-9fd0-447f-87a1-8f419eed8a63`.
See `result.json` for source hashes, preservation results and current budget;
the actual startup run manifest and controller receipts supersede this pre-run note.
