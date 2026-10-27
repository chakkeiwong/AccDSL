# R06 — four retained typed-dimension date values

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–06, MC23–26, MC28–35.
Output: data/accounting-master/r06-typed-domain-dates-20261020/.

Question: do the four retained typedMember values identify the declared typed
dimension/domain element, and what does their exact xs:date declaration support?
The retained shape inventory preserved these four subtrees while leaving
typed-domain interpretation unknown. Contexts c-58–c-61 carry four dates under
the remaining-performance-obligation timing axis; eight fact occurrences use
those contexts. The completed period inquiry concerns different XML elements.

Evidence contract: use the exact retained instance, packet, portable evidence,
27-resource map, actual global axis/domain declarations, Dimensions 1.0 with
2012 corrections and XSD 1.0 Second Edition. No new acquisition. Check the
axis QName using each element's namespace scope; locate its unique abstract
dimension declaration and nonempty typedDomainRef; resolve the observed
same-document fragment to a unique nonabstract global element; compare each
single child to that declaration and inspect its type/facets. For the observed
direct xs:date type, derive the four positive date values without assigning
timezone or applying XBRL period endpoint shifts.

Primary criterion: four source-bound typed values and eight fact-context joins,
with exact source/portable subtree preservation and separate typed date
interpretations. Single-child/name/type/source/calendar checks are vetoes for
their local records. Other dimensions, hypercube applicability, default-member
rules, full XML Schema validity and installed DTS membership remain separate;
passing this inquiry cannot establish dimensional validity of the facts.

Research intent: the mechanism tested is exact declaration/reference/value
correspondence. Expected failures are converting a typed value to an explicit
member QName, accepting any valid date under the wrong child name, dropping the
date subtree, borrowing the preceding XBRL instant/end-date +1 rule, or calling
a retained resource map the installed DTS. A failed match triggers repair or
outside-scope status; it is not automatically evidence against the filing or
research direction. Protected-state change and uncontrolled execution veto
continuation.

| Choice | Provenance / reason | Failure mode / diagnostic | Status |
| --- | --- | --- | --- |
| Per-element namespace scopes | XML source helper already retains them | Prefix rebinding or invented namespace; fixture uses equivalent prefix and an altered URI | Required source identity |
| Same-document bare fragment resolver | Exact observed typedDomainRef | Generic URI/XML Base behavior implied; guard reference form and absence of XML Base | Finite convenience profile |
| Direct xs:date interpretation | Must be confirmed on the actual domain declaration | Period endpoint shift incorrectly transferred; same token interpreted in both roles as a discriminator | Hypothesis until declaration inspection |
| Non-nil, attribute-free, simple child | Actual observed subtrees | Nillable declaration mistaken for observed nil, or xsi:type silently ignored; changed cases return outside_scope | Finite local profile |
| Unknown member QName and financial time | Frozen portable proposal | New documentary evidence overwrites original candidate status | Preserve exact original records |

Skeptical audit passes for this narrow source question. A complete context
validity claim would be unsound without the dimensional relationship networks;
the task explicitly leaves that claim unmade. Typed domains are XML element
instances, not explicit-member reachability. End/instant boundary shifts apply
to xbrli period elements, not every element whose local name includes Date.
The smallest discriminator is a valid date under an incorrect domain child.

Construct four interpretations, exact declarations, context/fact joins, fixtures,
source and six literature ledgers, result/review, manifest and additive R08
supplement. One-time prepare/construct/check/record; no-argument replay only
after completion. Edit only four live controls. Preserve3.44/396/not_ready,
53/6/46,zero whole-row closures,the36 dirty paths,HEAD/index and empty staging.

Environment: CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B; standard library only.
Predecessor: r06-context-periods-20261020. No upstream runtime, installation,
empirical campaign, commit, publication, outreach or fees.
