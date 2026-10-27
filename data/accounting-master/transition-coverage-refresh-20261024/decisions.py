"""Scoped updates; complete original entries remain preserved in the inventory."""
EVIDENCE={
 'readiness':'real-company-input-readiness-20261024',
 'partial':'source-constrained-state-20261024',
 'relations':'source-relations-20261024',
 'contexts':'statement-context-coverage-20261024',
 'requirements':'requirement-version-interoperability-20261024',
 'collections':'state-domain-requirements-20261024',
 'structure':'native-state-structure-20261024',
 'monetary':'typed-monetary-effects-20261024',
 'memory':'typed-memory-effects-20261024',
 'transition':'typed-return-composition-20261024',
 'source':'return-source-binding-20261024',
 'manuscript':'typed-transition-integration-20261024'}
UPDATES={}
def add(ids,evidence,advance,residual,next_action):
    for key in ids.split():
        assert key not in UPDATES,key
        UPDATES[key]={'evidence':evidence.split(),'advance':advance,'residual':residual,
                     'next_action':next_action,'full_requirement_closed':False,'acceptance':'not_promoted'}

add('MC01 MC03 MC07 MC28 G5 G11 G12 I01','readiness partial relations contexts source',
 'Real-source readiness preserves 256 observations and 143 relations, original fiscal dates, units, perimeters, dashes, omissions and independent derived-target distinctions. Exact synthetic return source-prefix binding is a separate route.',
 'Actual legal/economic latent state, source authority, whole-report semantics and general source adapters remain incomplete. No executable real-company opening exists.',
 'Audit joint selected measurement consistency without allocating consolidated values into invented legal or contract state.')
add('MC04 MC08 MC09 MC10 G1 G15 P17-08.01 P17-08.02 P17-08.03 P17-08.06','partial relations contexts requirements',
 'Display-only and explicitly hypothetical rounding/identity premises remain separate. Local residual intervals and contradiction counterexamples are explicit; typed unknown reasons survive method assessment.',
 'Per-relation compatibility is not joint feasibility, admissible history, uniqueness or an admitted measure. Shared unknown identity in requirements is not an entailment solver.',
 'Inspect exact reconstruction support, then define conditional joint measurement constraints with unknown/unsupported/infeasible outcomes separated.')
add('MC05 MC14 G13 G14 P17-08.05','partial contexts transition source',
 'Fiscal intervals and stock/flow dates are source-bound. Selected transition checks period/state/tax-close chronology, raw identities and exact source-prefix order.',
 'Declared context rebinding and synthetic replay do not establish actual historical availability or causal intervention semantics.',
 'Preserve every observation clock and perimeter while auditing joint constraints; do not infer an exact historical information set.')
add('MC13 MC15 MC17 MC23 MC24 MC26 MC27 G2 G4 G10 G17 P17-04.03','requirements collections structure monetary memory transition source',
 'Reusable guarded requirements, collections/totals, complete native state structure, typed rational effects, atomic memory and full selected proposal recomputation now compose. Source binding rejects arbitrary balanced current books.',
 'The selected return adapter reuses native invariants and concrete membership checks. Broader methods, partial returns, general functions, code generation and complete admission remain open.',
 'Retain checked reusable layers while addressing shared measurement constraints; revisit complete module coverage after its mathematical contract.')
add('MC11 G16 P17-08.04','collections memory transition',
 'Typed memory retains disposed lots, lifetime IDs, ordered appends and original-state reads with no partial writes.',
 'General state sufficiency, compression, cross-sector grouping and durable transaction semantics are not established.',
 'Keep sufficient-state obligations explicit; a feasible measurement assignment must not be promoted to contract/cohort state.')
add('P17-04.05 P17-04.10 P17-04.11 I03 I06','monetary memory transition source',
 'Selected recovered inventory and conditional tax-adjustment memory join a shared book; whole-lot sale and two gross settlement flows have exact effects and replay.',
 'General costing, tax law, reporting/carry, sector and group methods retain earlier scoped evidence; this pass does not re-audit or admit them.',
 'Preserve existing rows and distinguish aggregate statement constraints from complete module methods.')
add('MC31 MC32 MC33 MC34 MC35','manuscript transition source',
 'Version 3.62 protects 157 predecessor sources and teaches the complete selected transition with bounded rendered author review; no paid review was used.',
 'Full-document, independent/domain/human acceptance and the full mission remain open.',
 'Continue internal substantive repairs and keep candidate not_ready until the relevant evidence exists.')
