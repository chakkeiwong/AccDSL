# Cumulative Chapter 2/source-support crosswalk

10 October 2026. E01/C03/C08; MC01–05/08/10–16/18–20/25/28/30/32–35;
G4–7/G11/G13–18. Author preparation only; readiness remains `not_ready`.

## Question and bounded unit

The question is whether the retained Apple source claims and queries already
have reader-facing mechanisms in the current Chapter 2, “A complete company
and a real disclosure”, or whether a distinct missing bridge must be added.
The target reader is a technically prepared accounting/modeling reader who
must be able to explain why a reported Apple amount or risk assertion does not
identify the economic exposure, what conditional state would preserve it, and
which facts remain required before a journal or scenario result is allowed.
The bounded unit is the complete rendered Chapter 2, PDF pages 11–41 (printed
pages 4–34), read in six-page ordered slices, plus the source-support mapping
for all retained Apple claim/query ledgers. The canonical TeX is
`docs/design/proposal/manuscript-quality-inventory-20261010/chapters/13-reference-company.tex`
and its included Apple section files; the canonical PDF is Version 2.23 with
SHA256 `bd252760c16bf1f3aa3c46cb5b1b496c4e1ac9105483f8ce1235b3252e7c0659`.

The crosswalk may identify a repair, but it does not authorize a claim of
semantic completeness, accounting compliance, forecast validity or
independent/human acceptance. Source assertions, author interpretations,
assumptions and unresolved queries remain separate.

## Evidence contract

| Field | Contract |
| --- | --- |
| Scientific/engineering question | Does current Chapter 2 explain the retained source mechanisms and their limits, or is a distinct reader-facing bridge absent? |
| Baseline/comparator | Unedited Version 2.23 Chapter 2 and its bound TeX/PDF hashes; each ledger's retained source claims and queries are the comparator population. |
| Primary criterion | Every retained claim/query family receives a claim-level disposition: supported by an existing section, duplicate/covered by a broader mechanism, source-only with a justified boundary, or genuine missing bridge. |
| Promotion vetoes | Wrong PDF/TeX hash, omitted ledger, source/query collapse, filing-order duplication presented as explanation, or an inferred fact/probability/treatment not in the retained evidence. |
| Continuation vetoes | Corrupt source ledger, unresolvable canonical page/section boundary, or a reader-facing defect whose repair cannot be stated without changing the source boundary. A source-only unresolved fact is not a continuation veto. |
| Explanatory diagnostics | Keyword candidates, counts, section names, extracted text, page images and surface warnings. They nominate review; they do not establish support or semantic acceptance. |
| Non-conclusions | The crosswalk will not establish whole-filing completeness, actual Apple contracts/events, operative law, publication-date validity, probability weights, accounting compliance, forecast accuracy or product readiness. |
| Preserving artifact | `data/accounting-master/chapter2-source-crosswalk-20261010/` containing the manifest, ledger inventory, claim/query crosswalk, ordered rendered-slice records, result, and any bounded TeX/PDF repair evidence. |

## Skeptical/default audit

The plan passes the pre-run audit subject to the following controls:

* A heading or keyword match is only a candidate. Support is accepted only
  after reading the relevant paragraph and the section's transition in the
  rendered Chapter 2.
* The latest Item 1A retention unit is source-retention evidence, not semantic
  acceptance. Its 34 claims and 20 queries remain distinct from earlier Apple
  note ledgers; all ledgers are inventoried by path and hash before mapping.
* Filing-order summaries are a known wrong baseline for reader support. The
  comparator is the mechanism-bearing Chapter 2 argument, including sections
  that already cover ecosystem dependence, disruption, competition,
  regulation, legal exposure, channels, FX, financing, tax and uncertainty.
* No source assertion will be upgraded to an incident, operative rule,
  probability, loss, elasticity, contract term, journal or forecast. Missing
  facts remain explicit query dispositions.
* A crosswalk row is not a promotion criterion for the product. It can justify
  a local repair or a source-only disposition; it cannot certify readability,
  mathematical correctness or domain acceptance.

| Choice/provenance/status | Justification | Failure and earliest diagnostic |
| --- | --- | --- |
| Version 2.23 PDF and included TeX | Current checkpoint and final source-unit manifest | SHA256 and live TeX/PDF comparison before reading |
| All `claim-query-ledger.json` and `source-claim-supplement.json` under `data/accounting-master` | These are the retained claim/query populations; source supplements without a claim ledger are still inventoried separately | Path/hash inventory and explicit excluded disposition |
| Mechanism section rather than filing order | The reader needs the economic relation and missing dependency, not a catalogue of Item 1A headings | Manual section read and duplicate-coverage check |
| Six-page PDF slices | Required bounded scholarly-readability unit | Page-range and ordered entry/exit records; no contact sheet counted as reading |
| No manuscript edit unless a distinct bridge is found | Avoid duplicating source coverage or changing a supported candidate without evidence | Claim-level disposition and local interruption test |

## Pre-mortem and next actions

