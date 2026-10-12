# Version 2.47: the share component and a guaranteed benefit

12 October 2026. E07/C05, P18/C08; MC16/19/22/28/30/32–35, G7/G8/G16.
The separate **184-page Version 2.47** adds direct-participation eligibility
and the guarantee mechanism on PDF 136–137, retaining the prior conditional
10% illustration. It distinguishes the settlement payoff from fulfilment
cash flows and the complete CSM movement, within the retained historical
AASB 17 edition.

Candidate: docs/design/proposal/manuscript-vfa-20261012/accounting-product-proposal.pdf
SHA256: 7c7f76426717293127b4469a937eff9ddb50a543ff7fee5b4a87f309a97f40a5

All **123 integration checks pass**. Every old paragraph, all 48 displays
and all 93 references are preserved; the addition uses the existing aasb17
reference. The source unit's 30 source checks and 15 exact-arithmetic checks
and all manifest-bound input/artifact hashes remain valid. The full final
LuaLaTeX/BibTeX build is clean, with no TeX, box or bibliography warning.

## Bounded rendered review

Baseline pages 135–137 were read before editing. Final pages 1, 5, 135–139
and 184 were read at page resolution, at most two per tool output. The first
build split the short derivation between pages 136 and 137. One explicit page
break before the new example keeps its assumptions, formula, three-row table
and interpretation together on final PDF 137. The earlier PDF, build/check
records and initial renders are retained as superseded layout evidence;
only its pages 136–137 received visual review. No prose was removed.

Final PDF 136 retains the prior PAA, edition and reinsurance boundaries,
the original 10% component example and the new eligibility paragraph. PDF 137
shows the complete payoff/CSM explanation and the inherited claims-development
formula and caution. PDF 138 begins the existing adoption section coherently;
PDF 139 retains the basis/version and information-date limitations. The cover
prints 2.47, contents entries agree with printed pages, and the final
bibliography page remains legible.

Answers to the five pre-edit reader questions, by the author:

1. Eligibility requires the specified contract link and inception expectations
   about substantial returns and variability over the contract duration using
   probability-weighted present values. The 90% value is an assumed benefit
   term and the three rows have no probabilities; neither decides eligibility.
2. The reference pool determines contractual payments; the insurer need not
   own it. The illustrative pool is expressly held, and asset records remain
   separate from insurance measurement.
3. Below the floor boundary, the first 20 increase both adds a 2 share
   component and removes an 18 extra floor payment. Above it, only the 2
   share component changes. The negative amount is a component funding gap.
4. The example computes an amount left at settlement. Measured expected cash
   flows, discount/RA inputs, group CSM and loss component, service information
   and mitigation conditions are still needed for accounting.
5. B104 includes the additional FCF component; B111–B113 give different
   destinations to pass-through, share and guarantee changes. Paragraph 45
   retains other movements and the loss/mitigation exceptions. The original
   multiplication is correct for its stated component.

The root/insurance surface scans found no missing or duplicated labels,
repeated words, punctuation issues or placeholders. The isolated section
reports two inherited unnumbered displays, five unreferenced navigation labels
and one long initial-assumptions sentence. The displays are locally explained
and retained unchanged; the labels support navigation; the sentence lists
explicit assumptions of the earlier separate two-year case. None is a new
defect or a reason to delete substantive content. A surface scan is not a
comprehension verdict.

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Keep Version 2.47 as the provisional current candidate | Supported material addition; exact preservation; 123 checks; clean build; eight final pages read | No source, quantity, preservation or build veto | Independent/human/domain comprehension and complete-document regression pending | Scoped commit, then inspect transition-method information limits | Whole-document acceptance, current compliance or E07 closure |
| Keep the original share illustration and explain its limits | Component calculation remains correct; guarantee example separates the additional exposure | Whole-CSM or eligibility inference from the payoff table remains vetoed | Actual contracts and measured inputs | Preserve source and example scope in future work | A full insurance contract, expected valuation, profit or CSM journal |

No stochastic comparison ran; no ranking or numerical default changed. The
finite values are exact only for the authored settlement component. The
post-run red team focused on confusing the table with profit/FCF or treating
a guarantee as automatically disqualifying. The final prose explicitly
separates those quantities and preserves the duration/inception conditions.
The source applies to stated historical period starts; current amendments and
actual insurer application remain open. Author review is not independent or
human acceptance.

Readiness stays **not_ready**; E01/E05/E07/E08/E14 remain open. The frozen
forty-target frontier, 56/136 date split and source-access blocks remain.
Next: docs/plans/accounting-insurance-transition-source-20261012.md.
