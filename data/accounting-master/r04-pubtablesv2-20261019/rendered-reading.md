# Manual reading of physical pages21–28

Source: sources/02-paper.pdf, arXiv2512.10888v3. Images paper-21.png through
paper-28.png were viewed in batches of at most3. These notes are manual
observations from the images, not extracted text. The pdftotext output is blank
for these pages following a mismatched EMC warning.

- Page21, C.1 Eq(1): GriTS_f(A,B)=2 sum_ij f(Atilde_ij,Btilde_ij)/(|A|+|B|),
  with f in[0,1]; cell-similarity sum is a real-valued true-positive score.
  C.2 explains TEDS and its structure-only variant. C.3 says matching maximizes
  the sum of individual GriTS or TEDS scores, and calls that sum an unnormalised
  true-positive score. This wording needs distinguishing from raw cell scores.
- Page22, C.4: aggregate true-positive scores across inputs; TEDS denominators
  are numbers of true/predicted tables. GriTS additionally weights by cells;
  this replaces the original mean over input-level scores. C.5 graph matching
  requires identical class labels and node-box IoU0.8. D.1 initializes the
  TATR successor from v1.1-Pub; no new architecture is claimed.
- Page23, Table9/D.2: docling-core2.48.4 parses DocTags. SmolDocling/Granite
  parsing failures are16/43 on cropped and958/35 on single-page collections,
  each with7,680 test inputs. The passage does not specify the complete scoring
  disposition for each failed parse. Qwen full-document inputs fail on the
  two longest of878 documents,65 and72 pages. BeautifulSoup can parse malformed
  or truncated HTML; successful parsing is not structural correctness.
- Page24, D.2/E/E.1: custom Granite spanning-markdown parsing and tried prompts.
  TATR-v1.2-Pub:8 T4s,batch2/GPU,100,000 examples per epoch,160 epochs,
  learning rate5e-5,gamma0.9 every4 epochs,eos_coef0.3. Other TATR settings are
  inherited. F.1: Granite always output one table in this study, an advantage
  for the selected within-page split-table task that hurts other tasks.
- Page25, Table10/F.1:64 selected split-table examples; all reported AccCon
  values0 and largest AccTop0.0625. Table11/F.2 stratifies under/equal/over counts
  by zero,one unsplit,one split,multiple true tables. Matching table counts is
  explanatory, not correctness of cells or accounting.
- Page26, Table12/F.3: training sizes250/1000/4000/15830;200 epochs,validation
  after each epoch,best-F1 checkpoint. F.4 reports ViT20/1862 failures and
  ResNet46/1862,with16 shared. This supplies a heldout-case denominator omitted
  by the short main-text discussion, without establishing document-disjoint
  sampling or per-model confusion counts. F.5 begins qualitative VLM failures.
- Page27, Figure8: example false continuation from both classifiers. F.5 says
  one output can fuse content from several true tables; one-to-one metric
  matching penalises it. Recommended Qwen system prompt matters. Repetition
  until token limit can occur even on a two-page document.
- Page28, Figure9/F.5: the two-page list-of-reviewers example; larger Qwen7B
  qualitative cases also fail or omit a page. These are explicitly anecdotal
  observations; no larger-model full-test evaluation. Do not promote them to
  a systematic ranking.

No unique split-ID manifest, per-failure score policy, exact continuation
threshold, all-classifier confusion matrix or experiment-era GriTS commit is
established by these inspected pages. Their absence here is not proof of
leakage, dropped cases or incorrect published scores.
