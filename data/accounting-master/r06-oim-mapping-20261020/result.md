# Retained xBRL-XML compatibility and OIM dimension mapping

20 October 2026. The twelve xBRL-XML §2.1 constraints are supported within
this retained instance and its inspected declaration profile. All 1,127 fact
occurrences have proposed OIM dimension signatures. The resulting 1,043 classes
have exactly the same memberships as the frozen XML identity partition:
70 duplicate classes, 154 occurrences and 101 pairs. No occurrence is removed.
This finite agreement is checked, not assumed from matching class counts.

The direct source contains one schemaRef, 193 contexts, seven units and 1,127
root-level facts. All 382 used concepts are declared in the item substitution
group; 52 type nodes have checked direct base references. No tuple, fraction
ancestry, footnote resource, footnote arc/link, instance linkbaseRef, roleRef,
arcroleRef, precision attribute or non-root xml:base occurs. Both link:footnote
and the xbrli:footnote spelling in §2.1.10 are absent. Thus this report requires
neither a new note fact nor generated fact IDs. This does not implement general
footnote effectivity, XHTML serialization or schemaRef-only DTS discovery.

Root xml:lang=en-US applies in scope throughout the instance. OIM's text
classification admits language for 112 facts; it is absent on 963 numeric and
52 other non-text facts. In particular, enumeration sets derive through the
DTR noLangToken type and must not acquire a language dimension. The equality
representation lowercases the language to en-us while the source spelling
remains recorded. All 33 numeric facts using the single xbrli:pure measure omit
the unit dimension. Other measures preserve numerator/denominator multiplicity.

Date-only ends/instants map to the following midnight and starts to the same
day's midnight; all independent boundaries agree with the prior period evidence.
No timezone is invented. Four direct xs:date typed occurrences preserve their
canonical dates, distinct from QName explicit members. Only reported taxonomy
dimensions enter identity; no taxonomy defaults are inserted. Reported source
values remain independently bound candidate values, not full OIM value objects.
Two nil numeric facts have no OIM decimals property in this proposal.

The checks comprise 2,347 counted assertions, 39 deterministic fixtures,
24 source anchors and 41 direct input bindings. They cover exact partition
membership, type-dependent language, unit multiplicity, finite date boundaries,
source structure and preservation. They do not establish generic conformance.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain proposed finite dimension mapping | All occurrences covered; both partitions exactly equal | No observed unsupported structure; protection passes | Full schema/DTS/value validation remains absent | Audit conditional numeric Calculations 1.1 arithmetic prerequisites | Complete OIM report or installed processor validity |
| Preserve numeric duplicates | All original members retained | No deduplication or value substitution | Issuer measurement/rounding policy unknown | Compare optional whole-report rounding modes separately | Accounting error or adoption of Calculations 1.1 |
| Keep wider mapping work explicit | Finite absence of note/reference cases documented | General functions unimplemented | XHTML/DTR, arbitrary types/IDs/links | Continue independent source/design work | Whole-row closure or manuscript acceptance |

The strongest alternative explanation for partition agreement is that the
actual data lack language/container collisions that would expose a generic
mapper defect. Fixtures distinguish some such cases; they do not eliminate
that limitation. A source or declaration mismatch would overturn the finite
claim. The weakest evidence is still full validation/installed correspondence,
not the observed partition membership. Candidate 3.44 remains 396 pages and
not_ready, with 53 obligations, six interactions, 46 operations and zero rows
closed. This unit contains no stochastic comparison or method ranking.
