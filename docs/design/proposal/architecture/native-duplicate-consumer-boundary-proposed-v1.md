# Native source occurrences and consumer reductions

23 October 2026. Additive proposed clarification of the older software reuse
method, R4. The evidence and extraction contracts govern this distinction;
their existing schemas and admission rules continue to apply.

The older method says that equal values in different contexts remain separate
occurrences “until an explicit alias decision.” The word “until” is misleading:
an assertion alias cannot end the identity of an original occurrence. Read that
sentence as follows. Equal values at different source locations remain separate
source occurrences. Different financial contexts remain separate assertion
candidates. An assertion alias requires an explicit equivalence decision with
compatible context and source/reading lineage, and preserves every supporting
occurrence afterward. Equal numbers or overlapping rounding intervals alone do
not establish that equivalence. This clarification corrects the wording, not a
demonstrated deletion in an importer.

Content storage and assertion identity answer different questions. Two spans
with identical content may share that content's stored body while retaining
both occurrence locators. Two different XML fact elements can have the same
decoded numeric text while their original bytes differ, for example because
their IDs differ. A hash of the decoded text must not be presented as the hash
of either original element. A reviewed assertion supported by two occurrences
must retain both links; counting that evidence twice as independent likelihood
input would be a separate error.

The authored Apple examples preserve f-207 and f-256 separately despite their
equal concept, source context, unit, decimals and value. Both have their own
occurrence, assertion and candidate Context records. Their source context is
c-21, unit usd and text 56950000000. No financial context or assertion alias is
admitted by those examples. The full example retains all 1,127 fact occurrences,
including all members of 69 repeated source-signature groups. These counts
describe the retained instance and the stated signature, not semantic duplicate
classification or installed importer behavior.

A later consumer may construct a reduced view only under its own named method,
edition, scope and observation target. Its inputs and occurrence provenance
remain retrievable. Inline target-document mapping must satisfy every applicable
input obligation, including required IDs, attributes and relationships. The
2018 note's complete-duplicate classification alone is insufficient. For
Calculations 1.1, the final interval-intersection instruction differs from the
earlier highest-accuracy recommendation. The unresolved wording in sections 5.1
and 5.4 is not repaired here. None of these rules is a universal assertion alias.

Formula is disabled in the selected first importer. Future Formula execution
needs its own variable/filter, implicit-filtering, sequence/matches,
precondition, identity and assertion-processing specification. Under the frozen
two-by-two hypotheses, singleton bindings have four possible data sets;
sequence bindings have one when matches=true and four when matches=false.
Validation's MAY does not require four processor calls. Removing a distinct
node can change a sequence-cardinality test even when its numeric value equals
another node's. These conditional examples refute general losslessness of
occurrence removal; they are not processor conformance tests.

Source preparation constructs candidates. Reduced views, content sharing and
assertion aliases grant neither financial admission nor accounting posting
authority. A future reduction proposal must state what observations it
preserves, justify that equivalence under explicit assumptions, retain the
input-to-output relation and fail visibly outside its scope. This note does not
select such an algorithm or add a runtime/schema implementation.

Exact local clauses, source-ledger identities, conditional examples and the
bounded correspondence check are retained in
`data/accounting-master/r06-native-duplicate-contract-20261023/`.
