# Model identities and declared terms

The two model references in the pinned Docling source now have official
repository metadata retained locally. This resolves a source-preparation gap;
it does not retain or verify any weight file.

| Reference queried | Commit returned | Returned file inventory | Declaration |
| --- | --- | --- | --- |
| `docling-project/docling-layout-heron@main` | `8f39ad3c0b4c58e9c2d2c84a38465abf757272d8` | Six files, including one weight file | Model card: Apache-2.0 |
| `docling-project/docling-models@v2.3.0` | `fc0f2d45e2218ea24bce5045f58a389aed16dc23` | Eight files, including accurate and fast table weights | Model card: CDLA-Permissive-2.0 |

Heron's commit is the response to `main` at this retrieval, not proof of the
model selected when the older Docling source commit was created or previously
executed. The table tag has been resolved at retrieval; neither name is silently
promoted to an AccDSL default. The seven retained card/config bodies match their
upstream Git blob IDs. Every weight remains metadata-only, with local bytes
absent and no runtime or accuracy claim.

## What the configuration says

Heron's configuration declares `RTDetrV2ForObjectDetection`, model type
`rt_detr_v2`, float32, seventeen labels and `transformers_version=4.53.0.dev0`.
That serialized version string is not a current installed-package requirement
or compatibility guarantee. Its preprocessor configuration resizes to 640 by
640, rescales by 1/255, and has normalization and padding disabled. These are
declared settings; their exact execution still depends on the selected loader.
The card's inference example uses threshold 0.6, whereas the inspected Docling
engine default is 0.3. Neither threshold has been validated for this filing
task, and the example is not authority to replace the proposed baseline.

The table configurations declare `TableModel04_rs` with a ResNet18 backbone.
The accurate variant has six encoder and six decoder layers; fast has four
and two. A structural comparison finds only these two differing JSON values.
Both specify a 448-pixel resized image, dataset normalization, prediction
`max_steps=1024`, `beam_size=5` and `pdf_cell_iou_thres=0.05`. Training settings
and dataset names also remain in the source JSON. They are not evidence that
all those fields execute during inference or that the named training corpus
was lawfully assembled. Actual checkpoint selection and consumers of each
configuration field require the exact `docling-ibm-models` loader source.

The TableFormer card still describes a layout model, while the returned
`v2.3.0` file list contains table assets and no layout weights. Its card alone
cannot establish the bundle's contents; Heron has its own repository. The card
also reports comparative scores and calls TableFormer state of the art. Those
are upstream claims, not checked local rankings. No numerical score is used
to nominate or promote either configuration here.

## Terms actually inspected

Neither returned file inventory lists a standalone LICENSE or NOTICE. Both
retained cards include the licence identifier in front matter but no full
licence body or complete contributor/third-party notice chain. The official
standard texts were therefore retained separately. Their conditions describe
the declared licences; the cards remain the evidence of the repositories'
declarations. No blanket licence completeness or distribution admission follows.

Apache-2.0 was read in full, including definitions, sections 2–9 and the
application appendix. It grants copyright permissions subject to its terms,
and a contributor-scoped patent licence with a patent-litigation termination
condition. Redistribution requires a copy of the licence; modified files must
carry prominent change notices; source-form derivatives retain applicable
copyright/patent/trademark/attribution notices; an included NOTICE brings the
specified attribution requirements. It does not grant general trademark rights
and disclaims warranties/liability. Its definition of Work and evidence of
licensor authority still matter; the bare model-card tag is not a complete
provenance audit.

The CDLA-Permissive-2.0 agreement was read in full on its official page,
sections 1–5. Section 1.1 permits use, modification and sharing under its terms;
section 2.1 requires the agreement text to accompany shared Data. Section 3.1
does not impose restrictions or obligations on Results. Sections 5.1 and 5.4
distinguish received material from outcomes of computational analysis, with
machine learning models among the examples of Results. A model received as
licensed Data is not automatically exempt from sharing conditions merely
because models can also be Results in a different transaction. Section 4
disclaims warranties and liability. The web page's separate site-content
copyright footer is not substituted for the model's declared licence.

## Proposed use dispositions

| Proposed activity | Prepared interpretation | Still required |
| --- | --- | --- |
| Internal evaluation of retained model bytes | Licence declarations support further preparation; record exact files and attached terms before use | Actual verified bytes, exact package environment, component notices and execution protocol |
| Redistributing unchanged weights | Apply the declared licence to the received files; preserve text/notices required for that licence | Intended file set, upstream authority/component audit and actual distribution decision |
| Modifying and distributing Heron files | Track modifications and Apache attribution/notice obligations | Exact derivative scope and terms review |
| Sharing TableFormer weights or modified Data | CDLA section 2.1 requires agreement text | Exact received/modified material and other applicable rights |
| Publishing extracted accounting records | Model terms do not establish permission for source filings or validity of extraction | Source/data rights and accounting acceptance remain separate |

No professional engagement or external distribution has occurred. These are
internal proposed answers with exact source bodies and competing interpretations
prepared under MC35; wider unresolved legal facts remain on the internal queue.

## Source leads and limits

The Heron card references the layout-analysis report `2509.11720` and Docling
report `2408.09869v4`; the table card references DocLayNet `2206.01062`, the
Docling report and TableFormer CVPR 2022. This unit read the model cards, not
those papers. Do not cite their technical or benchmark claims from this unit.
Reconcile these leads with the retained literature packet before any new
technical review so that earlier work is not repeated.

The strongest alternative explanation for a later mismatch is a different
weight/loader combination or an unexamined configuration consumer. The weakest
evidence here is that remote LFS hashes identify announced bytes but do not
verify a local file. A changed repository commit, source mismatch or additional
component notice would reopen the affected record. None prevents continuing
the exact package/loader source audit.
