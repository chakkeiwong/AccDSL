# Acquisition assessment decision supplement v1

This bounded P16 proposal supplement fills two gaps in the saved acquisition
preconditions: mixed valuation-evidence states and simultaneous adverse findings.
It addresses MC08, MC13, MC25, MC34 and MC35, with G4/G18 interactions. The
eligibility dossier and this supplement remain pending independent substantive
review. Earlier acceptance covers the request-binding repair and inspected finite
records only. A01 remains conditional; original A03 remains unresolved.

## Evidence, defaults and stopping rule

The question is whether the specified assessments preserve all evidence states
and reasons while giving a deterministic summary. Completion requires all nine
valuation pairs, six expanded new valuation packets and three combined-finding
packets. The matched comparators deliberately coerce unknown to false or stop at
the first adverse finding on the same inputs. They diagnose information loss;
they do not represent or rank accounting products. Wrong branches, lost findings,
posting permission or changed predecessor evidence veto this slice. Arithmetic
and source/reference hashes are explanatory or integrity checks, not accounting
validity criteria. Stop after these examples, finite document calculations and
the registered structural check. No lifecycle method or record integration is
part of this task.

Skeptical pre-execution audit: retained inputs and the exact authority version
provide matched comparisons; absent methods remain absent; unknown facts cannot
be promoted to false. The proposed reporting precedence has no accounting
normative status. Standard-library calculations need no special environment,
GPU, network service or new package. No stochastic or performance claim follows.

| Choice and provenance | Why used | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| AASB 9 Compilation 5, retained S9 | Preserves the dossier's exact paragraph support | Applying an edition outside its annual-period window | Verify source hash and C01 period start | Source-scoped baseline, not current universal authority |
| Price 100, supplied fair value 105; E06 | Isolates evidence quality on identical amounts | Treating synthetic valuation/classification as established | Expanded-input comparison against E06 | Synthetic hypothesis |
| True/false/unknown for two qualifying routes | Distinguishes positive, contrary and missing evidence | Unknown coerced to false selects an unsupported branch | Explicit nine-row table | Provisional representation |
| ineligible, outside_scope, unresolved, eligible precedence; dossier | Gives one stable summary while retaining detail | First-failure return loses repair obligations | Three combined-category packets with full C01–C10 findings | Provisional engineering convention |
| No unequal-price posting method; dossier | Keeps branch identification distinct from method coverage | Inferring permission from a known branch | C10 and posting_permitted=false in every new packet | Explicit method limit |

The predecessor hashes, approved plan hash and pre-edit deliverable hashes are
in `accounting-eligibility-decision-inputs-v1.json`. The new fixtures also pin
the dossier, predecessor fixtures and retained source text. All predecessor
files, including accepted record/replay evidence, are preserved byte-for-byte.

## Valuation evidence: the complete decision table

S9 is the retained AASB 9 Compilation 5 (31 December 2022), prepared 6 April
2023, authorised version F2023C00399. Its cover gives annual periods beginning
on/after 2023-01-01 and before 2026-07-01. B5.1.2A on physical PDF pages 74–75
(text lines 4394–4417 in `docs/design/research/p08-v1/aasb9.txt`) distinguishes
an identical-instrument quoted price in an active market or a valuation technique
using only observable-market data from other cases. See the dossier for the
retained official URL, PDF/text hashes and wider recognition/classification
anchors. Source rules support this distinction; they do not establish the
synthetic transaction facts or confer posting permission.

Let Q mean qualifying identical-instrument active-market evidence and O mean
qualifying observable-market-only technique evidence. True stipulates positive
qualifying evidence; false stipulates that this route does not qualify; unknown
means evidence is missing. Each refers to evidence for the supplied fair value,
not mere market-data availability. When either route is true the source's (a)
condition is met conditionally; when both are false it is not, selecting (b).
With neither known true and at least one unknown the available facts cannot
distinguish these source branches. This last outcome is an epistemic state of
the proposal, not a third accounting treatment in the standard.

| Q | O | Identified branch | Assessment summary | Example |
| --- | --- | --- | --- | --- |
| true | true | (a) | outside_scope | E09, new |
| true | false | (a) | outside_scope | E07, retained |
| true | unknown | (a) | outside_scope | E10, new |
| false | true | (a) | outside_scope | E11, new |
| false | false | (b) | outside_scope | E08, retained |
| false | unknown | unresolved | unresolved | E12, new |
| unknown | true | (a) | outside_scope | E13, new |
| unknown | false | unresolved | unresolved | E14, new |
| unknown | unknown | unresolved | unresolved | E06, retained |

