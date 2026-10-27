# Pinned native loader source findings

18 October 2026. P16/P17/R06; MC01/02/04/05/23–25/27/30–35.

Ten exact-commit source files were successfully retrieved, with HTTP 200,
original response headers, complete curl responses and retained bytes. Thirty
inspected spans cover those files and already-retained caller/helper sources.
All 100 source/preservation checks pass and exact read-only replay succeeds.
Eighteen protected inputs, the current PDF, original R08 judgments and the
existing dirty-worktree/index state remain unchanged. No upstream code ran.

The proposed delta is
docs/design/proposal/architecture/native-loader-source-delta-v1.md. It supplies
source-grounded refinements to the completed offline prerequisite specification:

- Preserve retained bytes, selected archive/member bytes and parser text/bytes
  separately. Decoding and declaration stripping can change representation.
- Record recover=True, huge_tree=True and resolve_entities=False as explicit
  parser arguments, and retain syntax diagnostics. A tree alone is not clean
  XML validation. Other library defaults remain unverified.
- Cover schema-location discovery triggered by element-class lookup.
- Record repeated mapping stages and their distinct rules: FileSource first
  prefix, package longest prefix, disclosure exact file/first prefix.
- Preserve mapping-file xinclude and server-cache retrieval as configuration
  paths requiring disposition, without claiming this selected run entered them.
- Narrow the requested-state finding: Session clears global managers and the
  new command-line controller passes hasGui=False; persistent GUI configuration
  loading is not requested on that path. Effective runtime state stays pending.
- Keep percent-decoded fragments outside the earlier plain-fragment examples.

The claimed target is exact pinned source behavior at the inspected branches,
not installed execution. The checked quantities are file identities, response
status/size, source-span identity, Python syntax trees and explicit constructor
arguments. They support the stated source findings. They do not establish
native-library defaults, successful parsing, actual network behavior or
accounting validity. The source contains an encoding-order concern: FF FE
matches before FF FE 00 00 in XmlUtil.encoding. This follows directly from the
inspected branch order; downstream decoding consequences remain untested.

## Decision

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Deliver source delta | Exact commit retrieval, inspected call chain and 100 passing checks; replay agrees | No wrong source or protected-input change found | Library/build and effective runtime behavior unobserved | Use the delta to prepare original-byte/decoded-text examples on retained native resources | Runtime compatibility, no-network guarantee, XML/XBRL success or admission |
| Preserve twelve runtime lock duties | Source preparation advances four duties without inventing their runtime values | Missing runtime artifacts veto promotion only | Target/dependency/native builds, actual opens and terms remain unresolved | Continue documentary work; keep installations and execution held | Exact dependency lock or rights clearance |
| Continue proposal preparation | R06 evidence bound to unchanged candidate | No global continuation veto | Broader mission/acceptance gaps remain | Refresh controls and proceed to the next finite preparation unit | Whole-row or program completion |

No stochastic comparison or method ranking applies. Candidate rejection did
not occur: this was source preparation. The initial checker attempt found two
span endpoints one line beyond their source files; it stopped before writing
outputs. Endpoints were corrected to the actual inspected file ends, then
--record and read-only replay passed. No saved evidence was overwritten.

## Reproduction and challenge

source-manifest.json records the exact ten curl argument lists, trusted
permission context, response/header/body bindings and retrieval times. The
checker commands were python3 data/accounting-master/native-loader-source-20261018/check.py
--record (one rejected attempt and one success), followed by default replay.
The manifest identifies Python 3.11.15 in tfgpu, the exact Git commit and
approximately 0.034 seconds of check/record time. Only standard-library
AST/file/hash operations ran; no TensorFlow/Arelle import, GPU use or empirical
experiment. Author source-reading time was not measured.

Strongest alternative explanation: downstream helpers or effective
configuration change behavior relative to the inspected branch. The source
delta records that boundary, and no runtime acceptance follows. An observed
different stream, mapping or effective parser setting would require a new
receipt and affected-specification repair. The weakest evidence is exact
lxml/libxml2 behavior for an as-yet unselected build. More static counts cannot
settle that question.

Version 3.44 remains 396 pages and not_ready. All 53 obligations, six
interactions and 46 operations remain. Independent technical/domain/human
acceptance is pending. No manuscript rebuild, commit, installation, publication,
outreach or fees.
