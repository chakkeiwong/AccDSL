# Note 20 classification correction: author review

12 October 2026. I inspected the frozen normal-resolution render of the
retained 2025 10-K Note 20, printed page 281/PDF 283. The Parent company
block ends in its own subtotal. The Subsidiaries block ends in a second
subtotal of 180,573 million in 2025 and 161,792 million in 2024. Below that
rule, **Junior subordinated debt** is a new bold left-aligned heading, with
its own 1,594/1,603 million subtotal. The consolidated total follows it.
The three bold headings share the same left edge; the PDF span coordinates
and reading order are checked by `verify.py`. The image and PDF hashes bind
this reading to the source preserved by the prior unit.

The old ledger's `subsidiary.junior.*` identifiers and the Version 2.36
phrase “Subsidiaries junior-subordinated-debt subtotal” misclassify the
displayed band. The 50 previous checks did not test that hierarchy. This is
a source-fidelity error, not merely an unproved causal explanation. The
totals establish the three-band arithmetic:

- 2025: 253,039 + 180,573 + 1,594 = 435,206.
- 2024: 238,023 + 161,792 + 1,603 = 401,418.

Note 33's parent-only 254,633/239,626 million balances still exceed Note
20's Parent company subtotals by 1,594/1,603 million. The match remains
worth investigating, but the table does not assign the separate junior band
to a legal issuer or explain its parent-only accounting relation. No current
ASC conclusion, contract reading or parent payment schedule follows. This
author review is not independent accounting or legal acceptance.
