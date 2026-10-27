# Exact information timing in complete bank requests

26 October 2026. MC05/19/20/24/25/33/34; S2/S4. Continue from the checked
ExactBankInformation/1 information submethod into full native requests.
Artifacts: data/accounting-master/exact-bank-request-conformance-20261026/.

Question: do the exact-time refusals survive request identity, submission bytes,
view, signature, accounting-head, output and query-publication checks? Baseline:
the retained BankAssessment/1 request/response auditor and all 271 regulatory
response cases. Preserve that profile and packet. The independently named exact
checker is a proposed semantic successor, not an already migrated profile.

Skeptical audit: the earlier eleven tests call information directly. They do
not prove complete requests fail for the intended timing reason or that a
refusal leaves query and accounting state unchanged. Reusing malformed record
shapes or stale digests would test a different question. Construct complete
derived requests with dependency closure repinned and submission bytes updated;
retain ordinary context/state and financial inputs. Inspect the native owners
before generating outputs. Reuse original complete responses when unchanged,
and derive new responses from the exact refusal and publication contract.

Primary criterion: complete request/response checks agree where timestamps have
unchanged meaning, and later submicrosecond availability/ingestion is refused
without a published query or accounting mutation. Independently assert the
expected refusal reasons and equal financial results for equal instants.
Vetoes: damaged predecessor evidence, stale closure/submission identities,
changed financial inputs, false publication, missing context/head checks or
mislabelled profile adoption. Counts and shape checks are explanatory only.

Assumptions: finite synthetic timestamps are adversarial fixtures, not observed
issuer publication times; fractional UTC coordinates use the pinned converter's
calendar and precision bounds. Same-instant offsets must agree; unknown offsets
remain unsupported. No change to accounting authority or execution admission.

1. Inspect complete request dependency and submission/publication ownership.
2. Construct the smallest paired full request/response cases, then retained
   regressions and meaningful adverse identity/control cases.
3. Save exact records, outcomes, source locks and run manifest. State remaining
   schema/profile migration work rather than calling isolated checks adoption.
4. Refresh checkpoint and next dependency; continue ready internal work.

CPU-only deterministic diagnostics, no long benchmark. No commits, agents,
installations, GPU, paid review, external messages, publication or forecasting.
