# Retrospective information and a market-based liability value

12 October 2026. Author technical-source review under the bounded dependency
plan. Eight official requests acquired six HTML responses and two primary
PDFs. Both failed URLs from the preceding unit remain untouched. The first
AASB 13 search selected a 2024-applicable compilation, so the explicit 2023
period search was used to locate its predecessor before technical reliance.

The AASB 108 PDF is compilation 3, dated 31 December 2022, prepared 6 February
2023, registered F2023C00187 on 10 February 2023, incorporating amendments
through 30 March 2021 and applying to annual periods beginning from 1 January
2023. The AASB 13 PDF is compilation 2, dated 30 June 2021, prepared 8 June
2021, registered F2021C00702 on 23 July 2021, incorporating amendments through
6 March 2020 and applying from 1 July 2021. Its official historical search
selection supports use for the declared 2023 comparison; the later HTML
preamble states a 1 January 2024 start and is retained as an excluded edition.
No complete current amendment chain or entity-specific early-adoption decision
is established. Compilation dates, amendment cutoffs, period applicability and
registration dates must not be conflated.

Reading coverage: AASB 108 PDF 1, 3–13, 16–17; AASB 13 PDF 1, 3, 5–16,
19–32, 34–35; AASB 17 PDF 10. That is 45 selected pages. The selected
108 reading includes paragraph 5, policy priority/application, estimates versus
errors and paragraphs 50–53, including the continuation on page 13. The 13
reading includes measurement through paragraph 90, definitions and complete
Appendix B, plus edition notes. Detailed disclosures on PDF 17–18, Tier 2
appendices, all external standards and subsequent amendments are not fully
reviewed. Of twenty generated renders, ten were inspected: 108 pages 1, 6,
12, 13; 13 pages 1, 9, 11, 16, 27, 28. Other renders are generated evidence
only. The exact inspected-page list controls, not the count of image files.

