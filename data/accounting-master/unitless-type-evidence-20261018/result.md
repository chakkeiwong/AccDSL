# Retained type evidence for seven unitless digit strings

18 October 2026. P16/P17/R06; MC01–06/23–25/27/28/30–35.

All seven instance QNames join unique retained element declarations and inspected
simple-content derivation chains. The 63 source/preservation checks pass; eight
corrupted variants reject. Source excerpts preserve exact byte/line spans,
restriction facets and shared nonnumeric attribute groups. This is declaration
evidence only; no XSD/XBRL validation ran and frozen portable Values stay Unknown.

| Source facts | Retained declared type | Inspected base chain |
| --- | --- | --- |
| Fiscal-year focus f-57; maturity-range years f-934/f-935 | xbrli:gYearItemType | Extension of XML Schema gYear with nonNumericItemAttrs |
| CIK f-59 | dei:centralIndexKeyItemType | Restriction of xbrli:tokenItemType with ten repeated [0-9] pattern terms, then extension of XML Schema token |
| ZIP f-13 and area code f-14 | xbrli:normalizedStringItemType | Extension of XML Schema normalizedString with nonNumericItemAttrs |
| Auditor firm ID f-1127 | dei:nonemptySequenceNumberItemType | Restriction of xbrli:tokenItemType with pattern [1-9][0-9]*, then extension of XML Schema token |

DEI element anchors are lines 167/188/234/238/318 of retained import-09-trusted.body;
issuer maturity declarations are lines 539–540 of the archived extension. Exact
excerpts and hashes are in declarations.json. The CIK token 0000320193 is retained,
including leading zeros. Shared nonNumericItemAttrs refers to itemAttrs, which
requires contextRef and inherits factAttrs; factAttrs supplies optional id and
lax other-namespace attributes. This source structure supports preserving the
tokens instead of treating every digit string as an arithmetic quantity.

The retained XBRL instance schema header explicitly calls its copy non-normative
and asserts identity to normative Appendix A. That asserted equivalence was not
independently verified. Built-in names are terminal references here; complete
XML Schema lexical/value-space semantics and validation were not reconstructed.
The inquiry does not claim that matching a local regex validates a fact.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Deliver seven declaration chains | Unique expanded-QName joins, complete inspected explicit bases/facets and exact source anchors pass | Eight wrong-type/base/token/false-validation cases reject | Built-in semantics and full schema validation unexecuted; retained copy status qualified | Preserve source-supported type evidence separately; investigate remaining declaration coverage without changing frozen Values | Validated PSVI values, accounting types or financial admission |
| Correct operational replay | New read-only verifier checks all real bindings and the archive schema's exact bytes | One optional acquisition receipt is absent, not a corrupt source | Original check.py replay assumes every receipt is a dictionary | Use verify_replay.py and completion.py; preserve original recording/manifest | Invented acquisition receipt or silently repaired historical result |
| Keep not_ready | Additive internal preparation only | No global continuation veto | Twelve runtime duties and wider methods/acceptance remain open | Reconcile ready source work and held runtime duties | Whole-row/program completion |

The one-time recording succeeded. Its default replay then failed on a null
acquisition_receipt for the issuer schema, which is archive-backed and separately
hash-bound. The source checks were not at fault. verify_replay.py explicitly
requires exactly that one absent receipt, verifies its source hash and all 79
real bindings, and reproduces the 63 checks/eight rejections. Original check.py,
checks and manifest are preserved. Do not rerun --record or rewrite them.

Post-run red-team: terminal built-in naming is not complete semantic validation;
an alternative retained definition or missed derivation would invalidate a join.
Exact unique QName matches and every inspected base/facet are bound, with no
claim of legal/current standards or historical publication availability. No
stochastic comparison applies. Only standard-library CPU source checks ran;
no network, upstream importer, numerical framework, GPU, installation or
empirical run. Manuscript 3.44/396 pages/not_ready is unchanged.
