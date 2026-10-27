# What prevents an AccDSL release

27 October 2026. Audit cutoff: Version 5.50, 827 main pages; simulation volume
261 total / 240 body pages. This is a release-readiness assessment, not release
approval. The working release is the governing scholarly design, simulation
volume and reproducible specification/evidence bundle. An executable product
and an empirically validated forecasting system require additional evidence.
The distinction does not remove any original mission requirement.

**The main bottleneck is now consolidation and acceptance, rather than manuscript
length.** Many valuable finite methods and examples exist. The live master still
leaves all 53 obligations, six interactions, 46 operations and 18 work packages
open. Adding another passing example does not decide whether an implementer can
follow one coherent specification or whether the evidence satisfies a complete
release condition. The next work should connect existing results, resolve the
few consequential unsupported joins, and make release decisions claim by claim.

## Baseline and what this audit actually checked

The audit began at 5.49. During the review the live work advanced to 5.50. The
previous snapshot is preserved; the delta adds recovery-source scope and an
unresolved-only intake. No earlier method was removed. The cutoff hashes are:

- Main PDF: fe85d4723605e5bdf1fb1602ffa957bf9bdc9f02a3bfa9f45f8719cd6111f795.
- Simulation PDF: 63fa2a2dc33c272ec31d0a842685cd3a52136977afd87a41592ca2ea261edee7.

The inventory covers all 277 recursively included TeX files, 43 chapter/appendix
nodes, 1,247 structural nodes and 446 lexical display-math nodes. The compiled PDF
independently contains 43 chapter bookmarks. There are 176 bibliography entries,
174 distinct cited keys and 939 citation occurrences; no missing keys, duplicate
bibliography keys, duplicate labels or unresolved TeX includes were found by this
structural check. These counts establish inventory coverage, not correctness.

All 18 package closure conditions and the current 53/6/46/9 obligation,
interaction, operation and literature records were inspected structurally.
Chapter openings, conclusions and selected scope statements were sampled across
all 43 chapters; release-critical sections were read more deeply. Five rendered
main-volume pages were inspected: physical pages 25, 166, 237, 267 and 632.
This was **not** a continuous 827-page technical reading, a new proof audit of
all equations, an independent accounting review, or a reproduction of all tests.
The machine reading record leaves those checks explicitly unperformed.


**Post-cutoff update:** the live draft advanced to Version 5.51 (828 main pages;
262 total / 241 simulation body pages) before this audit finished. Its new
insurance-stage section and integration result were read as a delta. They add two
stage-only issued/held cases; dates and separate group identities remain unknown,
and the existing fiscal adapter still does not accept those cases. R05/R06 thus
remain open, with a more precise next task: dated group identities, chronology,
a compatible opening and fiscal-report composition. The active plan is now the
acceptance-priority review. This note does not claim a fresh whole-candidate audit
of 5.51; the detailed inventory and hashes below remain bound to 5.50. See
[post-cutoff record](post-cutoff-drift.json) and
[5.51 result](../insurance-stage-integration-20261027/result.md).

Evidence files in this directory include baseline.json, candidate-drift.json,
inventory.json, structure.json, chapters.json, pages.json,
dependency-inventory.json, review-coverage.json and the requirement crosswalk.
The lexical inventory does not expand arbitrary TeX macros. Five pages without
visible clipping do not establish layout quality elsewhere.

## Ranked release gaps

Priority P0 means work needed to establish a trustworthy design-release boundary.
P1 means closure within that boundary before release. Product/empirical duties
remain open separately. An explicit unsupported result can satisfy only an
acceptance condition that actually permits it; it cannot waive a required method.

### R01 — One current release decision is missing (P0)

The historical mission and current package records preserve the goals, but they
do not supply a current release-specific acceptance decision for each one. The
requirements table still describes MC32 as Version 1.2 with 11 chapters and two
appendices. The live controller's compression_next_plan still points to the
coupon-resumption plan already integrated in 5.48. Several inherited obligation
next actions describe earlier conversion bridges despite later conversion and
control evidence. Historical entries should remain historical; active directions
must be reconciled with their successors.

