# JPMorgan source findings in Version 2.27

11 October 2026. This is a bounded reader-facing repair of the 168-page
Version 2.26 candidate. The target reader should be able to explain why a
bank's parent liquidity cannot be inferred from consolidated cash, how a
qualified subsidiary list differs from a complete group graph, and why a
guarantee is a distinct exposure. The second repair lets the reader distinguish
eight consecutive reporting years from complete filing contents in the source
panel.

The source claims are bound to the closed JPMorgan semantic and Exhibit 21/22.2
units. Four official issuer 10-K citations will be added with page anchors.
The repair changes prose and bibliography only; it preserves every displayed
equation, numerical example, source qualification and existing source
boundary. It will create a new Version 2.27 tree, leaving Version 2.26 and its
PDF untouched.

## Argument state and evidence contract

The bank chapter currently moves from a generic bank package to equations
before showing the group boundary that makes funding ambiguous. The repair
introduces the observed JPMorgan parent/IHC/bank arrangement, the qualified
Exhibit 21 roster and Exhibit 22.2 guaranteed issuer, then returns to the
existing illustrative allowance and liquidity examples. The reader's belief
should change from “the bank balance sheet supplies the funding perimeter” to
“legal entity, funding path, guarantee and accounting perimeter are separate
state variables.” The source does not establish ownership percentages,
balances, recognition, or unrestricted transfer rights.

The validation chapter currently says “eight consecutive complete years per
issuer” beside a panel whose selected JPMorgan annual counterparts omit pages.
The repair says eight consecutive reporting slots/years at the acquisition layer,
then states that complete issuer 10-K supplements and semantic annotation are
separate. The panel count, equation and 244-version distinction remain intact.

Promotion requires an actual TeX/PDF delta, four source citations, preserved
equations and labels, a clean build, changed-page inspection and a cold-reader
answer for the two repaired transitions. Vetoes are source drift, deleted
qualifications/equations, unresolved citations, build errors, or a claim that
the supplements close the whole panel. Compilation and surface metrics are
diagnostics only; author review cannot satisfy independent or domain acceptance.

## Skeptical audit and pre-mortem

The main risk is that a polished example overstates a partial Exhibit 21 list or
turns “fully and unconditionally guaranteed” into a recognized liability.
The text therefore labels the issuer's description and states the missing
amount, ownership and accounting facts immediately. A second risk is that the
panel qualification sounds like a retraction of the accepted source inventory;
the repair keeps acquisition coverage and semantic closure as separate layers.
The smallest diagnostic is a source-to-sentence check against the 147-check
exhibit result and the 108-check semantic result before compiling.

## Verification

Build the copied tree with the repository's LuaLaTeX command. Run the scholarly
surface auditor, inspect the changed and adjacent pages at normal resolution,
compare the copied TeX against the protected baseline, and run focused checks
for equation/citation/label preservation. Record the four readability ledgers:
reader comprehension, mathematical integrity, source fidelity, and rendering.
End with `independent_reader_pending`; no readiness or implementation claim is
made by this repair.
