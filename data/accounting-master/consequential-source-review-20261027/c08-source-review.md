# C08: financing models and the limits of verification

27 October 2026. This is a source-review record for the exact 5.53 passage
simulation/lit-05-debt-12.tex, bound in source-lock.json. Physical page numbers
refer to retained PDFs. Inspected means read, not independently proved or
numerically reproduced. The recovered inspection below is continued with
explicit additional findings rather than presented as a new complete reading.

The passage's distinction between a candidate policy and verified equilibrium
is supported. Full certification of the retained Benzoni verification proof is
withheld for the specific regularity and notation issues below. The other
financing papers do not identify actual company policies or accounting
treatments. No manuscript change is yet justified by these findings alone:
the current passage already requires verification and states model limits.

## Benzoni, Garlappi, Goldstein and Ying

Retained source: docs/papers/Debt dynamics with fixed issuance costs Benzoni
(2023).pdf, 78 pages, SHA256
42cd37f8ffeba1c88c97042412b925f2195469de6cd7de82dd1522b503d135e1.
This is Chicago WP 2023-01 with the appended formulation by Julien Hugonnier;
it is not silently equated to another journal or code edition.

Inspected scope: physical10–12 (model),20–23 (Propositions1–2),37–39
(AppendixA.1),49–78 (appended formulation and proof chain, LemmasII.1–II.10,
PropositionsII.1–II.3). Rendered physical38,39,74,75 checked for the material
wording/equations. Physical39 was re-viewed during recovery.

Face debt and price per unit face differ. Agents are risk neutral and default
recovery is zero. Barrier strategies are the candidate class; admissible
deviations are broader. Integrability(I.7) supports the limiting and uniform
integrability arguments. The stopping transformation uses v=e−ê and obstacle
ψ=ϕ⁺−ê. The weak HJB operator is a measure, not only a pointwise density.
Boundary/growth conditions are part of verification.

| Finding | Exact anchor and classification | Consequence and next action |
| --- | --- | --- |
| Continuous nondecreasing derivative is said to be absolutely continuous | Physical39/printed35, between(A.5) and(A.6). This general implication is wrong; a Cantor-function derivative supplies a counterexample. | Do not discard a possible singular part of the second derivative without another argument. Check the model's additional regularity or retain the full measure inequality. This alone does not falsify the final theorem. |
| Transformed unknown omitted in a proposition | Physical74/appendix25, PropositionII.3 says e solves(II.14); equation(II.14), PropositionII.2 and main AppendixA.1 use v=e−ê. | Preserve the literal source wording and use the transformed unknown in any local deduction. Likely notation omission; no theorem rejection follows merely from that diagnosis. |
| An open continuation interval is called compact | Physical76/appendix27 proof of LemmaII.9(v), C=(yb,yu) versus main physical38's closed[yb,yu]. | Verify extension to closed endpoints and location/uniqueness of maximizers before invoking the compact-set envelope corollary. |
| Strict versus weak threshold comparison | Main Proposition1 states yb<yb,NI; appendix LemmaII.9 states ≤. | Reconcile the strict case before relying on it; the weak comparison alone does not imply strictness. |
| Drift assumptions differ | Main μ<r; appended model0≤μ<r. | Preserve the stronger appendix restriction unless a proof extension is supplied. |

The claimed mathematical target is the nonpositive weak HJB measure for the
transformed value. A density-only check computes a different object unless the
singular component is known to vanish. Equality of those checks has not been
established from the retained proof's continuity/monotonicity argument.

Author-associated code: Mendeley10.17632/jcrg6zdtx8.1, published13July2022,
Robert Goldstein. sources/benzoni-code.zip is6,811,723 bytes, SHA256
908cef3b26ed8e16c0b6771404002030e8355ca00dc67afcdbda80e85006f75d.
Only main_prg.m and README.txt were extracted; author-code-manifest.json binds
their exact bytes. No MATLAB code or saved MAT result was executed/loaded.

Static scope: main_prg.m20–40 defaults to loading saved results;62–64 sets
tol1e−20 and large solver budgets;81 replaces infinity by1e9;93–98 scans5 or100
candidate points;520–578 checks finite grids and a separate asymptotic limit.
Functions1076–1125 and1177–1238 use fsolve and an implicit derivative with
denominator y s″(Y)−P″(Y). The viewed functions capture solver diagnostics
without testing them before using the solution;1230 disables an algebraic
cross-check. These are inspection findings, not observed numerical failures.
The finite checks do not prove a continuum inequality or the existence of a
globally smooth optimizing branch. Source defaults are not AccDSL defaults.

## Dewatripont, Legros and Matthews

Retained source: docs/papers/Moral Hazard and Capital Structure Dynamics
Dewatripont (2003).pdf,55 pages, SHA256
e708e32d6ccc0b3626a3f6b38bc6b31cb4210dddcdc041bae40d75a0c4c4dff9.
PIER03-006, January29 edition. Physical9–50 read continuously: Sections2–6,
AppendixA proofs (LemmasA1–A5, Propositions1–6), all AppendixB examples.

Strict MLRP, limited liability and monotonicity restrictions LE/MI/LI,
compact feasible contracts and efficient renegotiation matter. Message
strategies are pure; randomized contract payments are renegotiated before
lottery resolution. Proposition1's equilibrium-existence step is supplied by
compactness/continuity in AppendixA, physical34. Proposition2,physical36–37,
chooses the largest debt-effort maximizer and yields existence of a weakly
dominating debt equilibrium, not uniqueness or domination by every equilibrium.

Investor bargaining adds SEP/FOA/SP. Ray bargaining adds SEP′ and the specified
ray rule; it is not a general Nash-bargaining result. Footnote16,physical17,
distinguishes the wage option from equity. AppendixB's mixed-message example
uses high off-path payments and sufficiently loose investor liability bounds.
These qualifications support the current limited paragraph. They supply no
ordinary-equity conversion, legal restructuring or actual-issuer conclusion.

