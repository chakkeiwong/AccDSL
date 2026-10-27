# Bounded P18 integration review

Scope accepted as stated: manuscript argument, requirements and acceptance exposition only; P16/P17 are baselines; retained domain/source gaps are not new failures.

## Findings

**F1 (material) — Disconnected implementation sequence, `10-validation.tex`, §"Decisions and replaceable assumptions".**
The paragraph states "The proposed dependency order begins with portable records, review/time selection and durable receipts, then typed authoring, admitted history templates and connected corporate methods. The implementation stages below are a design sequence…". Two defects: (a) the milestone table (P0–P6) is *above* this paragraph, not below; (b) its vocabulary ("portable records", "durable receipts", "admitted history templates", "connected corporate methods") does not appear anywhere in the P0–P6 deliverables ("evidence registry, contextual types, versioned IR, exact posting engine…"). A reader is given two dependency orders that are never reconciled. Repair: either map each phrase onto a named stage (e.g. "portable records/receipts = P0 evidence registry and replay; typed authoring = P2 Core 0 frontend; admitted history templates = P1 bridges; connected corporate methods = P2–P3 corporate package") or delete the second ordering and fix "below" → "above". This is the only blocking item.

**F2 (minor, nonblocking) — Review-cycle residue presented as manuscript content, `10-validation.tex` §"Concrete conformance…" and §"Workload limits…", `12-research.tex` §"Companion records and status".**
"The present repair supplies a richer design candidate", "The repair adds Mack's reserving paper…", "The retained panel now contains…", "Every one of the 179 unique candidates … now has…". A product proposal reader has no referent for "the repair" or the implied prior state; the wording describes editing history, not the specification. Repair: replace with stative phrasing ("This version supplies…", "The research library includes Mack…", "The retained panel contains…"). The script name `check_repair_conformance.py` may stay since it is a literal file reference.

**F3 (minor, nonblocking) — Corpus arithmetic not taught, `10-validation.tex` §"Concrete conformance and corpus protocol".**
"192 target annual/interim reports … across nine issuers … eight consecutive complete years per issuer" does not divide evenly (192/9 ≠ integer) and is reconcilable only if issuers have different interim cadences (e.g. three quarterly filers × 32 + six semi-annual filers × 16 = 192). The counts 136 + 56 = 192 and 244 ≥ 192 are internally consistent. Repair: add one sentence giving the per-issuer report mix so the total is derivable; otherwise the count reads as unverifiable. Not labelled an error — the number may be correct.

**F4 (minor, nonblocking) — Duplicated baseline prescription, `10-validation.tex` §"Forecasting evaluation comes later".**
Paragraph 1 ("comparator ladder … naive, contractual runoff, tuned classical, structural, extensions") and paragraph 4 ("Baselines should include a naive persistence or ratio model, a tuned conventional financial model, the structural model with a single selected interpretation, and the same model preserving alternatives") specify overlapping but not identical ladders; the second adds the single-interpretation vs. alternatives split absent from the first. Repair: merge into one ladder so a later experiment plan has one normative list.

**F5 (minor, nonblocking) — Forward reference out of the literature chapter, `03-literature.tex` §"Accounting structure…".**
"AccDSL's event and counterparty records are specified and justified directly below" — nothing below in that chapter does so; the specification is in later chapters. Repair: "in Chapters~\ref{ch:math}–\ref{ch:execution}" or equivalent.

**F6 (minor, nonblocking) — Boundary of "render inspection", `12-research.tex` §"Companion records and status".**
The chapter states companion records cover "rendered-page inspection". The packet treats render inspection as separate from this review; the sentence is acceptable only if that record exists independently. Repair: none required for this packet; note that this review does not confirm it.

## Checks that passed

- Readiness language is consistently hedged: title page ("not a completed product or a claim of full proposal readiness"), Ch. 10 opening ("do not constitute a production implementation"), "No such forecast experiment has been run", "The present document runs only deterministic checks of its own examples". No unearned readiness claim found.
- Source boundaries: Ch. 3 and Ch. 12 agree on blocked candidates (McCarthy, Imieliński–Lipski, Caiani), on version discrepancies (Doshi 2024, Mernik 2003 report, Giacomini–Kitagawa 2020 WP, Docling/Auer, Libkin DOI), and on the 2 October 2026 freeze; 25 + 7 = 32 PDFs; six ledgers enumerated = six. Search-provenance is frozen as required.
- Test coverage: T01–T18 are each assigned to exactly one stage (P0: T01–T04, T09, T17; P1: T05–T10, T14, T18; P2: T11–T13; P3: T15; P4: T16). T05/T06 agree with eq. (1) in Ch. 1 (5, 7, $7-2\alpha$).
- Ch. 1 requirements R1–R10 are matched by Ch. 4 responsibilities and Ch. 10 veto conditions (source span, entity/unit/period/basis, invented evidence, hidden financing, dropped branch, cash reconciliation).
- Retained gaps (ASC access, ASBE 1 verification, actuarial/regulatory data, human review, 136 unverified publication dates) are stated at the operations they affect and are not treated as closed.

## Verdict reason

The integration is sound in its claims, boundaries and counts; the single material defect is that the manuscript now carries two unreconciled implementation sequences with a misdirected pointer, which is precisely the "disconnected implementation sequence" failure class. F2–F6 are editorial and nonblocking.

VERDICT: REVISE
