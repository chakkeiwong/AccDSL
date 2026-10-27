# Literature and source-support method

The literature method governs which technical claims may enter a proposal,
which alternatives must be considered and what remains source-blocked. It does
not use citation counts as correctness, does not infer a theorem from an
abstract, and does not call a bibliography complete because a file exists.
It addresses MC23, MC26, MC28–MC30 and MC35 under the scholarly literature policy.

## L1. Six ledgers and claim admission

SourceSupport records title/authors/year/identifier, local PDF/text/hash,
publication and version status, technical sections/equations/algorithms actually
read, claims allowed and forbidden, correction/retraction check and classification.
ClaimSupport maps each important proposal statement to either an inspected primary
technical passage, a local derivation, implementation evidence, survey context,
source-gap blocker or quarantine. It records what the source explicitly says,
what is derived in AccDSL notation and what is not established. A blocked full
text cannot support a method claim. A source may support a narrow observation and
forbid a transferred theorem.

BackwardSnowball starts at each method seed, inspects its related-work/method/
comparison passages and classifies relevant cited works as foundational,
direct method, competitor, survey, implementation, empirical, peripheral,
superseded, blocked or quarantined. ForwardSnowball records query source/date,
high-citation and recent citing works, corrections/extensions/replications and
access limits. OmissionRisk records a plausible missing work, why it is omitted,
expected reviewer objection and next action. Citation/venue metadata is dated
context, never a promotion score. Retraction/erratum/version checks occur before
claim use; a material adverse notice quarantines the source.

Admission is claim-specific: a technical equation needs the inspected equation,
algorithm or proof; a software availability claim needs the pinned source and
license; a historical claim may use a checked survey passage; an accounting
rule needs the dated primary authority method. An inspected source does not
establish an AccDSL default. Every derived formula includes its assumptions and
independent check where feasible.

## L2. Domain routing and method construction

For an open method question, record the target proposition, source candidates,
required technical passage, competing interpretation, facts needed, diagnostic,
and consequence. Read the technical method/theory/evaluation sections before
deciding. Translate only the permitted claim into an AccDSL specification:
inputs, assumptions, state, algorithm, output, failure and interface. Preserve
the source's probability measure, conditioning event, baseline, units and target;
if any changes, name the new target rather than calling it the same method.

For forecasting, Stuart2010 §2.2 equations(2.5)–(2.8) supports an observation
operator, noise model, prior and posterior relation; it does not supply an
accounting identifiability theorem. Pearl2009 §3.2 equations(5)–(9) and
(15)–(17) supports conditioning/intervention distinction and Markovian
factorization; it does not establish a causal company model. Giacomini/Kitagawa
§§2.1–2.3 equations(2.2)–(2.4) supports posterior classes under an unresolved
conditional prior; no SVAR guarantee transfers. Mack1993 equations(1)–(3),
Theorems1–3 supports chain-ladder assumptions/error formulas; a triangle with
one observed factor cannot produce a zero uncertainty estimate. These explicit
boundaries are part of method evidence.

For language and history design, Green2007 Sections2–4 supports compositional
provenance annotations in its relational setting; Merigoux2021 Sections3–4 and
Figure13 supports scoped exceptions, conflict/empty outcomes and staged compiler
representations; Doshi2024 Chapters4,7–9 supports an accounting DSL's explicit
time/correction concepts. None establishes accounting compliance or complete
source translation. The source-support ledger keeps their forbidden claims.

## L3. Worked review and limits

The 2026 retained corpus and literature inventory are development evidence. The
current source-support ledger contains inspected local PDFs/text plus explicitly
blocked papers such as McCarthy1982, Caiani2016, Imielinski1984 and Tamer2010.
Those blocked records remain visible and cannot support technical claims. A
source count, citation count, venue, PDF page count or successful metadata query
does not establish breadth or correctness. The proposal's final hostile review
must ask why a famous/recent competitor is missing, whether technical passages
were actually inspected, whether retractions/versions were checked and whether
omissions are justified.

The method returns `supported`, `derived`, `context_only`, `source_blocked`,
`quarantined` or `not_checked` per claim. A source correction invalidates only
the descendants bound to its claim/edition; prior result artifacts remain tied
to their original evidence view. An unresolved source question may carry a
proposed answer, alternative and consequence into P18/P19, but it cannot close
P15-E07/E08 or authorize real accounting treatment by prose alone.
