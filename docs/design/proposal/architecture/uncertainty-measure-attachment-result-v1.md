# P16 bounded measure-example consistency repair

The reviewed repair is complete at author level. The saved attachment and event
examples now use coherent immutable identities, complete operation-specific
requests/results and resolvable support records. P16 remains PARTIAL. This does
not complete the attachment assessment or register the uncertainty contract.
Product implementation remains disabled; independent substantive review and
human acceptance are pending.

Scope is MC12/G15 with MC08/MC10/MC14/MC18/MC25 dependencies. The baseline is the
P15 MC12 obligation and reviewed repair plan
`34f26dbcb28cdc96611d3944c0a31242b7b20d3d8e1c6d8f4b0626baf139f554`, not historical
prototype behavior. The existing FiniteMeasure code and Core 0 paragraphs were
inspected only as historical evidence. In particular, the whole-product
proposal continues to allow unweighted future domains. No external authority
research or model/API call was needed for this arithmetic repair.

## Saved specification and author reconciliation

The v2 contract reconciles its field table with the exact fixture schema.
Registry references resolve immutable ID/version pairs; changing a model or
family requires a new identity. Models have explicit coordinate order, domain,
purpose, cutoffs, justification and dependencies. Stored malformed submissions
remain candidates, never admitted probability laws. All six groups were saved
as drafted; the fixture contains eighteen complete cases and 49 support records.

| Cases | Checked input and specified consequence | Separate status interpretation |
| --- | --- | --- |
| MA01a/b | An unweighted continuous domain is retained; branch counting is rejected as a measure. | No law, no probability; mathematics unresolved. |
| MA02a | Three masses 1/2, 1/3, 1/6 sum to one and attach as an assumption. | Valid structure and satisfied finite obligations; empirical support unestablished. |
| MA02b/c | Negative mass fails despite total one; the non-unit candidate totals 7/6 and fails. | Structure valid, mathematics failed; no renormalization or event probability. |
| MA02d | Duplicate elementary identity fails before any sum can count it twice. | Structure invalid; no new attachment. |
| MA03a | A={a,b}, B={b,c} give 5/6, 1/2, intersection 1/3 and union 1. | EVALUATED under exactly one stipulated law. |
| MA03b | Two disjoint cells omit c and fail exhaustive coverage. | Representation valid, partition mathematics failed. |
| MA03c | The same event reference appears twice and gives 5/6 once. | Idempotent event lookup only; no duplicate-likelihood conclusion. |
| MA04a | Two Bernoulli marginals without a joint law remain constraints on possible couplings. | RETAINED_ONLY; no independence assumption. |
| MA04b | Two separately identified outcomes project to rate=1 with combined mass one. | Both elementary identities remain; a different family/model from MA02/03. |
| MA04c/d | Diagonal versus off-diagonal half/half laws share the four-outcome domain and Bernoulli(1/2) marginals. | Equality probabilities 1 versus 0; explicit zero masses remain in the declared space. |
| MA05a/b/c | Changed family/support and purpose are rejected; a requested model successor is retained without migrating the old attachment. | Old views remain identifiable; invalid reuse never becomes evaluation. |
| MA06a/b | Continuous and mixed expressions have separate compatible domains/models and retained symbolic events. | Structure valid, mathematics unresolved, evaluator unsupported, numerical probability null. |

Every result separately states structural validity, mathematical status,
attachment status, empirical justification, proposed capability and computation
status. Conditioning, likelihood updates, model migration and conditional
outcomes appear as future dependencies. None is offered as an available next
operation. All operation/capability statements describe proposed behavior;
there is no product evaluator behind these examples.

The sample space includes explicitly zero-weight outcomes, whereas positive-mass
support is derived from the law. Missing outcomes cannot silently become zeros.
The two Bernoulli examples establish the dependence point by exact summation:
the same marginal constraints permit both laws, while the diagonal event has
different probabilities. This is a local mathematical deduction from stipulated
inputs, with no estimated company probability or empirical forecast claim.

## Verification and evidence limits

