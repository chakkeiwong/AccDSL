# Constrain selected cash histories with retained balance-sheet evidence

25 October 2026. MC01,MC06,MC09,MC10,MC24,MC28. S2-S4.
Baseline: RetainedSourceHistoryAttachment/1 and RetainedJointSourceRelations/1,
accepted retained-source-history-20261025 exchanges; governing Version4.33.
Question: can the same supplied history satisfy selected cash movements and
selected reported closing balance relations together, with explicit mappings?

Skeptical audit: a cash-only history may conflict with disclosed liabilities
or equity. Retaining those rows without constraining the history cannot prove
joint compatibility. The new evidence must expose that conflict, not merely
duplicate source wrappers. Use the existing balance relation definitions and
their exact source coefficients, not invented accounting equations. Do not
silently equate similarly labelled populations or bridge different report bases.

Evidence contract: preserve the full256-observation/143-relation report;
retain separate annual/interim contexts, all optional rounding/identity
hypotheses and complete supplied histories. Derive time-typed snapshots from
the retained instant contexts, documenting the removal of time/unit metadata
from value context exactly as the temporal source adapter does. Merge only
explicitly selected same-context constraints and exact mappings. Compare
snapshot-only arithmetic with RetainedJointSourceRelations/1 and cash-only
behavior with RetainedSourceHistoryAttachment/1. Full parent constraints must
be retained, including source equations whose quantities are unmapped.

Primary criterion: known cash-compatible hypothetical histories become
conditionally infeasible when an explicit conflicting reported balance
constraint is attached; independently authored compatible cases retain all
constraints and valid alternative witnesses. No absent source row becomes zero,
no incompatible context is relabelled and no feasibility yields actual admission.
Veto: changed source hashes, dropped constraints, silent mapping, wrong units
or forged replay. Candidate infeasibility triggers analysis, not direction
rejection. Budget exhaustion remains unknown. Witness/timing choices are
explanatory only; no performance ranking.

Assumption audit: selected source identities and rounding retain their proposed
status; field mappings and signed account interpretation are caller premises.
Authored histories remain counterexamples or conditional candidates, not
recovered facts. Source values are read from retained records, never retyped
as unexplained constants. No equity/liability account or balancing residual is
invented to force a fit. A constructed compatible case must document every
supplied account/opening/event and still keep full-company obligations open.

1. Inspect the exact selected balance relations and context/time conversion.
2. Define a bounded optional composition using existing exact solvers; require
   explicit source-to-field mappings and preserve unmapped obligations.
3. Run focused same-context, missing-premise, source-tamper, no-budget,
   cash-only-preservation, conflicting and compatible full-parent checks.
4. Record exact inputs, environment, commands, complete exchanges and replay;
   refresh controls and prepare separate manuscript integration on success.

Artifacts: data/accounting-master/retained-statement-history-20261025/.
CPU Python3.11.15/Z3 4.16.0; CUDA_VISIBLE_DEVICES=-1. No GPU/import/install.
S1-S5 partial,S6 held,S7/E3 deferred. No whole requirement closes.
