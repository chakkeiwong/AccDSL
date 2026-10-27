# SQL null semantics: technical closeout

14 October 2026. P17-01; E08, with the related MC/G scope in
[the execution note](execution-note.md). The source-specific inquiry is
complete. Proposal Version 2.72 remains the protected baseline and
**not_ready**; this result is literature support, not a readiness promotion.

## Source identity and version

The retained author-hosted 28-page PDF,
[`sources/tods16.pdf`](sources/tods16.pdf), has SHA256
`b72ca55e64a4c890a2ee0bf3053af55b449a8b52a521329a378bb70a54715dbf`.
The earlier [technical review](technical-review.md) records the explicit link
from the author's publication page and the original HTTP response. The
retained Crossref search item matches title, author, *ACM Transactions on
Database Systems* 41(1), pages 1–28, DOI `10.1145/2877206`; it records online
publication on 18 March 2016 and print publication on 7 April 2016. The PDF's
first-page DOI `10.1145/0000000.0000000` and recurring “January YYYY” footer
are placeholders, not competing bibliographic evidence. Neither publisher-byte
equivalence nor identity with the ICDT preliminary version has been checked.
The retained Crossref item has no update/relation entry, but it is a search
response, not an exhaustive current correction/notice clearance. Do not use
the absence of a field as proof of no notice.

The [source supplement](source-support-supplement.json) records inspected
sections, supported claims, forbidden transfers, the prior forward-screening
candidate and omission decision. The original research ledgers remain
historical; the wider P17-09 literature survey is still open.

## What the paper establishes

Definition 3.1 (printed A:6–7) calls an evaluation sound for a query class
when every returned tuple of constants is in the intersection of answers over
all valuations of the marked nulls. Definition 5.1 (A:9–10) extends the target
to tuples that themselves contain nulls: for every valuation `h`, the image of
the returned tuple must be in the result on `h(D)`. Proposition 5.2 proves
that filtering those extended answers to constant tuples recovers ordinary
certain answers. These are two different output targets, not a change to the
input's closed-world completion semantics.

Libkin's modified `Eval3v` changes the rules for membership and equality.
Membership is false only when no stored tuple can unify with the candidate;
equality is false only for distinct constants. Theorem 5.3 (A:10–12) proves,
by induction over first-order formulas, that output `1` entails membership in
the certain answers with nulls and output `0` entails membership for the
negated query. Theorem 4.1 follows for constant tuples through Proposition
5.2. The induction starts from those atomic guarantees, preserves them through
conjunction/disjunction/negation, and handles quantifiers through active-domain
witnesses and universal branches. It does **not** prove completeness.
Corollary 5.4 supplies an over-approximation by excluding tuples for which
the negated query is soundly positive. Proposition 5.5 recovers ordinary
two-valued evaluation on complete inputs.

Theorem 5.3 says output `1/2` **comes with no guarantee**. It does not mean
that both truth values occur in feasible completions. The paper's printed
false-negative example at A:7 uses `T={(1,⊥)}` and
`ψ(x)=∃y[T(x,y)∧(y=1∨¬(y=1))]`. Its extracted text misleadingly reads the
inner variable as `x`; the rendered page was checked. In every valuation of
`⊥`, the disjunction is true, so `1` is a certain answer. Ordinary SQL misses
it because comparison with null is unknown. Applying the paper's modified
atomic and Kleene rules locally also gives `Eval3v(ψ,D,1)=1/2`: `T(1,⊥)` is
present, while both `⊥=1` and its negation evaluate to `1/2`. This last
`Eval3v` calculation is a local derivation from the stated rules, not a claim
the paper presented this particular output or a runtime database test. It
demonstrates a certain truth that the sound approximation leaves undecided.
Likewise, the same unknown equality under `P∧¬P` remains `1/2` under those
rules although the completed proposition is always false. Two witnessed
opposite completions, not an evaluation outcome of `1/2`, are needed to prove
variation.

The paper's positive and negative guarantees are for marked-null incomplete
relational instances, first-order queries and textbook **set** semantics
under its declared closed-world completion model. Its open-world variant
changes the atomic/quantifier rules and does not retain the same negative
guarantees. Section 6 translates relational algebra to positive/negative
queries and permits contained approximations; it does not make arbitrary
algebra/FO rewrites equivalent under incomplete evaluation. Sections 7–8
illustrate nested-query failures and leave bag semantics, grouping,
aggregation, implementation performance and optimization beyond the proved
contract. None of this proves accounting measurement, temporal history,
scenario intervention or a general financial query engine.

## Relation to the existing proposal and P18 decision

The current Version 2.72 manuscript already defines `entailed`, `refuted`
and `undetermined` over a nonempty declared history family in
`chapters/11-contracts.tex` (logical-query paragraphs and the following
full-family proof conditions). It explicitly distinguishes witnesses on both
sides from timeout, unsupported operation and unfinished search. Section
`sections/certain-answer-semantics.tex` distinguishes Boolean truth, certain
rows and answer families, and warns about SQL nulls and theorem transfer.
There is **no identified defect in that core contract**.

The body still omits this direct sound-but-incomplete relational-query
competitor and its counterexample. [P18-01's disposition](p18-disposition.md)
therefore adds a short scoped comparison and source citation beside the
existing query-semantics discussion, while retaining the exact/mixed/undecided
financial contract. The preliminary note's “No transfer veto” is superseded:
**there is a theorem-transfer veto** for financial queries outside the paper's
relational, marked-null, query and set-semantics assumptions. The source may
still be cited accurately as a competitor and limitation.

| Decision | Primary criterion | Veto diagnostic | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Admit source within its version scope | Author PDF and printed technical definitions/proof inspected; Crossref identity corroborates | Placeholder PDF metadata prevents exact publisher-version claim | Current notice history and exact publisher equivalence | Retain source limits and P17-09 follow-up | A journal-byte identity or exhaustive notice clearance |
| Credit sound, incomplete approximation | Theorems 4.1/5.3 and the A:7 example reconstructed; printed variable checked | No completeness or financial theorem transfer | Practical quality/efficiency and different query/data domains | Add scoped P18 comparison | Mixed financial histories, runtime behavior or default policy |
| Keep proposal not_ready | Existing financial query contract is correct within its declared scope; wider MC/G obligations remain | Five E workstreams and independent/human acceptance remain open | Required methods, cases, interfaces and review | Continue ready P17/P18 work | Proposal acceptance or implementation correctness |

Engineering evidence consists of retained source hashes, metadata and rendered
notation inspection. Mathematical evidence is the paper's stated proof plus
the local exact truth-table derivation. The scientific conclusion is limited
to this relational competitor; no issuer facts, accounting treatment or
stochastic ranking are evaluated. The strongest alternative explanation is
that the existing manuscript already prevents conflating operational unknown
with mixed histories; it does, so the proposed edit supplies comparison and
reader justification rather than a claimed bug fix. If a later publisher
version changes the theorem, or if the proposed comparison overstates the
transfer, revise or remove that passage.
