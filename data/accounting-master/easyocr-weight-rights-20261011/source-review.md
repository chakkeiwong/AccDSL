# CRAFT and English G2 source authority

The official CRAFT source repository identifies itself as the authors'
implementation and resolves `master` at retrieval to
`e332dd8b718e291f51b66ff8f9ef2c98ee4474c8`. Its complete tree, README and
licence are retained; the latter two match their Git blobs. The MIT notice names
NAVER Corp., 2019–present. The complete README repeats the notice and links three
pretrained models. Its general model is described as trained on SynthText,
IC13 and IC17, for English and multilingual use. Those are source descriptions;
the paper, training procedure and dataset licences were not inspected here.

EasyOCR's pinned README credits both CRAFT code and a pretrained model to that
project. The official model hub independently links the same CRAFT ZIP as
EasyOCR's pinned config and the preceding GitHub release metadata. It also links
the same English G2 archive. These links establish consistent advertised origin.
They do not establish byte equality between the EasyOCR mirror and CRAFT's
separate Google Drive checkpoint. No such bytes were downloaded or compared.

| Record | Positive evidence | Remaining boundary |
| --- | --- | --- |
| Official CRAFT README and MIT notice | Author repository, model links, notice and redistribution condition retained | Licence wording defines Software and documentation; no separate weight-specific statement or checked link-to-mirror byte identity |
| EasyOCR model hub | Direct links agree with selected CRAFT and English G2 archive URLs | Page supplies no checkpoint-specific licence or strong digest |
| EasyOCR pinned source licence | Package declares Apache-2.0; full text retained in prior unit | A package declaration does not alone establish all external checkpoint or dependency obligations |
| Model hub's linked terms | Full terms retained, effective 19 May 2021; covers website, services and products | Free-service personal/noncommercial clause is not expressly mapped to the two downloadable checkpoints |
| Official-repository issue records | CRAFT users have asked the exact commercial-model question | No inspected maintainer statement resolves it; user questions are not legal findings |

The proposed interpretation is that the author-distributed CRAFT model is
intended to accompany the MIT software, while EasyOCR advertises its own
recognizers within an Apache-2.0 project. The competing interpretation is that
the general software notices do not identify all weight rights, particularly
where CRAFT acknowledges external training datasets. The checked consequence is
limited: source preparation may retain the candidates, but the record does not
yet justify a blanket model-distribution admission. This is an evidentiary
boundary, not a conclusion that commercial use is prohibited.

The current model-hub terms require care with subject matter. Section 2 limits
the free demo/service to personal, noncommercial use unless permission is
obtained; other sections describe accounts, subscriptions and billing. The page
does not expressly state that this clause overrides EasyOCR's source licence
or attaches to these GitHub checkpoint files. Applying it categorically to
local EasyOCR would be unsupported. Ignoring its existence would also leave an
unrecorded source. Preserve it with this unresolved scope question.

Two bounded issue searches added context. CRAFT issues 105 and 161 ask about
commercial model use and training-dataset permissions. Issue 161 has no returned
comments. Issue 105 has one response linking the project licence, with API
`author_association=NONE`; this does not establish maintainer authority. The
EasyOCR weight-specific search returned zero, and a broader licence search
returned the first 20 of 26 results. Relevant returned issues 1422, 845 and 1444
have no comments. Their allegations about placeholders, python-bidi and licence
changes are not adopted. The placeholder is in Apache's application appendix;
an issue alone does not show invalid licensing. The exact selected python-bidi
version and its terms still need inspection before any transitive conclusion.
No exhaustive issue search is claimed.

This unit exhausted its declared twelve-source budget with all requests
successful. Remaining remote inquiries require a concrete new premise. A
specific exact python-bidi release or an authoritative checkpoint notice would
qualify; repeating these sources unchanged would not. No professional contact,
fee, model download, code installation or publication occurred. The unresolved
rights question blocks a stronger claim about these model distributions, not
the other proposal workstreams or the entire research direction.
