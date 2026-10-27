# R6: static dependency and field-preservation preparation

The retained Arelle commit remains01f6a4656c2c6551d2f05f31c9d74366d133ee7e.
It requires Python>=3.10,15 base requirements and three build ranges.
No optional extra is selected. The retained pdfplumber commit remains
4c64b92d5caccd71c645e98e0fabb0c4dba7ff45, whose newly acquired setup.py,
requirements.txt, version and licence identify version0.11.10. The attempted
pyproject.toml returned404; setup.py actually reads requirements.txt. No
downloaded Python was executed.

The PDF dependencies are pdfminer.six==20260107, Pillow>=12.2.0 and
pypdfium2>=5.9.0. Arelle's Pillow>=10,<13 intersects the PDF requirement at
>=12.2.0,<13. This nonempty declaration intersection proves neither a resolver
solution nor runtime compatibility. pdfplumber's setup.py says Python>=3.8,
but pinned pdfminer requires>=3.10; the declared combined minimum is therefore
at least3.10. README tested-version lists and packaging minima are different
evidence and neither selects the target platform.

Exact pdfminer release metadata adds charset-normalizer>=2.0.0 and
cryptography>=36.0.0; Pillow is optional under its image extra. That extra is
not selected here, although pdfplumber requires Pillow independently. Inspected
Pillow12.2.0 and pypdfium2 5.9.0 metadata are lower-bound witnesses only, not
chosen runtime versions. Pillow's declared dependencies are extras in that
metadata; pypdfium2's Python requires_dist is absent. Neither observation removes
native-library, wheel/platform, build or licence dependencies. Its metadata
expressly names dependency licences. No solver or package installer ran.

The graph records exact inspected edges and marks each unresolved range's
transitive closure as an open frontier. A complete lock still needs actual
platform/Python, wheel or build identities/hashes, recursively selected versions,
native libraries/notices and compatibility evidence. Source metadata availability
is not a reason to choose unreviewed latest packages.

| Preserved item | Required adapter behavior | Failure/fallback |
|---|---|---|
| Original document and occurrence | Keep source hash, raw token/bytes, locator and immutable document edition | Missing bytes invalidate dependent facts; retain unresolved source record |
| XBRL concept/context/dimensions | Preserve QName, entity, period, unit, explicit and typed dimensions, precision and nil | A formatted value alone cannot replace context. Unsupported typed/content relation remains raw and unresolved |
| Footnotes, duplicates and conflicts | Preserve occurrence IDs and all differing evidence before selection | Never use fact deduplication as a silent accounting-conflict resolution |
| PDF glyphs/coordinates/order | Retain page/bbox, original character runs and extraction settings alongside table reading | Ambiguous column/reading order falls back to displayed source/manual review; no guessed financial fact |
| Missing tables or image text | Account for every declared source unit and explain unresolved content | Deterministic geometry does not imply OCR capability or complete narrative extraction |
| Joined bank/insurance events | Preserve legal entity, profile, dates, unit scale and component ownership | No alias-based profile conversion or notional-capital injection; J1 refusal semantics apply |
| Cancellation/replay | Bind output to source/config identity and publish only complete accepted exchange | Preserve failure; no stale partial output may appear as a completed run |

Terms remain component-specific. pdfplumber's newly inspected MIT notice
requires retention of its copyright/permission text with covered copies.
This does not cover the dependency collection. Retained xbrldt-2005.xsd has its
own copying/explanatory-work notice; core instance/XLink headers merely point
to XBRL legal terms. FASB/SRT, SEC, issuer and XBRL resources remain separate.
The prior guessed software-notice URL's404 is not evidence of absent rights.
Additional official-specification discovery is recorded separately. Nothing here
authorizes distribution or supplies a blanket legal conclusion.
