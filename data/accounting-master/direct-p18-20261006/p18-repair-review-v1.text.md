# Focused P18 integration-repair review

## Blocking repair (1): persistent-records table — resolved

`09-implementation.tex`, §Persistent records. The longtable now carries `branch` (key, immutable definition ref, entity/book, required synthetic/real mode), `branch_head` (owner, state ref, generation, advanced only by the expected-head transaction), `posting_authorization` (basis, profile, method, authority, findings, permission, view — matches A1 field set), `journal_batch` restricted to committed balanced postings with candidates explicitly outside the relation, `economic_delta` bound to the same basis/authorization, `committed_receipt` (stable key, full fingerprint, original request, opening/closing state, journal/delta refs, published atomically with the head advance), `review_view`, `dependency` (including candidate-set membership), and `search_checkpoint` (manifest, partition, explored/unresolved regions, frontier, budget, results committed together). `economic_event` is keyed by the entity/book/branch/business-event four-tuple. The "atomic commit status" column is gone, and the section preamble states that candidate calculations and diagnostics stay outside the committed relations. This matches operations-storage §Durability, P1 and P2 with no speculative publication. The §Reference implementation ownership sentence (committed journals/deltas/receipts/heads in the one transactional store, columnar files as derived exports only) resolves the prior nonblocking ambiguity.

## Blocking repair (2): single implementation sequence — resolved

`10-validation.tex`. The milestone table P0 now reads portable records/contextual types, source/review/time selection, typed constructors/versioned IR, and separate authorization plus atomic journal/delta/state/receipt transactions; P1 admitted history templates/finite choices/shared symbols/linear adapter/bridges; P2 matched debt text frontend with identical IR plus connected corporate methods via the typed authoring API; P3–P6 retain contract/valuation adapters, banking, insurance and optional inference obligations unchanged. The §Decisions paragraph now points "to the table above" and maps its phrases onto P0/P1/P2 with the same vocabulary, keeping "a design sequence, not an already running product campaign" and "Product implementation follows … explicit implementation authorization." One normative sequence remains.

## Nearby corrections — checked

- `07-execution.tex` pseudocode: `execute_event(operation_request)`; body order (closure/bindings/admission → authorization/journal/delta → key lookup → equal fingerprint replay → different fingerprint conflict → expected head → atomic recheck/commit) matches §replay and P2. The following paragraph now states inputs include request identifier, expected head and execution settings and cross-references §\ref{sec:replay}.
- Fingerprint identity: §replay, operations-storage §Versioned requests and 09 §Identity agree (payload, version, opening state/expected head, request ID, settings in the fingerprint; four-tuple as lookup key).
- Correction: `authorization.tex` §replay adds the new-linked-event paragraph with admitted method, preserved original receipt and unresolved-when-authority-absent, consistent with P4.
- Migration: operations-storage §Durability names the envelope as the sole expected-head carrier, consistent with the `OperationRequest` closed body and P5's requirement that the head be compared.
- Solver outcome: 09 §Plugin interfaces links adapter `unknown` → `SolverIncomplete` → unresolved coverage, "not infeasibility"; T10 and A2 consistent.
- Forecast ladder: one ladder in §Forecasting paragraph 1 includes both "one selected interpretation" and "preserving alternatives"; the later paragraph refers to "the comparator ladder above" and the inexpensive-comparator paragraph gives instances, not a second normative list.
- Corpus: $3\times8\times4+6\times8\times2=192$, $136+56=192$, $244\ge192$ all consistent.
- Review-cycle residue: "This version supplies…", "The retained panel contains…" are stative; `check_repair_conformance.py` retained as a literal file name.

## Remaining items

No remaining repair blockers and no introduced contradictions found in the supplied files. Two editorial residues, neither blocking:

1. `09-implementation.tex`, §Identity, last paragraph: "SQLite owns source, review and run metadata transactions" is narrower than the new §Reference implementation sentence (committed journals/deltas/receipts/heads also live in that store). Minimal fix: "source, review, accounting and run metadata transactions". Reason: avoids a reader inferring accounting domains are outside SQLite's ownership despite the earlier statement.

2. `10-validation.tex`, milestone table: T09 appears in both P0 and P1 exit evidence (via "T05--T10"). Pre-existing, not introduced by the repair, and harmless if read as cumulative exit evidence; optionally write "T05--T08, T10". Reason: keeps each test's first-required stage unambiguous.

`03-literature.tex` (F5) was not supplied and is not certified here; build/render records are regenerated separately.

VERDICT: AGREE
