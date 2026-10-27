# Insurance component request-index successor

This is a local metadata representation repair for the exact
InsuranceComponents/1 profile lock. It changes neither that frozen financial
profile nor its wire records. The successor index format is
accdsl.insurance-component-request-index.v2. It contains one exact profile
reference and entries keyed by canonical UTF-8 JSON of [client_id, request_id].
Both strings retain the old schema's allowed characters, including slash.
Decoding the array recovers both fields; delimiter placement cannot merge pairs.

An exact request-reference match returns the retained decision and receipt.
A different request under the same pair conflicts. A missing pair returns
absent only: all ordinary profile, source, permission, state and freshness
checks still precede any new publication. This helper contains no posting or
publication operation and grants no common accounting-dispatch compatibility.

Migration requires the old index, retained immutable decision history and
referenced records. It checks request/response/receipt/output hashes and direct
bindings, and copies complete decisions unchanged. It does not repeat financial
or source admission. Different pairs sharing an old slash key refuse the whole
conversion; conflicting decisions, missing bodies, corrupt digests and incomplete
index/history correspondence also refuse. Inputs remain unchanged on every path.
Only a complete returned index may be separately published by a future store.
Physical atomic publication and crash recovery remain runtime obligations.

The supplied history is an evidence limit. If an old collision already erased
a decision and no independent copy remains, this helper cannot detect or recover
that missing decision. Migration success is conditional on the retained history;
it is not proof that the history is complete. Missing/colliding history remains
a recovery problem, and must never be repaired by posting the event again.

GroupComponents/1 already encodes its workspace/request pair as a JSON array.
InsuranceAssessment/1 also uses a JSON array for client/request. Their different
owners are intentional. BankAssessment/1 uses additional_commit for new query
publication, while InsuranceAssessment/1 uses it for financial commitment and
therefore returns false on query publication. Both meanings are explicitly
specified under separate locks. A future common adapter must translate the
actual publication effects; copying this Boolean or relabelling profile IDs
would not establish equivalent semantics.
