# Proposed metric-input adapter profile

This optional profile governs a future diagnostic adapter, not the accounting
evidence store or a selected production default. It accepts a metric request,
immutable true/predicted evidence references, explicit table extents, cells,
coordinate frame when location is requested, text policy, implementation/build
identities and reviewed resource limits. A failure preserves the evidence and
returns a named outcome; it must not manufacture a zero metric or drop a sample.

Each request identifies the metric variant, raw-cell versus normalized table
assignment objective, macro/micro aggregation, empty-input convention and the
scope of every upper bound. A build identity must bind the wrapper, pylcs,
pybind11 and native dependencies before an installed result is admissible.
This document does not choose a build or claim binary correspondence.

For content scoring, distinguish absent text, explicit empty text and supplied
text. Only built-in strings containing Unicode scalar values enter the strict
codepoint profile. A bytes value must be decoded by a separately declared
encoding step with provenance; a surrogate must remain an unresolved input.
Preserve original strings and all transformations. No canonical normalization,
whitespace rewrite or grapheme target is selected implicitly. Embedded NUL is
preserved unless a separately justified data policy explicitly changes it.
Validate before the equality shortcut, so invalid equal inputs cannot receive
an accepted score by avoiding conversion.

For topology, declare row/column extents independently of the observed cells.
Each span supplies nonempty, distinct, consecutive nonnegative exact integer
indices inside the extents. Boolean indices are not integer indices in this
profile. Reordering can be an explicit lossless canonicalization with a retained
map; no reordering or contiguity repair occurs silently. Occupied slots may not
overlap. Mark holes as unknown, explicit blanks or excluded-with-reason under
the declared scoring population. Unknown holes make the relevant score
unavailable; they do not become blank content or a unit topology box by default.
Direct grids must be rectangular and match declared extents. Empty grids need
a stated convention and remain distinct from an absent or failed parse.

For location, require four finite numeric coordinates, ordered axes, a common
declared frame, units, page identity and any transformation needed between the
two inputs. Missing boxes make location unavailable while preserving any valid
content/topology request. Evaluate width, height, area, intersection and union
under a specified numeric representation. Finite endpoints alone are
insufficient: reject nonfinite derived values, positive-width/height area
underflow to zero, impossible negative areas and zero/nonfinite positive-area
union. A repair may use reviewed common-frame rescaling or exact arithmetic;
it must retain the original coordinates and demonstrate metric equivalence.
Zero-area boxes need an explicit policy: the retained helper assigns zero
overlap reward even to identical degenerate boxes. This is a convention, not
evidence that the boxes identify different locations.

Before allocation, check declared row/column counts, occupied-slot counts,
pairwise reward counts and string lengths against supplied budgets. Bound the
product of the two grid cell counts and the per-pair string DP footprint.
HTML span caps alone do not bound complete-grid allocation. Budget values
remain unselected until the workload and evidence contract are reviewed; no
convenient constants are promoted here. A missing budget returns budget_unset.

After evaluation, verify every reward is finite and within [0,1], retain
selected alignments and each bound's scope, and check aggregation denominators.
These checks can reject bad results, but a finite zero alone cannot identify
overflow hidden upstream; the earlier arithmetic checks remain necessary.
Stage all requested metric outcomes before changing a shared sample ledger.
Commit the sample once with either complete results or explicit metric-specific
unavailable statuses. No automatic retry may append an already accepted metric
again. Raw source evidence, input validation, computation validity and financial
meaning are separate records.

Outcomes include ready_for_metric, input_unresolved, invalid_text,
invalid_span, overlapping_cells, incompatible_frame, location_unavailable,
numeric_range_failure, budget_unset, budget_exceeded, evaluation_failure and
result_invalid. The proposal assigns no numeric score to these failure states.
Acceptance fixtures below check only selected preconditions; they are not a
complete runtime implementation or proof of financial correctness.
