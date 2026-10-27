# EDD model source exists; published wording still needs care

19 October2026. This source-only continuation resolves the two candidate-route
identities left by the PubTabNet inquiry. The IBM EDD repository provides
models.py and training/preparation/evaluation code at pinned commit
e6bb2bd509d7c89cdf1fb9608f9db9a044413bed. The ECVA endpoint supplies a17-page
main paper with the expected title and all three authors. Six receipts and27
passages bind the result. Discovery was model recall followed by verification;
the unsuccessful web-tool search is not cited as discovering these sources.

The global statement that EDD code is unavailable is wrong relative to the
acquired files. PubTabNet's old nonrelease sentence remains historical source
evidence only. Availability does not establish that this revision generated the
published scores: repository release date, original experiment commit, data
membership, dependencies, checkpoints and run logs remain unverified.

The published main paper retains the60/20/20 partition statement,548,592 training
count and balanced10,000-example heldout selections (Section3,pp4–5). Section5,
p7, retains both the cell-cost “similarity” wording and noncell substitution
cost description found in v5; visual inspection confirms the text. Its node
count description still does not specify the exact raw-HTML descendant counting
used in the previously inspected PubTabNet metric. No correction by publication
can therefore be asserted. This is a textual/code comparison, not evidence that
the authors' actual numerical implementation followed the ambiguous wording.

Sections4 and6.1 preserve the dual-decoder mechanism, equation1, size filtering,
encoder alternatives, staged Adam schedule, dimensions and beam3. Sections6.2
and6.5 preserve the reported comparisons and synthetic retraining distinction.
Section7 still assumes supplied table locations. The main paper refers to a
separate supplement, especially TableS3 for validation model selection; that
supplement remains unread in this unit. Its claims are not promoted as checked.

## What selected official code adds

The root README's explicit recipe targets PubTabNet2.0.0 and separately trains
structure and content with epoch totals10,13,23,25. Resume reads the completed
epoch and begins at the next; restored optimizers can have their rates changed.
This state-dependent schedule cannot be replaced by four fresh launches with
the same epoch arguments. The driver waits indefinitely in ten-minute intervals
for a missing checkpoint. That behavior requires an external stop policy before
any future run; none is launched here.

The recipe overrides important CLI defaults: cell embedding80 versus16,
encoded grid28 versus14, attention256 versus512, tag hidden256 versus512,
batch10 or8 versus16, and separate stride1 branches versus the default stride2.
Content prediction is disabled unless requested. Source selection and explicit
configuration must be preserved together. Defaults also include dropout0.5,
gradient clipping5 and zero attention regularisation coefficients. They are
implementation facts, not validated choices for financial-report extraction.

The encoder initialises ResNet18 without pretrained weights. The selected
structure decoder stores a hidden state when a cell-opening token is consumed;
the baseline cell decoder uses that state and its own recurrent state in
attention. Training retains or detaches the structure-state gradient according
to a flag. Both structure and cell beam searches can append an end token when
their step limits are reached without a completed sequence; successful return
alone therefore does not establish unconstrained completion or valid HTML.

The training criterion is CrossEntropyLoss for both branches. The inspected
code packs structural tokens together for one loss, but computes cell loss per
image and averages those image losses across the batch. Under the ordinary mean
reduction of that library call, this weights images equally for cell loss rather
than pooling every cell token in the batch. The exact installed dependency and
batch construction remain unverified; this static grouping is enough to reject
an unqualified claim that both objectives use the same pooled-token weighting.
Optional bbox loss exists. The driver passes the cell-content optimizer into
the bbox-optimizer argument: that is wrong for independent bbox updates, but
the selected content-only recipe disables bbox prediction. It does not justify
claiming that the selected original task fails.

Data preparation filters only training samples by the stated maximum sizes;
validation rows follow the supplied split. It builds vocabulary using a minimum
frequency5 and maps excluded tokens to unknown. These are later implementation
choices, distinct from the paper's corpus-curation threshold50. The script
expects a plural cells array and optional box annotations. It writes an hdf5
image file while the README inventory labels h5; loader correspondence remains
to be checked before interpreting that as an actual failure.

Evaluation loops over all ground-truth keys and retains zeros for missing
conversion results or caught conversion/scoring exceptions. This preserves the
denominator, but its JSON merges operational failure with a valid zero score.
The future protocol needs separate failure class and score fields. Without
ground truth it writes an empty HTML string on conversion exception. Neither
branch supplies failure frequency evidence in this source-only inquiry. The
imported EDD metric is a different file from the prior PubTabNet metric; their
equivalence remains unchecked.

|Decision|Primary criterion|Veto status|Main uncertainty|Next justified action|Not concluded|
|---|---|---|---|---|---|
|Resolve model availability positively|Exact official model source acquired and selected path read|No preservation veto|Historical revision and dependencies|Inspect remaining loader/helper/metric files|Reproduced original experiments|
|Preserve published-wording mismatch|Matching main paper and renderedp7 checked|Paper/code literal-equivalence claim blocked|Separate supplement/errata|Inspect explicitly referenced supplement|Authors ran the literal ambiguous formula|
|Retain EDD only as candidate component|Recipe and failure behavior documented|No target validation or runtime admission|Actual financial errors and reproducibility|Prepare explicit future configuration/failure records|Default readiness or financial correctness|

|Inference status|Finding|
|---|---|
|Hard veto screen|Unsupported global source absence is rejected; literal metric equality remains blocked; optional bbox argument mismatch is static evidence only|
|Statistically supported ranking|None evaluated or established here|
|Descriptive-only differences|The source's reported score comparisons and runtime|
|Default-readiness|No model/dependency/default is admitted|
|Next evidence needed|Published supplement, exact EDD metric and loader/helper/dependency identities; target-specific evidence only under later authority|

All source reads are bounded in source-ledger.json: three complete entry files
and four selected ranges of models.py, not every alternative model. Version3.44,
396 pages, not_ready and all53/6/46 obligations/interactions/operations remain
unchanged. A separate R08 supplement closes no whole row. No global continuation
veto fired; continue the source dependency inquiry without running the model.
