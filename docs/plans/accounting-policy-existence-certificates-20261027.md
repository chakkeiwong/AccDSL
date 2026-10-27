# Decide common-policy existence beyond full enumeration

27 October 2026. MC03/05/10/12/13/18/24/25/26/28/33/34;
W01/03/11/12/13/16. Predecessor: revised-source-actor-messages attempt 02.

Research intent: can the exact supplied two-stage pay/draw restrictions be
decided beyond twelve message keys without enumerating all total policies?
Mechanism: each refused first action forbids one Boolean assignment; each refused
second action forbids a pair. Thus the exact rule-existence question is 2-CNF.
This observation changes the requested output from population enumeration to
existence plus a checkable certificate. It does not change source selection,
world assumptions, observation keys, actions or refusal conditions.

Skeptical audit: no counts, probabilities or utility ranking can follow from a
satisfying assignment. A contradiction in the resolved subset can refute a
common rule for that subset, but unresolved contexts preclude full-family
feasibility. No-world and inconsistent-clock cases are unassessed. Domains must
remain prospective, with exact first-message and action memory. Keep original
12-key results unchanged; use a separately identified existence profile.

Derivation: forbidding (x_i=a) is the clause x_i!=a; forbidding (x_i=a and x_j=b)
is (x_i!=a or x_j!=b). The latter gives implications (i,a)->(j,1-b) and
(j,b)->(i,1-a). Unary clauses give (i,a)->(i,1-a). A satisfying total rule is a
certificate checked directly against every retained refused row. An unsatisfiable
certificate contains one literal and explicit implication paths to its opposite
and back, each edge justified by an original refused row. No external theorem
is needed to verify that such a cycle makes either truth assignment impossible.
The candidate uses strongly connected components only to find certificates.

Promotion criterion: every assessed saved context has a certificate verified
against independently reconstructed rows/keys. On <=12-key complete domains,
existence must agree with the entire protected population. For larger domains,
certificate validity is primary; the selected witness is not called optimal or
representative. Cross-check all small authored Boolean formulas exhaustively,
including tautological, unary, contradictory, unused-key and binary-cycle cases.
Controls alter clauses, witness bits, paths, edge sources, source supports,
conclusion scope and external identities. Invalid row reconstruction, bad source
locks, oracle disagreement or a false accepted certificate veto this increment.
Local implementation failure triggers a bounded repair; an actual unsatisfiable
candidate triggers information/model diagnosis, not a halt to the research.

Default audit: prospective 30/38/54-key domains come from the preceding declared
interfaces. A 64-key execution ceiling is a convenience resource bound covering
the observed maximum, not a product limit. Maximum 10,000 selected rows and
20,000 implication edges are protective hypotheses; report overflow explicitly.
Two Boolean actions and at most two keys per refusal are checked prerequisites.
No default change, probability, prediction, actual source admission or empirical
performance claim. Runtime only explains workload.

At most three fresh 120-second CPU attempts, GPU hidden, no new dependencies.
Contract and authored expectations before execution. Store source locks,
certificates, controls, manifest and result under
data/accounting-master/policy-existence-certificates-20261027/.
After successful comparison, integrate the message and existence companions in
a bounded manuscript addition and refresh the master. All 18 packages stay open;
financing evidence continues separately, S6 held and E3 deferred.
