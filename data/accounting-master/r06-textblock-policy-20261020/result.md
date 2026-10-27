# Text-block validation and content preservation

20 October 2026. The pinned Arelle text-block check applies a filing profile
and changes a temporary validation string. It does not establish generic DTR
or XHTML validity, and that string cannot replace the original disclosure.
All 101 checks pass: 30 static findings, ten authored/source-bound witnesses,
14 distinct duties, 15 passage anchors and 22 direct input bindings. Four
bounded source acquisitions returned HTTP 200. No upstream code or DTD ran.

The DTR Structure 1.1 document linked by the retained OIM source is the
17 January 2018 Candidate Recommendation. Its sections 5–6 locate definitions
in schema documentation and distinguish DTR support from base-specification
support. It supplies no general textBlockItemType fragment-validation
algorithm. The retained 2020/2022 type annotations still govern the separate
semantic inquiry; this older structural document is not asserted to be current.

At Arelle commit 01f6a4656c2c6551d2f05f31c9d74366d133ee7e,
ValidateFilingText.py lines 524–533 select xhtml1-strict-ix.dtd for inline
documents and edbody.dtd otherwise, from the runtime configuration directory.
Lines 551–692 select facts using nil spelling, concept type and a markup
pattern; they validate the original value and additional CDATA captures.
The inline wrapper adds a div inside body. Additional link, image, active
content and nested-table checks exceed DTD validation. Actual caller activation,
configuration and parser behavior have not been established.

The transformation at line 549 deletes named entities and escapes remaining
ampersands. On the explicit witness R&amp;D it produces RD, whereas normal
fragment parsing preserves R&D. On R&#38;D its projection parses as the literal
R&#38;D. Quotation and encoded-markup witnesses also change. These are exact
consequences of an authored ASCII-name subset on the listed strings, not an
execution of the upstream regex library. A validation projection may be
intentional; treating it as a lossless adapter value would be wrong.

Fact f-684 preserves source XML R&amp;amp;D and decoded stored text R&amp;D;
fragment parsing yields R&D. Applying the inspected transformation to that
literal conditionally gives RD. Equality with the actual runtime f.value
remains untested. The finding does not show that the issuer's fact is invalid
or that Arelle replaces its stored original value.

The edbody DTD describes an EDGAR-specific modification. Its body accepts
mixed Flow content; the inline DTD's body accepts Block content, with the
added div accepting Flow. Both name three external entity dependencies that
were not acquired in this unit. Selected DTD portions were inspected, not a
complete conformance review. All 56 previously parsed fragments remain XML
structure evidence only: 9,884 elements, 12,518 attributes and 941,509 UTF-8
bytes under the earlier neutral wrapper. Empty namespaces under that wrapper
are not by themselves a generic XHTML invalidity verdict.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Preserve original and validation projection separately | Exact source branch and explicit counterexamples | No source/protection veto | Actual runtime value and selection | Trace caller and configuration; retain both values | Lossless projection or issuer invalidity |
| Separate profile checks from DTR/XHTML semantics | DTD identity, wrapper and DTR status inspected | Missing dependencies veto full validation only | Applicable profile and parser environment | Acquire the named entities and inspect the caller source | Generic validity or current filing compliance |
| Continue internal reuse preparation | 101 checks pass with scoped evidence | No continuation veto | Full schema/DTS, runtime and build identities remain open | Complete the next bounded source duty | Whole-row closure or installed readiness |

The strongest alternative explanation is that the transformation is suitable
for the validator's limited structural purpose. That does not rescue a
content-preservation claim. A verified upstream accessor/caller showing a
different input would change the real-fact consequence, not these conditional
witnesses. Source-to-runtime correspondence is the weakest evidence.

The current adapter manuscript already preserves source values and leaves
validation pending; this inquiry exposes no contradiction requiring a rebuild.
Version 3.44 remains 396 pages and not_ready, with all 53 obligations, six
interactions and 46 operations preserved and zero whole-row closures.