## Inspected dependencies and retrieval limits

Milgrom–Segal: sources/milgrom-segal.pdf,20 pages, SHA256
0c31ba565c69fa6f8d10b589b12ab8c191ec9b04d2bf49e7a70faa3946f06eb1,
author-hosted publisher layout. Physical10–12,16–17 read. Corollary4 uses
compact X, upper semicontinuity and continuous parameter derivative;
differentiability requires agreement of parameter derivatives at maximizers.
It establishes absolute continuity of value V, not automatically of V′.
Corollary5 requires convex compact constraints and local Slater conditions.
Matched DOI10.1111/1468-0262.00296; inspected metadata has no update field,
which is not exhaustive correction clearance.

Lamberton–Zervos: sources/lamberton-zervos-preprint.pdf,60 pages, SHA256
073c3f1397ae74ebb2f053306815cc64ac25676735bf608efa30e4c8b40b2c42.
Header arXiv1207.5491v1 dated23July2012 versus manuscript date7February2018:
version anomaly remains explicit. Matched journal DOI10.1214/EJP.v18-2182.
Physical9–11,33–50 read for assumptions, weak VI, Theorems12–13,
verification, smooth fit and counterexamples. Corollary18,physical47, gives
f′+≤v′+≤v′−≤f′− at contact. The measure operator retains a possible singular
second derivative. Proof12 on physical37–40 has now been inspected; earlier
potential-theory dependencies remain open. Preprint12/13/18 are
not asserted equivalent to the cited journal6.3/6.4/7.5 without comparison.

The two journal retrievals saved with .pdf names are HTML failures, not PDFs.
The guessed DOI10.1214/EJP.v18-2271 resolved to an unrelated preferential-
attachment paper and is rejected; its response is retained as failed discovery.
Matched metadata is in lamberton-crossref-search.json. A direct matched DOI
refresh and Dewatripont metadata refresh returned429; no exhaustive refreshed
correction clearance is claimed. Benzoni current Crossref metadata matched and
contained no update fields. October26 source/correction records remain retained.
Empty web-tool responses provide no citation evidence. Local exact primary
sources, inspected anchors and explicit retrieval outcomes support this note.

## Lambrecht and Myers: current implication review

Retained source: docs/papers/The Dynamics of Investment Payout and Debt
Lambrecht (2017).pdf, SHA256
9487a76d78397891ae57906990bfbd4fa73fb66ee5ba86e7b5af42124260210b.
Cambridge manuscript dated26January2017; DOI10.1093/rfs/hhx081 identifies
the publication, not checked equation identity with this manuscript.

In this continuation physical9–16,34–37,41–52 were read. Earlier technical
scope9–12,15–16,23,36,43–45 is retained. The dated budget and governance
constraints are(1)–(3),(11),(15) and no-Ponzi restriction(16). Footnote9,
physical14–15, expressly omits the optimal switching point between the two
governance constraints. Current C08 makes no claim to solve that problem.
Proposition4 and physical35–36 impose constant returns, CARA preferences,
continuous net-worth paths, immediate liquidation at N=0 and a specified
outside utility. Debt then equals capital at the first boundary hit. This
supports safe debt under those assumptions; jumps, delay or disposal costs
would change the repayment argument. The current paragraph states these
substantive limits. The appendix's physical44–52 supplies HJB, first- and
second-order, transversality and value-matching calculations, not an identified
issuer policy. No parameter/default or full optimal-control proof is adopted.
Prior October26 correction/index records are reused at their exact bounded
scope; no new exhaustive publisher clearance is asserted.

## Finite participation example

The other current C08 location, lit-26-finite-finance-8.tex,lines4–48, was read.
The risk-neutral one-period example is a local calculation. An independent
stdlib Fraction recomputation allocates each estate sequentially to senior
then junior creditors, rather than copying the displayed allocation formula.
It confirms all stated amounts, quote inconsistency, cash refusal and outside-
option feasibility. The source/file bindings and amounts pass74 scoped checks
in c08-verification.json. This supports C24's finite distinction as well.
It proves neither an unrestricted financing equilibrium nor actual-company
participation, accounting recognition or a legal remedy.

The whole current C08 implication is now provisionally supported at this
scope. Source edition/correction residuals, the unaccepted full Benzoni
verification proof and independent review remain explicit. The other current
claims retain their individual unread/dependency frontiers.

## Decision and continuation

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain scoped C08 conceptual discussion provisionally | Price/policy distinction, constrained contract comparison and exact finite example supported | No contradiction with current scoped sentences identified; full Benzoni proof remains withheld | Source editions/corrections and independent acceptance | Continue other current claims; retain the specific proof frontier | Full equilibrium-proof acceptance or company-policy default |
| Withhold Benzoni density-only verification acceptance | Equivalence to the weak measure target not established by the printed regularity step | Missing regularity premise vetoes this promotion | Can model-specific regularity supply the missing step? | Derive explicit sufficient conditions; test them against source assumptions | The theorem is false or all uses of the model invalid |
| Continue the program | No global continuation veto | Local claim limits preserved | Other consequential claims and specification joins remain | Continue available source and C2/C4 work | Release readiness, forecasting validity or statistical ranking |

Strongest alternative explanation: the model's analytic continuation-region
solutions and unique optimizer may supply regularity not justified by the
quoted general implication. A checked derivation under the original assumptions
would resolve that gap. The weakest evidence is edition/proof equivalence and
the unproved removal of a singular derivative component. Static code does not
resolve either. This record preserves engineering inspection, mathematical
validity and substantive interpretation separately.
