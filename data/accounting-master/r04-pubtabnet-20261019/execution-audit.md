# Resumed source inquiry: evidence contract and diagnostic plan

19 October 2026, Asia/Hong_Kong. This continues the prepared unit; no lifecycle
stage is repeated. The original plan and verifier are already protected.

The primary question is whether the original PubTabNet/EDD/TEDS evidence can
support the proposal's financial-report extraction requirements (MC01–05,
MC23/26/28–35). The exact comparator is chapter 3, lines 201–240, of the
protected 3.44 manuscript, plus the whole-report requirement; it is not a
new model leaderboard. The paper read is arXiv 1911.10683v5, 4 March 2020,
not a verified copy of the final ECCV publication. The version was selected
before metadata verification and is retained explicitly rather than silently
called the latest or final publication.

The paper links the IBM repository. Its captured default-branch page identifies
commit 8ffde9024bd331f5a61c3c549fdf30dd3c3e43a5; subsequent directory, metric.py
and metric README requests use that exact commit. This is a contemporary code
snapshot, not proof of the code used in the 2020 experiments. The repository
expressly withholds EDD model code; the released metric is a different scope.
No model, parser dependency, APTED implementation or upstream example is run.

## Skeptical audit before the local checker

The printed paper contains unresolved descriptions: a 60/20/20 raw partition
alongside 548,592 training tables and the approximately 568k released total;
the use of “similarity” in a substitution cost where the code uses distance;
and a tree-node denominator whose exact implementation counts raw HTML
descendants, excludes the table root and includes inline elements. Pages 3–4
were visually read to distinguish printed wording from extraction defects.
The first issue is an unresolved population/accounting explanation, not proof
that the study's split leaked. No source count is silently corrected.

Primary documentary pass: bind exact bytes, read relevant sections I–VII,
equations 1–3, tables I–III, references and official metric source; preserve
source statements, static code observations and local deductions separately.
Source-only checks test these bindings and a few explicitly defined finite
consequences. They cannot certify the external paper, dependencies or model.

### Finite witness contract

Construct well-formed one-cell HTML examples with a fixed table/tbody/tr/td
topology. A standard-library edit-distance routine computes only cell-token
Levenshtein distance. For a single changed cell, same topology, and cost d<1,
the exact minimum tree cost is d: matching all structural nodes and renaming
the sole cell attains d, while every structural insertion/deletion or unequal
structural relabel costs at least 1. This proves the closed form for these
examples without implementing or executing APTED.

Compare plain 100 versus 900, identically bold-formatted 100 versus 900, and
100 versus -100. Count the raw descendants exactly as the inspected source
does. A second pair retains identical table text but changes an explicitly
supplied unit outside the table. Its table-only score stays perfect while the
defined amounts differ by a factor of 1,000. These are mathematical examples,
not observations from any financial report. Their role is a promotion veto
against using a TEDS threshold alone as financial correctness. They do not
reject TEDS as a structure/text diagnostic.

Defaults: one-cell topology and integer amounts are convenience choices to
make the proof inspectable; no real-population claim follows. Formatting-token
rules are source-derived hypotheses for the selected well-formed subset;
actual lxml repair/parsing remains unevaluated. The distance routine receives
identity, substitution, insertion and deletion controls, and altered expected
results must fail. No stochastic ranking or statistical inference is attempted.

Continuation vetoes remain protected-file/HEAD/index/dirty-set violations or
held runtime/install/empirical actions. Paper/code discrepancies block exact
equivalence claims; they trigger a documented specification repair, not a
global stop. No manuscript defect requiring a changed PDF is established by
this narrower inquiry: its existing warning about units and context is apt.

Preserve artifacts in this unit, six additive literature ledgers, the separate
R08 supplement, four live control updates and one final read-only replay.
Acquisition is capped at six distinct official URLs; all six are now retained.

## Discovery that repairs the next phase

A subsequent bounded web search for the exact title with erratum/correction/
retraction and for arXiv1911.10683/TEDS returned no readable content to this
client. Candidate routes from model recall, not inspected search results, are
https://github.com/ibm-aur-nlp/EDD and
https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123660562.pdf .
Their identity and contents remain unverified. An interim progress sentence
overstated these as search discoveries; this record corrects that provenance.
These are leads, not full technical reads in this unit. The retained PubTabNet
README's nonrelease sentence cannot support a current global absence claim.
The next unit must read the separate repository and published edition before
deciding code availability, reproducibility or which wording the final paper
uses. No extra acquisition is hidden inside this unit's six-URL budget.