The manuscript also uses “first release” for a complete source-to-history-to-
scenario workflow, while the validation chapter separates proposal completion
from subsequent implementation. Both are legitimate milestones, but they need
unambiguous names and different acceptance decisions.

**Finish when:** a current matrix preserves the exact original acceptance wording,
records the relevant release class, identifies supporting sources/fixtures and
remaining evidence, and assigns a reasoned disposition to every requirement.
Distinguish design-supported, design-blocked, explicitly unsupported within an
allowed profile, product-stage and empirical-stage obligations. Keep broad rows
open where necessary, but state which precise subcondition is missing. Every
active next-action field must resolve to unfinished work or a superseding record.

Evidence: [mission requirements](../../../docs/plans/accounting-mission-requirements.md),
[current package records](../gap-credit-recovery-refresh-20261027/closure-packages.json),
[cutoff controller](cutoff-v550/data/accounting-master/next-plan.json), and governing
chapters/01-purpose.tex:77 and chapters/10-validation.tex:275–304. The companion
[closure plan](../../../docs/plans/accounting-release-closure-20261027.md) builds
on the existing acceptance-priority plan rather than starting another competing
scientific queue.

### R02 — The manuscript needs a complete semantic and reader regression (P0)

Successive integrations preserve sources and inspect added pages, but the current
integration explicitly leaves whole-document acceptance pending. Preserving old
text can preserve old scope statements as well. In simulation/family-policies.tex:55,
saved partial frontiers remain future work; observation-binding.tex:40 describes
a resumable partition as an unresolved difficulty. The following section supplies
a scoped temporal-frontier method. The rendered page 143 makes this an intelligible
teaching transition locally. It is therefore a **scope/navigation ambiguity to
resolve**, not proof that the method is absent or that every such passage is wrong.
The release should say which earlier profile is being discussed and point to its
successor where readers otherwise infer a current global limitation.

A more concrete consistency issue appears in the repeated fixed/floating example.
Simulation chapter 1 defines alpha as the floating fraction and obtains 5+2alpha;
product chapter 27 defines alpha as the fixed fraction and obtains 7−2alpha.
Both calculations are correct locally. Reusing the symbol for complementary
quantities without an explicit cross-volume convention makes transfer error easy.
Use distinct symbols or an explicit reset and update connected examples.

**Finish when:** a protected successor has a section/equation/notation review map,
current versus historical profile statements, checked cross-references and a
coherent beginning-to-end argument. Investigate every changed or removed equation,
citation, qualification and finding. Read the connected prose, not only added
paragraphs; render and inspect both volumes. An independent reader and implementer
must then assess the exact candidate. Page count, compilation and author review
cannot substitute for that acceptance.

Evidence: [rendered review coverage](review-coverage.json), governing
simulation/01-observations.tex:11–16, chapters/01-purpose.tex:48–54,
simulation/family-policies.tex:14,55, simulation/observation-binding.tex:40,
simulation/temporal-frontier.tex:6–42, and
[5.50 integration result](../credit-recovery-integration-20261027/result.md).

### R03 — The distributed specification/evidence bundle is not self-contained (P0)

A concrete packaging defect is visible now. The governing source package contains
only core-0.lark under spec, but chapters/09-implementation.tex:293–295 and
chapters/11-contracts.tex:19 refer to spec/core-ir.schema.json and the historical
core-contract. Those files exist elsewhere under docs/design/spec and the archive;
they have not vanished from the repository. Their package-relative references are
unresolved for a recipient of the candidate source directory. The docs landing
page also says the source package includes LuaLaTeX build instructions, while no
README/build-instructions file was found in the 5.50 candidate root.

