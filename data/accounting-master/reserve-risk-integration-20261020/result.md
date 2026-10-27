# Version 3.45: finite reserve-risk integration

20 October 2026. P15–P19; R03/R04/R07/R08;
MC10–12/18/22/26/29/30/32–35. **Proposal remains not_ready.**

The 401-page candidate adds an implementable finite explanation of quantiles,
expected shortfall with boundary atoms, corrected proportional-hazards weights,
future-information risk, conditional-mean CDR variances and capital-charge
timing. It does not select an insurer's law, preferences, capital basis or
accounting policy. The baseline is Version 3.44, 396 pages.

Candidate: `docs/design/proposal/manuscript-reserve-risk-20261020/accounting-product-proposal.pdf`.
SHA256: `92b1ab24970cb301ba96d409edcadd3679fc778917c81e82b1c82da592e3dd0d`.
Baseline SHA256: `afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80`.

## Evidence and scientific disposition

The completed source inquiry at `../r04-reserve-risk-20261020/` supplies
50 exact assertions, five PH cases and 21 checked source anchors. It found
the accepted manuscript's post-first-observation PH subtraction wrong relative
to its own integral. The addition derives the correction and preserves the
unverified status of the final journal edition, author code and table impact.
The conditional variance result concerns expected future standard deviation,
not every future state or quantile capital. True conditional means are needed
for the reverse-CDR variance sum. The finite ES convention is a declared
local choice whose boundary atom differs from naive conditional tail means.

Exact expanded-source comparison preserves the entire earlier body after
removing only the addition and reversing the title/date change. All 143
baseline source files, 208 displays and 718 citation occurrences survive.
Only the root title/date and one include change in existing source files.
The new section adds eleven displays, nine citations and one information
tree. No bibliography entry was added. References resolve, critical build
warnings are absent and no out-of-page text was found.

The successful final LuaLaTeX build took 7.733 seconds; its exact command,
environment, provenance and source lock are in `build-manifest.json`. GPU
devices were intentionally hidden. First-attempt sources, checks, build and
reading evidence remain in `attempt-01/`. The repairs specify present values,
positive normalized probabilities and the two CDF boundaries explicitly.

`review.md` records actual ordered local inspection of physical 306–313,
separate title/contents inspection at 1 and 6, four review ledgers, eleven
display judgments and six reader questions. These are local author judgments.
The completed 3.44 whole-document review remains historical; the 3.45
affected-chapter and full regression are separate unfinished work.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain the finite explanation provisionally | Local reader questions answered; exact source/body preservation and source-unit arithmetic pass | No local binding, equation, reference or clipping failure remains | Actual insurer inputs, allocation, authority and original-source extensions | Review the affected chapter and whole 3.45 argument; inspect consequential originals | A general risk-adjustment engine, compliance, calibration or an entity default |
| Preserve all original obligations and not_ready | 53 requirements, six interactions and 46 operation rows remain unchanged in substance | Missing acceptance and source evidence veto only dependent claims | Independent implementability, domain judgment and human comprehension | Continue internal work and maintain exact-candidate assessment | Whole-row closure or completed master program |

There is no stochastic comparison or ranking in this unit. The strongest
alternative explanation for successful examples is simply that authored laws
satisfy their premises; that does not establish a usable real-world law.
Contrary applicable authority or different information/valuation conventions
would require a different application. The weakest evidence is actual-company
applicability, deliberately unadmitted. No continuation veto has fired.
