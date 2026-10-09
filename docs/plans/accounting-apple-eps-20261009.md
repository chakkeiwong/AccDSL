# Apple earnings per share, repurchases and employee awards

9 October 2026. Authorised E01/C03/C08 proposal preparation. This bounded unit
addresses MC01–05/07–12/19–20/28/30/32–35 and G1/G4/G5/G7/G11/G13/G15/G16.
Baseline: closed 141-page Version 2.10; Git checkpoint `47afa90`. Full proposal
readiness remains `not_ready`; product implementation and the old controller
remain held. The user's requested commit is complete; preserve unrelated work.

## Question, population and evidence contract

What do reported earnings, weighted-average shares, closing shares, repurchases
and employee awards identify about ownership through time? Read all of annual
Notes 3/10/11 and interim Notes 3/7/8, with the linked operating, balance-sheet,
equity and cash-flow rows, fiscal calendar, unit headings and compensation
policy. Record each complete note and every material narrative disposition;
supporting statements are retained in context but only declared rows are
formalised. Award contracts appended to the annual text are outside this
population; actual award terms remain unresolved. No acquisition is required.

Comparator: Version 2.10 and explicit shortcuts substituting closing shares for
weighted shares, treating total repurchases as a dated history, equating shares
vested less withheld with all net issuance, or equating purchase narratives,
equity charges and cash settlements. Primary pass: faithful source/context
mapping, checked ratios and movement identities, and a useful counterexample
showing what timing remains unidentified even after the weighted average is
known. Every numerical example must distinguish displayed source amounts from
authored assumptions. Source/check counts and compilation are explanatory only.

Wrong units/dates/signs, invented award terms or causes of cash/equity differences,
invalid arithmetic and presenting authored schedules as actual Apple histories
veto the affected claim. A failed shortcut triggers the next reconciliation or
counterexample, not rejection of the filing or research direction. Corrupt
sources or a mathematically invalid model stop dependent work until repaired.
No complete history family, probability, actual transaction chronology, full
ASC 260/718 implementation, accounting compliance or independent acceptance is
claimed. This is deterministic source and mathematical work, not a statistical
comparison or product implementation.

Artifacts: `data/accounting-master/apple-eps-20261009/`; separate candidate
`docs/design/proposal/manuscript-eps-20261009/`, Version 2.11. Preserve both
original sources, the preceding unit and four live pointers before updating.

## Skeptical audit and default/assumption audit

The baseline separates closing and weighted shares conceptually but lacks the
source-backed timing example. Screening found shares in thousands alongside
income in millions and EPS in dollars. Annual Note 11 and interim Note 8 are
necessary to interpret dilution; an EPS-only reading would omit known scope.
Fiscal 2024 has 52 weeks, so a 364-day teaching model is a proposed convention
to verify, not a calendar-year default. Fiscal 2023 has a different length.
Neither the rounded purchase narrative nor the authorised repurchase capacity
identifies cash paid, an obligation, or dated purchases. These distinctions are
required before arithmetic. The revised bounded plan passes this audit because
it tests the exact targets and keeps causes and actual histories unresolved.

| Choice and provenance | Status / justification | Failure mode / early check |
| --- | --- | --- |
| Retained annual PDF and interim HTML | Pinned source versions | Wrong comparative or source extraction: hash, date/unit headings, original PDF and DOM checks |
| Six complete notes plus explicit dependencies | Reviewed bounded population | Missing dilution/settlement qualifiers: partition entire notes and read all narrative before calculations |
| Income millions × 1,000 / shares thousands | Source-unit conversion | Thousandfold error or dated denominator: verify all five reported periods and both EPS ratios |
| Two-decimal EPS compatibility | Conditional nearest-rounding convention; tie rule unverified | False exactness: keep displayed centres and rounding envelope; avoid exact claims about undisclosed amounts |
| Ordinary integer shares, piecewise-constant 364-day model | Authored hypothesis for non-identification | Off-by-one or false chronology: explicit elapsed-day convention, exact rational arithmetic, independent day-by-day sum |
| Aggregate net issuance as one event; two repurchase events | Deliberately simplified witness construction | Mistaking net issuance for RSU vesting or legal transaction scope: label model, omit splits/other share movements, do not estimate Apple dates |
| Equity, cash and award movement arithmetic | Reported targets kept separate | Invented residual causes: retain differences without assigning tax, fees or unsettled trades |
| Existing Python/PDF/HTML/LuaLaTeX tools | Convenience tooling; no new dependencies | Successful extraction/build can hide source or layout errors: inspect original/derived sources and final rendered slice |

