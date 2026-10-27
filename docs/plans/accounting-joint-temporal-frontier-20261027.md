# Resume a joint two-decision source search without changing its policy question

27 October2026. MC01/03/05/11/12/13/18/24/25/26/28/33/34;
W01/03/04/11/12/13/16. Design evidence only;product implementation held.

Question:can the shared-clock joint partition pause/resume with complete pending
coverage,andcan its known selected pairs restrict afixed prospective joint-stage
policy universe without hindsight? Baselines:JointTwoDecisionSourceViews/1,
JointStagePolicy/1,andthe earlier single-date resumable frontier. Reuse semantics,
not saved fields whose stage indices mean something different.

Skeptical audit:copying single-date source heads loses cross-date correlations.
The successor orders pairs(stage,source head) overthe same original variables;
reconstruct each pending cell's constraints fromits complete joint path. A node
expands into all first-failed-guard children before pausing. Preserve both stage
eligibility maps,known joint outcomes,all support paths andpending domains.
Counterpart complete evaluator/checker is protected. Compare final exact tree,
outcomes andsupports with that baseline underseveral step sizes. Counts alone
are insufficient. An interrupted write isnot crash-safe storage;state only pure
logical continuation andsave successful checkpoints externally.

Before execution define fixed-domain partial-policy semantics:verify frontier;
derive domain fromoriginal registry;maponly fully selected joint pairs;retain
unresolved pairs andpending cells. Known constraints can eliminate allrules before
completion;surviving rules cannot establish universal feasibility withpending
orunresolved sources. Contradictory clocks are notan empty feasible family.
Keepdomain andtemporal budgets separate. Changing declarations invalidates result
identity;do notimplement arbitrary domain transport duringthis increment.

Primary criterion:independent reconstruction ofevery checked partition,exact
final trees/supports understep sizes1 and7 anduninterrupted4096,monotone known-rule
sets inafixed domain,andcomplete endpoint policy equality withprotected binding.
Include strict boundaries,between-date correction,correlated interval,unknown
access,retraction/conflict,inconsistent clocks andexecution cap2. Alteration
controls:dropchild/pending/support,change stage orfirst outcome,false complete,
reusechanged input/domain,wrong refusal witness andfalse feasible status.

Defaults:step1 exposes every finite prefix;step7 isaconvenience different grouping,
notafaster schedule claim. Existing4096-node/12-key limits arebounded scope;
refuse/retain larger cases. Numericrows andsynthetic source clocks areprotected
comparison assumptions. Exact finite proofs need nostochastic ranking. Runtime
andcounts explanatory. Start withbaseline/between diagnostic,then bounded full
comparison;no successful writer reruns.

Atmost3 fresh120-second CPU attempts under
 data/accounting-master/joint-temporal-frontier-20261027/. Save contract,source
locks,expected outputs,checkpoints,manifest,failures anddecision/inference tables.
Corrupt baseline invalidates affectedcomparison;candidatefailure triggersrepair.
No agents,GPU,installs,commits,fees,outreach,publication orE3. Preservefinance
allocation evidenceplan andall18 openpackages. Noactual actoraccess,probability,
general-horizon,scalability,durable-storage orproduction claim.