All inspected explicit repository-root paths in TeX exist locally. Of 323 literal
path occurrences, 162 do not resolve directly from the source directory; many
are contextual shorthand, not proven broken links. They need classification and
a dependency map rather than a claim of 162 defects. The compiled project's 285
local inputs are inside the candidate, so the PDF build's inputs and the wider
reproducibility bundle are different sets.

**Finish when:** one release manifest pins the normative schemas/contracts,
examples, reference programs, tests, source/claim records and external dependency
versions; each prose reference resolves from a documented root. Include build and
read-only verification commands, environment versions, expected semantic results,
checksums, known failures, and licensing/access dispositions. A clean staged copy
must rebuild both volumes and verify the declared reference suite without reading
undeclared workspace files or overwriting frozen results. Do not copy restricted
source material into a public bundle without an appropriate disposition.

Evidence: [dependency inventory](dependency-inventory.json), governing
chapters/09-implementation.tex:291–310, chapters/11-contracts.tex:19 and
[docs landing page](../../../docs/README.md). No clean-room reproduction was run
in this audit; the absence finding is scoped to the inspected candidate package.
The missing schema is expressly a historical Core 0 reference, not evidence that
all current portable schemas are absent. The release must identify its actual root
and preserve the version relationship.

### R04 — Local profiles do not yet establish one compatible implementation (P0/P1)

The project already has a typed IR, authoring examples, exact evaluators,
versioned exchanges, native-off comparisons and many negative tests. The missing
work is not “write a compiler from scratch.” The current W11 closure condition
still requires general compatible composition and cross-profile migration; W12
separately requires real transactional behavior. The portable operation appendix
explicitly describes specified exchanges rather than deployed endpoints.

**Finish when:** a release profile selects authoritative versions and describes
how source, actor information, history families, methods, numerical results,
financial state and reports compose. Supply complete lexical/type/error rules,
state and effect ownership, version compatibility and migration rules, resource
and incomplete-result semantics, and source→IR→state/report golden cases. A fresh
implementation exercise should expose any decision that still requires reading
private scripts or guessing. Existing finite profiles may remain separate when
incompatible, but their boundaries must be explicit. Real-store concurrency and
crash recovery are executable-product obligations; their contracts belong in the
design even while their implementation remains deferred.

Evidence: W11/W12; governing chapters/06-language.tex,
chapters/09-implementation.tex, chapters/17-portable-reference.tex:1–10 and
chapters/10-validation.tex:261–304. No finding here denies the existing bounded
reference execution.

### R05 — Consequential accounting and financing joins remain unresolved (P1)

Three current examples deserve focused closure rather than another generic demo:

- **Conversion into control:** checked issuer/creditor worksheets and finite
  transaction partitions do not yet establish measured acquisition allocation.
  The existing plan requires rights extinguished, transaction ordering, control
  and business assessment, separate consideration/settlement measurements, and
  complete paired/consolidated worksheets. A loan carrying-value plug, circular
  goodwill, omitted allowance or double settlement would invalidate the result.
- **Recovery after financial write-off:** Version 5.50 deliberately accepts only
  missing-evidence records with no financial effects. Its 239 assertions and
  50 controls do not establish a positive recovery method. Actual receipt,
  allocation, recognition, presentation and timing evidence are still required
  before that method can be admitted.
- **Insurance composition:** shared issued/held groups, changing treaty terms,
  estimates and termination need separately justified call chains and origin-
  preserving reports. The active plan correctly distinguishes changing an
  estimate from early termination; one supported case cannot admit the other.

Corporate, bank and insurance authority also needs dated applicability and
same-fact treatment comparisons for every promoted operation. A retained older
standard is not automatic evidence for a current jurisdiction/entity election.

**Finish when:** each operation claimed in the release has a full fact pattern,
applicable authority/derivation, explicit unsupported alternatives, independent
complete-state/journal/report expectations, and adverse composition tests. For an
unresolved operation, identify every dependent claim and ensure it remains
unavailable or conditional. Do not quietly defer a method explicitly required by
the original design acceptance; record the blocker and finish its internal work.

