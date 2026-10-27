# InsuranceComponentsIdentity/1 execution policy

This documentary execution-policy successor is bound to the exact retained
InsuranceComponents/1 financial Profile, its schemas and its semantic contract.
It does not define a replacement accounting method or permit an unreviewed
financial-profile conversion. Requests use the original OperationRequest and
Submission schemas and canonical body bytes. All underlying accounting source,
authority, uncertainty and finite-method limits remain.

The new world contains identity_profile_ref naming an immutable policy record.
Its decisions map uses canonical JSON arrays [client_id,request_id] as keys.
Equal encoded keys imply equal ordered string pairs because JSON array decoding
recovers both strings. Each field retains the original identifier alphabet.
The identity record binds the original financial profile, original schemas,
original financial semantic contract, successor policy schema and this contract.
It grants no new accounting authority.

A conditional migration changes only those keys and adds the policy reference.
All original decision/request/response/output/receipt references, owner heads,
journals, publication digests, current view and unrelated state remain exact.
Known incomplete, conflicting or ambiguous supplied decision history refuses.
An erased decision with no retained evidence cannot be detected; success is
conditional on the supplied history's completeness. Migration never posts.

Dispatch first checks the bound execution policy, complete request/submission
shape, canonical exact bytes and immutable dependency integrity. A prior decision
under the pair yields a conflict if its request reference differs. An exact
retry returns the original output, receipt, diagnostics and publication list
with disposition replayed and additional_commit false, preserving every world
field even if current view or heads advanced. A fresh request retains the
native whole-read-set, information, authority, lineage and financial checks.

Accepted commits publish all changed owners, journal and decision together in
the documentary world. Reports and unresolved results retain their native
metadata-publication meanings. A rejected request changes no world and has no
receipt/output/publication. No transport observation distinguishes committed
from uncommitted worlds after acknowledgement loss; recovery uses the original
request and submission in both. This is finite documentary atomicity, not a
physical store, multiwriter guarantee or hardware-crash experiment.
