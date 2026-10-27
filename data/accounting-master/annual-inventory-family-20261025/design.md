# Annual inventory scenario families, finite profile 1

AnnualInventoryFamily/1 binds one checked root request, consecutive periods,
ordered named members, explicit assumptions and a member-run budget. Each
member compiles through AnnualInventoryAuthoring/1 and executes its exact
AnnualInventoryProgram/1 request. Validation itself executes no finances.

The common root is executed even for an empty selection or zero budget.
Unavailable root means no member is visited. Unvisited members retain identity,
assumptions and request digest with no result. Evaluated failures retain their
valid prefix and all remaining operations. Member limits and period limits are
64. Budget is an explicit integer between zero and 64; booleans are invalid.

AnnualInventoryReports/1 recomputes the saved family before returning the whole
archived or current-prefix statement vector for a requested declared period.
Unreached periods have no report, not a numeric zero. Equal outputs never merge
separately named members. No probabilities, actual-history membership or exhaustive
feasible coverage are asserted. Tax and accounting admission remain false.

The adapter preserves frozen family behavior for old-only operations, except
explicit new profile and content hashes. Financial comparisons omit only these
named result fields: profile, optional_inventory_reference, request_sha256,
source_bundle_sha256 and implementation_sha256. All remaining fields, including
entire books, traces, statements, refusals and unresolved findings, must match.
