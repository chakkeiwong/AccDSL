# Publisher follow-up: zero eligible carrying weights

18 October 2026. P17/R03–R04; MC17/19/24/26/29/30/35.
Plan: `docs/plans/accounting-zero-weight-cgu-publisher-followup-20261018.md`.

## Question and inspected source

The target is allocation of a positive CGU impairment reversal when every
eligible non-goodwill asset has zero carrying amount and at least two assets
have positive restoration capacity. The retained IAS 36.122 carrying-weight
instruction is the comparator. No substitute weighting rule is admitted.

The publisher's actual insights index exposes its IAS 36 collection and
*Reversing impairment losses*, dated 23 March 2022. The article in turn links
the retained eight-page PDF of that title, copyright 2022. Its technical text
and both examples were inspected; PDF pages 5–7 were also rendered and viewed
to verify the tables, flowchart and apparent arithmetic discrepancy. The HTML
extraction is in `sources/gt-reversal.txt`, lines 257–306. PDF page boundaries
are retained in `sources/gt-reversal-pdf.txt`. This is an accounting firm's
interpretation, not an amendment to the Standard or evidence of current
entity-specific applicability.

The first article and collection downloads failed with sandbox DNS exit 6.
The required trusted retries both returned HTTP 200, as did the linked PDF.
The failure records remain separate from the successful response records.
The failed attempts therefore do not establish publisher inaccessibility.

## Technical argument and limits

Pages 2–3 require a change in estimates that increases service potential;
passage of time or unwinding alone is insufficient. Goodwill reversal is
excluded. Individual-asset reversals are subject to the amount that would
have remained without the impairment, with revaluation treatment kept
separate. Page 4 depicts that single-asset decision. None selects an allocation
between two zero-carrying assets inside one CGU.

Page 6 states carrying-amount pro rata allocation for non-goodwill CGU assets.
An asset is capped by the lower of its determinable recoverable amount and
its unimpaired depreciated carrying amount; excess allocation is redistributed
to the other assets subject to their caps. The flowchart repeats this sequence
without an all-zero branch. A cap restricts an allocation but does not select
relative weights when the prescribed denominator is zero.

Example 2 on page 7 first writes off goodwill 750 and impairs identifiable
assets by 500, leaving those assets at 1,180. After displayed depreciation
168, the eligible assets still carry 1,012. Their aggregate recoverable amount
is 1,500 and unimpaired depreciated cost is 1,440, giving a displayed reversal
of 428. Goodwill stays zero. This is zero goodwill with positive non-goodwill
carrying amount, not zero eligible weights. It does not provide individual
weights for the target multi-asset case or establish that such a case is
impossible.

The strongest tempting inference is to treat the all-zero case as a limiting
version of this ordinary allocation or to use restoration capacities as
weights. Neither inference is stated or derived in the inspected source.
Changing to a single-asset unit of account would also change the question.

## Source arithmetic finding

Example 1 on page 5 prints carrying amount 1,012 and recoverable amount 1,300.
Its table correctly gives the difference as 288, but the analysis paragraph
states an increase of 316. Relative to its own displayed target, 316 is wrong:
1,012 + 316 = 1,328, which exceeds 1,300 by 28. The rendered page confirms
this is present in the source, not a text-extraction substitution. The source
also rounds 1,180/14 to an annual 84; that rounding does not reconcile the
28 discrepancy. The printed value is preserved and is not used as a local
oracle. This finding does not refute the separate carrying-weight instruction.

## Decision

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| This lead does not support an all-zero allocation | No explicit solution or impossibility argument | Positive eligible carrying amount makes Example 2 inapplicable; missing zero branch blocks extrapolation | An applicable treatment may exist elsewhere | Retain the unsupported-method disposition; inspect a genuinely new technical authority addressing fully written-down non-goodwill CGU assets | No literature-wide absence, allocation default or accounting compliance |
| Reject Example 1's printed 316 as an arithmetic oracle | 316 does not equal the stated capped increase | Rendered discrepancy confirmed | Editorial origin of the discrepancy is unknown | Preserve source and local discrepancy check | No general rejection of the publisher or all of its impairment guidance |
| Continue independent proposal work | Documentary source and review records remain valid | No global continuation veto | Wider methods and independent/human acceptance remain open | Resume the exact 3.44 ordered review | No runtime or whole-mission completion |

This inquiry has no stochastic comparison and makes no ranking. The source
result is documentary, the arithmetic check concerns only the displayed
example, and the scientific/accounting interpretation remains a separate
ledger. The candidate source fails the narrow promotion question; it does not
invalidate the manuscript review, the wider program or the target itself.

Post-run red team: the most plausible alternative is an unstated specialist
practice for fully impaired assets. An explicit applicable passage or a
reviewed derivation would overturn this source-gap disposition. The weakest
part is coverage: one publisher's article and examples are not a comprehensive
search. No paid referral, outreach or manuscript change follows.
