# Located annotation pilot result

Prepared **31 provisional records, including 12 amount occurrences**, on four
explicitly identified accepted reports. Their source copies, hashes, retained
landing records and selection reasons are in `selection.json`. Labels use the
existing corpus schema; the locator/context/time sidecar remains a proposal.
The supporting code creates and checks these author-entered fixtures only.

Actual checks: `python3 build_pilot.py` wrote the records;
`python3 verify_pilot.py` checked the four original and four landing hashes,
all source-schema records, referenced support IDs, physical-page rectangles,
HTML IDs/context/unit records and pinned renders. It checked the twelve declared
amounts, selected reported identities, distinct group/parent perimeters, retained
duplicate occurrences, Apple's original instant date, and SEC filing-date
metadata. `verification.json` preserves the result and elapsed check time.
No parser package was installed or product engine implemented.

The adapter investigator independently reviewed the candidate labels, identified
two source-preservation defects and verified their repairs. Exact original HTML
byte spans now preserve XML name case and original attributes; parsed attributes
are separate. PDF support clips isolate undamaged headings and row labels.
See `../03-adapters/annotation-cross-review.json` for its pinned review. This is
a bounded cross-review, not blind second annotation or full financial adjudication.

The supervisor inspected original HTML fields and seven rendered PDF pages:
HSBC physical 343, 355, 356; Munich Re 206, 211; Midea 158, 166. Physical 202 of
Munich Re was an initial search hit in the contents table and is explicitly
excluded from labels. The page renders were retained with source-bound hashes.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Keep as candidate proposal input | Locators and bounded integrity checks pass | No unresolved source-hash/locator failure | Readings remain author-provisional; complete dimensions and qualifications not adjudicated | Blind second annotation and controlled evaluation design | Gold truth, whole-corpus coverage, accounting compliance or product accuracy |
| Keep difficult cases | Duplicate locations, dashes, restatement and rounded mismatch retained | No silent zero, date shift, perimeter merge or number rewrite | Qualifier/reference interpretation remains partial | Extend source-grounded labels and repair interpretations when evidence warrants | Rejection of extraction as a whole |

The strongest alternative explanation for apparently clean labels is that the
author selected readable units and knew the expected result. The pilot therefore
supports fixture design, not a tool ranking. A second source reading that changes
a row/column, sign, date or qualifier would overturn the affected label. The
weakest evidence remains semantic coverage outside the selected spans. See the
handbook and ambiguity log for exact follow-up work.

The frozen 192-report corpus was read only. No source acceptance, mission
assessment or master phase status was promoted by this packet.
