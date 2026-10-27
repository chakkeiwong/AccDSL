# Integration of the nine proposed contracts

The active contract list in P16 architecture.json is the document index. This
supplement resolves interactions among those contracts without altering earlier
evidence or treating saved fixture outcomes as executed product behavior. It
addresses MC02–MC14, MC18–MC27 and MC33–MC35. The baseline is the five existing
P16 contracts and their accepted amendments; Core 0/P03/P07 are investigated
prototypes, not automatic defaults.

`cross-contract-amendment-v1.md` A1–A6 is the active named amendment for the
portable commit schema, accounting/coverage mappings, repeated conditions,
corrected-view selection, native uncertainty schema/validation meanings and
semantic-versus-audit dependencies. It takes precedence for those exact
interactions while retaining original native bytes and their evidence limits.

## Meaning carried between contracts

| Boundary | Meaning that must survive | Rejection or unresolved consequence |
| --- | --- | --- |
| Evidence → time | Original bytes, source occurrence, review layer, economic/reporting/publication/ingestion clocks | Missing clocks cannot support stronger historical-knowledge claims |
| Evidence/time → history | Scoped admitted interpretation/assumption, joint symbols, conflicts and exclusions | Faithful reading alone cannot become an admitted accounting constraint |
| History → uncertainty | Full family/view, partition, dependence and query-relevant economic memory | No weights from witness counts; missing law gives a symbolic/unweighted result |
| Scenario/history → accounting | Branch opening, exact event identity, date/context, permitted information and eligible method | Unresolved or unsupported treatment produces no posting |
| Accounting → persistence | Validated request, source/method versions, proposal/delta and expected head | Exact replay before freshness; all-or-none transition; unknown commit reconciled under original identity |
| Calculation → report | Common history/scenario index, native statuses, unresolved regions/mass and unit/time semantics | No successful-subset renormalization or independent selection of line extrema |
| Correction → all descendants | Immutable old view, replacement scope, candidate-set membership and transitive dependency | Current reuse invalidated even for descendants created after the correction |
| Any contract → IR/interface | Versioned type, lineage and admission requirements | Unknown schema or required semantics cannot be ignored or coerced |

## Explicit amendments and precedence

L1's portable encoding applies only to new portable records. Existing native
record digests, original files, source byte hashes and receipts stay unchanged.
Integer metadata remains integer; financial quantities use exact rationals.
There is no global NFC normalization. A named legacy import retains both IDs
and checked decoded correspondence. Source-map identity is separate from model
identity, so formatting changes do not alter a model's financial meaning.

P2 resolves the early accounting contract's ambiguous “event/version” language:
the stable lookup key excludes version and payload. A correction uses a new
business-event identity with an explicit treatment/lineage; merely changing a
version under an existing key conflicts. Branch identity includes an explicit
projection namespace, distinguishing separately requested hypotheticals from
retries of the same projection. No double counting of hypothetical projections
is permitted when reporting realized transactions.

Native accounting retains its established validation order and assess-only
boundary. New portable wrappers validate their own envelopes and then delegate
to that native order. Dependency recognition is guarded by reference shape;
malformed refs are not followed. A shape error cannot be masked by finding an
old receipt. Output defects are distinguished from ineligible economic events:
reject publication as ASSESSMENT_OUTPUT_INVALID while retaining the validated
request and diagnostic candidate. All four committed accounting domains remain
unchanged for assess-only, rejection and replay.

Uncertainty fixture v2 rejection receipts supersede only their explicitly named
v1 predecessors. Their valid requests, joint laws, calculation payloads and
unchanged successes remain evidence. Derived law/view bundles require separate
admission and selection; a numerical posterior does not admit itself. No
platform wrapper changes an existing domain's status values in place.

## Status mapping at the new platform boundary

The native uncertainty schema has seven distinct statuses. The new platform
schema preserves the full native result and applies these mappings only with
the operation's tagged disposition and payload. Unknown combinations return
`STATUS_MAPPING_UNSUPPORTED`; they are not guessed.

| Native meaning | Platform interpretation |
| --- | --- |
| REQUEST_INVALID with invalid/unresolved/not_computed | rejected; invalid/unresolved/not_computed; no usable payload |
| satisfied + specified_exact, with a valid finite calculation payload | completed; valid/defined/complete; evidence_mode=specification_example |
| undefined, with established zero normalizer | completed; valid/undefined/complete; no posterior |
| specified_partial with retained unresolved regions | partial; valid/unresolved/partial, even when some local values are defined |
| symbolic without a requested executable evaluator | partial with retained formulas; valid/unresolved/not_computed |
| UNSUPPORTED operation/capability | unsupported; valid/unresolved/not_computed; retain input family |
| failed mathematics after well-formed request evaluation, such as an evaluated proposed law whose masses do not sum to one | rejected; structural_validity=valid, mathematical_status=failed, computation_status=complete; never `infeasible` without proof of an empty family |

For the last row a platform diagnostic names the failed mathematical predicate
and preserves the native result; no probability value is published.
This post-evaluation rejection differs from the invalid/unresolved/not_computed
pre-evaluation row. A numerical failure to evaluate the predicate would instead
leave mathematics unresolved and computation failed.
`structural_validity` is copied from the native request validation,
not inferred from the law's failure. A proof of infeasibility is a different
tagged result and maps to `infeasible`. Numeric/service failure has computation
`failed` and math `unresolved`, not mathematical infeasibility. These rules
preserve the failed mathematical verdict without conflating it with an empty
financial model or a service failure.

Native accounting `assessed` with `eligible` means the requested assessment was
specified, not that a journal was committed. Outer disposition is completed,
commit observation not_committed; its native accounting-validity field remains
not_assessed for the synthetic examples. `unresolved`/`outside_scope`/`ineligible`
remain explicit assessment results, with no JournalProposal. Input rejection
maps as above. A replay payload carries the original committed receipt and
additional_commit=false; outer disposition replayed, commit observation
not_committed. A lost acknowledgement of a requested write maps to commit_unknown
with unknown observation until the original identity is reconciled.

Empirical justification and capability values are preserved. Forecast validity,
product readiness and human acceptance cannot be inferred from any mapping.
All platform examples are specification examples; their finite arithmetic is
checked separately, and product_implemented remains false.

## Continuous company family and insufficient summaries

The protected Northstar example has one shared unidentified floating fraction
x∈[0,1]. Historical interest of 5 does not identify it when both loan types
charged 5%. The 2025 scenario changes floating interest, profit, tax, cash and
equity together. I3's statement payload must therefore retain their common x,
not just independent endpoint lists. The source package's closed synthetic
scope, teaching tax model, assumed intraperiod ordering and aggregate event
resolution all travel with the result.

Grouping two instruments with the same currency, rate/reset schedule, maturity,
seniority, collateral/guarantee rights and relevant accounting memory may preserve
a specified linear interest query by adding principals. Grouping fixed and
floating instruments only by their historical interest loses the stress exposure
and fails that query. Even the safe grouping must be reconsidered for a new
default, prepayment or instrument-specific tax question. This is a query-scoped
sufficiency rule, not a general compiler proof of economic equivalence.

The real source-backed conflict requested in E05 is still missing: seven inspected
candidates did not establish one. The fourteen synthetic conflict cases specify
behavior but cannot supply that source evidence. P17 must complete the exact
authority/method and real-source obligations. The initial-profile choice and
interface decisions are proposed answers now, with actual evidence and owning
phase in P16's decision records. Open source/method decisions remain proposal
blockers through P19; they are not closed by writing this integration document.
