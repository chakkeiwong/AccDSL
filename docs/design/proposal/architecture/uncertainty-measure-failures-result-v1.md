# P16 bounded prerequisite-failure supplement

The reviewed five-case task is complete at author level. MF01–MF05 specify
missing finite mass coverage, an unavailable event, a selector outside its
sample space, an omitted required dependency and an unavailable exact dependency
version. P16 remains PARTIAL. The uncertainty contract and attachment assessment
remain incomplete. Product implementation is disabled; independent substantive
review and human acceptance are pending.

The task addresses MC12/G15, with MC08/MC10/MC14/MC18/MC25 interactions. Its
reviewed plan hash is
`59837457ef465a7b2b9abdf6f3627322799994af7cb28db24b369887ac323a95`.
The pinned v2 specification and eighteen baseline cases govern the comparison;
prototype behavior does not. The previous result is preserved byte-for-byte in
`uncertainty-measure-attachment-result-v1.md`. All prior v1/v2 evidence remains.

## Specified behavior and actual author checks

The additive contract makes validation order and rejection receipts explicit.
The fixture imports the 49-record baseline and adds two uniquely identified
candidate records. It supplies exactly five new rejection cases, one unchanged
successful baseline control and one complete diagonal-attachment control using
the existing admitted diagonal law. Each candidate changes one semantic
condition from its cited control; necessary identity changes are explicit.

| Case | Input-derived finding | Specified consequence |
| --- | --- | --- |
| MF01 | `bin:01@1` has no mass entry; the three supplied entries still total exactly one. | Reject incomplete coverage without inferring zero or replacing the existing diagonal law. |
| MF02 | `event:unavailable@1` resolves to no record. | Preserve its submitted identifier; report unresolved event before secondary dependency failure. |
| MF03 | The new event resolves, but its selector includes `tri:outside@1`. | Reject the selector without clipping or creating an outcome. |
| MF04 | The justification is available and directly referenced, but absent from dependencies. | Reject the incomplete declaration without silently filling it. |
| MF05 | Declared evidence version 2 is unavailable while version 1 exists. | Reject exact-version reuse without substitution. |

Every rejection specifies invalid request structure, unresolved requested
mathematics, no computed probability and unchanged family/view/attachment state.
A separate field preserves the old attachment's valid finite law. Submitted
UTF-8 bytes and hashes retain unresolved identifiers; support lists contain only
available records. Rejected candidates are retained submissions, not admitted
models. These are specified receipts, not observed runtime transactions.

The standard-library diagnostic derives coverage sets, exact sums, reference
resolution, required dependency closure and selector membership from inputs.
It checks independent status dimensions, old-law validity, state hashes,
submission preservation, matching model/event identities and restoration of
one semantic difference. The valid event control gives 5/6; the diagonal
attachment control has two explicit zeros and total one. All **266** diagnostic
checks pass. The command, timestamp, Python version, input hashes and observations
are saved in `uncertainty-measure-failures-consistency-v1.json`:

```
PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-measure-failures-diagnostic-v1.py --output docs/design/proposal/architecture/uncertainty-measure-failures-consistency-v1.json
```

Before registration, all 47 existing architecture reference occurrences matched
their saved hashes. The earlier result matched its preserved snapshot. The new
work is registered separately, without adding a completed uncertainty row,
changing the three existing rows, selecting a profile or closing any decision.
The fresh registered structural check and its separate execution receipt are
saved as `uncertainty-measure-failures-structural-v1.json` and
`uncertainty-measure-failures-structural-execution-v1.json`. It returned **133/134** passing checks, with only `whole architecture contracts`
failing (exit 1). It stopped before per-contract/profile validation, so this
report cannot accept those fields. The first report pins the result note before
this outcome was added; those exact bytes are preserved in
`uncertainty-measure-failures-precheck-result-v1.md`. A fresh v2 structural report
and execution receipt repeat the check solely to bind the final note after
this change. Both reports are retained; no existing report is overwritten.

| Decision | Primary criterion | Veto diagnostic | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Preserve the completed bounded supplement | Five complete input/result pairs and two valid controls saved | No input-derived consistency failure | Author and diagnostic may share an unstated assumption | Independent substantive review when available; separately reviewed next drafting plan | Attachment completeness or P16 acceptance |
| Reject each malformed request without changing its old law | Earliest failed prerequisite identified from submitted inputs | Exact identity, dependency, coverage and selector checks applied | Atomic runtime persistence is not implemented | Carry unchanged-state requirement into persistence/failure design | A tested runtime transaction |
| Keep phase partial | Six contract rows remain unfinished | Whole-architecture inventory cannot pass | Profile and integrated dependency order unresolved | Finish remaining bounded proposal tasks | Product, accounting, empirical or human acceptance |

This was a deterministic document diagnostic, not a scientific experiment,
benchmark or stochastic comparison. Rational arithmetic is an example
convention. No superiority ranking is made. The strongest alternative
explanation for a missed defect is a shared schema assumption; independent
review should challenge validation precedence, dependency closure and receipt
meaning. A resolvable input producing a different first failure under the
specified order would overturn the local conclusion. Full failure coverage
remains the weakest part of the attachment evidence.

## Changed files and continuation

Only the following allowed files were created or changed in this task:

- `data/accounting-master/deliverables/P16/architecture.json`
- `data/accounting-master/deliverables/P16/result.md`
- `data/accounting-master/deliverables/P16/progress.md`
- `docs/design/proposal/architecture/uncertainty-measure-failures-contract-v1.md`
- `docs/design/proposal/architecture/uncertainty-measure-failures-fixtures-v1.json`
- `docs/design/proposal/architecture/uncertainty-measure-failures-diagnostic-v1.py`
- `docs/design/proposal/architecture/uncertainty-measure-failures-consistency-v1.json`
- `docs/design/proposal/architecture/uncertainty-measure-failures-structural-v1.json`
- `docs/design/proposal/architecture/uncertainty-measure-failures-structural-execution-v1.json`
- `docs/design/proposal/architecture/uncertainty-measure-failures-precheck-result-v1.md`
- `docs/design/proposal/architecture/uncertainty-measure-failures-structural-v2.json`
- `docs/design/proposal/architecture/uncertainty-measure-failures-structural-execution-v2.json`
- `docs/design/proposal/architecture/uncertainty-measure-failures-result-v1.md`

The Python file is a bounded documentation diagnostic. No production modules,
controller/checker/tests, catalog, release-pinned data or protected snapshots
were edited. The last file preserves this result for later drafting.

Next task: separately review the matched comparison of family-linked and
self-contained joint-model representations, and reconcile remaining attachment
failures (stale but available dependencies, other malformed inputs, partition
and projection failures). Do not call attachment coverage complete yet.
Conditioning, semantic duplicate-evidence protection, likelihood updates and
conditional outcome payloads remain later tasks. Six architecture contracts,
profile selection, integrated acceptance criteria and dependency order remain
unfinished. All fourteen decisions and MC01–MC35/G1–G18 survive. E05's genuine
source-conflict requirement remains open; its no-pair finding covers only seven
inspected candidates.

Optional bounded result review remains pending where unavailable and does not
block the next freshly reviewed drafting plan. Complete structural checks and
full independent P16 result review remain mandatory before phase acceptance.
Earlier substantive reviews, accounting authority, empirical forecast validity
and human acceptance remain pending. No outreach or professional engagement
was undertaken.
