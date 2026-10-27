# A smaller perturbation cannot select the all-zero CGU allocation

23 October 2026. P17/P19; MC02/04/17/19/24/26/28/29/30/33–35.

The existing positive-weight capped reversal rule has no path-independent
continuous extension at an all-zero carrying vector when at least two eligible
assets have positive ceilings and the desired final total lies strictly between
zero and total capacity. This is a mathematical result under fixed ceilings
and a supplied total. It rejects continuity as a way to manufacture the missing
allocation weights; it does not select an IAS 36 treatment or rule out recovery.

`derivation.md` first proves that the positive-weight procedure ends at
x_i=min(C_i,lambda b_i), with the multiplier chosen to make sum x_i=T. It then
proves that every vector satisfying 0<=x_i<=C_i and sum x_i=T is attainable as
a limit along some strictly positive starting weights. One inclusion follows
from the closed constraints; the other uses an explicit interior mixture and
a shrinking starting balance. Two distinct paths therefore suffice to refute
uniqueness, while the construction describes the entire possible limit set.

For ceilings (10,10) and final total 6, starting balances epsilon(3,3) yield
(3,3), while epsilon(1,5) yields (1,5). Both have starting total 6 epsilon and
requested reversal 6(1-epsilon). Both approach the same zero vector as epsilon
decreases. Their restored balances remain different. The requested reversal
and asset capacities were recomputed consistently as T-sum b and C-b; they
were not held fixed while changing starting balances.

Fourteen hand-authored rational fixtures pass against the iterative allocator
and independently supplied expected balances and multipliers. They include
binding ceilings, several capped assets, an exact cap equality, a single asset
and full capacity. Two constructive paths to boundary vectors pass at six
exact points, including a target with both a zero component and a binding cap.
Eight outside-domain inputs are refused before allocation. No stochastic
simulation, sweep, floating tolerance or actual-company calculation was run.
Finite checks support transcription and correspondence; the written proof
supports the general statement.

The singleton cases remain explicit. With one eligible asset, the final total
fixes its amount. At total capacity every asset reaches its ceiling. At target
zero the constraint set contains only zero, but a positive starting balance
cannot satisfy the positive-reversal domain. None of these mathematical facts
establishes accounting authority. Targets above capacity, changing ceilings,
mixed zero/nonzero starting weights and quantized rounding are outside the
theorem. The existing capacity-shortfall and unresolved-method dispositions
are preserved.

The claimed target is the limit set of the stated mathematical allocator. The
computed quantities are exact hypothetical restored balances, reversal amounts
and path errors. They equal the proof's expressions at the declared fixtures.
They are different from an accounting-admitted allocation, which remains
unresolved. The historical AASB 136 paragraphs 122–125 were reread and bound;
the earlier positive-weight examples and source-access results were reused.
There was no fresh source acquisition or broad literature inquiry.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept the limit-set deduction on its stated domain | Algorithm characterization, both set inclusions and exact fixtures pass | No unresolved algebra or input-validity veto | Applicability of fixed ceilings/target to a real case | Retain proof as an implementation boundary | IAS 36 treatment or economic impossibility |
| Reject a canonical limit-only fallback | Distinct approaches to the same zero vector have different limits | Promotion veto fires for this proposed fallback | A separately justified policy may supply additional premises | Keep allocation_basis_unresolved; require applicable authority or additional asset-level evidence | Rejection of impairment reversal or all alternative treatments |
| Preserve singleton qualifications | One asset/full capacity/zero boundary separated | Zero target is excluded from positive-reversal approach | Accounting recognition and actual facts remain unadmitted | Do not confuse mathematical uniqueness with authorization | A new default at special cases |
| Continue independent internal work | Required evidence remains intact | No global continuation veto | Other methods and empirical target choices remain open | Reconcile the substantive target choices before dependent empirical planning | Whole-row closure or readiness |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Eight out-of-domain inputs refused; unique-limit fallback contradicted under the stated domain |
| Statistically supported ranking | N/A: exact deterministic algebra |
| Descriptive-only differences | Fixture counts, scales and execution time do not establish prevalence or performance |
| Default-readiness | No allocation, numerical policy or runtime admitted |
| Next evidence needed | Applicable all-zero accounting treatment and actual asset/perimeter/valuation premises |

Post-run red team: the strongest alternative explanation would change the
ceilings, target or weight-updating rule while taking the limit. That is a
different model and is outside this theorem. A valid counterexample within
the stated domain would overturn the proof. Agreement of finite code with
expected vectors alone would be weak evidence; the active-set invariant and
explicit all-limit construction are the main support. The weakest practical
evidence is accounting applicability, which this result intentionally leaves
unselected rather than hiding with an epsilon.

The calculation manifest binds the exact command, inputs, proof and measured
duration. No failed calculation or changed fixture expectation occurred. The
completion verifier protects 11,232 inherited files, HEAD/index and the same
36 tracked dirty paths, with only four planned live-control updates. Version
3.48 stays 401 pages and not_ready; 53 obligations, six interactions and 46
operations remain, zero whole rows close, and all 192 vintages remain
unadmitted. During completion the user selected E3 expected performance at future
dates for the same named companies; a separate decision record follows. The
origin law and six quantitative scientific choices remain unselected. Runtime/controller,
installation, empirical runs, acquired-code execution, commits, outreach,
publication and fees remain held. Default `verify.py` is read-only; completed
preparation, calculation recording, source-binding recording and completion
recording must not be repeated.
