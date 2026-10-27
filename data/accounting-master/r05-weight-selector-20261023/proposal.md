# Predictive history weights and a locked fixed selector

This proposal turns a finite family of alternative history-conditioned forecast
laws into a predictive procedure without claiming that the fitted coefficients
are probabilities that any one history is true. It is designed for the selected
E3 comparison: future full-year operating cash flow for the nine named
companies, equal company contribution after common positive asset scaling, and a
candidate-minus-locked-comparator CRPS contrast.

For each admitted cell let `H(D)` be the semantic history family and let
`F_j,o` be the common-kernel forecast law for component `j` at earlier origin
`o`. Encodings that have the same source-supported joint state and the same
future kernel are first quotiented into one canonical component. A history with
the same past journals but a different future kernel is not merged. This is the
only place where representation multiplicity is removed; it does not create
probability mass.

History families can change across origins. Semantic identifiers alone do not
justify transferring a fitted simplex vector from an earlier family to the
current one. The candidate procedure therefore requires a stable feature map
`phi(h, D_o)` and a fitted score rule that can be applied to each origin's own
family. The map, score family, penalty, minimum history and tuning budget are
unselected. For example, normalising finite feature scores could produce
origin-specific simplex weights, but this is a candidate construction, not an
adopted fitting method. A missing law, feature meaning or sufficient eligible
history produces `law_unavailable`; equal weights do not repair it.

Earlier pseudo-forecasts use only sources, inputs and scales available at their
own pre-start forecast cutoff. Their realised outcomes become validation
labels after release and may enter a later fit only when released by that
later fitting cutoff. The current forecast's future outcome cannot enter its
fit. Coefficients are forecast-combination weights, not interpreted as posterior
belief in the truth of a history. An unavailable probabilistic forecast retains
its unweighted family for the set-valued protocol.

The fixed comparator likewise needs a stable selection procedure, trained on
the same eligible earlier-origin data and applied to the current family before
its outcome. A feature-based selector and a source-priority rule are distinct
candidates; neither is selected here. Lexicographic semantic-ID order resolves
only an exact tie after substantive scoring. Candidate and comparator must
share inputs, target, scale, economic kernel, fitting budget, timing and service
policy. Independent fitting rules define a broader procedure contrast, so any
score difference cannot be attributed solely to integrating interpretations.

A Bayesian or elicited measure mode remains a different contract. It requires a
source-level prior and likelihood, a dependence-aware update, a measurable
history space and the semantic duplicate policy already specified in the
manuscript. Until those inputs are admitted, forecast-combination coefficients
must not be described as a posterior or as the probability that an accounting
interpretation is correct.

The exact reference uses persistent synthetic component IDs, point laws at 0
and 2, and validation outcomes 0 and 2. It does not test cross-origin transport.
The equal-weight mixture minimises the average mixture CRPS; the component
selector has a deterministic tie. Splitting one semantic component into two
encodings leaves the law unchanged after quotienting. Invalid weights, missing
laws and labels released after the later fitting cutoff are refused. It also
checks the ordering forecast lock < outcome release <= later fitting cutoff.
These checks validate
bookkeeping and the finite objective only; they do not evaluate a company or
select a future resource, grid or inference policy.
