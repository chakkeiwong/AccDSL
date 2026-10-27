# Simulation failure cases

Each entry links a failure mechanism to a discriminating case and a proposed repair. Chapters refer to the new simulation part in both editions. These are documented cases, not a claim that the engine implements every fixture.

| ID | Chapters | Failure | Discriminating case | Proposed repair |
|---|---|---|---|---|
| SIM-F001 | 2, 12 | Wrong row, sign, scale, period or currency | Use repeated labels with different units and dates | Preserve context and report ambiguous extraction |
| SIM-F002 | 2, 12, 22 | Omitted note or incorporated document | Place decisive covenant in a referenced scanned note | Track retrieved, parsed and modeled coverage separately |
| SIM-F003 | 3, 22, 24 | Revision used as original knowledge | Publish corrected terms after the forecast cutoff | Version evidence and prohibit later knowledge in earlier decisions |
| SIM-F004 | 2, 22 | Missing value silently treated as zero | Omit an outstanding guarantee disclosure field | Retain unknown value and structural omission |
| SIM-F005 | 1, 2, 13 | One feasible journal treated as identified | Same debt and interest from fixed and floating contracts | Retain the joint admissible history family |
| SIM-F006 | 2, 15 | Net movement mistaken for gross transactions | Issue thirty shares and repurchase ten versus issue twenty | Preserve gross-event alternatives and constrain with notes |
| SIM-F007 | 1, 8, 17 | Marginal ranges combined independently | Interest 7 combined with cash 90 although total is 95 | Store shared variables and joint relations |
| SIM-F008 | 1, 19 | Duplicate encodings alter weights | Duplicate one contract syntax without new evidence | Define economic identity and explicit probability measures |
| SIM-F009 | 2, 12, 20 | Solver timeout declared infeasible | Use a feasible family beyond the search budget | Return unresolved feasibility with witnesses and bounds |
| SIM-F010 | 1, 22 | Correct reports hide an omitted contract class | Add a guarantee that has never paid | Retain completeness scope and structural model alternatives |
| SIM-F011 | 3, 8, 10 | Persistent type redrawn each period | Fixed versus floating loan over two years | Carry latent type until an explicit modification event |
| SIM-F012 | 3, 4, 16 | Policy sees a future sampled shock | Change future demand while holding current information fixed | Enforce actor-specific information and nonanticipativity |
| SIM-F013 | 3, 14, 16 | Manager and analyst knowledge conflated | Manager knows loan terms absent from public reports | Separate actor information views |
| SIM-F014 | 3, 16 | Uninformative observations remove ambiguity | Repeat identical interest reports without a rate reset | Preserve unresolved types and prior dependence |
| SIM-F015 | 3, 16, 22 | Signals counted twice or assumed independent | Reuse the same disclosure through two data providers | Model signal identity and dependence |
| SIM-F016 | 3, 22 | Zero-likelihood update silently selects a type | Evidence contradicts every retained history | Return a conflict and investigate source/model scope |
| SIM-F017 | 4, 19 | Conditioning described as intervention | High-rate sample also changes demand composition | Specify structural intervention or conditional stress semantics |
| SIM-F018 | 4, 5, 12 | Shock applied twice or with wrong reset timing | Apply a two-point shock to fixed coupon and reset spread | Use contract dates, shock identity and zero-shock checks |
| SIM-F019 | 4, 18 | Policy effect confounded with different histories | Compare policy A on H1 with B on H2 | Evaluate paired policies on the same worlds |
| SIM-F020 | 4, 10 | Joint stress loses economic dependence | Combine inconsistent exchange-rate and demand assumptions | Admit an explicit joint scenario family or law |
| SIM-F021 | 5, 26 | Face treated as cash proceeds | F100, default .1, recovery40 and risk-free .05 | Separate face, proceeds and recovery; check creditor break-even |
| SIM-F022 | 5, 14 | Net proceeds ignore fees or caps | Bridge principal cap30 with fee1 cannot fund need30 | Check dated offers and gross-to-net cash |
| SIM-F023 | 5, 14, 26 | Funding plug invents market access | Set closing cash to zero by unlimited borrowing | Require an admitted offer or solved pricing/eligibility model |
| SIM-F024 | 5, 14 | Funding arrives after maturity | Term issue settles day5 but maturity is day4 | Schedule funding and payment in dependency order |
| SIM-F025 | 5, 11, 26 | Pricing anticipates a different policy | Price safe project then allow risky asset substitution | Solve pricing with the admitted commitment and actor policy |
| SIM-F026 | 5, 25 | Book debt used as promised repayment | Face110 and carrying amount100 | Require explicit contract-to-accounting mapping |
| SIM-F027 | 5, 14, 21 | Recovery exceeds available collateral | Claims40 and30 each take collateral50 | Apply one asset ownership and priority waterfall |
| SIM-F028 | 5, 11, 12 | Numerical nonconvergence called economic default | Pricing algorithm fails although an external offer exists | Separate solver status, offer feasibility and default events |
| SIM-F029 | 26 | No funding root replaced by a large face | Need110 when maximum expected payoff is100 | Return infeasible within admitted channel; retain other channels |
| SIM-F030 | 6, 15 | Percentage dilution equated with value loss | Fair issue at10 versus discounted issue at8 | Keep ownership and economic valuation separately |
| SIM-F031 | 6, 15 | Wrong conversion denominator | Sixteen new shares on one hundred old shares | Use post-conversion count116 and extinguish converted debt |
| SIM-F032 | 6, 15 | Preference and conversion paid simultaneously | Low-value and high-value nonparticipating preference cases | Encode mutually exclusive rights and conserve exit value |
| SIM-F033 | 6, 15 | Authorization or settlement ignored | Fifteen-share cap and failed subscription | Check approvals, offers and settled cash before posting |
| SIM-F034 | 6, 15 | Book value dictates an unsupported issue price | Economic asset value differs from carrying amount | Declare valuation premise and model market offer separately |
| SIM-F035 | 7, 12 | Balanced journal misstates economics | Borrowing credited to revenue | Use event-specific recognition and counterpart checks |
| SIM-F036 | 7, 23 | Accrual paid and expensed a second time | Coupon5 unpaid in year1, paid in year2 | Carry payable and settle without duplicate expense |
| SIM-F037 | 7, 23 | Measurement change treated as cash | Deferred tax asset falls10 to4 | Separate measurement state from legal tax rights and cash |
| SIM-F038 | 7, 19 | Wrong standard, perimeter or cash-flow category | Import economic OCF including principal as reported OCF | Preserve authority scope and concept definitions |
| SIM-F039 | 21 | Consolidated cash treated as freely transferable | Parent cash5 maturity20; subsidiary30 but transfer cap10 | Maintain entity-specific constraints and transfers |
| SIM-F040 | 21 | Currency cash netted across entities or settlement times | Foreign receipt arrives after foreign debt payment | Retain currency, location and exact settlement ordering |
| SIM-F041 | 21, 25 | Guarantee or collateral feedback omitted | Collateral deficiency6, subsidiary cash4, parent support2 | Propagate shared exposure and cash consequences |
| SIM-F042 | 23 | Tax loss balance forgotten or double-counted | Loss40 then taxable income30,30 or negative10 | Carry legal losses with sign-correct recurrence and vintages |
| SIM-F043 | 23 | Equal carrying amounts imply equal depreciation | Machine20 with remaining charges10 versus20 | Preserve relevant asset vintage and useful life |
| SIM-F044 | 14, 23 | Cure clock or payment priority dropped | Fee2 interest5 payment6; receipt before/after cure deadline | Retain contractual allocation and dated deadlines |
| SIM-F045 | 23 | Quiet option deleted | Identical past coupons but different early-call rights | Preserve unexercised rights when future scenarios can activate them |
| SIM-F046 | 8, 16 | Equal means used as exact state equivalence | Same immediate output but different later signal quality | Preserve feasible actions and joint observation/output transition law |
| SIM-F047 | 8, 17 | Projection drops implied constraints | x=z+1 with z in[0,2] | Eliminate variables while retaining x in[1,3] |
| SIM-F048 | 10 | Stagewise worst case switches fixed type | Paths(0,10),(10,0) become(10,10) | Retain persistent dependence or label rectangular enlargement |
| SIM-F049 | 8, 20, 25 | Cache reused outside its query scope | Extend horizon past a maturity or add a covenant | Invalidate on evidence, policy, horizon and relevant state changes |
| SIM-F050 | 8, 17 | Interval dependency gives a false range | x-x or cash plus linked interest | Use relational propagation or validated outer bounds |
| SIM-F051 | 9, 17, 18 | Sample minimum reported as exact worst case | Largest sampled alpha .9 misses true endpoint1 | Label inner witnesses and bound unsampled regions |
| SIM-F052 | 9 | Particle resampling destroys persistent types | Rare static contract type is removed without evidence | Retain feasible family and monitor diversity beyond ESS |
| SIM-F053 | 9, 18 | Importance proposal weights omitted | Target tail .001 sampled at .1 | Use correct likelihood ratio and support checks |
| SIM-F054 | 9, 18 | Rare event absent in a short sample | Loss1000 with probability.001 and100 draws | Report uncertainty and use justified rare-event methods |
| SIM-F055 | 9, 17, 26 | Small smooth error misclassifies a guard | Capacity estimate straddles required funding | Refine threshold band or return unresolved classification |
| SIM-F056 | 11, 18 | Squared sampled residual changes the objective | r=theta-1+theta epsilon | Use the intended conditional residual and independent-draw construction |
| SIM-F057 | 11 | Interior derivative enforced at a boundary | Minimize(a+1)^2 subject to a>=0 | Use valid constrained conditions and active-set checks |
| SIM-F058 | 11, 25 | Partial derivative claimed as total equilibrium derivative | Price depends on action through policy | State detached dependencies and validate full target |
| SIM-F059 | 11, 18, 26 | Smoothing or neural extrapolation invents funding | Positive learned slope beyond true capacity100 | Evaluate original payoff, boundary and downstream feasibility |
| SIM-F060 | 11, 18 | One local root declared unique/global | Different basins or equilibrium branches | Search, bound or report local status and selection premises |
| SIM-F061 | 11, 12 | Unit scaling changes the economic decision | Dollars transformed consistently to millions | Audit residual normalization and unit-invariance |
| SIM-F062 | 12, 23 | Distress pushed beyond terminal date | Borrow20 at year-end and repay22 next month | Retain obligations, extend horizon or justify continuation value |
| SIM-F063 | 12, 24 | In-sample reconciliation called forecast validation | Evaluate on statements already imposed as constraints | Use information cutoffs and separate future outcomes |
| SIM-F064 | 18, 24 | Mean forecast hides wrong tail probability | Two-point approximation matches mean89 but breach.5 not.7 | Evaluate the queried distribution and threshold events |
| SIM-F065 | 12, 24 | Failed paths dropped and remaining mass normalized | Solver failures occur mainly under distress | Retain unresolved mass and branch outcomes |
| SIM-F066 | 20, 25 | Modules agree on amounts but not IDs, dates or units | Refinancing updates cash but leaves old tax/ownership cache | Test complete event sequences and dependency invalidation |
| SIM-F067 | 22, 24 | Model family excludes the real mechanism | Guarantee, private covenant or new behavior absent from family | Preserve structural limits, expand models and stress assumptions |
