# Page-result call path at the retained Docling pin

Source pin: `eda5b5fc86d10b2b79a900ff3e69fc159d5f6014`, declared package
`docling-slim` 2.133.0. The original source register supplies the converter,
pipeline, datamodel, options, dependency metadata and MIT licence. The newly
retrieved base pipeline comes from the same official commit. Exact paths,
line ranges and hashes are recorded in `source-anchors.json`.

The caller constructs one page per expected number, records successful and
failed pages separately, and marks the remaining pages failed after timeout
(`StandardPdfPipeline._build_document`, lines 809–989). Thus positive expected
pages, no successes, all pages failed and a timeout flag are consistent with
the inspected builder. A zero-page requested range instead returns failure
early; it must not be fed to the integration branch as if it were equivalent.

`ProcessingResult` defines partial success by the count of successful pages.
However, `_integrate_results` checks timeout first: with positive expected
pages it assigns `PARTIAL_SUCCESS`, even when no pages succeeded. Without
timeout, no successes and at least one failure yields `FAILURE`. The page list
is filtered to successful processing; structured errors remain separate.

`_assemble_document` calls `_add_failed_pages_to_document`. That helper inserts
empty `PageItem` objects for missing expected numbers, using known dimensions
or zero dimensions. Those objects preserve numbering; their presence does not
establish extracted text or table content. Original page inventory, requested
range, successful processing and document-page keys therefore answer different
questions. `get_expected_page_nos` clips the requested interval to actual page
count: success on a subset cannot establish whole-document processing.

The base `execute` runs build, assembly, enrichment and status determination.
If they complete, it preserves partial status and also changes a success with
errors to partial success. Exceptions have a different path, and unloading is
called in `finally`. The standard pipeline's status method returns the stored
status. The converter then yields success **or partial success** with
`raises_on_error=True`; it raises for other returned statuses. Consequently
absence of an exception cannot be the adapter's completeness criterion.

The probe executes retained integration, status, expected-page, base-execution,
placeholder and converter methods. The builder supplies synthetic outcomes;
assembly supplies successful placeholder objects then calls the exact missing
page helper. It does not execute the reading-order model, OCR, page backend,
threaded builder or full assembly. Results show the specified method decisions,
conditional on these supplied stage outcomes, not a real zero-page backend run.
The source inspection establishes the timeout-state construction separately;
end-to-end assembly and installed compatibility remain untested.

Worker termination is a separate obligation. `ThreadedPipelineStage.stop`
joins with a timeout and can log that the thread remains alive; the builder
also bounds the producer join. The diagnostic starts no threads. A reported
timeout is not evidence that all work or resource use stopped. Later process
isolation and termination checks need implementation authority and a separate
execution contract.

The declared dependency file identifies `docling-slim`, despite the repository
being named Docling. Its comment says eight base packages but the array contains
nine; the array is authoritative for this inventory. Optional extras, range
constraints and a build requirement do not identify an installed lock, weights,
transitive licences or supported compatibility. No such admission is made.