Evidence: [conversion allocation plan](../../../docs/plans/accounting-conversion-allocation-evidence-20261027.md),
[recovery intake result](../credit-recovery-intake-20261027/result.md),
governing simulation/credit-recovery.tex, and
[insurance audit plan](../../../docs/plans/accounting-insurance-shared-group-audit-20261027.md).
These are local evidence findings, not new accounting opinions or legal rulings.

### R06 — Real-company coverage and integrated adverse cases need acceptance evidence (P1)

There is already a connected Apple disclosure case; calling real-company work
absent would be wrong. There is also a large preserved report population. The
validation chapter nevertheless distinguishes 192 acquired report slots and
244 original versions from semantic closure. It records 136 unverified publication
dates, 56 filing-date metadata records, and 31 provisional annotations across four
reports used for development. These are manuscript/current-register statements;
this audit did not independently reacquire or adjudicate the corpus.

The failure register contains 67 original mechanisms, 48 literature extensions and
86 cross-interface challenges. Its own statuses explicitly avoid claiming runtime
coverage. A growing list is useful, but the release needs a failure-to-case-to-
result map for the supported profile. No finite list proves all possible failures
have been found.

**Finish when:** declared real annual/interim packages have complete reference-
frontier dispositions, exact source contexts and availability evidence where
required by the query, adjudicated critical facts/alternatives, and a reproducible
trace to joint histories and affected statements. Unknown real journals remain
unknown. Couple this with complete synthetic original/revised/failed-prefix cases
and an independently entered output oracle. Test hidden information, unjustified
weights, infeasible financing, invalid merges, unsupported accounting, partial
execution, rounding boundaries and changed versions at their actual joins. An
expected unresolved result is acceptable only where its contract permits it.

For a design release, this is inspectable case and specification evidence.
General extraction quality, population representativeness and forecasting accuracy
require separate later evaluation; do not impose full eight-year forecast testing
as an invented prerequisite for the manuscript.

Evidence: governing chapters/10-validation.tex:305–355;
[current failure register](../gap-credit-recovery-refresh-20261027/failure-register.json),
[requirement crosswalk](requirement-crosswalk.json), W01/W02/W16.

### R07 — Literature closure must follow actual claims, not citation counts (P1)

Bibliographic resolution is good, but it does not establish that all consequential
technical claims have inspected support. The six research ledgers coexist with
later versioned supplements. The release needs a single current index linking
claims to the relevant retained source/version/technical anchor and local transfer
argument, while preserving historical source records.

The current package queue retains Francis–Rowell technical-text access,
Gentry edition/appendix correspondence, Strebulaev conventions, available
Benzoni/Dewatripont and adapted-topology dependencies, modern inference and
competitor comparisons. The literature residual file also records ACTUS matched
runtime, authentic Duarte–Fonseca replication and TC-VAE published/preprint/code
correspondence. These are source-qualified unresolved entries, not a fresh
internet search or an assertion that no later source exists. Some older method
next steps have already been overtaken by subsequent financing work; reconcile
them against the current release before scheduling them.

**Finish when:** every consequential cited/imported claim has inspected technical
support or a complete local derivation, with premises and transfer limits. Every
named consequential competitor has a fair technical disposition. Every retained
access/edition gap has a dependent-claim decision. Acquired but unread material
stays internal reading work. An unavailable optional source need not block release
when no claim relies on its uninspected contents and adequate alternatives are
covered; a required unsupported argument does block. Assess official code where
available before adopting a method or claiming faithful reuse.

Evidence: [literature residuals](../literature-closure-20261026/remaining-work.md),
W14/W15, governing chapters/12-research.tex and the six ledgers under
../../../docs/design/research/. No claim of exhaustive literature discovery is made.

### R08 — Generality and computational limits need a defensible supported boundary (P1)

