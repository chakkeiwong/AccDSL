**Scope checked:** Northstar arithmetic (opening state, both half-years, annual P&L, two cash-flow routes, bridges, interim correction, 2025 joint family), Apple carrying/notional/stress arithmetic, rounding enclosures, Bayes/Gaussian/causal/root examples, JSON expected values, and the stated initial-vs-extension inference boundary.

**Arithmetic verified (no mismatch found):**
- Opening 190/190; June 197/197 (cash 65, RE 22, prepaid 2); December 220.6/220.6 (cash 74.6, RE 40.6, prepaid 0). H2 depreciation 6 = 5 + 10/5/2. Tax 1.5/5.9; PBT 37, tax 7.4, profit 29.6; equity 70+29.6−9=90.6.
- Direct OCF 245−145−42−5−7.4=45.6; indirect 29.6+11−15+10+10=45.6; investing −22, financing −9, Δcash 14.6.
- Bridges C=245, P=155, S=145.
- Interim original: PBT 17.5, tax 3.5, profit 14, equity 80; corrected profit 6, equity 72, prepaid 2.
- 2025: depreciation 13, I=7−2α, PBT 80+2α, profit 64+1.6α, cash 93.6+1.6α, equity 146.6+1.6α, assets 286.6+1.6α; `joint_forecast` with x=1−α at 0, ½, 1 matches (6 / 64.8 / 94.4 / 147.4 / 287.4).
- Apple: 97,341−321−358=96,662=10,912+85,750; 10,848+83,956=94,804; 0.02×13/52×14,575=72.875; stressed statements balance (344,012.125 = 277,327+66,685.125).
- Rounded-debt family: inf 4.975 attained, sup 7.035 not attained; correct.
- Bayes 0.12/0.32→3/11, 8/11; 1/4, 2/3 → evidence 11/12 → 3/11, 8/11. Gaussian: precision 5/4, var 4/5, mean 8/5; cash 116/80; second independent 9/4, 4/9, 16/9. Causal 3 vs 2.5. √1.1∈[1.0488,1.0489]; bracket [0.1,0.2] brackets the 98→121 root. Rounding JSON enclosures consistent with `source-admission.tex`.
- Variance decomposition and inf/sup-over-point-masses argument are sound as stated.

**Scope/teaching order:** Ch 5 declares the initial fragment (exact linear + finite choice + symbolic α∈[0,1]); Ch 5 §finite-law gives the only evaluable probability model; `inference-methods.tex` explicitly confines Gaussian/continuous/causal to separately admitted extension schemas; `method-cases-v1.json` labels those cases as document calculations, not runtime conformance. This is consistent across the packet.

**Findings (all minor, nonblocking):**

1. **`05-mathematics.tex` §1 vs `source-admission.tex` §"Displayed precision".** Ch 5 presents the half-open interval $[v_i-q_i/2,v_i+q_i/2)$ as illustrative; the source-admission section makes the *closed* enclosure the conservative default when the tie rule is unknown, and §7 of Ch 5 then uses "declared half-open intervals". Repair: add one sentence in Ch 5 §1 cross-referencing §\ref{sec:source-admission} and stating that half-open is only used where a tie rule is declared, so the solver example is not read as the import default.

2. **`13-reference-company.tex` §"A correction changes what was knowable".** "The same query as of 3 March 2025 returns 110" relies on the date-only rule in `source-admission.tex` ($b_D$ = local midnight beginning 3 March for publication date 2 March). A date-only cutoff "3 March" could itself fall inside an unresolved interval under the same rule. Repair: state the cutoff as an instant with timezone (e.g. 3 March 2025 00:00 local or later) and mirror this in `fixtures/northstar.json`.

3. **`05-mathematics.tex` §"A finite probability model".** The unresolved-branch paragraph cites "mass 0.4" (the prior) immediately after deriving posterior 8/11; `inference-methods.tex` and `finite_law.unresolved_mass` use 8/11. Repair: say explicitly whether the unresolved example is under the prior (no evidence admitted) or the posterior, to avoid an apparent 0.4 vs 8/11 inconsistency.

4. **`05-mathematics.tex` §"Why published statements cannot identify all transactions".** References `Equation~\eqref{eq:running}`, which is not defined in any packet file (Ch 13 defines no labelled equation for the loan). Repair: confirm the label exists in a non-packet chapter; otherwise point to the Ch 13 $F+V=100$ discussion. Out-of-packet; not a transcription failure.

5. **`02-history.tex` opening paragraph.** The chapter opens by invoking "Northstar's corrected receivable and Apple's several debt amounts" before either is introduced (the only explicit forward reference is in the last section). Repair: add "(Chapter~\ref{ch:case})" to the opening sentence so the teaching order is explicit for a linear reader.

6. **`13-reference-company.tex` §"Recovering movements" vs `05-mathematics.tex` §"Building the family".** Ch 13 declares *per-half-year* slots while the identification claim is for *annual* totals; Ch 5 says the templates "identify annual collections, purchases and supplier payments". Under annual disclosure alone the half-year split is not identified; it is identified only because the interim statements are also admitted. Repair: one clause in Ch 13 stating that the half-year allocation depends on the interim filing, not on the annual bridges.

**Verdict reason:** Every number in the packet reconciles across the two cash-flow routes, the balance identity, the joint affine family in both parameterisations, the Apple carrying/stress arithmetic and the JSON expected values. Measure handling (families vs mixtures, no double counting, unresolved mass not renormalised), Gaussian completion, Bayes normalisation, causal observe-vs-intervene and root enclosures are correctly derived and correctly bounded. The initial (finite law, exact linear, symbolic α) versus later (continuous, MCMC, causal) scope is stated consistently in Ch 5, the inference section and the JSON purpose line. Retained open gaps (ASC, real-company semantics, insurance, regulatory data, human acceptance) are honestly labelled and not counted here. The six findings are clarifications, not material mismatches.

VERDICT: AGREE
