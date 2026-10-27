# Identity repair audit

19 October2026. The two recalled routes now resolve to matching primary
sources: an IBM EDD repository identifying the paper and an ECVA-hosted
17-page paper with matching title/authors. Discovery provenance remains model
recall; successful identity checking is subsequent evidence. No search result
is retroactively invented. Repository commit:
e6bb2bd509d7c89cdf1fb9608f9db9a044413bed.

Six requests are complete: repository page, published PDF, pinned models.py,
train_dual_decoder.py, prepare_data.py and eval.py. No dataset/weights fetched.
The paper's sections3–5,6.1–6.2,6.4–6.5 and7 are the scope of the targeted
edition comparison. Page7 is visually read. The supplementary material,
including TableS3, is separately referenced and not yet inspected. No claim
that the whole published package or all reference papers has been read follows.

Read all of training/preparation/evaluation entry points. Read these model
spans:1–253;1008–1251;1510–1777;2081–2485. Unread alternatives and bbox routines
are outside the selected README cell_decoder_type1 path. Some bbox classes are
nevertheless instantiated; their correctness is not admitted. The selected
code is explicitly incomplete as an execution audit until datasets.py, utils.py,
metric.py, requirements and the exact dependency semantics are inspected.

Static observations requiring protocol repair: CLI defaults differ from the
README training recipe; resume state/optimizer affects the schedule; eval
catches all conversion/scoring exceptions as zero; decoding can forcibly append
an end token at the limit; the data preparation requires later2.0.0 annotations.
Also, the training driver passes cell_decoder_optimizer as the bbox optimizer
argument. This is wrong for an intended independent bbox optimizer, but that
path is disabled in the cited content-only recipe; no training failure is
claimed for that recipe. No tensor execution is needed to identify the argument.

Primary local check: exact six receipts and file hashes, scoped reading spans,
AST-checked CLI defaults/optimizer argument and exact edition passages.
Counts are verification of the record, not correctness or replication evidence.
No model tests, numerical ranking, default adoption or runtime promotion.
The old root README's nonrelease statement is superseded as global availability
evidence by acquired model source; preserve the historical bytes unchanged.
This is a substantive repair of the next plan, not another read of the same
completed source packet. Remaining supplemental/dependency gaps trigger a new
bounded inquiry. No protection/continuation veto has fired.
