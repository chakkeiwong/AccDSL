# Explain direct participation and a guaranteed benefit

12 October 2026. E07/C05 and P18/C08; MC16/19/22/28/30/32–35, G7/G8/G16.
Protected baseline: 183-page Version 2.46, SHA256
b13be68b6c5de2027f9f7a773dee70361feedb2c4b46a65bf81836e98418513e,
docs/design/proposal/manuscript-otsl-20261012/accounting-product-proposal.pdf.
Create a separate Version 2.47 after the VFA source unit closes.

Reader: an accounting researcher or implementer who has read the existing
general-measurement examples and needs to understand why a stated return
share does not determine the entire guaranteed-contract exposure or CSM.
Read baseline PDF 135–137 and preserve the source outside the candidate.
Keep the current conditional 20-times-10% component illustration intact.
Add a compact explanation immediately after it: the inception/duration
conditions, the distinction between reference pool and held assets, a small
settlement-component example, and the resulting separation between the share
change, other FCF changes and full CSM movement.

Use only the already checked historical AASB 17 edition and existing aasb17
reference. Cite B101–B108 for eligibility, B104/B111–B113 for the fee and its
components, and 45/B115–B118 for exceptions. Do not introduce numerical
eligibility thresholds. Define the authored 90 minimum, 90% benefit share,
held-pool amount U and one settlement date before using the payoff relation.
Use the three checked rows to explain the difference between a 20 and a 2
change. A small table is acceptable if it makes those rows easier to compare.
Keep the example distinct from a complete insurance contract, probability
model, fair value, fulfilment cash-flow measure, CSM or profit calculation.
Do not imply guarantees automatically disqualify direct participation.

Evidence contract: exact Version 2.46 is the comparator. Pass requires a
material supported addition; every old paragraph, all 48 displays and 93
references preserved; a clean LuaLaTeX/BibTeX build; resolved labels/citations;
and actual inspection of changed pages, transitions and affected navigation.
Content loss, source/edition drift, a wrong quantity, missing caveat or broken
render vetoes the candidate. Counts and scans are engineering diagnostics;
author answers do not supply independent/human acceptance.

Skeptical/default audit: the baseline illustration is correct within its scope
and must not be described as a discovered accounting error. The new payoff
inputs are authored convenience choices, with an exact finite diagnostic
already declared and run. Their role is explanation, not a new model/default.
The material risk is confusing settlement cash arithmetic with an expected
present value or CSM movement. The plan passes only with those quantities
distinguished in the prose. No current-rule or full-compliance claim follows.

Artifacts: data/accounting-master/insurance-vfa-integration-20261012 and
docs/design/proposal/manuscript-vfa-20261012. Record before/after reader tasks,
source and candidate hashes, commands, preservation/build/surface checks,
renders, decision and manifest. Refresh the four live controls and commit the
scoped result. Then continue the remaining source/method queue under a concrete
audited next plan. Preserve all closed units, not_ready and the five wider
evidence gaps. Runtime implementation, installation, fees, outreach and
publication remain held.
