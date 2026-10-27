# Attach temporal observations to typed economic histories

24 October 2026. S2–S4; MC04/05/08/09/10/11/13/16/24/26/28/35.

Question: can complete temporal measurement families constrain both monetary
accounts and typed economic quantities while retaining every intermediate
history condition? Comparator: the unchanged TypedAffineHistory/1 exact replay
and TemporalMeasurementConstraints/1 witness checker on the same assignment.
The existing HistoryMeasurementAttachment/1 accepts only a monetary value type
and scalar coefficients; it cannot attach unit quantities. Passing only the
typed history's scalar lowering would also drop its additional state constraints.

Skeptical audit passes for a separate typed successor, not modification of the
frozen monetary profile. Reuse the complete typed parent's build_problem, then
rename and retain all parent constraints. Use scalar lowering only to construct
mapping expressions after exact dimensional checks. This avoids pretending
that units are money or that a balanced closing stock proves an admissible path.
The full temporal parent retains all observations, relations and intervals.

Define TypedHistoryMeasurementAttachment/1 with complete history, measurements,
bindings and obligations. Each binding keeps its quantity name, snapshot/movement
kind and proposed premise. Each term has kind, field and a fixed coefficient
record with value and type. Coefficient type times field type must equal the
observation value type, including context and scale; no implicit conversion.
Snapshot dates and half-open period endpoints follow the existing attachment.
Movement sums event changes only, never opening balances. Preserve event order
and every opening/post-event condition. Parent and mapping premises must agree.
Unmapped observations remain target obligations, not dropped equations.

Evidence contract: pass requires both original parent checks, exact Fraction
replay of all mappings, units and money in one shared family, and rejection of
an intermediate stock shortage despite a compatible closing report. Also test
separately feasible but incompatible parents; preserving alternate assignments
instead of substituting one parent witness; wrong coefficient dimensions,
context, scale and time; missing premises; incomplete mapping; strict bounds;
zero budgets; forged witnesses/results and unmeasured economic state.

Hard veto: missing original constraint, mismatched units, original-parent replay
failure or fabricated admission. Repair before recording. Counts and smoke
results are engineering checks, not full simulator promotion. Source/legal
state, wider methods and real-company reconciliation remain open; their absence
does not block this explicitly conditional test. No stochastic ranking.

Default audit: fixed typed coefficients and existing date conventions are an
explicit restricted profile, not universal accounting defaults. Keep combined
variables <=256 and mapping terms <=4096 plus existing input/formula/solver
limits; these are bounded-reference engineering choices. Reject unsupported
types rather than guessing scale. CPU only; no new solver or production default.

Record scripts/typed_history_measurement_attachment_v1.py, focused tests and
data/accounting-master/typed-history-attachment-20261024/ with exact definitions,
dependency lock, commands, results and remaining work. After checked evidence,
refresh controls and review method/history state composition as the next distinct
dependency; do not create another authoring wrapper by default. Integrate the
accumulated substantive design after that review.
