# Docling page outcomes and partial conversion

10 October 2026. E14/C07/C08; MC23–25/27–29/31–35; G5/G8/G11/G14/G17–18.
Active scope is proposal preparation. Product implementation remains held.

## Question and research intent

Can the pinned Docling API's return, status and document-page count establish
that all requested pages were converted? The candidate is the proposed
exchange record: independent source-page inventory, requested page set,
successfully processed pages, placeholders, structured errors and unprocessed
frontier. The expected failure is a permissive success signal concealing zero
or partial extraction. The prior AD08 fixture already illustrates placeholders;
this unit must add the inspected status/exception path, including a timeout
before any page finishes, rather than repeat that fixture unchanged.

Baseline: frozen Version 2.24 and the source audit at
`docs/design/proposal/methods/preparation-20261005-v1/03-adapters`, specifically
Docling commit `eda5b5fc86d10b2b79a900ff3e69fc159d5f6014`, declared version
2.133.0. The naive comparator is accepting no exception, `PARTIAL_SUCCESS`, or
the document's page count as complete conversion. No software is installed.

| Evidence role | Contract |
| --- | --- |
| Primary pass criterion | Bind the inspected status/exception/page paths to exact code bytes and supply source-derived exchanges that preserve the requested/processed/missing distinction, including zero-success timeout. |
| Promotion veto | Wrong source pin; generic placeholder example presented as new evidence; a fragment probe described as an installed backend run; silently dropping page failures or treating page placeholders as extracted content. |
| Continuation veto | Corrupted retained source or a claim whose necessary call path cannot be checked. Restrict that claim or acquire its missing source before proceeding. |
| Repair trigger | A counterexample to a proposed acceptance signal requires correcting the proposal's exchange/failure explanation. |
| Explanatory diagnostics | Page counts, status names, source searches and isolated method outputs nominate/explain failures; they are not extraction accuracy or compatibility evidence. |
| Non-conclusions | No actual Apple extraction failure, installed-package compatibility, OCR accuracy, performance, thread cleanup success, model/dependency clearance or full E14 acceptance. |
| Preserving artifact | `data/accounting-master/docling-page-failure-20261010/`: baseline, source anchors, probe/fixtures, result, manifest and any bounded manuscript regression. |

The target reader is an implementer who must decide what a proposed conversion
record can admit. The bound manuscript unit is Section 13.13 and its adjacent
pages. Diagnose the rendered baseline before editing a separate candidate;
retain every previous display, citation and qualification. Add prose only if
the API counterexample materially sharpens the existing preservation rule.

## Skeptical audit and defaults

The initial status-only approach is wrong: inspected `_integrate_results`
selects `PARTIAL_SUCCESS` for timeout with positive expected pages before the
complete-failure branch, and `convert_all` yields partial success even when
`raises_on_error=True`. `_add_failed_pages_to_document` restores missing page
numbers with empty page objects. A timeout also does not by itself establish
worker termination; the source uses bounded joins. None is an observed runtime
failure here. These are the discriminating paths to inspect completely.

The revised plan passes the skeptical audit because its comparator and output
are documentary interface claims. It will execute only selected exact methods
with disclosed stand-ins, never the library modules or model/backend code.
Reachability is checked separately in the retained caller. A source-derived
probe cannot establish the behavior of an installed package. No proxy becomes
a product-promotion criterion. The 1062-reference preceding manifest and live
pointer copies must verify before writing candidate artifacts.

| Choice/provenance/status | Justification | Risk and early diagnostic |
| --- | --- | --- |
| Retained Docling pin, reviewed source baseline | Existing official-source register provides full hashes | Mixed revisions: validate every selected file against the same recorded commit. |
| Three requested pages, convenience fixture | Smallest useful all/partial/none page partition | Not a real filing measurement: label every outcome synthetic and bind the actual method fragment separately. |
| Isolated exact methods, diagnostic only | Exercises the branch under review without installing models or running product code | Stand-ins may omit framework behavior: enumerate them and limit conclusions to method bodies and inspected caller. |
| Timeout flag and failure lists supplied explicitly | Distinguishes status precedence from OCR/timing performance | Impossible state: inspect caller's missing-page completion before declaring reachability. |
| Plain retained default `raises_on_error=True` | Material upstream API choice under audit, not an AccDSL default | No exception may be misread as complete success: test partial and complete-failure cases. |

## Execution and stop conditions

1. Preserve the prior manifest and four live-pointer bytes; verify the retained
   register, converter, pipeline, result/status schemas and declared dependency
   metadata. Read the full relevant methods/caller and record source anchors.
2. Run `CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3
   data/accounting-master/docling-page-failure-20261010/probe.py`. Use only the
   standard library and selected AST method bodies; no library imports, GPU,
   network, models, background threads or installation. Compare all-complete,
   partial-failure, zero-success-timeout and complete-failure cases. Keep
   requested subsets distinct from whole-document coverage.
3. Record the exchange contract, observed fragment outcomes, source-only
   implications and remaining dependencies separately. If warranted, copy the
   48 manuscript sources into Version 2.25, add the bounded explanation, build
   with the normal LuaLaTeX command and inspect all affected/adjacent pages plus
   navigation. CPU PDF tools and the existing temporary TeX cache suffice.
4. Record decision/inference tables, preservation checks and exact commands;
   update current controls without changing frozen requirements or controller
   state. Continue the next internally feasible obligation.

Pre-mortem: the probe could pass because a stand-in supplies the answer or
because an impossible state bypasses the real caller. Execute retained method
bodies unchanged, identify the injected objects and inspect branch reachability.
It could also appear to close dependencies while recording version ranges;
declared ranges must remain separate from an exact installed/transitive lock.
Any source conflict reopens the affected claim; it does not reject Docling's
separate role as a layout candidate.

## Caller-source revision before probing

The retained converter delegates to `pipeline.execute`, whose base-class body
is absent from the old source packet. A method-only result cannot establish
the intervening call path. Acquire the exact pinned
`docling/pipeline/base_pipeline.py` from the official raw repository at the
same commit, preserving URL, headers, bytes and receipt. This is a new source
route, not a retry of an unavailable paper or filing. Allow at most two new
source paths and one trusted retry per sandbox network failure, with a
45-second request deadline. Inspect the base execution/status handling before
claiming that a partial result can reach `convert_all`. Failure blocks that
broader claim but permits the explicitly conditional fragment result. The
diagnostic itself remains offline and imports no Docling package.

## Final execution record

Five exact-method fragment cases pass 35 checks. Version 2.25 adds the bounded
page/subset/termination explanation and one pinned-source citation. All 23
candidate/preservation checks pass; 48 displays and all 66 earlier bibliography
entries survive unchanged. The final five-page unit, navigation and new
bibliography page were inspected at 120 dpi. No installed library, OCR/model,
worker or termination experiment ran. Exact locks/models/terms and broader E14
acceptance remain open. The result and run manifest preserve the source receipt,
disclosed stand-ins, command/timing limits and four live-pointer relocations.
