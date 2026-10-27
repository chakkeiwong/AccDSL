# Complete the finite-coupling error bound

MC10/11/12/26/29/32/33; C2/C3/C4/C5. Baseline: 5.52-R1,
simulation/lit-09-approximation-4.tex, lines 87–155 (C21).

Question: does the stated one-step coupling condition suffice for its claimed
whole-path expected-loss bound, including date zero and the requested loss?
The manuscript requires initial observations to agree but does not expressly
require an initially related state pair with matching current output. It also
says that a bounded path loss agrees on the no-mismatch event without requiring
a common loss functional of the preserved records. Those hypotheses must be
stated. The finite examples use shared initial states and common loss; their
numerical values need not change.

Primary criterion: a reconstructible proof under explicit initial pairing,
common feasible information/policy, and matched-loss conditions; exact examples
show why omitted conditions matter, and the previous three-period arithmetic
remains valid. Baseline is the printed argument, not a weak alternate algorithm.
Promotion vetoes: lost source distinction, altered numerical example, incorrect
probability recurrence or unjustified policy transfer. Explanatory only: check
counts, manuscript length and compiler success. No empirical superiority or
general state identification follows.

Default audit: finite T, bounded nonnegative loss and rational examples are the
existing scope. Initially related states with matching current reports and
private/public information are necessary assumptions, not an inferred financial
fact. If initial mismatch probability is delta0, it contributes to the bound.
If loss disagreement on matched paths is at most eta, it contributes separately.
Bounds delta_t in [0,1] are supplied premises, not estimated error bars.

Skeptical audit passes after replacing the potentially undefined conditional
probability on a zero-probability survival event by an unconditional recurrence.
The method compares common admissible policies; it cannot average a discrete
action or allow hidden-state-dependent decisions. The repaired bound should
retain the exact original formula as the delta0=eta=0 special case.

Implement independent Fraction-based adversarial examples before editing.
Preserve the complete original source and write a protected successor. Read
rendered affected pages before and after, retain exact source/math/citation
deltas and build both volumes. Record separate mathematical, source, reader and
engineering judgments. Whole-manuscript review remains separate.