The project already answers the user's tree-explosion question in important
bounded settings: symbolic families, shared state, exact temporal partitions,
partial policies and resumable calculations preserve possibilities without one
materialized branch per world. Repeating that proposal would ignore completed work.
The remaining issue is knowing when a particular reduction remains correct and
how much of an actual query has been computed.

**Finish when:** each promoted transformation declares the query, horizon, actor
observations, policy class and state information it preserves; exact methods have
checked premises, and approximations identify their actual target and output-error
conditions. Changed evidence or policy must invalidate inappropriate reuse.
Numerical profiles specify roots, resets, rounding, strict bounds, infeasibility,
solver failure and resource exhaustion distinctly. Mixed/continuous extensions
remain unsupported where their premises are unproved. Do not imply a universal
compression theorem or calibrated probability law. Small finite tests establish
those finite tests; measured workload and scalable runtime belong to a subsequent
software evaluation. The chapter's 10,000 observations/64 cells/30-second limits
are explicitly provisional, not measured capacity.

Evidence: W03/W04/W13; governing simulation/08-compression.tex,
simulation/17-continuous-methods.tex and included successors;
chapters/10-validation.tex:367–386. Broad multi-period endogenous financing and
inference remain research obligations where stronger results are claimed.

### R09 — Independent acceptance has not occurred (P1, after internal closure)

The current release record explicitly leaves reader, domain and whole-document
acceptance pending. Author checks, hash preservation and assertion totals are
useful but cannot establish that another person can understand, implement and
critically assess the design.

**Finish when:** the exact release candidate receives separate recorded reviews
for narrative comprehension, implementability and promoted accounting/method claims;
findings are repaired and connected evidence rerun. Before any professional
referral, finish feasible internal research and prepare the proposed answer,
exact sources, competing interpretation and checked consequences. Ordinary reader
feedback need not be purchased. No outreach, engagement, fee, publication or
production deployment is authorized by this audit.

Evidence: MC32–35, W17/W18,
[internal-before-expert policy](../../../docs/design/review/internal-before-expert.md),
[5.50 integration result](../credit-recovery-integration-20261027/result.md).
Human acceptance being pending does not stop the internal R01–R08 work.

## What can remain later, and what cannot

A truthful design release can retain clearly bounded unsupported algorithms,
optional adapters, unimplemented storage/concurrency, unmeasured performance and
unevaluated forecasts where the original acceptance condition permits that stage.
It must still define the intended contracts and preserve those obligations.
It cannot ship broken normative references, incompatible meanings, unsupported
promoted accounting/math claims, invented real-company facts, hidden assumptions,
or an assertion that independent acceptance already happened.

The shortest defensible route is: **current release matrix and bundle inventory →
common specification and high-impact evidence joins → integrated cases and
claim/source reconciliation → full manuscript regression → isolated reproduction →
independent acceptance.** Source work, case preparation and dependency packaging
can proceed independently after their scope is fixed. Finish these deliverables
before expanding the manuscript merely to increase coverage counts.

## Decision and limits

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept this as a bounded release-gap audit | Every current package/requirement has a source-preserving release mapping and concrete closure route | No release approval; current gaps remain | Full technical/independent acceptance still unperformed | Execute the audited closure plan in staged units | All pages read, all proofs checked, all literature exhausted, or product readiness |
| Keep 5.50 not_ready | Current acceptance record and concrete R01–R09 findings | Broken packaging references and unresolved release evidence prevent promotion | Which broad rows can close after reconciliation | Decide against exact original acceptance wording | Every open broad row lacks useful evidence |

No stochastic comparison was performed and no method ranking is supported.
The strongest alternative explanation for apparent missing work is that its
support exists in a later or separately versioned record. R01 therefore requires
successor reconciliation before reimplementation. The weakest part of this audit
is global mathematical/source verification: inventory and focused reading cannot
replace that work. Later source changes require a delta review, not silent reuse
of this cutoff's acceptance status.