Pre-mortem: schedules can match all displayed centres and still invent Apple's
timing; source numbers are rounded and actual share rules are richer. Use exact
centres only inside an explicitly conditional illustration. Distinct witnesses
prove non-uniqueness in that model, not exhaustion, equal plausibility, or a
forecast. A successful EPS check cannot validate the dilutive-award methodology.

## Reader argument and execution

Reader: an accounting-literate designer who has just read Chapter 10's equity
discussion. The reader should reproduce the EPS scale conversion, distinguish
stock from weighted flow measures, explain the timing counterexample, and know
which award/settlement facts a future implementation still needs. The bounded
repair is the equity/EPS passage and its adjacent rendered pages; the unchanged
Version 2.10 is the protected comparison. Existing 41 displays and all 66
bibliography entries must survive.

Argument: a correct closing share bridge cannot supply EPS; the weighted
denominator supplies timing information but still permits distinct histories;
award and cash disclosures constrain different quantities, so none may silently
replace another. Introduce the real share bridge and ratio before the weighted
event equation, define elapsed days/units before the display, then use two
explicit schedules and the separate award/settlement facts. Insert near equity
in Chapter 10, preserving later consolidation and method obligations.

1. Preserve pointers; verify prior manifest and protected evidence; record new
   Git HEAD, source hashes and start time before source/calculation work.
2. Read/map all six notes and dependencies. Inspect annual original PDF and
   clearly labelled derived interim HTML views. Check every declared table
   column, not just the current year.
3. Verify basic/diluted EPS, annual shares and annual/interim RSU movements;
   preserve monetary equity/cash/expense distinctions. Verify the two timing
   witnesses by formula and independent day-by-day sums. Record query outcomes.
4. Create Version 2.11, build, render/read changed and adjacent pages, and
   validate source, display, bibliography and prior-evidence preservation.
5. Record result, four-ledger author review, missing facts and the next useful
   bounded question. Sequentially update the four live master records, then
   finalize a manifest. Do not run finalization concurrently with pointer edits.

Use `CUDA_VISIBLE_DEVICES=-1 python3` for helpers. Build using LuaLaTeX/latexmk;
if the known font-cache restriction recurs, preserve its log and use the required
trusted retry. No network, installations, GPU, paid review, outreach, background
worker or publication is planned. Stop at checked integration of this unit;
retain the five E workstreams, 40 exhibit targets and 136 unverified dates.

Reader checks: Why is the closing denominator wrong? What information does a
weighted average add? How can different dates yield the same average? What
changes under different timing? Why do vested awards not equal diluted shares
or all net issuance? Which amount represents equity, cash, authorisation or
expense? Which actual facts are still needed?

## Dependency audit amendment before calculations

The annual Item 5 and interim Item 2 purchase tables add exact displayed share
totals by monthly reporting interval. Add both complete purchase tables and
their programme footnotes, and both capital-return MD&A passages, to the
declared dependencies. The interim table may narrow the previously screened
rounded 100-million repurchase count; do not retain a note-only unknown after
reading that table. Original-page inspection corrected an incomplete text
screen: annual Note 1 does have a separate compensation-policy paragraph,
stating straight-line recognition for estimated awards that ultimately vest.
Add that exact paragraph as the fifteenth dependency. It supplies a recognition
method, but does not make aggregate unrecognised cost divided by a weighted
period a complete cohort schedule. Note 11 separately supplies plan terms.

The initially screened two midyear-purchase schedules omit all fourth-quarter
purchases and therefore fail the added annual Item 5 constraints. Do not promote
them as histories compatible with the declared population. Record their narrow
annual-total fit and that veto, then repair by fixing one purchase event inside
each of the three fourth-quarter intervals and constructing two earlier
purchase/issuance schedules that preserve the annual weighted average. Check
integer quantities, dates, monthly totals and a different intermediate balance.
These still remain conditional quantity histories: prices, actual issuance
dates, monetary journals and award terms are not reconstructed. The amendment
passes the skeptical audit; a new source constraint triggers model refinement
rather than a claim that the source is inconsistent.

Before manuscript integration, the interim comparative EPS row adds another
FY2024 constraint: the first-quarter basic weighted average. Include it in the
quantity examples. Fix two equal repurchases after days 45/46 to reproduce that
91-day mean, alongside the three fourth-quarter interval events. Solve the two
remaining early-year repurchases for each alternative issuance day, checking
the first-quarter and annual averages independently. Without this refinement,
annual-plus-fourth-quarter witnesses would still fail a retained comparative.