A one-shot standard-library diagnostic reads the actual inputs, resolves
references, checks typed coordinates and family/model/event bindings, validates
admitted synthetic preconditions, and recomputes finite totals, supports,
partitions, overlaps, projections and marginals with Fraction. It also compares
specified rejection reasons and status dimensions with input defects and checks
that unsupported cases expose no numerical probability. The current report
passes 542 author consistency assertions across eighteen cases; zero failures.
This is not a new product module or test suite and does not certify prose.

Exact final diagnostic command:

```
PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-measure-attachment-diagnostic-v1.py --output docs/design/proposal/architecture/uncertainty-measure-attachment-consistency-check-v2.json
```

The initial report v1 also passed. A subsequent manual review reconciled the
legacy A-table field names with section F and made validation order explicit.
The pre-reconciliation document and first report are retained; report v2 pins
the current specification. Repetition was justified by that document change.
Both reports preserve computed observations, input hashes and diagnostic source.
The older measure v1 documents and admission result snapshot are unchanged.

The registered command is:

```
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_accounting_proposal.py --phase P16 --check
```

Its fresh output is `uncertainty-measure-attachment-structural-check-v1.json`
and its execution receipt is
`uncertainty-measure-attachment-structural-execution-v1.json`, both in the
architecture directory. These files record the actual exit status and errors.
The preceding supervisor report was 101/102 with only whole architecture
contracts failing. The architecture still contains three of nine contract rows;
the fresh report is authoritative for current structural counts. The checker
stops at missing whole-architecture contracts, so it cannot be cited as review
of individual contract completeness or the unresolved profile.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Save this bounded repair as partial proposal evidence | Required example repairs and input-based checks completed | No local inconsistency found; full-phase inventory remains incomplete | Independent semantic review pending; failure coverage incomplete | Separately plan attachment completeness and matched alternatives | Complete uncertainty contract or P16 acceptance |
| Preserve both dependence examples | Exact finite sums yield identical marginals and distinct equality probabilities | Neither law violates finite probability axioms | Laws are stipulated, not estimated | Carry into the attachment assessment | Empirical prevalence or a preferred joint law |

This was a bounded document diagnostic, not a scientific run, statistical
comparison, benchmark or GPU task. There is no superiority ranking. The strongest
alternative explanation for a missed defect is that author and diagnostic share
an unstated schema assumption. Independent review should challenge bindings,
validation precedence and the division between retained candidates and admitted
laws. A contradictory resolvable request/result pair would overturn the local
consistency conclusion. Comprehensive failure coverage is the weakest evidence.

## Changed files and remaining task

Only permitted P16 deliverables and architecture documents changed:

- `data/accounting-master/deliverables/P16/architecture.json`
- `data/accounting-master/deliverables/P16/result.md`
- `data/accounting-master/deliverables/P16/progress.md`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-contract-v2.md`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-contract-v2-before-field-reconciliation.md`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-fixtures-v2.json`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-diagnostic-v1.py`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-consistency-check-v1.json`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-consistency-check-v2.json`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-structural-check-v1.json`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-structural-execution-v1.json`
- `docs/design/proposal/architecture/uncertainty-measure-attachment-result-v1.md`

The Python file is the saved documentation diagnostic only. No production
source, controller, catalog, tests, release-pinned data or protected snapshot was
modified. The last file preserves this result note for subsequent drafting.

Next bounded task: reconcile attachment completeness and systematic matched
alternatives against the repaired examples and the earlier approved attachment
plan. Cover still-missing negative cases, including omitted masses, unknown
events and dependency failures, before claiming the attachment slice complete.
Then separately plan conditioning, semantic duplicate-evidence protection,
likelihood updates and conditional outcome payloads. Six architecture contracts,
initial-profile choice, integrated acceptance criteria and dependency order
remain unfinished. All fourteen open decisions and MC01–MC35/G1–G18 survive.
E05's no-pair finding remains limited to seven inspected candidates.

Optional bounded result review stays pending where unavailable; it is not a
prerequisite to the next freshly reviewed drafting task. Complete structural
checks and full independent P16 review remain mandatory before phase acceptance.
Accounting authority, runtime correctness, empirical forecast validity and human
acceptance remain unestablished. No expert engagement or outreach is authorized.
