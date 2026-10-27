# Native group selections checked — 25 October 2026

Eleven focused tests and 23 CompanyWorld/sector regressions pass. Both complete
snapshot cases replay exactly against 116 locked files. Initial closure is
five records/five blobs; final closure is 109 records/five blobs. Each closure
includes 12,592,927 source bytes. Native attempt-03's 681 passing checks and
14 input snapshots remain byte-identical; their financial calculations were
not rerun. See evidence.json, source-lock.json and run-manifest.json.

The initial selected cash balances are P=500 and S=100, ownership4/5. Final
cash is P=983/2 and S=305/2, ownership9/10. These are native conditional facts,
not newly admitted accounting observations. Each selected book keeps a typed
pointer into the unchanged group state, including shared instrument, return,
tax, lot and ownership state. The ownership assertion covers only the selected
snapshot day. It does not extend the fraction over the wider control interval.

The recovery review found an unbounded outer request before copying/hashing.
The existing request limit now covers that envelope. Independent rehashed
negative cases reach schema, rational, dependency, dangling-reference and
type checks; a 50-record test-only chain checks the closure depth refusal.
The first expanded test run failed due to a misplaced test tail and a fixture
that failed schema validation before its intended type check. Both fixtures
were repaired, then all 11 tests and the recorded/replayed suites passed.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept bounded reference selector | Exact native closure and unchanged context pass | Corruption, invalid semantics, mismatched owners/intervals and resource excess refuse | Native books still share group state | Compose separately valid synthetic books with explicit elimination entries | Independent executable books, consolidation recalculation or accounting admission |

The strongest alternative explanation is that tests merely restate digest
identity. Independently rehashed semantic failures and exact selected cash,
ownership and full-context comparisons address that concern within this
finite adapter. They do not establish completeness of native financial
semantics. General group/sector methods, noncontrolling interests, FX, actual
source binding and broader implementation remain open.

Version4.21 remains517 pages and not_ready; this addition is not integrated
into its frozen manuscript. S1–S5 remain partial, S6 held, S7 deferred.
All53 obligations/6 interactions/46 operations remain; no whole requirement
closes. Next: docs/plans/accounting-compatible-book-composition-20261025.md.
