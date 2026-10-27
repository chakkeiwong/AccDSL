# Preserve temporal meaning in joint measurement constraints

24 October 2026. S2–S4; MC05/08/09/10/13/16/24/26/28.

Question: how can a reusable joint-measurement contract express an opening
balance plus period movements equaling a closing balance while retaining each
operand's original date, measurement kind and source context? The v1 contract
correctly rejects unequal complete types. Removing date or kind fields merely
to reuse it would defeat that check. The retained statement description already
validates ten displayed stock-flow bridges, but does not assert latent identities.

Skeptical audit: inspect the exact temporal relation checks, generic solver,
reconstruction constructor and source terms before implementation. The annual
cash-flow opening is 30737 at 2023-09-30, change -794 over [2023-10-01,2024-09-29),
closing 29943 at 2024-09-28. The interim closing is 30299 at 2024-12-28. These
cash-flow captions must not silently become legal cash or be joined to other
populations. The annual and interim bases differ. Equal dates or equal displayed
values alone do not authorize aliasing two observation identities.

First deliverable: an audit and explicit temporal typing design, including exact
roles, source lineage and the permissible relation between contexts. Then build
the smallest reusable closed contract. Reuse existing exact rational solving;
do not loosen v1's equality rule or substitute its half-even rounding helper.
Keep local same-context relations valid under their old profile. Do not fabricate
admitted histories or feed hypothetical legal-book openings into reconstruction.

Evidence contract: baseline is v1's same-context conjunction and the frozen
displayed bridge checker. Primary pass requires preserved temporal types, explicit
opening/movement/closing roles, exact source coefficients and independent rational
witness verification. Wrong dates, inconsistent periods, swapped roles, changed
entity/perimeter/currency/population/basis, or silent source merging veto a result
and trigger repair. Missing hypotheses remain unresolved; resource exhaustion is
unknown. No source identity or historical accounting judgment follows from a
conditionally feasible bridge. Counts and runtime are explanatory only.

Defaults audit: civil-date snapshots use the existing source convention of the
day before the period start and the day before its exclusive end. It is a scoped
date convention, not a universal intraday model; test wrong endpoints and empty
periods. Treat population compatibility as explicit authored evidence with named
premises, not as a guess from account captions. The finite test budget inherits
the checked reference scale and is not a new default policy. No forecast runs.

Research intent: preserve one quantity per observation across relations and
separate conditional measurement consistency from executable history. A failed
bridge hypothesis rejects that candidate system only. Source corruption or an
invalid solver harness vetoes interpretation until repaired; it does not close
the whole design direction. Record design, source anchors, exact cases, manifests
and next dependencies under data/accounting-master/temporal-measurement-contexts-20261024/.
