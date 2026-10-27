# Bank chapter: parent income is not parent funding

12 October 2026. E01/P18; MC01/02/03/05/08/15/16/28/30/32–35 and
G4/G5/G7/G11/G13. Protected baseline: Version 2.34, 173 pages, SHA256
2546dfc7cb6ead7a1cf1b9a95a74bc1f6b625d604a6a95440c5730df2b3ea8cb.
Source: the closed JPMorgan 2025 Note 33 unit with 74 source/arithmetic and
60 closeout checks, plus its PDF 21 Item 1A funding restriction. Make a
separate Version 2.35 candidate; do not overwrite Version 2.34.

The target implementer has just read the parent/IHC transfer restriction and
asks what the reported parent-only statements reveal about cash available for
payments. Insert one concise numerical bridge before the existing instrument
term discussion. It should let the reader distinguish (1) reported parent-only
net income, (2) the cash-flow starting reconciliation and dividends, (3) cash
and deposits, and (4) equity investments and intercompany claims. The source
and later-funding boundary belongs in the same paragraph. The example is
historical issuer evidence, not a forward payment-capacity forecast.

Evidence contract: exact preservation of all inherited prose except the
bounded insertion and candidate title; all 48 displays; all 75 bibliography
entries; resolving citations and labels; clean LuaLaTeX/bibliography logs;
legible ordered renders of the affected bank pages and transition; four-ledger
author review. The primary pass criterion is that the rendered paragraph is
accurate, in the right argument position, and does not conflate those four
quantities. Counts/page length are diagnostics, not comprehension or accounting
promotion. An exact source mismatch or detached qualification vetoes this
candidate until repaired. Independent/human/accounting acceptance stays open.

Default and assumption audit: the 2025 parent-only figures are issuer-reported
US$ millions in the retained edition, not assumed unrounded values or current
cash. The existing bank paragraph supplies legal transfer conditions, but it
cannot quantify permitted future transfers; the new paragraph must not supply
an invented amount. The source unit's 2023 one-million displayed residual is
irrelevant to this 2025 illustration and remains recorded in the source result.
The existing TeX engine/style is an inherited build convenience, supported by
the clean Version 2.34 build; rerun and inspect rather than assume it holds.

Skeptical audit passes for a bounded provisional document integration. The
wrong baseline would be the earlier Version 2.27 guarantee-only candidate or
the consolidated cash balance. The exact 2.34 hash and Note 33 source ledger
prevent both. The dangerous proxy is a numerical reconciliation mistaken for
freely transferable parent funds. Read the footnote and funding restriction
beside the new paragraph and ask whether a prepared reader can identify the
missing future dates and transfer conditions. Stop only for source identity,
arithmetic, preservation or rendered legibility failure, then repair the
bounded candidate. No stochastic comparison, default change, GPU run,
installation, paid review, outreach, publication or Git write is in scope.

Artifacts go under
data/accounting-master/accounting-proposal-v235-integration-20261012/ and
docs/design/proposal/manuscript-parent-cash-20261012/. Preserve pre-update
control bytes in the unit, build once with the existing LuaLaTeX recipe, run
exact preservation/source checks, and inspect the changed and adjacent PDF
pages. Update the four live controls only after the candidate passes.

Reader checks: Which figure is net income and which is operating cash? Why
does the parent cash-flow statement subtract subsidiary income? How much cash
and deposits does the parent report, and what does the time-deposit footnote
add? Why is the equity investment not available cash? What conditions remain
before a future debt-service conclusion? No new equation is needed.

The first build placed only the tail of the instrument paragraph on the next
page. A layout-only `\\newpage` at the source-argument boundary separates the
parent cash example from the existing instrument-term discussion. Rebuild and
inspect before acceptance; page count remains a diagnostic.
