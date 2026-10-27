# Safe changes to a declared policy domain

27 October 2026. MC03/05/11/12/13/18/24/25/26/28/33/34;
W03/04/11/12/13/16. Product implementation held; design evidence only.

Question: when an explicitly revised message declaration changes the total-rule
universe, which old known constraints can be transported without changing their
meaning? Baseline: ProspectivePartialPolicy/1 rejects changed-domain reuse.
Candidate: a separate checked relation, not permission to reuse an old result
unchanged. Retain external identities of both declarations, original inputs,
frontiers and outputs. The new policy result always answers the new question.

Skeptical audit: subset keys alone are insufficient. A reused label may now mean
a different observation, or a renamed first message may change second-stage
own-action keys. Nor does equal candidate count establish equivalent constraints.
Inspect exact action-key meaning and finite forbidden assignments. The smallest
safe first profile keeps the original source request and verified frontier
identical, maps old keys injectively into new keys, and requires each old known
forbidden assignment to map to an exactly corresponding new assignment. Additional
new constraints may eliminate more candidates. This verifies a syntactic finite
constraint relation, not empirical equivalence of messages or economic welfare.

Before implementation compare: exact label renaming with a bijection; conservative
addition of keys unreachable at the current frontier; new constraints in an
already declared domain; collapsed labels; changed action meaning; mixed old/new
second-stage keys; unknown-source, pending and over-budget states. Determine
which can fit the first relation. A merged-key case should be explicitly refused
unless a separately justified many-to-one relation is designed. Do not silently
raise the12-key ceiling to make a case pass.

Primary criterion: for accepted relations, enumerate new total rules and check
that their projection obeys the transported old constraints; where exact
constraint equivalence is declared, the projected set must equal the old set.
Compare whole bit-vector sets with an independent direct oracle. Retain pending,
unknown, inconsistent and budget statuses from a fresh new-domain calculation;
constraint transport never grants feasibility or source admission. Verify
rejection witnesses and unchanged old artifacts.

Diagnostics that veto promotion: unchecked semantic relabelling,missing or
noninjective key mapping,dropped constraints/support/pending records,misstated
projection equality or acceptance of a changed original request. A protected
baseline mismatch invalidates comparison; local candidate failures trigger
repair. Runtime/counts are explanatory. No scalable incremental solver,actual
actor knowledge,probability,optimality or general domain-extension theorem.

Defaults audit:12 binary keys/4096 rules remain inherited bounded comparison
scope,not universal defaults. Choose minimal renamed/extended fixtures from
original inputs before reading new full answers. An empty old constraint set
is a useful control but cannot be the only positive case. At least one accepted
relation must transport nonempty first- and second-stage restrictions. Independent
oracle is the exact baseline; stochastic rankings and heuristic strategy
comparisons do not apply to this finite set identity question.

Budget:at most three fresh CPU attempts,120seconds each,under
 data/accounting-master/policy-domain-transport-20261027/. These are inherited
resource limits,not result criteria. Save the audited relation specification
before execution,all inputs/expected sets,failures,source locks,manifest and
result/decision tables. No successful writer reruns,agents,GPU,installs,commits,
fees,outreach,publication or E3. Preserve live financing evidence work and all18
open packages. After success integrate only checked conclusions; no global
continuation veto has fired.

