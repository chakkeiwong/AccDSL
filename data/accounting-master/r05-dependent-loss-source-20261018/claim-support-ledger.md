# Claims, targets and support classes

The six-ledger source investigation supports the bounded claims below.
`source-reading.md` records actual reading and `derivation.md` shows local algebra.

| ID / support class | Claimed target and quantity actually checked | Equality/relation and exact support | What remains unproved or unevaluated |
|---|---|---|---|
| C01 PRIMARY_TECHNICAL_SUPPORT | F26's scalar paired loss definition and equal-mean hypothesis | Direct description of F26 section 2, eqs 1–4; candidate-minus-comparator sign is a project naming of forecast 1/2 | Panel sampling law, stationarity/moments/CLT conditions and suitability of a selected score |
| C02 PRIMARY_TECHNICAL_SUPPORT | F26's smoothing/critical-value procedures | Section 3, eqs 5–13 and Tables 1–2 define distinct procedures; normal critical values with a wide bandwidth differ from fixed-b critical values | Original cited proofs and target-specific validity, one-sided margin bounds and choice of tuning |
| C03 PROJECT_DERIVATION | Constant-b interpretation versus displayed practical M=ceil(1.3 sqrt(P)) | M/P tends to zero; follows by division of F26 eq 9 by P | This does not disprove usefulness or establish any finite-sample calibration |
| C04 PRIMARY_TECHNICAL_SUPPORT | Horizon is not a guaranteed loss-dependence cutoff | F26 section 8.1 UCR rolling-estimation construction distinguishes R−1 from h−1 | Actual project covariance, data-generating process and exact original McCracken derivation |
| C05 IMPLEMENTATION_EVIDENCE | Missing/nonfinite handling in retrieved FC1 Plot_Tradeoff | R/Plot_Tradeoff.R 69–137, especially default option, match.arg and nonfinite replacement; code differs from simply preserving unknown losses | Runtime behavior of all branches, and any justified project missingness mechanism |
| C06 IMPLEMENTATION_EVIDENCE | PlotTradeoff's fitted sensitivity simulations | R/Plot_Tradeoff.R 201–241 and 278–360; auto.arima/Gaussian simulation, empirical null quantiles | Independent validation, uncertainty-supported rankings, exact equality to paper revision |
| C07 PRIMARY_TECHNICAL_SUPPORT | What F26 reports about finite simulation behavior | Section 8, Appendix B; Table 15 0.077 and Table 33 0.064 at specified diagonal coordinates | No local reproduction, interval comparison, project superiority or finite-panel coverage |
| C08 PROJECT_DERIVATION | Variance of a fixed weighted paired-loss mean | Exact double covariance sum in derivation.md; coefficient proof and independent finite enumeration | Unknown actual covariance, sampling population, missingness and uncertainty estimator |
| C09 PROJECT_DERIVATION | E3 margin improvement versus equality rejection | E3 protocol's favorable sign requires justified upper bound below -m; two-sided equality rejection is different | Margin, level, valid interval, multiplicity and critical-stratum criteria remain unset |
| C10 SOURCE_GAP_BLOCKER | Original DM95/HLN97/D15 theorem or detailed argument | No matching full text inspected; metadata only | Original assumptions/proofs and interpretation; no indirect promotion via F26 |
| C11 SOURCE_GAP_BLOCKER | Exact selected-byte availability and empirical admission | Prior vintage unit preserves 192 null availability values; this inquiry adds no byte-vintage facts | Reconstruct admissible origin/target availability before empirical comparison |

The source's two-sided scalar statistic and the desired E3 panel margin bound
are **different quantities**. There is no checked equality between them.
Calling the package a practical approximation cannot repair that mismatch.
Its methods remain candidate tools for a separately specified design.