Known branches remain outside this slice's supplied posting method (C10).
For E10 and E13 the unknown route remains a named child finding under C09 and
in `open_evidence`; it does not obstruct a branch already established by the
other route. For E12 and E14, C09 and C10 remain unresolved. Every new packet
expands C01–C10 with provenance, scope and version. Relative to E06 only C09
and its dependent C10 change: price, fair value, fees, entity, branch, dates and
conditional classification remain fixed. Changes to reasons and branch labels
follow those inputs. No new packet has a journal proposal or state delta.

Treating unknown as false on the same E06/E12/E14 inputs would select (b),
although the missing route might subsequently qualify for (a). The other six
pairs retain their branch label, but E10/E13 would still lose an unknown fact.
Identifying this loss is not evidence that either branch's posting method has
been specified. All assessments retain unchanged posted journals, account
state, event identity map and committed receipts; no receipt is invented.

## Simultaneous findings and their consequences

E15 combines E03's disproved contractual condition with E02's missing
classification rationale. E16 combines E04's outside-window authority with
E02. E17 combines all three. Their complete input packets and ten ordered
condition findings are saved alongside the six valuation cases.

| Example | Control and deliberate input changes | Retained adverse findings | Summary |
| --- | --- | --- | --- |
| E15 | E01; replace C03 from E03 and C05 from E02 | C03 ineligible; C05 unresolved | ineligible |
| E16 | E04; replace C05 from E02 | C01 outside_scope; C05 unresolved | outside_scope |
| E17 | E04; replace C03 from E03 and C05 from E02 | C01 outside_scope; C03 ineligible; C05 unresolved | ineligible |

E16 and E17 preserve E04's annual-period start 2026-07-01 and designated
trade, settlement, recognition and valuation dates 2026-07-03. E16 retains the
stipulated contractual date 2026-07-03. E15/E17 instead retain E03's false
party-to-contract flag and null contractual date. Their C04 dates are candidate
dates contingent on the contractual condition, not assertions of a completed
trade or recognition. Their conditional C04 finding concerns date-policy
consistency only; it cannot override C03. Amounts remain price/fair value 100,
fee 2; other facts are copied unchanged from the named control. E17's ineligible
label reports the failed prerequisite under this conditional method while C01
still forbids applying the retained edition as adequate authority for that
period. It is not a definitive accounting judgment under an uninspected later
edition.

All C01–C10 findings remain in that order, with their reasons. The summary
chooses ineligible before outside_scope before unresolved before eligible;
ordering the findings does not make the first adverse finding decisive.
Returning only the first adverse finding would omit C05 in E15/E16. In E17 it
would return outside_scope and omit both C03 and C05, changing the summary as
well as hiding repairs. These same-input counterexamples justify retaining the
whole assessment even when one condition already prevents a journal proposal.
Fixing a leading condition does not clear the others: E15 still needs a
classification rationale; E16 also needs applicable authority; E17 needs both
as well as contractual recognition evidence. None has a journal proposal,
state delta or posting permission. All four no-mutation domains remain
unchanged. No request or receipt is fabricated.

Accepted processing order remains structure/reference validation, stable
identity lookup, matching committed-receipt retrieval or identity conflict,
then (only for a fresh request) state freshness and eligibility assessment.
Replay is not renewed eligibility. These local example IDs and provenance
versions do not integrate this dossier into an immutable request schema.

## Decision and remaining work

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit this supplement with the dossier | Nine valuation pairs and three combined examples specified | Finite checks reported in the accompanying verification; any failed branch, finding or preservation check blocks this slice | Actual instrument facts/classification and completeness need substantive review | Supervisor reviews both together | Accounting validity, runtime enforcement or an available unequal-price posting method |
| Preserve P16 partial status | This bounded specification is saved | Whole-architecture acceptance remains blocked | Four missing groups, initial profile/order and fourteen decisions | After review, integrate versioned preconditions in a separate task; lifecycle separately | Full-phase acceptance, empirical forecast validity or human acceptance |

The calculation file checks these finite packets against an explicit independent
truth table and specified composition controls. It is a document calculation,
not an accounting classifier or a new prose-certification test suite. Its
verification records the actual command, environment, input hashes and limits.
The registered checker establishes structure only and stops at its first
failure; unreached contract/profile checks cannot be reported as passed.

Post-draft red team: internally consistent examples could preserve the wrong
fact or omit a relevant scope exception. Contrary contractual evidence or a
source interpretation that changes the conditional rule would overturn the
associated result. Synthetic upstream classification and branch admission remain
the weakest substantive evidence. All MC01–MC35/G1–G18 obligations remain,
including whole-company representation, later sectors, standards and source
research. MC35 keeps unfinished preparation internal; no paid review, engagement
or outreach is requested.
