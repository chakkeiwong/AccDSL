# Author review of typed-domain correspondence

The pre-run audit isolated typed-domain identity from both explicit-member
reachability and XBRL period boundaries. The inspected Dimensions source
explicitly requires the referenced element, and its corrected-content erratum
supports the wrong-child discriminator. Both the axis and domain declarations
are retained with exact source anchors and parsed attribute agreement.

All four selected subtrees and their eight fact joins pass. The selected
schema has no XML Base; the reference is a bare same-document ID and uniquely
resolves to a global nonabstract xs:date element. Actual values have no child
attributes, xsi:nil or xsi:type. Attribute-bearing/nil fixtures return
outside_scope instead of silently applying incomplete semantics. A nillable
declaration does not mean an observed value is nil.

The date interpreter is the completed bounded source helper, checked against
Gregorian calendar arithmetic. No XBRL end-date shift is applied. The comparison
with the preceding period interpreter is explanatory evidence that type and
XML role matter; it is not a proposed transformation of typed dates.

The local fixture set distinguishes namespace identity, alternate prefixes,
wrong child/axis, cardinality, mixed text, nil/type attributes and invalid
calendar values. Ten altered declaration profiles are refused. Per-element
namespace scopes are used in the source and fixture parsing; the original
portable axis names, raw subtrees, member Unknowns and financial-time Unknowns
remain intact.

A pre-construction shape inspection found that the documentary packet names
its field financial_time, while the portable Context calls it time. The guard
was corrected before construction. No frozen records changed.

Full dimensional correctness remains untested: correctly typed values alone
do not establish valid hypercube use. Retained-map membership is not installed
DTS membership. No manuscript contradiction was identified. This is author
review only, and independent/domain/human acceptance remains pending.
