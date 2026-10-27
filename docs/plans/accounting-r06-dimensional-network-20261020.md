# R06 — retained dimensional relationships and role transitions

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–07,
MC23–26, MC28–35. Predecessor: r06-numeric-accuracy-20261020.
Output: data/accounting-master/r06-dimensional-network-20261020/.

Research question: what dimensional relationships can be reconstructed from
the 27 retained resources, with exact endpoint identity, base-set separation,
equivalence, priority and target-role transitions preserved? This is the
prerequisite for checking the 231 explicit and four typed dimension occurrences
and fact-specific hypercube applicability. It does not itself validate a filing.

Comparator: the retained logical-URI/resource map and exact declaration IDs,
XBRL 2.1 corrected 2013 sections 3.5.3.9.7 and 4.10, Dimensions 1.0 corrected
2012 sections 2.2–2.7 and applicable embedded/retained schema declarations.
The completed enumeration inquiry's single-role simple-arc profile is an
insufficient comparator for the wider graph. Its 718 arcs are a selected subset
of the exploratory 1,085 domain-member arcs; those counts must not be conflated.

Evidence contract: bind every input resource; preserve every raw dimensional
arc and locator endpoint, including source element indices and raw attributes.
Resolve only retained exact URI/ID references; never fetch or execute upstream
code. Group by arc/link expanded names, arcrole and extended-link role.
Determine equivalence only for a documented schema-supported attribute profile;
use/priority/XLink attributes are exempt, order and other non-exempt attributes
are not. Preserve schema-default versus specification-default distinctions.
If a missing PSVI rule could change actual grouping, withhold that grouping
instead of claiming a generic XML Schema engine. One optional highest-priority
representative survives unless a highest-priority prohibition exists. Retain
every tied representative and record the deterministic local choice separately.

Resolve targetRole declarations/references and enumerate consecutive paths with
the correct role transitions. Check appropriate endpoint declaration categories,
directed-cycle constraints and global default uniqueness within the retained
set. Record unsupported cases rather than silently broadening the profile.
Use small authored cases to distinguish order-sensitive equivalence, lower-
priority prohibition, tied prohibition, role isolation, role switching and
unusable-parent traversal. These are deterministic source-rule checks, not an
empirical comparison or installed-validator certification.

Primary pass criterion: every retained dimensional arc has a source-bound
disposition and every admitted effective relationship/path is reconstructible
under the inspected rules. Source corruption, unresolved endpoints or unknown
attributes veto the affected admission. Broken preservation or uncontrolled
execution veto continuation. A source-network inconsistency is evidence for
repair, not a reason to stop independent work. Counts are explanatory only.
No financial-context mapping, whole-row closure, full PSVI/DTS/schema validity,
whole-fact dimensional validity, historical currency validity, runtime result,
or accounting compliance is concluded here.

| Choice | Provenance and reason | Failure mode / smallest diagnostic | Status |
| --- | --- | --- | --- |
| 27-resource boundary | Frozen offline map | Mistake retained graph for installed DTS; bind all resources and state limit | Documentary baseline |
| Endpoint IDs rather than QName alone | XBRL fragment-identity rule | Collapse distinct declarations; retain URI and ID alongside QName | Required identity |
| Typed attribute comparison | XBRL post-schema equivalence | Treat order 1 and 1.0 as different, or discard order entirely; schema/type fixtures | Restricted reconstruction |
| Highest optional tie by source identity | Source allows application-dependent choice | Imply a unique authoritative representative; retain tie set | Convenience choice |
| Role-directed traversal | Dimensions 2.4 | Union links across unrelated roles; explicit branch-switch witness | Required rule |
| Defaults do not add domain members | Dimensions 2.7 | Infer membership from default arc alone; preserve distinct networks | Required rule |

Skeptical audit: the initial global-reachability approach fails because retained
arcs include 135 priority=10 attributes and 16 targetRole attributes. The revised
plan first inspects equivalence, defaults and transition semantics; it does not
reuse the enumeration shortcut. Source/version identity and restricted attribute
coverage are checked before output admission. Remaining schema/installed claims
are explicitly withheld. Audit passes for this bounded prerequisite inquiry.

Pre-mortem: a successful parser could silently select a wrong role, equate
different-order arcs, conflate QName with identical fragments, or admit an absent
default into every domain. Authored counterexamples and full raw-to-effective
dispositions expose these risks. A missing imported resource would invalidate
only dependent relationships, not establish a defect in the filing.

Lifecycle: add local verifier, then --prepare once, construction once, --check
once and --record once; no-flag replay thereafter. Inherit predecessor protection
and completion bindings. Only the four live controls may advance. Add a separate
R08 supplement; preserve 3.44/396/not_ready, 53 obligations/six interactions/46
operations, zero whole-row closures, HEAD/index/empty staging and 36 dirty paths.
CPU-only standard library using CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. No acquisitions, installation,
upstream execution, empirical campaign, commit, outreach, publication or fees.
