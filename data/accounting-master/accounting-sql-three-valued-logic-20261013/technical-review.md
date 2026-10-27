# SQL three-valued logic inquiry

13 October 2026. Proposal 2.72; readiness remains `not_ready`.

## Identity and evidence contract

The retained author publication page links `papers/tods16.pdf` as **SQL's
Three-Valued Logic and Certain Answers**, by Leonid Libkin, *ACM Transactions
on Database Systems* 41(1), 2016, pages 1--28, and identifies `papers/icdt15.pdf`
as a preliminary version. The downloaded author-hosted PDF is 28 pages,
SHA256 `b72ca55e64a4c890a2ee0bf3053af55b449a8b52a521329a378bb70a54715dbf`;
HTTP returned 200, `Content-Length: 320236`, `Last-Modified: 22 February
2016`. Crossref independently identifies the title, author, venue, volume,
issue, pages and DOI `10.1145/2877206`, published 7 April 2016. The Crossref
receipt and response are retained in `sources/crossref.headers` and
`sources/crossref.json`.

The complete retrieved text was extracted and read. The paper's source is the
explicit author link, not a title-only discovery result. No claim is made that
this PDF is byte-identical to the publisher copy or the ICDT preliminary
version.

## Technical findings

The paper defines incomplete relational instances containing constants and
marked nulls. Its main closed-world semantics replaces nulls by constants and
uses the intersection of answers over all valuations as ordinary certain
answers. SQL's ordinary three-valued comparison semantics can have both false
negatives and false positives relative to those answers. The paper gives a
counterexample for nested negation/difference and explains that SQL collapses
`unknown` with `false` when filtering, so later negation can turn uncertainty
into a returned false positive.

Libkin's `Eval3v` changes atomic relation and equality evaluation while retaining
three-valued Boolean/quantifier rules. Atomic membership is 1 when the tuple is
present, 0 only when no stored tuple can unify with it, and 1/2 otherwise;
equality is 1 for identical terms, 0 for distinct constants, and 1/2 otherwise.
Theorem 4.1 and the more general Theorem 5.3 establish soundness: value 1 is
contained in certain answers with nulls, and value 0 is certain for the negated
query, for first-order queries under the closed-world setting. Value 1 is a
sound under-approximation, not completeness. The paper also gives an
open-world variant, but changes the rules and loses negative certainty for
atoms and existential formulas.

For query classes, ordinary SQL evaluation has certainty guarantees for unions
of conjunctive queries. The paper's modified procedures cover first-order
calculus, UCQ with inequalities, relational algebra and selected nested
semi/anti-joins. The relational-algebra translation returns paired positive and
negative queries; tuples in neither are unknown. It preserves guarantees under
contained translation replacements, exposing an efficiency-versus-approximation
trade-off. The paper proves agreement with ordinary evaluation on complete
instances.

The technical limits are material for AccDSL. The source assumes textbook set
semantics; SQL's default bag/multiset semantics is explicitly left for future
work. Grouping and aggregation are outside the covered query fragment. The
closed-world and open-world semantics are distinct, and the open-world result
has different, weaker negative behavior. The authors use a single domain as a
theoretical simplification, flag type-specific domains and large Cartesian
products as practical issues, and call for implementation and experimental
study. The approach is relational and does not supply accounting measurement,
nonlinear valuation, temporal history, scenario intervention, probabilistic
conditioning, or a joint financial-history model.

## Relation to AccDSL

This is a direct competitor and a useful omission boundary for E08. It supports
AccDSL's existing distinction among `certainly true`, `certainly false`, and
`unknown`, and supplies a concrete soundness target for a bounded relational
subquery. It does **not** establish that AccDSL's financial queries satisfy the
paper's relational schema, marked-null, homomorphism, query-fragment, or
representation conditions. In particular, no transfer is justified for
financial negation, aggregates, bags, nonlinear constraints, temporal joins,
scenario conditioning, or outputs whose omitted rows have economic meaning.
The proposal must retain explicit query class, input/output world assumption,
answer scope, and completeness metadata.

A local derivation confirms the paper's central counterexample: with `R={1}`
and `S={null}`, ordinary `R - S`-style negation can return `1` although a
valuation of the null to `1` removes it; the modified three-valued procedure
returns unknown rather than a false positive. This is explanatory evidence,
not a runtime SQL experiment or a production conformance result.

## Decision

The identity and technical-reading criterion passes within source/version scope.
The competitor is admitted as scoped literature support for three-valued
certainty semantics and as a boundary on genericity. No manuscript edit is
made in this inquiry because the current 2.72 text already states the relevant
SQL-null warning and preserves the closed-world-input/open-world-output
qualification from the distinct certainty proof. The evidence advances E08
within scope but leaves all five workstreams, P19, implementation hold,
independent review and human/domain acceptance unchanged.

| Decision | Primary criterion | Veto | Next action | Not concluded |
|---|---|---|---|---|
| Admit SQL/TODS source | Identity, source bytes and full technical text checked | None | Preserve source/version and scope in controls | Publisher-byte equivalence |
| Credit three-valued soundness | Theorems and limitations inspected | No transfer veto; domain mismatch remains | Retain explicit query/world/completeness contract | Financial theorem transfer or runtime correctness |
| Continue P19 negative | Broader design and acceptance remain incomplete | Promotion veto remains active | Refresh controls and continue next ready E01/E05/E07/E14 unit | Readiness, implementation, accounting compliance |

Post-run red team: the strongest alternative explanation is that the paper's
result is only a database-null result. That is correct as a limitation: its
value here is the explicit competitor and boundary, not a financial theorem.
The weakest evidence is the lack of an implementation benchmark and exact
publisher-byte comparison; neither is needed to identify the paper or inspect
its stated theorems, but both remain non-claims.
