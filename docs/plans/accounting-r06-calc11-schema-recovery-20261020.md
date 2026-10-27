# R06 — recover the Calculations1.1 publication schema

20 October 2026, Asia/Shanghai. P15/P16/P17/P19; MC01–07, MC24–26,
MC28–35. Output: data/accounting-master/r06-calc11-schema-recovery-20261020/.
Predecessor: completed r06-currency-history-20261020. The relevant comparator
is the completed r06-calculations11-source-20261020 source inquiry and its
preserved trusted connection timeout for the publication schema.

Question: can the exact AppendixA publication URL now be recovered, and do
its declarations agree with the explicitly non-normative appendix copy?
Use https://www.xbrl.org/2023/calculation-1.1.xsd exactly. AppendixA requires
publication-URL identity after XML Base/relative resolution; it does not treat
alternate host/scheme spellings as equivalent. Keep source identity, parsed
declaration equivalence, DTS discovery and installed conformance separate.

Evidence contract: retain the old failed receipt unchanged, preserve every new
response, inspect the complete small schema, and compare namespace-aware
declarations/attributes plus QName-valued usedOn. Exact-byte comparison and
namespace-aware comparison answer different questions. Primary success is a
source-bound recovery/identity account; successful acquisition does not prove
that an installed processor uses it or that a filing adopts Calculations1.1.
HTTP/body identity failure vetoes the dependent recovered-schema claim, not
independent work. Missing imports or unsupported syntax trigger a bounded
follow-up; do not fetch unknown dependencies automatically. Protected-state
mismatch, external-entity expansion or acquired-code execution veto continuation.

| Choice | Provenance / justification | Failure mode / earliest diagnostic | Status |
| --- | --- | --- | --- |
| Exact publication URL | Retained AppendixA, lines359–365 | Alternate URL mistaken for required reference; bind request and final URL | Source requirement |
| Non-normative appendix | Retained official corrected2024 recommendation | Treat convenience copy as normative before recovery; separate hashes and roles | Baseline only |
| Namespace-aware comparison | XML declaration semantics | Prefix spelling hides QName difference; expand element/attribute/usedOn names | Proposed finite diagnostic |
| Static inspection | Runtime remains held | XML parse mistaken for XSD/DTS conformance; explicit untested fields | Documentary scope |

Skeptical audit passes: this retries a specific transient source failure and
does not repeat completed interval examples. Premortem: an HTTP200 HTML error
or stale/mismatched schema could falsely appear to close the source duty.
Check response, root namespace, target namespace, complete declared content,
and source role before comparison. Do not infer history from retrieval time.
Preserve the separate unresolved5.4 duplicate-definition cross-reference and
all contextual calculations; schema recovery cannot correct normative prose.

Budget: one ordinary request, then one trusted retry only if sandbox/network
failure occurs; each <=2MiB,15-second connect/45-second total. A new redirect
or actual dependency requires a scoped addendum before adaptive work. No
installation, upstream execution, default change or empirical run.

CPU-only standard library: CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. Prepare once, successful
construction once, --check, --record once; then no-flag replay only. Four live
controls plus additive R08 may advance. Preserve3.44/396/not_ready,53/6/46,
zero whole-row closures,HEAD/index,36 tracked dirty paths and empty staging.
No runtime/controller,commit,outreach,publication or fees. Continue distinct
ready internal duties if this source remains inaccessible.