| Source | Checked condition | Consequence for the transition design |
| --- | --- | --- |
| 108.5, PDF 6 | Impracticable means the entity cannot apply a requirement after every reasonable effort. Prior-period effects may be indeterminable, require assumptions about past management intent, or require significant estimates whose contemporaneous evidence cannot be objectively separated from later information. | A missing local document or high inconvenience is not by itself a concluded impracticability judgment. Keep efforts, missing information and the applicable criterion. |
| 108.7 and 19(a), PDF 6, 8 | A specifically applicable standard determines policy; initial application follows its specific transitional provisions. | General 108 guidance does not erase AASB 17's C5A exception or its express modified/fair-value information rules. |
| 108.22–28, PDF 8–9 | Retrospective equity/comparative adjustment and its limitations distinguish period-specific and cumulative effects; disclosure includes the condition and how/from when policy was applied. | Record affected periods and components; do not apply generic prospective relief instead of insurance-specific transition. |
| 108.32–38, 48, PDF 10–12 | New information can change an estimate without being an error; changes in measurement basis are policy changes. | A later claim outcome does not automatically prove the previous estimate was erroneous. |
| 108.50–53, PDF 12–13 | Earlier estimates must reflect earlier circumstances; distinguish evidence that would have been available at prior authorisation from other information. Hindsight is excluded. Estimates developed later are not automatically forbidden, and significant estimation alone does not prevent reliable adjustment. | Preserve what each assumption describes and why its evidence belongs to that date. The authorisation test is an accounting test, distinct from public availability to investors. |
| 13.2–3, 9, 15–24, PDF 6–8 | Fair value is a market-based exit price in an orderly transaction at the measurement date, with an accessible principal market or, absent one, most advantageous market. | Identify the measured group, market and market-participant assumptions; management's intention to fulfil does not define fair value. No actual sale is necessary, but market access/measurement assumptions still matter. |
| 13.13–14, 25–26, PDF 7–8 | Unit of account comes from the requiring standard; transaction costs do not adjust the price, with separate transport treatment where relevant. | C20 concerns the insurance group; a portfolio investment value or transaction's total consideration is not automatically that value. |
| 13.34–41, PDF 9–10 | Liability transfer leaves the obligation outstanding with a transferee. Quoted/observable information and asset-holder versus obligor techniques have different branches. | Liability valuation is not settlement with the policyholder. Do not treat every insurance liability as satisfying the branch for liabilities not held by anyone as assets. |
| 13.42–44, PDF 11; 17.31, PDF 10 | Fair value reflects non-performance risk, including own credit, assumed unchanged through the hypothetical transfer. Issued-insurance FCF excludes the issuer's own non-performance risk. | The two C20 inputs have different risk treatment. One cannot silently be substituted for the other even if some cash-flow data overlap. |
| 13.45–47, PDF 11; 17.C20 | Transfer restrictions do not justify a separate adjustment. The ordinary demand-feature floor is in paragraph 47; insurance transition expressly excludes it. | Preserve the exact C20 exception; do not use it to suppress all other valuation conditions. |
| 13.48–56, PDF 11–12 | The net-exposure exception has management, reporting and recurring-measurement conditions; 52 limits it to specified AASB 9/139 contracts. | No blanket permission to net insurance obligations against investment assets. Broader portfolio eligibility remains outside this inquiry. |
| 13.57–66, B4–B12, PDF 12–13, 23–24 | Entry price may differ from exit price; technique choice needs suitable available data, calibration and consistency, with justified changes. | A convenient technique or last transaction price is a hypothesis requiring suitability evidence, not an automatic valuation default. |
| 13.67–90, PDF 14–16 | Use relevant observable inputs as far as possible; hierarchy ranks inputs, not models. Significant unobservable inputs affect the level. Own data can be a starting point but must be adjusted when reasonably available evidence indicates different participant assumptions or entity-only features. | Missing quotes permit supported estimates, not arbitrary marks. No actual insurance group is assigned a level here. |
| 13.B13–B17, PDF 24–25 | Cash flows/rates must reflect consistent risks, inflation, tax and currency; risk compensation cannot be omitted merely because difficult. | Preserve the treatment of each risk once, along with cash-flow definition and discount convention. |
| 13.B18–B30, PDF 25–27 | Conditional contractual-cash-flow discounting differs from expected-cash-flow methods; consistent cash-flow or rate risk adjustments can give equivalent values under the stated premises. | The source's illustrative asset probabilities/rates are not transferred to insurance liabilities or adopted as defaults. Its rounded example is read as source exposition, not a new numerical experiment. |
| 13.B31–B33, PDF 27–28 | For the specified liability branch, participant fulfilment costs and compensation for activity/risk enter; risk may increase outflows or reduce discount rates, without double counting. | The sign of a liability risk adjustment must not be copied mechanically from an asset example. Applicability of this branch and calibration are still required. |
| 13.B34–B47, PDF 28–31 | Markets and input examples, significant activity declines, orderly-transaction assessment and third-party quotes have distinct evidence tests. Low activity alone does not show all transactions are disorderly. | Preserve quotation date, whether binding, comparability and orderly-market evidence; a quote is not self-validating. |

Local design inference: the transition calculation needs two source-bound
measurements, not merely a single imported balance and subtraction. Store the
valuation unit and date, accessible market, participant assumptions, relevant
observable data, justified unobservable adjustments, non-performance risk,
technique/calibration and separate FCF inputs. Preserve the reconstruction's
historical information tests independently of the report's public-availability
clock. These are implementable data obligations derived from the inspected
provisions, not a claim that an actual valuation has been completed.

The competing simplifications fail for different reasons. Requiring an
existing historical estimate file in every case is too strong: 108.51 permits
estimates developed later under its information test. Treating any estimate
made today as admissible is too weak: 108.52–53 constrain the evidence.
Requiring quoted prices in every case is too strong: 13.87–89 permits supported
unobservable inputs. Treating a company's own forecast as fair value without
participant adjustment is wrong relative to 13.2–3 and 89. These findings
resolve selected source questions; group facts, full applicability, actuarial
calibration, later amendments, ASBE authority and independent acceptance remain.
