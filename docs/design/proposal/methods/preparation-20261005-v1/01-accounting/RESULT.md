# Packet 1 result and review

Lease and tax dossiers are ready as **candidate P17 preparation**. They supply
declared source conditions, worked journals, balance/movement schedules and
failure cases. They do not accept P17, finalize P16 interfaces, implement a product
engine or certify tax-law/accounting compliance. Files were created only in
`01-accounting`; the main worktree and controller state were not changed.

Deliverables are `lease-dossier.md`, `tax-dossier.md`, `fixtures.json`,
`source-register.json`, `source-inspection.md`, retained `sources/`, and the
single bounded diagnostic `arithmetic-check.py` with `arithmetic-report.json`.
`prepare-fixtures.py` preserves how author-selected declarative fixtures and
source anchors were serialized; it is not the independent arithmetic comparator.
The run manifest in the report pins inputs, exact command, Python/platform,
wall time, CPU-only standard-library calculation, plan and result locations.

Commands run from the packet directory: official-source `curl -fL` requests
with connection/total timeout, `pdftotext -layout` for each of four PDFs,
`python3 prepare-fixtures.py`, and `python3 arithmetic-check.py`. The last
diagnostic passes **559 checks**, including independent present values, balance
consequences, tax-base/reversal equations, dated settlements and exact source
anchors. Five copied defective fixture sets fail the same independent oracle:
stale opening-balance interest,
old-rate modification measurement, reversed deferred-tax sign, discounted
deferred tax and suppressing gross paired lease tax because initial net is zero.
The count is bookkeeping of diagnostic assertions, not a measure of semantic
coverage or readiness. No stochastic comparison or GPU operation was performed.

## Skeptical review and resulting changes

The plan audit preceded acquisition and substantive preparation. Source review
resolved actual compilation dates instead of trusting filenames. L16.B19's
specific substitution-right presumption prevents a blanket unknown-data failure
from overriding the standard. T112.22A/98J–98L prevents reuse of the obsolete
single-transaction initial-recognition shortcut. Tax-rate enactment and effective
dates remain distinct. Lease and tax future schedules explicitly hold selected
rules fixed and require later applicability review.

Independent arithmetic confirms lease base PV 210, closing liability 110/0,
ROU 105/0 and expenses 126/116; a same-asset modification gives revised PV 220 and
ROU 215. PPE tax gives FY 2024 current 75 plus deferred 50; the enacted future-rate
case gives FY 2025 current 100 plus deferred 40. Separate lease tax under the
declared attribution gives gross DTA/DTL 52.5 initially and 27.5/26.25 at 2024 end.
These calculations remain conditional on facts, legal deductions, rate and
recoverability evidence, not substitutes for those inputs.

Review found and repaired one source-locator defect: a form feed immediately
before a paragraph caused its physical-page anchor to point to the previous
page. The generator now counts it and the diagnostic checks every saved page
against the retained text. This changes no accounting amount. P116.29/30 and
L16.31/38 were added to explicit anchors after checking the delegated cost and
depreciation rules.

Root review found that the first negative-control loop compared entered wrong
and expected numbers without submitting a defective payload to the invariants.
That loop did not support the original detection claim. It is replaced by five
copied fixture sets under `mutants/`; each changes journal payloads while keeping
all journal events balanced. The unchanged copied baseline passes the same probe
entry point. Each mutant then fails its targeted independent invariant, and the
report preserves the exact payload hash, return code and first actual mismatch:

| Mutant | Independent failed invariant | Actual defective balance | Required balance |
| --- | --- | ---: | ---: |
| N01: second-year interest on initial balance | Liability versus PV of remaining payments at 2025 end | 10 | 0 |
| N02: old rate used at modification | Modification-date liability versus revised-rate PV | 30240/121 | 220 |
| N03: deferred-tax entry sides reversed | 2024 DTL versus taxable difference times rate | −50 | 50 |
| N04: deferred tax discounted | 2024 DTL versus undiscounted tax consequence | 500/11 | 50 |
| N05: initial gross lease tax omitted | Initial DTA versus deductible liability difference | 0 | 105/2 |

The diagnostic rejects a surviving mutant or unrelated subprocess error. These
are verification of specific specification invariants, not proof that every
incorrect accounting treatment can be detected. The `--mutant-probe` entry point
reads a complete fixture set from standard input and returns code 3 on the first
invariant failure without writing a report; ordinary execution records all five
probe outcomes. No product posting engine was added. Prose dates, rates and
amounts in both dossiers and this result note were also inspected and spaced for
reading; formulas, fixtures and source quotations retain their separate form.

Read `../02-authority/authority-matrix.md` against the matched facts. No numerical
or source-scope contradiction was found in its base lease, current/deferred tax,
enacted-rate change or gross lease-tax extension. Its historical US operating
candidate has ROU 110 at 2024-end and single cost 121, unlike L01's 105 and 126; that
is an explicit framework comparison, not an inconsistency. It correctly retains
current ASC and official-current ASBE admission gaps. Packet 2 independently read
these dossier drafts and reported the matched base/rate/lease-tax values align.
That peer check is bounded internal review, not professional or full-domain
acceptance. The actual source/version facts for ASBE's official application case
remain owned by packet 2; this packet does not republish or promote them.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Keep as proposed P17 method inputs | Exact source conditions and independent arithmetic agree for stated cases | No arithmetic/source-integrity failure; real-law and full-domain admission remain blocked where absent | Actual contract/rate/tax law; later version chain; loss recoverability; full methods/disclosures | Root review, controlled stopped-master import, P16 interface mapping and targeted remaining cases | Complete proposal, runtime correctness, current universal framework support or professional acceptance |

Strongest alternative explanation: correct calculations can still use the wrong
contract classification, tax attribution or applicable rule. An actual contract,
operative amendment, authoritative tax law or credible recoverability evidence
contradicting the assumptions would overturn the dependent treatment. The weakest
evidence is actual-entity applicability, not the rational arithmetic. Continue
with real facts and remaining methods; do not replace this internal queue with
a generic request for paid accounting review.
