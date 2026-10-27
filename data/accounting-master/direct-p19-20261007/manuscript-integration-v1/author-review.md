# Bounded manuscript review

Author review of candidate version 2.1, 7 October 2026. This is the five-page
standards slice, title/contents and affected references, not a whole-document
read or human acceptance. Exact PDF/source/render hashes are in
`candidate-manifest-v1.json`.

## Rendered reading and layout

Read physical pages 67–71 (printed 60–64) continuously at 110 dpi. The entry
explains rule applicability before the ASBE subsection. Physical 68 ends after
the complete mandatory-date paragraph; physical 69 starts with early adoption,
retains the existing lease mechanics, introduces the tax question and states
the qualifying conditions before the numerical example. The example continues
across the 69/70 page boundary without losing its adjacent assumptions.
Physical 70 shows the complete transition equation and its interpretation,
comparative effect, offset limitation and decision table. Physical 71 contains
the short closing source-coverage paragraph; it is a sparse chapter ending,
with no clipped, missing or stranded fragment. Kept rather than shrinking the
type or deleting a substantive qualification merely to reduce page count.
Physical 72 begins the next chapter normally.

Inspected title physical 1, relevant contents physical 4 and bibliography
physical 124–125. Version/date, subsection title and page destinations agree.
The three added references show their distinct notice/text dates, provisions
and official URLs. Interpretation 16 metadata are expressly attributed to the
issuance notice; its bibliography URL points to the operative PDF. Sources are
original Chinese with translated English titles. No missing glyph, clipped
display, broken citation or overlapping text was found in these pages. There
are no warning candidates in the final LuaLaTeX log.

## Reader-question answers from the rendered slice

1. Equal carrying amounts need not create equal tax differences. For a
   qualifying transaction under Interpretation 16 I(a), equal taxable and
   deductible temporary differences require separate recognition, subject to
   ASBE 18's asset recognition condition. Omitting both balances can preserve
   net opening equity while losing gross assets/liabilities and the first
   year's 1.25 net benefit. Physical 69–70 supplies the mechanism and example.
2. The 2019 mandatory group comprises domestic/overseas dual listings and
   overseas-listed IFRS/ASBE preparers; other ASBE enterprises face 2021. Early
   adoption requires the specified overseas-listed parent/subsidiary relation
   and cannot precede simultaneous use of the specified 2017 standards. The
   single-transaction tax rule applies from 2023, with disclosed early use from
   2022. Physical 68–69 distinguishes the decisions and dates.
3. No business combination, no initial accounting/taxable-profit effect and
   equal taxable/deductible temporary differences are the transaction
   conditions. The example assumes zero tax bases, deductions allocated to
   the liability, 25% tax and sufficient taxable profit. Gross recognition
   does not establish offset eligibility. Physical 69–70 states the assumptions
   before use and the separate presentation question afterward.
4. At the assumed comparative opening, DTA 27.5 exceeds DTL 26.25 by 1.25.
   The credit is opening retained earnings; assets 632.5 equal liabilities
   136.25 plus equity 496.25. Expiry in the remaining comparative year reverses
   both balances, creating expense 1.25. The calculation is a local accounting
   identity under the stipulated facts, not an estimate of a real company's
   tax. Physical 70 explains why neither the lease adoption election nor
   Section III's share-payment rule governs this tax transition.
5. Actual tax deductions/bases/rates, recoverable profit, adoption/elections,
   presentation facts and later operative amendments remain required. Physical
   70–71 also retains broader US/ASBE sector source work. The next justified
   action is claim-specific internal investigation, not real-issuer admission.

These are author answers, not observations from a human reader. Independent
model review is recorded separately; human comprehension remains pending.

## Mathematical and source integrity

The new unnumbered display is a balance-sheet identity. Its values, monetary
unit, time and assumed tax treatment are established immediately beforehand;
underbraces identify assets, liabilities and equity. The next paragraph
interprets opening equity and the comparative reversal. It is not referenced
elsewhere, so an equation number would add no navigation value. The exact
rational calculation is already reproduced by `check_source_repair.py`.

All 34 pre-existing displayed equations and all 54 bibliography keys survive;
one display and three primary-source entries are added. All 33 source/spec
inputs are copied, only three intentionally differ, and all 41 original
manuscript files remain unchanged. The matched-case table is byte-identical.
No assumption, numerical finding or substantive limitation was removed.
The removed assertions are the explicitly superseded access failures and
source-status summaries; their historical source records remain preserved.

## Deterministic diagnostic dispositions

The top-level surface audit only sees the main file, not included chapters; its
zero-heading/equation counts are not whole-document evidence. A second audit
targets `sections/standards-methods.tex` directly. Its one unlabeled display is
the intentionally unnumbered local identity above. Its three repeated-word
flags are adjacent `minipage` environment names from the unchanged table,
not reader-visible duplicated prose. Its five unreferenced section labels
are retained stable anchors and contents destinations. No manuscript repair
is warranted for those false positives. The separate 59-check diagnostic
traverses all copied TeX inputs for preservation, references and citations.

## Red-team limit

The strongest misleading inference would treat inspected original standards
and an illustrative calculation as current, issuer-specific ASBE permission.
The explicit entity/tax-law/amendment limits prevent that inference; a later
applicable amendment or different tax facts could change the answer. The
weakest remaining evidence is actual issuer applicability, not the arithmetic.
This correction narrows E07 and leaves full readiness false.
