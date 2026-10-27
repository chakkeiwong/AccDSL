# Integrate the conditional indirect cash-flow explanation

25 October 2026. S2–S5; MC02/06/08/10–13/16/19–22/24–28/30/32–35.
This is the next dependent work unit after the record and read-only replay in
accounting-indirect-profit-components-20261025.md. That verification is still
running at plan creation. Do not integrate or claim acceptance before it passes.
Forecasting/E3 remains deferred.

## Question and skeptical audit

Can an accounting modeller and language implementer reconstruct the explicit
profit-to-operating-cash explanation, including disposal gain/loss and interest
classification, without inventing a residual adjustment? The bounded addition
belongs after the financing schedules in company-family-language.tex, where the
existing four-account explanation still leaves unpaid interest unresolved.

Baseline: Version 4.25, 521 pages, PDF SHA256
d35590f4ea484616340fbcaf30eca1b69807f443d3a82f0f75b365819f955f8e in
docs/design/proposal/manuscript-term-authoring-20261025/. Preserve all 174 source
files and every existing equation, citation, label and reference. The new target
is manuscript-indirect-cash-20261025/, Version 4.26. Work is additive; old scope
statements describe the earlier reports and remain accurate for those profiles.

Audit passes conditionally on accepted engineering evidence. The comparator is
the actual locked v2 requests/results and independently stated journal algebra,
not a claim of compliance with a financial reporting standard. A passing identity
cannot admit a classification or prove complete events. The one-category-per-
account/method restriction and non-unique decompositions must stay explicit.
Inherited author-only reviews cannot establish independent or human acceptance.
Page count and successful compilation are explanatory diagnostics only.

## Assumptions and evidence contract

Debit-positive postings, exact rational amounts, cash categories and selected
period boundaries come from the frozen declared-book engine. They are profile
conventions, not universal accounting defaults. A classification is a supplied
conditional premise. Compare all manuscript amounts against the finite cases;
derive the exclusion identity from the balanced journal before explaining its
implication for operating cash. Wrong signs, missing gross postings, lost prior
content, changed evidence hashes, undefined references or new build warnings
veto this integration. An engineering failure returns to the repair plan.

The reader enters knowing direct cash and financing movements. A plant disposal
for 12 with carrying amount 10 makes the question concrete: profit is 2 but none
of the receipt is operating cash under the supplied classification. Introduce
the adjustment categories in words, define all signed quantities and units, then
derive the equation. Follow it with the gain/loss and interest examples. The
reader should leave able to explain both the reconciliation and why it cannot
select the accounting policy. The following receivable discussion then resumes
with its existing claim-level question.

## Execution and acceptance

1. Finish the existing 20-case record and exact replay. Record actual test,
   comparison and lock counts; preserve failed attempts if any.
2. Inspect predecessor PDF 396–398 and the corresponding source. Record separate
   comprehension, mathematics, source and typography judgments using the already
   applied repair-scholarly-readability skill. Keep the repair to this passage.
3. Freeze source/evidence hashes, copy the source baseline outside the target,
   add the explanation and update only the cover version. Build with the existing
   LuaLaTeX toolchain and isolated /tmp cache. No installation or GPU execution.
4. Check exact additive deltas, references, citations and displayed mathematics;
   reject new warnings. Read the cover, addition and adjacent rendered pages at
   normal resolution. Preserve unresolved whole-document and human review.
5. Record result and manifest, retain all 53 obligations / 6 interactions /
   46 operations, then refresh the ten current controls. Reassess the next
   substantive simulator dependency before continuing; no whole requirement
   closes from this finite algebra.

Artifacts: data/accounting-master/indirect-cash-integration-20261025/.
Commands: python3 -B integrate.py prepare, build, verify within that directory;
finish.py only after rendered inspection. Full output goes to local files;
tool results stay bounded. No commits, workers, external review or publication.
