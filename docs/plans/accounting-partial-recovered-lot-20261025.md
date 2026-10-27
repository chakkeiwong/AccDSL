# Sell part of a recovered lot under explicit allocation assumptions

25 October2026. S2–S5;MC11/15/16/18/23/24/26/28/35;P17-04.10.

## Question and baseline

Can a sale of part of one recovered lot preserve its remaining quantity,
carrying amount, selected tax base and shared-company statements? The current
shared-book and typed return methods reject fractions other than1 and consume
the entire lot. The lot already stores units,carrying,tax_base,acquired date and
disposed status; quantity need not be invented from carrying value.

Compare a full-quantity sale with the protected whole-lot method. For a proper
partial sale, compare an independently derived exact journal and remaining lot.
Use the retained synthetic shared-book opening and settlement before adding
any new numerical example. The successor must not mutate frozen methods.

## Mechanism and assumptions

Define a separate optional method for homogeneous divisible recovered inventory.
The caller explicitly selects proportional allocation, supplies sold units and
cash proceeds, and provides known affirmative findings for homogeneous units,
divisibility,unchanged measurement basis,performance completion and the retained
equal carrying/tax-base treatment. Missing findings remain unresolved; false
findings are unsupported by this method. No general cost formula or actual-law
compliance is inferred. No business demand,price or sale is generated.

For opening unitsN>0,carryingC>=0,tax baseT=C and sold units0<q<=N, choose
f=q/N. Released carrying=f*C and released selected tax base=f*T. Remaining
units=N-q,carrying=C-f*C,tax base=T-f*T. Disposal is true only when q=N.
The journal debits cashP,credits revenueP,debits cost of salesf*C and credits
inventoryf*C. Derive balance,quantity and cash conservation in design notation.
Account/date/lot/event identities and unrelated state remain protected.

## Skeptical audit and evidence contract

Main failure risks: confusing fraction of original and remaining units; losing
lot memory after the first sale; silently selecting heterogeneous-cost policy;
using final balance equality to conceal different cash dates or histories.
Proportional splitting is an authored hypothesis,not an inferred accounting rule.

Primary pass: complete full-sale journal/cash/state equality with the old method
for matching conditions; exact independent partial arithmetic; invariant and
statement tie-outs; retained event identity and history; full-result apply
verification. Split-sale comparisons may compare aggregate financial effects
under identical dates and additive proceeds only; individual flows/ids remain
separate and are never claimed byte-identical. A zero-cost positive-unit lot
must remain live until its units are exhausted.

Promotion vetoes: wrong quantity/cost/tax allocation,unbalanced journal,changed
unrelated state,unsupported assumptions accepted,wrong period or accepted
proposal tampering. These trigger repair. Only corrupt baselines or missing
necessary facts without an explicit conditional interpretation stop this unit.
Counts and timing are explanatory. No scientific ranking is attempted.

## Execution and artifacts

1. Lock source code,schemas,fixtures and this plan under
   data/accounting-master/partial-recovered-lot-20261025/. Record inspected
   functions and the exact derivation and model boundary before implementation.
2. Add a separate closed optional event and pure proposal/apply interface using
   existing shared-book invariants. Retain whole-lot native behavior unchanged.
3. Check partial/full/repeated sales,zero carrying amount,multiple lot isolation,
   cash/profit/inventory/quantity reconciliation and remaining unsold inventory.
   Check over-sale,zero/negative units,unknown/false/ill-typed findings,unsupported
   method,chronology,duplicate ids,missing/disposed lots and rehashed tampering.
4. Compare affected statements through existing reporting formulas;run directly
   dependent regression tests. Record failures before repair and freeze exact
   evidence only after review. CPU only;CUDA_VISIBLE_DEVICES=-1.
5. Integrate the scoped explanation and refresh full53/6/46 coverage. Then audit
   the shared-book/annual authoring and dispatch boundary for this optional method.

No real-company valuation,inventory standard admission,partial return-right
settlement,general tax method or production readiness follows. S1–S5 partial;
S6 held;S7 deferred. Forecasting remains deferred.
