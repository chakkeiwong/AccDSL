# Populated source contracts for repeated company claims

25 October 2026. S2–S4; MC01–05/07–13/16/19/20/24–28/30/32–35.

Question: can a declared company book admit more than one source-backed
invoice or claim across reporting periods while preserving source time,
economic time, revised terms, claim identity, settlement state and the complete
financial-statement consequences? The current receivable lifecycle is a
typed synthetic contract with initially empty claims. The next boundary must
exercise populated source-backed contracts; it must not infer that the
synthetic sale case is a filing reconstruction.

The comparator is the existing typed lifecycle and CompanyBookTransition/2.
The smallest case is two identified claims for one named customer/book: one
original constructed assertion, one revised assertion with a distinct availability
view, a due date, a partial receipt and a remaining balance crossing a period
boundary. A second customer or claim must retain its own identity. Preserve
reported, extracted, derived and assumed fields separately. A missing amount,
unreadable term, conflicting revision and unsupported recognition treatment
must remain tagged; none becomes zero or a guessed date.

Skeptical audit before implementation: a balanced journal does not prove that
the source identifies an invoice or that a revised filing supersedes an older
assertion. A repeated label is not a claim identity. A later available filing
cannot enter an earlier information view. Carrying an assessed claim into a
later period must not assess a newly introduced claim, and a receipt must not
rewrite the original sale. The existing lifecycle's strict-after-due-date
policy and sealed assessment date are hypotheses to retain only where the
source contract declares them. A document build, populated row count or
balance equality is explanatory; exact source/claim bindings and adverse
refusals are primary.

Evidence contract: pass only when every accepted claim has a stable source span,
context, view, amount/term status, owner/book/customer, original event and
replay identity; each revised assertion retains its predecessor relation and
availability boundary; partial receipt and assessment update only the selected
claim; annual reports reconcile cash, receivable, income and operating cash
flow for the declared synthetic case. Veto on altered source bytes, duplicate
claim identity, future information leakage, missing required premise, negative
unexplained balance, non-atomic update or replay mismatch. Explanatory
diagnostics include counts and balance checks. Do not conclude filing
completeness, accounting compliance, tax correctness, real-company truth or
forecast performance.

Use a read-only source fixture with local byte locks, exact command-text
roundtrip, focused tests, predecessor regressions, a run manifest and replay.
Keep source evidence, interpretation, assumption, history family and
scenario-specific result separate. No external retrieval or paid review is
needed for this bounded synthetic/source-contract comparison. If the source
contract cannot supply a required premise, record an unresolved case and
continue any independent identity/typing checks. Promotion of this boundary
does not close whole-company reconstruction or annual statement coverage.

After this contract survives, add the smallest revised-term and multi-period
adapter, then decide whether a manuscript successor is warranted. Keep bank
and insurance methods on their own native profiles and keep E3 forecasting
deferred until the simulator and source vintages are ready.

## Qualified execution scope

The pre-execution audit at
`data/accounting-master/populated-source-contracts-20261025/audit.md`
found no supplied invoice-level source. This phase therefore uses explicitly
constructed JSON documents with exact byte spans. It establishes neither a
filing reconstruction nor actual source admission. The original real-source
obligation remains open. Every correction reconstructs a separate history from
the unchanged empty opening; it does not implement a contract amendment.
Known correction availability cannot precede its declared predecessor.

Run `python3 -B data/accounting-master/populated-source-contracts-20261025/verify.py --record`
once, then omit `--record` for read-only replay. The verifier runs the focused
source suite and lifecycle, text, report, carry, transition and P06 regressions.
It retains complete request/result pairs and command-text imports for both
charts under original and corrected views, a source lock, test logs and manifest.
Independent signed balances and statement targets are predeclared in the audit
and tested separately from replay. A corrected consideration of 35 leaves
cash 170, receivables 5, retained profit 55 after the unchanged receipts; this
tests distinct-history reconstruction without double-counting a revised sale.
