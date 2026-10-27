"""Current dispositions; original dependency records are retained separately."""
def row(capability, missing, action, evidence):
    return dict(current_capability=capability, remaining_issuer_dependency=missing,
                next_discriminating_action=action, evidence=evidence,
                original_target_ready=False, actual_issuer_admission=False)

DECISIONS = {
 'identity': row(
  'The retained source network binds exact issuer contexts and full source records; conditional opening and continuation now have separate contracts.',
  'Neither original finite target acquires a new source profile. A consolidated source context is not an identified legal book.',
  'Keep original targets blocked. Name the chosen later source/history/opening interfaces and require an explicit entity/book mapping before joining them.',
  ['retained-network-history-20261025/result.md','history-to-opening-20261025/result.md']),
 'context': row(
  'All 256 statement observations retain measurement time, unit and source basis. Network/history partitioning rejects implicit cross-context conversion.',
  'Legal books, control dates, eliminations and source-to-account classification are not supplied by compatible reported contexts.',
  'For every proposed cross-context join, retain both original contexts and provide its conversion/equivalence premise; otherwise leave separate families.',
  ['statement-context-coverage-20261024/result.md','retained-network-history-20261025/result.md']),
 'period': row(
  'Measurement instants/intervals and a synthetic fiscal timeline with deferred assessment and terminal carry exist. The old calendar-only target is unchanged.',
  'Mapping issuer accrual calendars, dated events and measurement conventions into those interfaces remains unestablished.',
  'Reuse explicit fiscal boundaries; require method-specific day counts, service dates and next-period continuity instead of relabeling calendar fixtures.',
  ['statement-context-coverage-20261024/result.md','fiscal-timeline-20261025/result.md']),
 'information': row(
  'Named-source readings remain usable without claiming a historical information set.',
  'Exact-byte publication, ingestion and review clocks remain unknown in the selected original packet.',
  'Bind newly located version-specific clock evidence if available; preserve named-source mode and unresolved historical as-of admission otherwise.',
  ['real-company-input-readiness-20261024/result.md']),
 'opening': row(
  'A checked complete conditional history can map into a next-day synthetic opening with all accounts and numeric memory; target obligations remain visible.',
  'No complete feasible issuer history, exact trial balance or admitted operational population has been established.',
  'Retain the source-network conjunction and each target obligation; do not pass a partial issuer family to continuation by dropping missing fields.',
  ['history-to-opening-20261025/result.md','conditional-continuation-20261025/result.md','retained-network-history-20261025/result.md']),
 'cash': row(
  'Dated overlap regions can augment the unchanged source network; distinct opening cash populations remain explicit.',
  'The displayed 772 difference is unallocated; restricted status does not identify a disjoint account, and equal closing totals do not prove equal membership.',
  'Require actual ownership, restriction, currency and population mappings for settlement cash. Do not create an account from the displayed residual.',
  ['cash-population-reconciliation-20261025/source-findings.md','retained-population-overlap-20261025/result.md']),
 'claims': row(
  'CompleteClaimsOpening/1 admits selected carried internal populations under an independently supplied completeness declaration and invariant selection.',
  'Issuer claim IDs, counterparties, maturities, allocations and completeness evidence are missing from the aggregate captions.',
  'Keep externally unknown population separate from supplied internal completeness; test any proposed source-to-claim map against gross totals and dated settlements.',
  ['complete-claims-opening-20261026/result.md','real-company-input-readiness-20261024/result.md']),
 'inventory': row(
  'Selected declared company openings and carried claim programs retain explicit unit-cost, inventory and invariant checks; this is a finite synthetic contract.',
  'Net issuer inventory does not provide lots, units, impairment, costs or return-recovery membership.',
  'Specify source-constrained lot/cohort alternatives and the selected measurement method; reject substituting synthetic P lots or homogeneous cost.',
  ['declared-opening-admission-20261026/result.md','complete-claims-opening-20261026/result.md','real-company-input-readiness-20261024/result.md']),
 'assets': row(
  'Retained source observations and conditional history constraints preserve net PPE and its unknown components.',
  'Gross cohorts, accumulated depreciation, service dates, lives, retirements and impairment state remain missing issuer facts.',
  'Retain separate source constraints and dated cohort requirements; demand complete gross/accumulation and service-period consequences before admitting depreciation.',
  ['statement-context-coverage-20261024/result.md','real-company-input-readiness-20261024/result.md']),
 'debt': row(
  'Source network preserves term-debt captions and the literal annual issuance dash; selected term programs preserve dated contractual history.',
  'The dash has no numeric meaning in this selected source interpretation; complete instrument terms, noncash movements and principal allocation are still missing.',
  'Inspect the exact retained filing occurrence and XBRL counterpart for the issuance dash before altering its interpretation; preserve literal, context and evidence independently.',
  ['retained-population-overlap-20261025/result.md','statement-context-coverage-20261024/result.md','selected-term-program-20261027/result.md']),
 'funding': row(
  'Conditional financial continuation invokes a declared transition only after checking its exact opening; it does not manufacture finance.',
  'Actual availability, eligibility, reserved capacity, rates, fees and financing choices are not identified by balances.',
  'Require named dated facility terms and an explicit supplied policy before any funding scenario; keep source uncertainty distinct from a hypothetical financing choice.',
  ['conditional-continuation-20261025/result.md','real-company-input-readiness-20261024/result.md']),
 'tax': row(
  'The fiscal timeline preserves supplied deferred measurement, distinct unknown/absent/false findings, stale-state refusal and carry.',
  'Actual jurisdictions, bases, reversals, recognition findings and settlements remain absent; synthetic recovery capacity is not issuer evidence.',
  'Bind dated jurisdiction-specific measurement and recognition findings; use native unresolved/invalid/unsupported statuses rather than supplying immediate deduction.',
  ['fiscal-timeline-20261025/result.md','real-company-input-readiness-20261024/result.md']),
 'behavior': row(
  'Source-constrained hypothetical histories and explicit conditional continuations remain separate from source observations.',
  'Actual events and future contract/behavior choices are not determined by aggregate revenue or cash flows.',
  'Declare each hypothetical mechanism and its source information separately, retain all selected source constraints, and compare full consequences without calling it recovered history.',
  ['retained-source-history-20261025/result.md','conditional-continuation-20261025/result.md']),
 'returns': row(
  'The original requirement identifies a source-specific synthetic return module; this audit does not establish a new issuer return mapping.',
  'Return rights, component allocations, expected refunds, recovery costs and recovered-lot history remain missing.',
  'Reconcile disclosed rights and component populations before choosing a return rule; retain explicit absent data instead of borrowing P components.',
  ['real-company-input-readiness-20261024/result.md']),
 'report_carry': row(
  'Full displayed source contexts and separate conditional reports/fiscal carry exist; complete source reports survive selected network reasoning.',
  'Issuer report mappings, OCI, leases, group state, noncash origins and complete carry memory are not established by those interfaces.',
  'Join only declared compatible book/report/carry contracts; preserve every source disposition and refuse whole-company completeness while a required population or mapping is missing.',
  ['statement-context-coverage-20261024/result.md','conditional-continuation-20261025/result.md','fiscal-timeline-20261025/result.md'])
}
