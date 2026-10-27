# Which lease-right allocations do aggregate balances leave possible?

24 October 2026. S2-S4; MC02/08/09/10/11/13/16/17/18/24/26/28/35;
G1/G3/G4/G15/G16 and P17-04.09. No product promotion or forecast run.

## Skeptical audit and intent

The checked shared-book lease reference requires known per-right amounts. The
mission requires preserving different histories compatible with reported totals.
Question: with supplied aggregate opening ROU120 and liability150, known liability
allocation A100/B50, and exactly two identified rights, what follows if B's ROU
is unknown? Test the whole conditional allocation family rather than select the
old authored B30 or the pooled B40 as if a reported total identified it.

Original comparators are unchanged CorporateResiduals/1 financial_checks.py and
authored_cases.py, plus the checked SharedLeaseBook/1 reference. Inspect the
original method's negative-remaining-ROU and depreciation refusals. The existing
typed affine history can express linear constraints but does not establish
native method admissibility by itself. The exact rational solver is reusable
for affine feasibility, not a source of accounting authority.

Primary pass criterion: derive all conditional effects and supported parameter
regions, prove finite bounds exactly under explicit assumptions, and replay
representative endpoints/interior/refused cases through the original methods.
Distinguish impossible declared inputs, outside-method-support cases and a failed
supplied event. A refusal cannot establish that the underlying real history is
impossible. Balanced books and isolated solver witnesses are explanatory only.
Wrong original replay or lost shared dependence vetoes the proposed family and
triggers repair. Corrupted originals or unavailable required comparators veto
continuation. Expected support/refusal cases motivate the next design.

## Assumptions and derivation to test

Let x be B's opening ROU. A's is120-x. Both are nonnegative, so 0<=x<=120.
These are supplied exact synthetic aggregates; there is no imported disclosure,
rounding convention or evidence that exactly two rights exist in an actual firm.
Liabilities100/50, rates10%, owner/book/source context and calendar remain fixed.
Cash200 is a company-opening premise. Equal weighting of allocations is forbidden.

Reuse the original four events. Terminating B removes x and50; A's first payment
schedule121 gives liability110 and ROU130-x; gain50-x. The second traced removal
10/11 and replacement payment99 gives liability90 and ROU111-x, gain1. Original
method support therefore needs x<=111. Payment99 creates expense9 and cash101.
The original supplied depreciation81 needs x<=30. For that complete supported
sequence, final ROU=30-x and cumulative profit=-39-x. Derive and check rather
than assume these formulae. The possible pairs retain profit-ROU=-69; separate
marginal ranges cannot be combined arbitrarily.

| Material choice | Provenance and status | Failure mode | Earliest check |
| --- | --- | --- | --- |
| Exact total120 and liabilities100/50 | Original authored fixture, conditional baseline | Treat aggregate as identifying right amounts | Compare x20 andx30 with identical opening totals |
| Exactly two complete rights | Explicit hypothetical membership premise | Hide unobserved contracts | Keep unknown membership unresolved; no real-source admission |
| x in[0,120] | Nonnegative asset allocation, derived | Add unjustified positivity or proportionality | Test both endpoints and pooled40 |
| Fixed schedules, rate and depreciation | Original events, not estimated behavior | Filter candidates under unstated changed events | Preserve input81 and report exact failed event |
| No-overdraft cash200 | Existing explicit company premise | Introduce funding or duplicated capital | Compare cash and original journals across replays |
| Rational affine solver | Existing restricted reference | Drop nonlinear rate effects or imply valuation support | Check every formula affine; rates are fixed |

## Commands and artifacts

Create data/accounting-master/lease-allocation-family-audit-20261024/ with the
derivation, source lock, bounded audit script, saved exact results and manifest.
Use Python CPU only (CUDA_VISIBLE_DEVICES=-1), Fraction arithmetic and the
existing bounded solver. No scientific stochastic ranking or new empirical
calibration is involved. Inspect every resulting refusal and all recorded JSON.
Run --check before the one-time --record; saved --replay precedes control refresh.

Before interpreting results, verify original outputs for x0/20/30/40/100/111/112/120,
exact bound proofs for complete support, non-combinable marginal endpoints, and
conditioning by a supplied final ROU observation. A hypothetical observation
ROU10 should select x20 within the declared family; label its provenance.

No claim of discovering actual rights, standard compliance, general lease
valuation, arbitrary histories or a probability distribution follows. Record a
decision table and the next smallest justified family-design repair. Keep broader
module, source, sector and independent-review obligations; S6 held,S7 deferred.
