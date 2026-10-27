# R04 — version-bounded pybind11 string conversion

20 October 2026. P15/P17/P19; MC01–05, MC23, MC26, MC28–35.
Output: data/accounting-master/r04-pybind-strings-20261020/.

Question: what reaches the inspected pylcs std::string arguments when callers
supply Unicode, bytes, embedded NUL, or unpaired surrogates? The parent setup
requires pybind11>=2.2 without an exact build lock. Inspect v2.2.0 (the allowed
lower-bound release) and v2.11.1 (a contemporary source comparator for the 2023
pylcs upload), without treating either as the installed or distributed build.
Do not claim these two snapshots exhaust the dependency range.

Evidence contract: trace each selected string caster from Python type checks
through conversion, length and error handling to std::string assignment. The
primary criterion is exact pinned source support; preserve line anchors and
actual acquisition receipts. Compare with pylcs's conditional valid-UTF8 token
contract and Python lengths, not with a claimed empirical performance baseline.
Missing source identity or uninspected conversion branches veto dependent
claims. Changed protected bytes, execution of acquired code or held runtime
work veto continuation. Metadata dates and finite examples are explanatory;
they do not establish installed behavior, all versions, package adoption,
historical experiments, model ranking or financial validity.

Research intent: expected failure modes are bytes bypassing Unicode validation,
strict rejection of surrogates, NUL truncation, or version-dependent error
handling. A source mismatch triggers a narrowly stated input contract and an
independent standard-library illustration, not rejection of the research
direction. Preserve invalid-input uncertainty when source inspection is partial.

Default audit: version endpoints are source hypotheses selected for a bounded
comparison; same source behavior in them does not prove all intervening builds.
UTF8 scalar identity, canonical normalization and graphemes are distinct. No
normalization policy is chosen. Python bytes length is not codepoint count.
CPU-only standard-library diagnostics hide GPU devices before execution and
never import, compile, install or execute acquired native/build/dependency code.

Skeptical audit passes with a repaired scope: following an unconstrained
dependency to current HEAD would not answer historical build semantics. Pin
two named releases and explicitly leave distribution/build provenance open.
Pre-mortem: documentation may describe output decoding rather than input
encoding; inspect load(), not only cast(). Distinguish explicit-length string
construction from NUL-terminated conversion. The earliest checks are tag
resolution, exact selected tree paths and source branch coverage.

Acquisition budget: at most twelve HTTPS requests, 35 seconds and 2 MiB each,
limited to official pybind11/CPython repositories and docs; save headers, bodies
and actual curl JSON receipts immediately. A staged wrapper fixes allowed paths
after tree inspection. No package archives or wheels. A plan addendum must
precede nontrivial calculations. Deliver six additive ledgers, result/review,
checks and separate R08 supplement. Update only four authorised live controls.
Preserve 3.44/396/not_ready, 53 obligations, six interactions, 46 operations,
HEAD/index/empty staging and 36 tracked dirty paths; close no whole row.
Preparation, construction, --check and --record run once; no-argument replay is
read-only. Runtime/controller campaigns, installs, commits, outreach, publication
and fees remain held. Continue the next ready gap after this inquiry.
