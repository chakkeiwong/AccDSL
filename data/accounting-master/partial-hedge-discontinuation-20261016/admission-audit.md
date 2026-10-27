# Pre-run loss-recoverability admission repair

The first fixture freeze retained separate stopped-reserve loss amounts and
later continuing-reserve recoverability, but did not explicitly admit
recoverability before discontinuation or for the continuing portion at that
instant. Qualification alone does not establish recoverability under
IFRS 9.6.5.11(d)(iii). A negative reserve could therefore appear to pass while
an omitted earlier loss should already have entered earnings.

Before any calculator execution, add explicit Boolean findings
`baseline_reserve_recoverable` and `continuing_reserve_recoverable` at those
two boundaries. False/unknown requires a different prior-history method or
unresolved result. The stopped part's later loss assessment remains explicit
and can change on new facts. No expected amount or accounting formula changes.
Preserve v1 fixture/lock and write v2 successors. The calculation uses v2.
This repairs an admission condition, not evidence against the source method.
