# Sequential transport: current-sentence technical review

27 October 2026. C03/C05, MC10–12/26/29/30/32. Baseline source sentences are
simulation/lit-09-approximation-4.tex (sampled-path section) and
simulation/lit-09-approximation-10.tex in protected 5.52-R2; those sentences
are byte-identical to 5.52-R1. This reading is a bounded technical audit, not
an entire-literature acceptance. Original reading ledgers remain unchanged.

## Adapted empirical measures

Retained arXiv 2002.07261v2, dated 17 May 2021; PDF SHA256
413977988516ce9b247d273dff1edf5de09a7e93a69babac6dc7e49e2ad6442d.
Read Definitions 1.1–1.2, Theorems 1.3/1.5/1.7, Assumption 1.4, proof
assembly in Sections 3–5, Lemmas 3.1–3.4 and 5.1–5.3, Theorem 6.1 and
its modified estimator/proof, and Example 7.1. Text routes: retained
literature-closure-20261026/text/adapted-estimation.txt, lines 103–300,
511–716, 718–858, 940–1122, 1277–1580 and 1590–1815. Lemma 3.3's
intermediate combinatorial lines 859–939 were not reread in this unit; the
earlier reading is retained and no new standalone proof-verification claim
is made for that lemma.

The source defines bicausal coupling and an iid sample of complete paths in
([0,1]^d)^T. Its estimator quantizes every date. The almost-sure result does
not require Lipschitz kernels; the rate and concentration results do. The
proof first handles continuous kernels, then uses Lusin extension and coupled
samples to remove that restriction. The Markov estimator pools by the current
state instead of the whole history. Its exponents omit T, but constants retain
T and the Lipschitz parameters. The manuscript states each of these boundaries
correctly. Example 7.1 shows that distinct first observations can disclose the
empirically stored future; an optimizer's extra information changes its value.

Verdict for the current sentences: supported within the retained version and
stated iid/bounded/finite-horizon or rate assumptions. Neither the estimator
construction nor its proof justifies an iid interpretation of one issuer's
reports, a Markov balance-sheet state, an arbitrary learned generator, or an
empirical forecasting claim. No runtime is adopted in this unit.

The arXiv abstract/version page was fetched and retained on 27 October 2026.
It names v2 as the last revision (17 May 2021). This supports the precise
version identity only. It does not prove absence of every publisher correction.
The DOI landing request returned a short access response rather than inspected
journal technical text; its bytes/headers are retained separately. No
working-paper/journal equation equivalence is inferred. Built-in search calls
returned no source content; the local primary PDF remains the technical source.
The bibliography should state v2 explicitly at the next coherent integration.

## Nested-distance policy transfer

Pflug–Pichler retained PDF SHA256 is recorded in source-records.json. Read
Definition 5.1 (constraints on both information structures), Theorem 6.1 and
its proof through the epsilon-optimal comparison (physical pages 6,10–11).
The proof transfers the decision by conditional averaging and uses Jensen's
inequality. Convex feasibility, convex cost in decisions and uniform Hölder
regularity in uncertainty are substantive hypotheses. The manuscript's example
of issuance sizes {0,1}, whose mean 1/2 is infeasible, correctly identifies
why the theorem does not automatically establish discrete-policy transfer.
The source bounds optimized values after admissible transfer; it does not by
itself validate reuse of an arbitrary unchanged policy.

## Financial adapted distance

Backhoff-Veraguas et al., retained journal PDF SHA256
45c3fc6746ad2771b21541bd144046a296a457e40d4a7b1bf6b7389c2e573aa0.
Read Theorem 1.5, Lemmas 3.7–3.8, Theorem 3.10/proof, Remark 3.11, proof
of Theorem 1.5 and Remarks 5.2–5.3 (physical pages 6,18–23,29).
The weak bound constructs another bounded predictable strategy; keeping the
same strategy requires additional Lipschitz regularity and the second-moment
term. The distance uses semimartingale decomposition, not merely a sum of
pathwise price differences. Exact superhedging and unbounded-position examples
show the limits. The manuscript's current caution is supported.

No new implementation, statistical ranking or general company-state distance
is accepted. The finite common-policy coupling correction is a separate local
derivation. The model relation, feasible actions, information, initial pair
and requested loss must be supplied before its numerical bound is useful.

| Decision | Criterion | Vetoes | Uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain current C03/C05 source statements | Technical assumptions and proof mechanism match current text | No conflicting claim found in inspected passages | Exact publication-version/correction and broader dependencies remain separately open | Pin adapted-estimation v2; continue C18/C19/C20/C26 and quantitative particle dependencies | Entire sources reread, general discrete-control transfer, issuer-data rates or release acceptance |
