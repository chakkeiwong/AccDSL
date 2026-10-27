# Baseline diagnosis before candidate creation

Target: a developer of the proposed accounting adapter who understands typed
records and can distinguish returned pages from processing evidence. The repair
is Section 13.13, entered from Sections 13.11–12, with adjacent page regression.
Canonical baseline is the frozen 168-page Version 2.25 and its 48 source files.
Its PDF hash is `caf4a818348b2a9df9c6943c2e9dcefd811ec302caaf91918db8d07541a624fc`.
The prior manifest binds its clean compiled PDF and rendered pages; reuse that
checked baseline rather than rebuild into the frozen manuscript directory.

Read the actual prior final renders, PDF pages 137–140, in order at full page
resolution, two images per call. This is an author diagnosis, not an independent
review or a whole-chapter read.

Page 137 establishes identity across schema/record changes and introduces typed
exchanges. The reader enters page 138 knowing why tool IDs and transformations
must preserve provenance. Page 138 moves from the adapter roles to a concrete
double-scaling error, context loss and returned-page incompleteness. The open
question at its end is what processing actually happened to those pages.
Page 139 completes the subset/termination distinction, then moves to retained
taxonomy dependencies and Arelle loading. It later says models must be pinned,
but supplies no example distinguishing an OCR request from an OCR engine that
actually ran. Page 140 distinguishes code and component terms; that material
must survive unchanged.

| Anchor | Missing explanation | Bounded repair | Source-fidelity risk |
| --- | --- | --- | --- |
| PDF 138–139, after page-outcome discussion | OCR enabled may be read as OCR performed | Explain the auto no-engine warning/pass-through branch and require engine/outcome evidence | Must preserve the language-error branch and avoid claiming an observed Apple failure |
| PDF 139, model pinning sentence | Code revision may be read as fixing model bytes or preventing network use | Explain Heron `main`, TableFormer tag, local directory identity and distinct remote/download controls | Must not generalize all-stage offline guarantees from a single helper |

Argument: returned pages can omit requested work; an OCR stage can also remain
unperformed; identifying the stage requires its engine and exact model bytes;
the following taxonomy example then extends the dependency argument to facts.
The new text adds these two explanatory steps without replacing the page,
financial-context or licence arguments. No display or mathematical claim changes.
Detailed options/dependencies stay in the source packet.

Before-edit reader questions:

1. Can OCR be requested while no engine processes the pages, and what evidence
   distinguishes that condition from successful OCR?
2. Why does a code commit fail to determine the layout model's bytes?
3. What does disabling remote inference actually leave unresolved?
4. Which checks belong to source inspection, and which require later execution?

All old prose, 48 displays, 67 bibliography entries and existing source
qualifications must survive. Add only two paragraphs plus the version increment
in a separate Version 2.26 tree. Continue provisional preparation while human
and independent acceptance remain pending.
