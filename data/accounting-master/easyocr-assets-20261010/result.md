# EasyOCR source and asset preparation result

EasyOCR 1.7.2 is source-identified. **46 documentary checks pass**; 1539 prior
references verify. The English Reader selects CRAFT and `english_g2`; Docling's
prefetch default also names `latin_g2`, which is not selected by this Reader
branch. Download-disabled Reader fails on missing or MD5-mismatched selected
files, but still creates directories and changes `sys.path`. Its checkpoint
loaders use `weights_only=False`. No model byte or installed path was tested.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain 1.7.2 as source candidate | Tag/tree and twelve source blobs verified | No source identity veto | Exact dependency resolution | Prepare a future lock only after compatibility work | Production lock |
| Require trusted, explicit assets | Two official archive listings and selected filenames/MD5s found | Local bytes absent; runtime admission veto | Checkpoint provenance, model rights | Investigate CRAFT and English asset authority; later acquire under approved runtime scope | Weights verified or distributable |
| Keep English config non-executable | Reader/Docling branch inspected | No source-branch veto | Installed package/wheel and actual documents | Later exact install, file checks and accounting-page OCR validation | OCR accuracy or semantic completeness |
| Preserve V2.26 | Generic model/download obligations already stated | Manuscript hash unchanged | Human/domain acceptance | Continue internal source work | Full readiness |

Seventeen bounded public URLs succeeded: PyPI metadata, tag list, Git tree,
twelve Git-verified source files and two release metadata bodies. Acquisition
receipts and request timings are retained. One local fetch invocation rejected
the `.in` filename before any network request; its filter was corrected and both
package-data files were then acquired successfully. The source review and
`asset-records.json` state exact selected filenames and remote declarations.

No stochastic ranking applies. The strongest alternative explanation is that a
different resolved EasyOCR release or installed wheel changes selection or
asset packaging. That cannot overturn the pinned source reading but limits its
use in a future runtime claim. No continuation veto fired. The candidate failed
no source-identity criterion; missing bytes/rights are deployment vetoes and
reasons to continue separate preparation. Version 2.26 remains 168 pages and
SHA256 `d7c60268490921ec7edbc964ece351ebcdbd478ce422fa20b59de844e3ab48d7`.
Full readiness remains `not_ready`; independent/human/domain acceptance pending.
