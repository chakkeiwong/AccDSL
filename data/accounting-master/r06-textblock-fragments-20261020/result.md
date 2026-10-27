# Retained text blocks: XML structure and source preservation

All 56 retained text-block strings pass the declared local XML fragment
diagnostic. They contain 9,884 elements and 12,518 attributes. Ordered character
content agrees between an explicit ElementTree node/text/tail traversal and
direct Expat callbacks. The original escaped source, decoded Text values and
full-validation flags remain unchanged. This establishes finite structural
correspondence, not XHTML conformance or displayed financial meaning.

The selected strings contain 941,509 UTF-8 bytes; f-415 is largest at 130,498
bytes. The element inventory is 329 div, 2,564 span, 57 table, 6,283 td, 599 tr
and 52 br. All elements have empty expanded-name namespaces under a wrapper
that supplies none. Seventeen fragments begin with plain text, including
f-349's “Summary of Significant Accounting Policies”. The tree contains 53
nonempty tail-text slots and no comments or processing instructions. Those
facts explain why keeping only each element's text or requiring one top-level
element would be insufficient. Fixture comments and processing instructions
are nevertheless preserved explicitly.

The tax disclosure f-684 provides a real entity example. The filing contains
`R&amp;amp;D`, its decoded Text value contains `R&amp;D`, and parsing the embedded
fragment produces the character content `R&D`. The stored Text value is not
rewritten. An additional unescape before fragment parsing instead produces a
bare ampersand and rejection. Separate fixtures show that unescaping encoded
angle brackets can invent an element where the source represented literal
text. Line-ending and attribute-normalization fixtures distinguish other
legitimate XML parsing changes from accidental data loss.

Both retained DTR versions state that escapedItemType alone does not require
well-formed unescaped content; xmlNodesItemType adds a sequence of XML text and
well-formed nodes; textBlockItemType adds simple string/XHTML-fragment/mixed
content. The XML document grammar requires one root, while the content grammar
allows the sequence used by this diagnostic. A synthetic wrapper therefore
serves only that content check. It does not supply a schema, XHTML namespace,
doctype, external entities or presentation context.

The acquired XHTML 1.0 Second Edition specifies whole-document conformance,
including its root, namespace and DTD conditions. The retained DTR annotation
does not select this edition or a complete fragment-conformance procedure.
Applying those whole-document conditions directly to these fragments would
be unsupported. Empty namespace is an observed property, not a finding that
the DTR values are invalid. No DTD/schema, CSS, script, browser, renderer or
upstream package executes. A non-XHTML tag passes the local structural fixture,
demonstrating the remaining semantic distinction.

## Evidence and decision

The unit binds two acquired primary documents, three request attempts, sixteen
technical/edition anchors and seventeen input files. The failed XHTML sandbox
request and successful trusted retry both have receipts. Readable views omit
explicit inline-hidden content while preserving original HTML.

The one-time check reports 297 assertions, 29 fixtures, four rejected source
corruptions and six distinguished fragment alterations. Source guards also
check every selected instance byte slice, concept, attributes, decoded content,
packet value and portable value. Node records preserve text/tails and attributes;
ordered tokens preserve their logical position. XML attribute order has no
semantic significance, but the original spelling and encounter-order records
remain available. No stochastic ranking or performance measurement is made.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept finite structural account | 56/56 bound source records and extraction agreement | Source/hash/order checks pass; declared controls reject or differ | Both extraction paths use Expat 2.7.5 | Retain additive evidence and reconcile the remaining R03–R06 queue | Independent parser certification |
| Keep broader content acceptance open | XML structure supported within local profile | Full XHTML/schema/XBRL validation not run | Edition/context, DTR fragment duties and installed validator behavior | Source-supported fragment policy and later separately authorised runtime checks | Full DTR or XHTML validity |
| Preserve proposal status | No confirmed manuscript contradiction found | Protected-state check passes | Independent/domain/human acceptance and other mission obligations remain | Continue independent preparation | Whole-row closure or implementation readiness |

The claimed local target is the XML-normalized ordered content of the exact
stored fragment, and that is what both extraction paths compute. Literal
fragment spelling, display text and financial interpretation are different
quantities and remain separately stored or unevaluated. Rejections of DTD,
declaration and unknown-entity fixtures are local-profile outcomes; they do not
establish that every such input is invalid under a richer DTR processing policy.

The checker was run once with:

    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-textblock-fragments-20261020/build_records.py
    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-textblock-fragments-20261020/verify.py --check

The run manifest records lifecycle commands and elapsed wall time, including
the interruption/recovery interval; it is not a runtime benchmark. Its held
runtime action and checks.json runtime_execution=false refer to the proposed
installed/upstream integration, not this executed standard-library diagnostic.
GPU devices were intentionally hidden. No random seed applies.

## Post-run challenge

The strongest alternative explanation for agreement is shared parser behavior.
The two paths are independent traversals, not independent parsers. Literal
fixtures expose extraction and decoding mistakes but cannot establish full
XML conformance. A source mismatch, lost tail, altered namespace or differing
event order would overturn the corresponding local record. A source-supported
XHTML fragment policy or installed validation result could change the broader
content verdict without invalidating these preserved observations.

This result rejects neither the filing nor the research direction. No
continuation veto fired. Version 3.44 remains 396 pages and not_ready; all
53 obligations, six interactions and 46 operations remain, with zero whole-row
closures. The separate R08 supplement adds evidence only.
