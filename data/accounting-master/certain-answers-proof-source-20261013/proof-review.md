# Primary proof audit: certainty as objects and knowledge

13 October 2026. The checked artifact is the author-hosted **26-page
17 November 2015 preprint** of Leonid Libkin, *Certain Answers as Objects and
Knowledge*. Its title page explicitly calls KR 2014 a preliminary version.
The author's publication page and Crossref identify the article as
*Artificial Intelligence* 232 (2016), 1–19,
DOI 10.1016/j.artint.2015.11.004. The exact KR proceedings text and final
publisher bytes were not compared. Cite this inspected author preprint with
the journal metadata and version qualifier. The original PODS 2014 PDF remains
distinct.

All 26 pages were read. Rendered original pages 1, 11, 12, 17, 18, 20, 21
and 23 were inspected for identity, hypotheses, proof and relational
corollary. There is no appendix. Full page/section disposition is in
reading-anchors.json.

The primary proof has this dependency chain:

1. Definitions 1–2, pp.8–9: a pre-domain has objects D, complete objects C
   and semantics [[x]] ⊆ C. Information order is x≼y iff [[y]]⊆[[x]]. This is
   **reverse inclusion of completion sets**, not ordinary row containment.
2. Definition 4, p.11: an abstract database domain includes an isomorphism
   family with a nonempty matching complete representative for every object
   and index, plus a common-refinement condition. Definition 5 also needs a
   formula class closed under conjunction, a formula δ_x defining each
   object's complete semantics, and finite-index invariance of each formula.
   These are material assumptions, not decorative notation.
3. Propositions 2–4, pp.13–14: in such a system the object lower bound of
   [[x]] is x; the common theory of [[x]] equals Th(x), and δ_x represents its
   certain knowledge. Proposition 5 constructs an object lower bound that
   does not express all certain knowledge. Neither form exists automatically.
4. Theorem 1, p.15: certain knowledge equals a greatest lower bound of the
   common theory, when that formula exists. The proof compares model sets
   and uses definability of δ_y to rule out a purported smaller model set.
5. Definition 6, p.15: a query must preserve informativeness between the
   **chosen input and output information orders**. Definition 7, p.17 adds
   genericity across the relevant isomorphism relations.
6. Theorem 2 proof, pp.17–18: monotonicity first gives
   Th(Q(x))⊆Th(Q([[x]])). For the reverse, take a formula true of all completed
   answers; finite-index invariance selects j, genericity selects k, and
   the domain condition supplies c∈[[x]] with c≈_k x. Hence Q(c) and Q(x)
   agree on that formula. Therefore Th(Q([[x]]))=Th(Q(x)), and the target
   representation system turns this into certain knowledge δ_{Q(x)}.
   Only then does the proof show Q(x) is the greatest lower bound of answers,
   using δ_y to compare any competing lower bound y.
7. Section 7.1, pp.18–19, gives a counterexample without the representation
   system: monotonicity alone leaves Q(x) below the true object lower bound.
   Without genericity the paper gives only an approximation guarantee
   (Corollary 2); a substitution property with source and target
   representation systems is an alternative hypothesis (Proposition 7).
   SQL's null comparison is an explicit nongeneric example. Do not treat
   ordinary SQL or an accounting query as automatically generic.
8. Proposition 9 and Corollary 3, p.20: for relational tuple answers
   interpreted under **OWA**, the input/query pairs are OWA/existential
   positive, WCWA/positive, CWA/positive with universal guards. The CWA
   case means **closed-world inputs and open-world outputs**. The proof
   invokes preservation results under the corresponding homomorphisms;
   the syntax-to-preservation direction is explained by structural
   induction, with cited technical predecessors for the general results.
   Corollary 4, p.23, relates the guarded fragment to a restricted
   relational division construction. It does not include arbitrary set
   difference, SQL negation, financial aggregation or nonlinear constraints.

## Verdict relative to proposal 2.71

The proposal's broad statement that naive evaluation needs chosen input and
output semantics, monotonicity, genericity and an answer representation
system is **correct**, now supported by the inspected primary proof.
The phrase “guarded extension under closed-world semantics” is **ambiguous**:
it can suggest closed-world output semantics. The actual relational corollary
uses CWA input and OWA output. A scoped 2.72 manuscript repair should name
both and cite this source. The two-history payable calculation is a local
exact derivation that does **not** depend on Theorem 2.

The quantity actually specified by AccDSL is a family of historical answers
and a Boolean all-histories query. No abstract domain, information ordering
on every financial output kind, isomorphism family, formula class or δ_x has
been established for the full accounting language. Thus the paper's theorem
does **not** establish financial naive evaluation, solver termination,
general conformance or empirical validity. A correct finite example is not
such a transfer.

The source PDF's CWA representation-system paragraph on p.12 typesets
RS_OWA where the surrounding CWA text clearly calls for RS_CWA. Record it as
an apparent local symbol typo; the subsequent Proposition1, Theorem2 and
Corollary3 names/scope were inspected independently. No correction to the
mathematical result is inferred from that typo.

## Literature disposition

Source-support: author-page URL, Crossref record/DOI, original PDF hash and
this full technical reading are retained. Crossref response has no
update-to/updated-by or relation field for this record; no comprehensive
retraction/erratum clearance is claimed.

Citation/venue: *Artificial Intelligence* 232, pp.1–19, published March2016
per Crossref. No citation-count/ranking refresh was obtained; neither would
support the theorem. The author preprint was submitted November2015 and is
longer in physical pages than the journal pagination.

Backward: the paper cites Imielinski/Lipski1984 [2] (SOURCE_BLOCKED),
Gheerbrant/Libkin/Sirangelo2014 [21] for naive relational evaluation,
Libkin2011 [30] for general data models, and Libkin2015 [38] for SQL
three-valued logic. They are relevant methodological leads, not papers
silently inspected by this proof audit. References [33]/[34]/[32] are proof
dependencies for the relational preservation claims. Constraints, XML and
graphs remain separate future extensions.

Forward: Crossref's second search row is an unrelated later paper and was
not treated as this source or as a verified citing work. No forward search was
performed in this bounded four-request inquiry.

Claim support: Definitions4–7, Theorem2 proof, Proposition9/Corollary3 are
primary technical support for the scoped correction. The payable example and
full-family satisfiability checks remain project derivations.

Omission/reviewer risk: the exact KR2014 preliminary version and final
publisher text were not compared. This blocks claims of version identity,
but not the bounded claim about the **inspected** preprint. Wider survey
coverage and the other source-blocked works remain open.
