# Connect authored methods to explicit transition versions

26 October 2026. MC20/23/24/25/33/34; S2/S3/S4, G2/G12/G18 and I04.

Question: can authored fixed-state and typed-growth methods be loaded and called
through one explicitly versioned registry without changing either native
transition or silently dropping unselected-entry checks?

Inspected baseline: CompanyMethodRegistry/2 uses company_method_clock_v1 and
CompanyBookTransition/1. Its closed entries have no transition selector or v2
memory definition. DeclaredCompanyProgram/2 retains that restriction. The
collection and receivable adapters generate selected methods internally; they
do not establish a general mixed-version registry. A registry v2 label is not
evidence of transition v2 support.

Skeptical audit passes for a separate bounded successor. Preserve frozen files;
do not patch their pinned dependency hashes. Explicitly name the selected
transition for every entry, retain supplied account classes, event types,
metadata bindings and direct-event clock. Require a v2 memory definition.
Reuse the existing declaration/type/context validators and transition engines.
Authored source identity remains separate from semantic method identity.

Primary criterion: full materialized requests and proposals equal original v1
registry calls for payments, and direct native v2 calls for claim-creating sales.
Check both company charts and a complete sequenced insertion then scalar update
on the same typed book. Independently check cash/claim effects. All registry
entries must validate, even when not selected. Test changed method/source hashes,
wrong contexts/types/account classes, missing schemas or memory definition,
unknown methods, unsupported clocks, duplicate identity and proposal tampering.
Unknown/false economic premises must retain their native statuses.

Assumptions: reuse the existing maximum of 32 entries and one-megabyte bound as
reference resource limits, not production capacity. Direct event dates are the
supported clock; no general fiscal scheduling is inferred. Placeholder unknowns
are structural checks only. Complete state equality is engineering evidence,
not proof of accounting applicability or source authenticity.

Implement a small successor using existing semantic owners. Run deterministic
CPU-only focused comparisons, preserve input hashes and record a manifest and
decision. Then audit program-level composition and reporting as the next
dependency; do not claim the existing program runner adopts the successor.
Stop this unit for invalid native baseline, corrupted inputs, inconsistent
state mapping or inability to state version dispatch exactly. Ordinary negative
economic cases are expected, not continuation vetoes.

Artifacts: data/accounting-master/authored-method-registry-20261026/.
No agents, installs, commits, GPU, external publication, paid review or E3.
