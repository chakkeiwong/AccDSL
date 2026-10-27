# Pinned PDF model and dependency findings

The target is a reproducible proposed PDF conversion, not a library installation.
Source anchors bind complete relevant constructors/helpers at Docling commit
`eda5b5fc86d10b2b79a900ff3e69fc159d5f6014`. The source map supports the following
claims. None was inferred from an installed package or an extraction run.

1. **Backend.** `PdfFormatOption` selects `StandardPdfPipeline` and
   `ThreadedDoclingParseDocumentBackend`. The retained backend includes the
   threaded implementation and compatibility subclass. The backend guards the
   optional `docling_parse` import and raises when unavailable. Its parser thread
   count uses explicit `parser_threads` or a separate `AcceleratorOptions()`;
   pipeline accelerator settings alone do not fix parser threads.
2. **Layout.** The PDF default is `LayoutObjectDetectionOptions`, not deprecated
   `LayoutOptions`. It selects Heron and a Transformers engine. The model preset
   identifies `docling-project/docling-layout-heron@main`. The ONNX override names
   another repository. A code commit therefore does not fix layout weight bytes.
   Preprocessor configuration, labels, weights, dtype and compilation behavior
   also matter; score threshold 0.3 is an inherited hypothesis, not measured
   suitability for financial statements.
3. **Local paths.** The shared layout resolver downloads when `artifacts_path`
   is absent. With a supplied root it requires the repository-specific folder,
   or raises; it does not fall back to downloading in that helper. Merely finding
   the folder does not compare the bytes with the requested revision. Later
   loading checks `preprocessor_config.json` and reads model configuration and
   weights. No end-to-end no-network behavior has been tested.
4. **TableFormer.** Enabled by default with cell matching and ACCURATE mode,
   it uses `docling-project/docling-models` at tag `v2.3.0`, under
   `model_artifacts/tableformer/accurate`. The local root may contain
   `docling-project--docling-models`; a legacy subdirectory form is also accepted.
   `tm_config.json` configures `docling_ibm_models`' `TFPredictor`. Its exact weight
   filenames, loader behavior and transitive model/package terms remain unchecked.
   A tag is more specific than `main` but is not a retained immutable asset hash.
5. **Download scope.** The shared HF helper calls `snapshot_download` with
   repository and revision, without an `allow_patterns` restriction or
   `local_files_only` argument. The table helper therefore does not itself limit
   acquisition to the accurate-table directory. Its elapsed-time cache-hit log
   is a heuristic, not evidence that no request occurred.
6. **Remote services.** The object-detection factory passes
   `enable_remote_services` only to the remote KServe engine, not local
   Transformers/ONNX constructors. The OCR constructor likewise passes it only
   to KServe OCR. Setting it false is not a model-download prohibition.
7. **Automatic OCR.** The inspected priority is ocrmac on Darwin; Nemotron on
   Linux; then RapidOCR/ONNX, EasyOCR and RapidOCR/Torch when no engine has been
   selected. Platform, availability, language and selected runtime failures can
   change the result. This differs from the options docstring's EasyOCR/Tesseract
   example; the actual auto constructor has no Tesseract branch. Direct
   Tesseract selection is a separate available factory option.
8. **No engine.** If no engine is selected and there were no language-specific
   rejections, the auto constructor logs a warning. Its call yields the original
   pages when `_engine is None`. Thus `do_ocr=True` does not prove OCR occurred.
   Language-specific aggregate failure raises instead; these cases must remain
   distinct. Other exceptions can propagate. No actual filing failure is claimed.
9. **EasyOCR.** The wrapper resolves languages, chooses CPU/GPU, and passes
   `model_storage_directory`, `recog_network` and `download_enabled` to
   `easyocr.Reader`. A non-null artifact root disables downloads only when the
   separate storage directory is unset. Setting both explicitly leaves the
   explicit download flag in effect. The proposed OCR arm sets it false directly.
   Docling's prefetch helper obtains URLs/filenames from installed EasyOCR
   configuration and skips already present files; it supplies no exact package
   or weight identity here. English maps to `english_g2` in the wrapper's
   prefetch mapping; the actual Reader's chosen files still need upstream audit.
10. **RapidOCR.** A supplied artifact root leads to explicit local-file checks;
    absent assets raise there. Without a root, the third-party reader manages
    model resolution. Late `rapidocr_params` override the assembled parameters,
    so the preceding checks do not validate arbitrary overridden paths. The
    wrapper's registry lookup depends on the installed RapidOCR package. This
    unit does not establish all downstream behavior or all OCR asset names.
11. **Settings.** Accelerator settings include DOCLING/OMP environment inputs.
    Compilation is supplied by the settings object. Explicit device, parser and
    model threads, dtype and compilation choices are proposed below; they are
    conveniences for a later baseline, not a performance recommendation.
12. **Packages.** The declaration is `docling-slim` 2.133.0, with nine base
    dependencies. Recursive expansion of the selected extras gives 20 declared
    requirements for the native-text proposal and 22 with EasyOCR. These are
    requirement strings, not solved distributions or a proof of import
    sufficiency. In particular Transformers is not directly listed in this
    selected expansion; any transitive supply and eager imports remain unverified.
    The broader `standard` extra includes unrelated formats and is not silently
    adopted. Package, model and data terms remain separate.

## Proposed preparation records

`configuration-records.json` preserves two **non-executable hypotheses**: native
PDF text with OCR disabled, and an English scanned-page arm with explicitly
selected EasyOCR. Both retain layout and table requirements. OCR disabled does
not remove learned layout/table stages. Neither proposal is ready to run: model
commits, file hashes, exact dependency resolution, terms and target-specific
budget/quality checks remain required. Other languages are not covered by the
English arm. Automatic OCR remains a comparator whose selected engine must be
observed, not a preferred configuration.

## Acquisition and execution limits

Twenty-seven distinct public URLs were used: one source tree, 25 raw source
paths and one immutable blob route. One raw re-export request timed out after
45 seconds in trusted execution and returned no body. The tree's immutable blob
route recovered that source, whose Git blob identity matched. All 25 unique
new Python source bodies match the pinned tree. The tree request first failed
with sandbox DNS resolution; its one trusted retry succeeded. No failed raw
URL was repeated unchanged. No package, weight or document was downloaded.

An initial local register verification used the wrong relative-path base and
raised before writing its output. Resolving paths against the retained packet
corrected it; all thirteen existing Docling entries then verified. The plan's
initial mistaken statement that only the non-threaded backend was retained was
corrected before acquisition. No retained source or prior manifest was changed.

## Red-team interpretation

The strongest alternative explanation for a later apparent discrepancy is an
unresolved dependency/version or explicit override, rather than an error in
these Docling branches. A different audited code/weight combination could
remove a particular failure path. The weakest evidence is downstream loading:
this audit stops at third-party calls and does not establish import compatibility,
complete download behavior, extraction accuracy or permission for distribution.
Those limitations block promotion of a configuration; they do not block the next
metadata/terms preparation unit.
