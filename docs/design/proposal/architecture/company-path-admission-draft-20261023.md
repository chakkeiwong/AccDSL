# Evidence for an archival conditional company path

The three-year operation path now has a portable documentary evidence packet.
CompanyPathEvidenceDraft/1 contains42 records:21 unchanged records for the
historical opening and its synthetic admission,14 local method definitions,
three conditional closing records, three linked reports and one export record.
The packet references35 exact byte payloads. It preserves the older portable
schemas and adds separate names for conditional projections and local methods.

An old CompanyState includes a Context, View, source Facts and sequence. The
historical opening's full dependency closure contains21 records when its
synthetic Admission is included. Validating just balances and context would miss
the source/readings/admission chain. The new checker validates every reachable
record's closed schema, typed content hash, dependency list, referenced record
kind and blob bytes. Unreachable exported records, missing dependencies,
inconsistent source bytes and unknown method identities are rejected.

Each executed operation names a local method whose definition binds its payload
schema, written calculation/preconditions/effects, exact implementation and the
passed174-check conformance evidence. All14 method definitions resolve across
the63 operations. Explicit local reference locks identify the reviewed synthetic
baseline. They do not act as professional accounting approval or cryptographic
signatures. The validator imports no code supplied by the packet; a separately
selected local interpreter replays the path and matches the stored result.

ConditionalClose records preserve the full claim, cohort, inventory, account and
facility memory, identify the originating historical opening, and link to the
preceding conditional close. They explicitly state historical_admission=false.
PathReport records bind the annual report to that closing and exact year result.
Changing a path, report, method or source and merely recomputing record hashes
does not satisfy the cross-record bindings or the external local identity locks.
These checks establish consistency against the selected local baseline, not
authenticity against an author who controls all evidence and reference locks.

## Source time and decision information

The opening depends on eight authored synthetic source units. Seven have a
publication date of2 March2025. A cutoff of1 January2025 therefore excludes
them. A cutoff during2 March remains unresolved because the source gives only
the date, not the time. The beginning of3 March passes this source-date test.
System-as-of selection distinguishes ingestion from acceptance:12:30UTC on
5 March is after ingestion but before two required acceptances at13:00UTC.

These outcomes follow the existing source precision convention. The input dates
remain authored synthetic dates, not verified availability of real issuer
documents. Passing a later source cutoff also does not establish when the future
operation assumptions were authored or available to a decision-maker. Therefore
the complete packet is admitted only for archival synthetic exploration.
Investor-information and system-as-of requests remain unresolved after source
timing passes, with reason path_assumption_information_not_admitted. An earlier
cutoff can be directly ineligible. No branch is silently rewritten to pass.

## Scope and remaining work

All65 conformance checks pass, including trusted-local re-execution, temporal
boundaries, rehashed semantic mutations and project-contained blob loading.
The packet and checker are in
data/accounting-master/company-path-admission-20261023/.

This export covers complete conditional paths. Exporting partial paths, portable
revision records, and explicitly time-admitted assumption/decision information
are still needed. The internal annual execution adapter remains an implementation
detail rather than a historical-state import. A text frontend, general method
package admission, production storage and broader sector methods also remain.
The new sequence is not yet incorporated into manuscript Version3.51.
