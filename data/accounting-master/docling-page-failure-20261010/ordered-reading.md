# Version 2.24 adapter-section diagnosis

Baseline PDF SHA256:
`3ce23bc9b84d25f22d23d7b806c274ce302ca28f38c43c0afbdfca920ecb8211`.
PDF 137–140 were viewed separately at 120 dpi in order before candidate copy.
Section 13.13 occupies PDF 138–139, printed 131–132. This is author diagnosis.

Entry: The reader knows that corrected evidence makes earlier derived views
stale, that source/model/run identities have different contents, and that
adapters propose typed records rather than independently admit facts.

PDF 137 explains replay, Unicode, migrations and immutable bytes; the adapter
interface begins at its end and continues naturally onto 138. Missing headers
and failed pages are named unresolved, but no mechanism explains how a returned
conversion might conceal those failures. Section 13.13 then teaches double
scaling, dates, dimensions and lost context. It gives an excellent concrete
distinction between a returned amount and preserved evidence. The next turn,
however, jumps from individual field loss directly to external taxonomy
dependencies. It omits the analogous page-level failure now established in
the pinned Docling source: partial status can be returned without an exception,
and restored page keys can conceal the absence of extracted content.

PDF 139 already separates Arelle boolean success from validation and supplies
the later generic partial-conversion obligation. The new Docling example can
make that obligation testable without restating the old AD08 placeholder case.
Place it after the individual-field/source-audit paragraph and before the
taxonomy case: the progression becomes field preservation, page preservation,
dependency availability and validation meaning. No new equation is needed.
PDF 140 begins Chapter 14 with separate engineering, accounting and scientific
evidence. Preserve that transition and the distinction between design checks
and an executed adapter.

Exit: Field, page and dependency preservation need separate evidence; a typed
record must retain unresolved portions before accounting or scientific
acceptance is considered.

Cold-reader questions frozen before editing:

1. Can no exception with `raises_on_error=True` establish complete conversion?
2. Can three output page objects establish three processed source pages?
3. Can `PARTIAL_SUCCESS` occur with zero successful pages under the inspected
   timeout branch, and what exactly has the fragment diagnostic established?
4. How should a successful one-page request differ from a whole-document claim?
5. Does a reported timeout demonstrate that worker execution has stopped?

Adverse baseline answers: the general preservation language gives the intended
disposition but does not expose any of these API-specific traps. Add a bounded
source-attributed explanation and exact proposed exchanges; preserve the
existing mathematics, licensing boundaries, matched comparison and all other
reader-facing paragraphs. This repair concerns the proposal, not implementation.
