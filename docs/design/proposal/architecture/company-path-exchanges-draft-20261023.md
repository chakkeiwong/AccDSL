# Exchanging interrupted company paths and assumption revisions

CompanyPathExchangeDraft/1 preserves the results of a company path even when a
year stops before closing. Each YearOutcome identifies the exact annual input,
its predecessor, the operations already applied and its report. A complete year
also identifies its conditional closing memory. An interrupted year has no
closing memory, so it cannot open the following year. The later periods remain
listed as unresolved rather than disappearing from the exchange.

This distinction preserves useful information. Northstar's interrupted second
year still has known opening cash and equity from its completed first year. Its
year-end amounts and full-year flows remain unresolved. Missing payroll and a
supplier-payment shortfall produce different stopping reasons while preserving
their respective applied operations. Neither is a historical accounting close.

A PathRevision identifies both input paths, the changed year, its exact
replacement and the author's reason. Validation compares the complete input
bodies: the child must equal the parent with only that replacement. The source,
opening and periods cannot change. Earlier annual results retain their
identities. Execution starts again at the historical root and recomputes the
affected suffix. The revision relation also supports explicit repair: supplying
the original payroll amount to the unresolved branch restores the baseline
complete path. This records a conditional assumption change, not a correction
to historical disclosures or a committed database transaction.

The new packet contains 66 records and 64 content-addressed blobs, including
all 42 records from the complete-path packet unchanged. Five paths contribute
13 available annual outcomes, with five declared parent-child relations. The
validator checks the frozen source and method bindings before considering the
new records. Packet bytes never select executable code; replay uses the trusted
local interpreter identified by the preceding admission evidence.

Content binding and semantic replay answer different questions. An adverse
fixture changes a reported cash value and recomputes every affected content
hash. Its record bindings are consistent, but the cash value does not follow
the operations. Trusted local replay rejects it. Accordingly, the validator
returns an explicit verification level; a binding-only result cannot establish
arithmetic conformance. The 119-check suite includes replay, partial-state
substitution, stale suffixes, undeclared additional-year changes and path
traversal refusals.

This remains a synthetic archival design example. It establishes no source or
assumption availability at an earlier information cutoff, real-book accounting
acceptance, authenticated author identity, crash recovery or production storage.
Version 3.52 remains unchanged; this extension awaits manuscript integration.

Evidence: data/accounting-master/company-path-exchanges-20261023/checks.json.
Plan: docs/plans/accounting-company-path-exchanges-20261023.md.
