# Version 2.33: commitments before funding

12 October 2026. E01/E07/P18; MC01/02/03/08/10/15/16/21/28/30/32–35.
The separate 173-page candidate adds a source-grounded bank commitment
example after the simple allowance calculation. All 139 integration checks
pass. All inherited prose, 48 displayed equations and 74 bibliography entries
are preserved. Only the title and banking chapter change.

PDF: docs/design/proposal/manuscript-jpmorgan-commitments-20261012/accounting-product-proposal.pdf
SHA256: 48bce1dae3f6b23b88a540489d064258870250673a57fce0ae681cc7ce598496

The new table separates the issuer's contractual amount, allowance population,
commitment allowance and carrying value. Its explanation preserves the
different populations and measurement components, conditional cancellation,
gross/net participations and omitted parent guarantees. The Apple Card
forward purchase example preserves the commitment, announcement, reporting
and expected closing dates. Expected loans at closing are not treated as
loans already owned at year-end. No draw, default or liquidity probability is
inferred from reported totals.

The source unit passes 123 checks, including 50 documentary reconciliations
and 25 separate closeout checks. The candidate build took 15.791 seconds and
has clean TeX and bibliography logs. Eight ordered page images bind the
affected bank slice and following insurance opening. The new table and
explanation stay together on PDF page 119. The first integration checker had
one faulty text predicate; whitespace normalization repaired it without
changing manuscript or source evidence.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain Version 2.33 as current provisional candidate | Exact insertion, unchanged inherited text/displays/bibliography, 139/0 checks, rendered reading | No source mismatch or remaining layout/build failure | Independent-reader and domain acceptance | Continue source and method gaps | Full proposal readiness |
| Preserve distinct commitment quantities and clocks | Notes 13/28 and Executive Overview with exact anchors | Equating populations or future loans with current ownership is unsupported | Actual contracts, future close, draws and funding | Supply missing inputs before any later numerical forecast | A working or compliant bank forecast |
| Continue authority preparation | Issuer policy is informative but not operative ASC verification | No current-law or full ASC inference admitted | Exact Codification wording and applicable amendments | Inspect a new primary-source lead for commitment/guarantee treatment | Current US GAAP has been independently verified |

The strongest alternative explanation for apparent table discrepancies is a
population or measurement difference; the source explicitly supports that
explanation. A complete contract-level reconciliation would improve detail
without making the four quantities interchangeable. Full readiness remains
not_ready. Runtime implementation and the former controller remain held.
No installation, model run, GPU, outreach, publication or Git write occurred.