The crosswalk could pass while a reader still cannot connect a risk to a
state variable, because a broad section label may conceal an abrupt transition.
The ordered rendered read and local interruption records distinguish that
failure. It could also fail because a source query needs actual contracts or
authority rather than prose; that is a source boundary and should remain open,
not be repaired with invented assumptions. It could appear complete because
all claims map to generic uncertainty language; the row must name the concrete
mechanism and the section paragraph that carries it.

Run the bounded inventory and claim/query crosswalk, then read PDF pages
11–16, 17–22, 23–28, 29–34, 35–40 and 41 in order. If a genuine bridge is
missing, write the smallest source-faithful TeX repair, compile a new candidate,
and perform the local interruption and slice regression. If no genuine bridge
is missing, keep Version 2.23 unchanged and record the source-only decision.
Update the live continuation requirements and master checkpoint only after the
result and hashes are written. Continue E01/E07/E08/E14 queues after this unit;
do not repeat the closed E05 comparison or failed acquisition route.

## Diagnostic revision before acceptance

The first generated mapping is rejected as semantic evidence. Its 281 rows
mix source spans, headings and explicit claims, omit the nested legal assertions
and the eight revenue queries in `revenue-history.json`, and assign coverage
from the source directory alone. Those choices violate the primary criterion.
Preserve that attempt. The replacement must enumerate JSON-pointer identities,
keep raw source support separate from explicit claim assertions, include the
nested legal assertions and all standalone query providers in the declared
Apple units, and assign no automatic coverage verdict. Author dispositions
must name exact manuscript paragraphs or explicitly retain source-only detail.
This is an implementation repair, not evidence against the representation.

The scope is the nineteen completed Apple source units, their five claim/query
ledgers and standalone query files. Insurance and literature units are outside
this Chapter 2 audit and are not silently claimed as included. Input file
hashes and the final prior manifest must verify before accepting any result.
The stale filename `chapters/02-history.tex` is rendered Chapter 3; Chapter 2
is `chapters/13-reference-company.tex`, as confirmed by the TeX input order.

Cold-reader questions, frozen before prose changes:

1. What can Northstar's aggregate bridges identify, and why does the interest
   split still produce jointly different future statements?
2. Why do Apple's revenue, purchase obligations and liquid-resource balances
   fail to identify receipts, delivery or spendable funds?
3. What do regional totals tell us about products, entities and facilities,
   and where do the conditional witnesses stop?
4. Which legal/operating changes can affect revenue without being a booked
   loss, and which dated facts would permit a financial calculation?
5. After supply, product transition and quality are represented, which
   nonphysical dependencies remain needed to sell or deliver a service?
6. Can a reader reach the historical-record chapter without relying on
   explanations that actually appear much later in the book?

Answer these against the rendered sequence, including adverse answers. A false
backward reference or a necessary missing dependence triggers a bounded repair;
an unquantified fact by itself does not justify another filing-order section.

## Diagnosis accepted for bounded author repair

The ordered 31-page diagnosis and 82 explicit disposition groups now cover 502
identified records from 25 files: 130 explicit assertions, 164 queries and 208
retained source records. These are different record kinds, not 502 independent
claims. Source-only dispositions retain later-method calculations and missing
facts. They do not assert Chapter 2 support or exhaustive semantic abstraction.
All 877 preceding manifest references verify; the four live pointers and the
rejected first attempt are preserved before any candidate change.

The repair is Version 2.24 in `manuscript-service-access-20261010`: three
misleading backward references plus a short concluding subsection on continuing
service access. The preceding quality/inventory example establishes usable
physical output; the new subsection asks whether the company still has the
rights, third-party support and data/payment access required to offer a service.
Apple's licence risk is printed page 9, developer/content risks page 10 and
data/payment rules page 15. These are attributed issuer assertions. The local
example compares explicitly assumed continuation and expiry of a content
agreement. It infers no actual event, legal requirement, probability, price,
revenue amount or journal. Developer continuation is explained as a separate
economic choice; a capacity estimate cannot substitute for it.

Keep every existing display and bibliography entry byte-for-byte. Make only
the necessary title-version change, three paragraph references and the added
subsection. Compile with the existing LuaLaTeX command, inspect changed pages,
and reread the complete Chapter 2 in ordered slices of at most six pages. Read
the Chapter 3 transition as a boundary check. Stop candidate acceptance for a
source mismatch, removed qualification, unresolved reference or material render
defect; fix it within this bounded scope before proceeding. Human/independent
acceptance remains pending, and the wider internal work continues afterwards.

## Final execution record

The 167-page Version 2.24 repairs the three references and adds the service
bridge. The complete Chapter 2 was read in six ordered slices; after a
one-word carryover repair, final pages 41–42 were reread and final pages 11–40
verified pixel-identical to the pages already read. Final navigation and
Chapter 3 opening were also inspected. All 33 candidate/crosswalk/preservation
checks pass. The rejected initial mapping and a final-checker archive-path
defect remain preserved with diagnoses. Five factual queries remain unresolved;
no candidate failure or continuation veto prevents the next E14 source unit.
See the unit's result, author review, source boundary and final run manifest.
