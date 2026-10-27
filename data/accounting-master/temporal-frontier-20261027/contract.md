# Resumable temporal partition: inspected evidence contract

27 October2026. MC01/03/05/11/12/13/24/25/26/28/33/34;
W01/03/04/11/12/16. Design reference only; product implementation held.

Question: can exact temporal work pause and resume with complete coverage of
both completed and unexamined clock domains? Baseline: the accepted exact
source-time tree and original-edge proof checker over the same closed revision
profile. Independently reconstruct every branch domain and leaf outcome; compare
completed resumed trees against every saved complete predecessor tree.

A checkpoint has one rooted tree. A pending node holds a path, no claim of
nonemptiness and no outcome. An expanded node has a checked nonempty proof and
all first-failure complement children. A terminal is a checked empty proof or a
checked full-eligibility leaf. Domain constraints are reconstructed from the
root and path, never trusted from a saved mutable constraints list. Consequently
pending domains may include empty sets; that is conservative unfinished work,
not a claim every pending branch contains a possible world.

One budget unit resolves one pending node by the exact solver, then checks its
certificate. A nonempty interior node splits into all children atomically before
a pause. No partly installed sibling list is a valid checkpoint. Use deterministic
left-first depth-first traversal and at most4096 resolved nodes across a run;
step budgets range1–4096. The two limits are separately recorded. A total cap
retains the pending tree and returns capped, never complete. No crash consistency
or durable-store atomicity follows from an in-memory atomic logical update.

Request, full source/trust observations, original prepared domain and executed
method dependencies bind to externally expected identities. Every resumed
checkpoint needs an expected digest held outside it. Full structural verification
still rejects missing siblings, duplicate/misplaced pending paths, altered proofs,
wrong outcomes, forged counts or premature complete status even after a caller
recomputes a digest. Closed input fields and original six-revision scope remain.
The old request max_nodes is required to be4096 and denotes selected total scope;
per-step work budget is an execution argument, not a change to source assumptions.

Primary criterion: at each checkpoint, independently verified partition coverage,
counts, completed outcomes and supports agree with reconstruction. At completion,
the entire stripped original-format proof tree, outcomes and leaf supports match
uninterrupted saved exact results. Test budgets1/2/7/4096, strict boundaries,
unknowns, corrections, conflicts, retraction and private delivery. Correct partial
results expose known outcomes and pending domains separately. Identical known
outcomes do not prove the remaining domains cannot introduce new ones.

Promotion veto: missing partition cell, lost support, wrong proof, changed inputs,
wrong count, repeated completed work, false progress or premature completeness.
These require repair. Corrupt baseline or invalid comparator is a continuation
veto for affected runs. Correct pending or inconsistent results are expected;
counts/runtime are explanatory, not performance or production evidence.

Defaults: fixed DFS follows predecessor order for a discriminating equality test;
no scheduling superiority follows. The4096 cap/six-revision scope is inherited
finite scope, not a scalability claim. Pending nonemptiness remains unknown.
Exact rational certificates preserve strict bounds. Cheap diagnostic: root budget1
must yield all children, some pending, no full-family claim; repeated budget1 must
monotonically increase resolved-node count and preserve earlier certificates.

Audit passes: whole-tree equality is stricter than only matching selected outcomes;
complete complement partitions establish coverage, while witnesses alone do not.
Use an independent checker/outcome selector, not the producer's visitor. First a
small diagnostic; then at most three120second full runs. Protect accepted sources,
save checkpoints and manifests, do not rerun accepted evidence writers. No agents,
GPU, installation, probabilities, actual source admission, fees or publication.

Inspected cap refinement: an explicitly caller-selected execution cap from1 to4096 is separately bound in the checkpoint and independently expected on resume. The request max_nodes stays4096; a smaller execution cap changes only how much work is permitted, never the original temporal question. Test smaller caps to exercise genuine capped states cheaply. Counts/proofs remain exact. The checker also requires a DFS prefix, preventing rearranged completed work after an earlier pending node.
