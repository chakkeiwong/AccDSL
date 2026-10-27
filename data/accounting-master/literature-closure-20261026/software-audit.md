# Paper, code and local target audit

26 October 2026. Static source inspection and independent exact arithmetic.
No downloaded source was executed, installed or used for neural training.
Git object hashes are checked separately in code-integrity.json.

## Maliar author-linked Krusell–Smith notebook

Repository: marcmaliar/deep-learning-euler-method-krusell-smith.
Commit: 4f086d9a2586969406a00f88d3b036ba1413b8d3.
File: code/python/Main_KS.ipynb; source cells numbered from zero.
README identifies Marc and Serguei Maliar and links the JME paper. This
notebook is an author-linked application, not every implementation in the paper.

| Target or assumption | Exact source anchor | Finding and local consequence |
|---|---|---|
| Square of conditional expected Euler residual | Cell 37, R2_a, R2_b and Residual2 | Mean of the product of two draws. Correct finite identity is checked locally under conditional independence. Do not replace it with the mean square of one draw. |
| Complementarity | Cell 37, R_mu_xi / Residual1 | Squared Fischer–Burmeister expression is added separately. Its residual and feasibility require separate validation. |
| Future draw generation | Cell 47, separate generate_epsilon calls | Two future draws enter the same current state. Clipping and within-draw cross-sectional normalization still belong to the transition. |
| Differentiation | Cell 47, GradientTape around run_model | Current and future network calls are inside the step's tape. Propagated training state crosses iterations outside the tape; this is not differentiation through the entire training trajectory's stationary distribution. |
| Parameter documentation | Markdown cell 8 versus executable cell 11 | Markdown rho_z=.95, rho_y=.9 and sigma_y=.2 sqrt(1-rho_y^2); code rho_z=.9, rho_y=.95, sigma_y=.2. Executed model differs from those stated markdown parameters. |
| Initialization documentation | Markdown cell 21 versus code cell 27 | Markdown He/Glorot initialization; weights use TruncatedNormal stddev .01. No local default adopted. |
| State support | Cell 18, consumption_capital and productivity_transition_to_next_period | Capital capped at w_max; productivity clipped; idiosyncratic productivity divided by cross-sectional mean. The comment says sum one, but the operation gives mean one. This modifies joint shocks. |
| Risky debt | Cell 37 and state/price functions | Household capital/consumption and equilibrium factor prices; no lender recovery, risky debt issue price, creditor seniority or issuer equity register. Not an implementation of the user's risky-debt system. |
| Local execution policy | tf.function in cell 37 | Source has no explicit input_signature here. Porting would need the project's bounded graph policy, target-specific tuning and downstream tests; no such port is promoted. |

The exact detached-price diagnostic is a local mathematical example. It is
not an allegation that this notebook detaches a risky-debt price that it never
computes. A low residual in its own model cannot establish the different
corporate-finance target.

## Modern SMC squared implementation

Author-linked repository nchopin/particles, commit
3388c4bd30ab9acc5a27c970089230f93610b627. Retained README, license,
particles/smc_samplers.py, particles/mcmc.py and the stochastic-volatility
example. The paper mentions the older py-smc2 package; this modern code is
not represented as the 2013 executable snapshot.

In smc_samplers.py lines 1052–1181, SMC2 creates a particle filter per theta.
current_target runs each proposed filter through the current observation date
and adds pf.logLt to the prior log density. logG adds incremental log weights.
M performs a move after resampling. exchange_step recomputes a larger state
filter and returns the log-target difference, rather than silently exchanging
particle counts. Default Nx=100 and len_chain=10 are source defaults only.

The docstring at lines 1068–1070 says the particle count increases when
acceptance is above the threshold, while executable lines 1119–1122 test
acceptance below it. The executable condition is the evidence for this
revision. This documentation discrepancy is recorded without claiming that
the statistical algorithm is invalid. Numerical execution and behavior on
rare contract types remain untested.

## ACTUS

The official downloaded specification is v1.1-843f7a3-2020-06-08.
Full specification revision: 843f7a362c0886f98619034f35a4cc753faec022.
The specification declares dictionary v1.2 alignment; the retained v1.2
dictionary revision is 6e84435c70e1325e114c931badaa7e80b01a9a0d.
Current test tree: f7a8064872b69db1f0beabac771c99dc3ce0c397.
These historical spec/dictionary and current-test versions are kept distinct.

The service build requests org.actus:actus-core:1.1.0 and Java 17, using
Maven Central and mavenLocal. The Dockerfile copies actus-core from a local
build context, runs Maven install, then builds the service. It supplies no
public core download itself. The queried core repository returned 404 and
the retained Maven query returned no artifact. javac, mvn and gradle are absent
in the inspected environment. No installation would establish the missing
core/source correspondence, so none was attempted.

actus_fixture_check.py independently calculates 24 published event records
for pam01/pam02 (A365/A360, discount, maturity and order). It uses expected
dates derived independently from the declared schedules, not dates copied
from each expected event. Tolerance 1e-10 currency units covers serialized
decimal rounding only. This is fixture arithmetic, not ACTUS execution or
full schedule conformance. Zero rate, resets, business-day shifts and missing
risk inputs remain runtime-adapter obligations. Existing adapter refusal
requirements remain in docs/design/research/actus-interface-boundary-20261023.md.

## Duarte and Fonseca

AI for Structural Estimation, NBER 35283, May 2026, is by Victor Duarte and
Julia Fonseca. The paper, NBER page and author homepage were inspected for
replication links. The paper says a package will be provided; no matching
author-linked implementation was recovered from those routes. The unrelated
GitHub book repository returned by search is explicitly rejected as official
code evidence. This is a bounded source-linkage blocker, not a claim that no
code exists anywhere.


## TimeCausalVAE paper-linked implementation

Paper footnote1 links justinhou95/TimeCausalVAE. Current inspected commit:
a43effe0125d7c778d0560e4704754991d8e271b. Eleven selected source/config/README
files match official Git blob hashes; tcvae-code-integrity.json records them.
This is static source inspection, not executed neural training or replication.

The encoder and decoder LSTMs run forward with per-time linear maps. Conditional
classes repeat c at all dates: causality is relative to c already being available;
a later-known conditioning statistic would violate that information assumption.
CLSTMResDecoder defaults to ReLU, concatenates latent noise, and ends in a linear
projection. The selected SP500VIX config uses CLSTMRes, RealNVP, log/exp transforms,
60 time steps and beta0.04. Its architecture does not enforce support in the
unit ball required by the preprint's KL-to-transport bound. This is a missing
certificate, not evidence of numerical failure in published experiments.
BetaCVAE adds beta times a sampled conditional entropy/prior-density term;
the aggregate-posterior KL in the theorem is a distinct population quantity.
The paper's data-processing and convexity argument motivates an upper bound,
not equality of those quantities. No parameter defaults or trained-model files
were adopted, and no pickle/checkpoint was loaded.
