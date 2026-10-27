# Retained fact-concept declaration coverage

18 October 2026. P16/P17/R06/R08; MC01–06/23–25/27/28/30–35.

All 1,127 retained fact occurrences join 382 unique global element declarations
in the 22 retained schema roots. Their explicitly declared type paths resolve
through 52 nodes to XML Schema namespace references. No concept join or fact
type path remains unresolved in this source set. The 4,253 source/preservation
checks and thirteen structural fixtures pass. No XSD/XBRL validation ran.

Exact declaration and type excerpts retain source hashes, byte and line spans,
restriction/extension syntax, facets, attribute references and annotations.
QName attributes use each element's namespace scope. Independent Expat byte
spans agree with ElementTree's root-child names/attributes. Local declarations
cannot satisfy global joins; repeated facts remain separate occurrences.
The fixtures check prefix rebinding/restoration, local/global distinction,
duplicate declarations, quoted greater-than characters, union/list edges,
base-attribute scope, cycles, missing/inline types, unbound prefixes and DTD
rejection. These checks concern source interpretation, not schema validity.

The lexical translator's frozen Values are preserved:

| Terminal source reference | Frozen portable tag | Occurrences |
| --- | --- | ---: |
| decimal | Decimal | 958 |
| integer | Decimal | 3 |
| decimal | Nil | 2 |
| gYear; normalizedString; token | Unknown | 3; 2; 2 |
| boolean; date; duration; gMonthDay | Text | 14; 1; 17; 1 |
| normalizedString; string; token | Text | 23; 77; 24 |

This cross-tab explains candidate representation. In particular, the three
integer-terminal facts retain Decimal candidate tags, boolean-terminal facts
retain unvalidated text, and the seven unitless tokens retain Unknown Values.
A terminal reference alone does not establish lexical membership, normalized
values, inherited constraints, units, financial meaning or accounting types.
No change to these frozen Values is justified by this inquiry.

The seven previously inspected unitless declaration/type-terminal joins agree
with the full-set result. Their evidence and corrected replay are preserved.
The retained XBRL schema labels its copy non-normative and asserts identity
to normative Appendix A; that equivalence remains unverified.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Deliver full retained declaration coverage | 1,127 ordered occurrences, 382 unique explicit declarations and complete source-bound type paths | All 4,253 checks/thirteen fixtures pass; protected hashes match | This retained source graph is not a schema validator or admitted taxonomy | Preserve coverage.json and add its R08 evidence | Validated PSVI values, lexical membership, complete taxonomy semantics or financial admission |
| Preserve candidate representations | All 961 Decimal/two Nil/157 Text/seven Unknown Values unchanged | No automatic promotion from type names | Source-declared type and candidate representation have different roles | Keep declaration evidence beside the candidate; require a separate reviewed conversion/validation protocol for value changes | New registered schemas, source sanitization or installed compatibility |
| Keep runtime and acceptance held | Twelve original runtime duties/nulls and exact 3.44/R08 files preserved | No global continuation veto; missing installed evidence still vetoes its dependent claims | Exact target/dependency/build identities, validation and independent acceptance remain open | Continue a separate ready master-program workstream rather than repeat completed R06 extraction | Whole-row closure or program completion |

The exact recording command, Python executable, Git commit, index hash,
protected input bindings and wall time are in run-manifest.json. Only
standard-library CPU XML/JSON/hash operations ran; no network, GPU, resolver,
installation, upstream package or empirical execution. No stochastic comparison
or ranking applies. Default completion replay is read-only.

Post-run red-team: source names can resolve cleanly while the filing violates
a lexical, dimensional, calculation or other XBRL requirement. Such a result
would not contradict this narrowly defined declaration-coverage result.
A wrong scoped QName, changed source excerpt or missed global ambiguity would
overturn an affected join. The type graph retains restrictions and exact text
so subsequent validation cannot silently discard them.

Version 3.44 remains 396 pages and not_ready. All 53 obligations, six
interactions and 46 operation rows remain; independent technical/domain/human
acceptance is pending. Unrelated dirty files and the Git index are preserved.
