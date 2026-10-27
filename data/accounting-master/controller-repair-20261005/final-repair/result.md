# Controller finding adjudication and restart

5 October 2026. Engineering scope: MC25, MC27, MC33 and MC34. The authorized
campaign remains proposal-only. P16 is incomplete; phase acceptance is unchanged.

The two fresh independent rounds (`20261005T083051-60af77f3` and
`20261005T085703-069c7255`) supplied concrete additional findings after the
original nine repairs. The supervisor inspected each path, implemented repairs
and ran fault tests. The final controller disposition uses the existing
“Controller review after repair” policy in `docs/plans/accounting-master-program.md`.
It is **supervisor finding adjudication**, not seven independent AGREE verdicts.
All original review responses remain preserved. `adjudication.json` records
each of the 22 findings, its repair and verification.

The latest seven findings are repaired as follows:

1. A newly launched, unreaped direct child anchors cleanup even if identity
   metadata repeatedly fails. The known initial group receives bounded signals;
   quiescence is checked before reaping. Unverifiable cleanup remains a durable
   `cleanup_required` stop and cannot authorize another worker.
2. SIGINT/SIGTERM are deferred across supervisor event/process publication,
   flush/fsync and expected-hash updates. Publication errors still veto.
3. Unknown editable phases are rejected before budgets, queries or model work.
4. Malformed active-process records are validated, preserved and recorded in a
   startup-stop record and terminal manifest with no executable next plan.
5. Malformed campaign input is preserved and replaced with a recovery status;
   neither a new deadline nor a new allowance is inferred.
6. Each required suite reports discovery, executed and skipped counts and its
   result. Empty or fully skipped required suites fail even when the companion
   suite passes.
7. P18 counts pages from the actual PDF, requires all page numbers, and binds
   that complete set into render/review evidence. A two-page PDF with one
   rendered page fails.

Executed commands in the project Python environment:

```text
python3 -m unittest discover -s tests -p test_accounting_master.py
python3 -m unittest discover -s tests -p test_accounting_proposal_current.py
git diff --check -- scripts/run_accounting_master.py scripts/accounting_master_support.py tests/test_accounting_master.py docs/plans/accounting-master-program.md
```

**205 controller tests passed in 47.180 seconds; 21 proposal tests passed in
2.453 seconds.** All 1,301 preservation checks passed. AST comparison confirmed
all 17 historical proposal test methods remain unchanged in the successor suite.
The saved P16 uncertainty review is still valid. The command logs,
`preservation.json` and run manifest retain exact source hashes and environment.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Limit |
| --- | --- | --- | --- | --- | --- |
| Resume after supervisor adjudication | Every material recorded finding has a concrete repair and executed regression | Current suites, protected evidence and saved-review validity pass | Reviews/tests can miss defects; P16 substance and later phases remain unfinished | Fresh startup suites, then independent P16 uncertainty review and remaining architecture work | No product readiness, accounting validity, forecast quality or human acceptance |

Post-review: the trusted single-writer model excludes hostile same-user forgery,
deliberate detached children and uncatchable failure between fork and durable
registration. Ordinary handled interruption and accidental mutations are covered
by targeted checks, not arbitrary power-loss certification. A malformed state
with unavailable filesystem writes cannot promise a persisted recovery record;
the controller must fail rather than invent successful recovery. Valid operator
stop requests always block response acceptance. The original deadline and
phase retry allowance remain unchanged. No additional approval is required by
this adjudication; it implements the standing continuation instruction.
