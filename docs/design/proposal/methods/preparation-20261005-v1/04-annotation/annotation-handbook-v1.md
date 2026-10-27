# Annotation handbook for the located development pilot

The unit of annotation is an occurrence in retained source bytes. A number in a
statement and the same number in a note remain two occurrences. An interpretation
may link them as the same reported assertion after comparing entity, perimeter,
concept, dimensions, period, currency, unit, scale, sign, precision and basis.
Neither equal values nor a successful parser establish that equivalence.

The 31 provisional records in `labels-v1.json` use the frozen corpus exchange
schema copied here. `occurrence-index-v1.json` carries proposed additional
locator and time information without altering that schema or choosing a product
API. These are development labels written and inspected by the supervising
agent. They are not gold labels or independently adjudicated financial truth.

## Reading and locating a unit

1. Verify the original SHA256 against `selection.json`. For PDFs, use physical
   page numbers starting at one. Keep printed page labels separately; the
   selected HSBC/Munich pages differ by two and Midea by one. Rectangles use
   PDF points from the top left and include page dimensions. Match the rendered
   row and column, not a search hit in the contents table.
2. Transcribe visible content before normalizing it. Preserve brackets, dashes,
   thousands separators, footnote markers and language. For inline HTML retain
   the original element ID, attributes, context and unit definitions. Record
   library transformations separately from the source values.
3. Identify row, year column, statement perimeter and units before assigning a
   reading. Support spans are occurrences too. The sidecar references their IDs;
   null fields mean unknown or not applicable at this selected span, and do not
   authorize a convenient default. Field state and support are provisional.
4. Keep source statements separate from local consequences. A source's assertion
   of IFRS or ASBE compliance is evidence about its stated reporting basis; this
   pilot does not audit compliance. Exact decimal arithmetic on reported numbers
   is not evidence that the underlying amounts are unrounded or true.
5. Retain a span even when it cannot yet be read. Empty `readings` and an explicit
   question are the correct representation for the parent-interest dash, an
   unclosed note reference or undecomposed footnote group. Do not convert these
   into zero, discard them, or count them as semantically completed content.

## Context and source conventions

The Apple quarter ends 28 December 2024 but is fiscal FY2025 Q1. The source
duration begins 29 September 2024. Its instant context says 28 December 2024;
an XBRL library's exclusive midnight endpoint can be 29 December without changing
that source date. Revenue f-58 and f-279 have the same c-1/unit/value attributes
but occur in the statement and Note 2, respectively. Their proposed alias must
not become two independent likelihood contributions.

HSBC's interest figures are consolidated, in millions of US dollars. The $m
header obtains its currency meaning from Note 1.1(d). Parentheses indicate a
negative presentation of expense; they do not specify a journal debit or credit.
Footnotes 1–3 matter to what interest income and expense include. The retained
footnote span is not yet a full set of interpreted component assertions.

Munich Re explicitly states EU-adopted IFRS with additional HGB requirements.
Preserve that wording. Values are rounded million euros; the note warns that
totals can deviate. The visible 60,830 and –1,666 have defective extracted comma
characters in this PDF. Store the visible transcription and the extracted string,
with a reason for the difference. Never globally replace arbitrary unknown
characters with commas. The reported reinsurance subtotal of –1,181 survives
even though the displayed components sum to –1,180.

Midea's four columns distinguish consolidated 2024, restated consolidated 2023,
parent 2024 and parent 2023. 营业收入 (revenue) is a component of 营业总收入 (total
operating revenue); interest and fees have separate rows. The current group
revenue is 407,149,600 thousand RMB and parent revenue is 946,607 thousand RMB.
The restated 2023 figure remains qualified as a revised comparative. The original
2023 version and restatement causes have not been compared in this packet.

## Time, references and review

Only Apple's regulator filing-date metadata is verified here: 31 January 2025,
from the retained SEC submission record for accession 0000320193-25-000008.
That date does not establish that the exact retained bytes were public then.
HSBC, Munich Re and Midea publication dates remain unverified. Acquisition,
annotation and report-period dates must not fill those fields.

Apple Note 1 incorporates the FY2024 annual statements and notes. A matching
report exists in the accepted corpus, but its presence does not close that
semantic frontier. Midea's group/parent revenue-note references also remain
open annotation work. A full package inventory must account for every referenced
unit, record why a target is relevant and identify any unavailable material.

A second annotator should receive the original bytes and selected units without
the candidate readings, then compare literals, locations, context, qualification
scope and unresolved status. Adjudication must record the disagreement, proposed
readings, consulted sources, resolution and affected IDs. Retain alternatives
when the source cannot decide. Corrected labels append a version and supersession
link; preserve the original occurrence and prior review event. The present
supervisor/adapter consistency review does not replace blind annotation.

## Evaluation use and exposure

All four reports are exposed development data. This is a purposive sample with
no inclusion probabilities. It contains no OCR-only scan, sector-complete package,
full incorporated-reference closure or historical byte-vintage evaluation.
Keep report revisions, incorporated evidence and issuer histories together for a
static split, or use a reviewed temporal protocol that explicitly controls what
was public and which bytes were available. Never score this pilot as heldout.

Evaluate transcription, original-location resolution, context fields, table
structure, assertion mapping, source support and unresolved-frontier handling
separately. Location resolution can pass while the reading is wrong. A parser
that omits hard units must not improve its score by changing the denominator.
Record both selected-unit inventory and exclusions; abstentions retain their
reasons. Any future performance/default decision needs its own predeclared
criteria and unseen/adjudicated evaluation evidence.
