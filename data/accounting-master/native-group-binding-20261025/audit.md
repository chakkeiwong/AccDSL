# Native group binding audit

25 October 2026. The immutable attempt-03 State record contains `books/P` and
`books/S` plus joint lot, return, compound-instrument, tax, ownership and cash
history. It is not an individual CompanyBook. Its native records omit the
top-level revision field required by the bank/insurance resolver and use
path/sha256/byte_length blob references. Reusing that resolver unchanged would
therefore reject valid native data or invite weakening its distinct contract.

The native source explicitly describes P and S as separate USD legal books;
their dictionary keys are the available native book identities. Bind a
CompanyWorld book with entity=P/book=P (and S/S) to a new typed selector record
containing the exact group-State reference and /books/P (or /books/S). The
selector digest, not the group digest, occupies the opaque state_ref. This is
a selection reference, not a new independent executable ledger. Return all
shared native state and the selected native world unchanged. No copying into
CompanyBook/1, account mapping, period carry or common-ledger authority follows.

Supported snapshots are the named initial and final native worlds only. The
owner fraction is 4/5 initially and 9/10 finally. It must not be attached to
the full 2024–2026 control interval as though ownership were constant. Bind
only the selected state date's one-day interval, inside the retained supplied
control interval, and label the control premise as supplied native facts.
This adapter preserves the premise; it does not assess control. Other world
books and unresolved components must remain unchanged.

Primary checks: native record shape, canonical rational strings, schema and
domain-separated digest; exact dependencies and complete closure from the
selected world's head/view/receipts/proposals/decisions; every selected blob's
path, length and hash; correct member selectors, owners, source/view and
snapshot control edge. Direct group-hash-as-book, changed currency/date,
invented member, mistyped/dangling reference or altered source bytes veto
binding. Verify that original 681-check and 14-input preservation evidence
still matches without claiming to rerun its financial derivations.

The finite selector approach is an engineering proposal with provenance in
the native dictionary, not a default company identity scheme. Its failure mode
is detached shared context, tested by requiring the full native group state
and snapshot in every result. A downstream caller that needs independently
executable books must still provide a separately checked state/method adapter.
No accounting, source or posting admission is established. The audit passes
for this bounded read-only reference adapter.

Recovery review on 25 October: the request envelope itself was not bounded
before hashing and copying; only its nested world was checked. Apply the same
existing structure/scalar/byte bounds to the complete request. Test malformed
and cyclic requests before freezing. Also test independently rehashed records
with invalid schemas, noncanonical rationals or incorrect dependencies, so a
digest mismatch cannot mask those checks. The retained packet is pinned and
size-bounded, not an arbitrary import endpoint; no new untrusted-service
security protocol is needed. The 48-level/4096-record closure limits are
existing engineering bounds, tested as refusal behaviour, not completeness.
