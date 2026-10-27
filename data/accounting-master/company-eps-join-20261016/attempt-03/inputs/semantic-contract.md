# CompanyEPSJoin/1 — finite documentary bridge

The bridge supplies an OrderedEPS/1 request from the protected P5 company plus
the separately authored July-to-October compound instrument. It supports only
the maturity-conversion and cash-redemption worlds in `premises.json`. It does
not migrate P5 state or change its authorization/commit interfaces. All files
are documentary calculations; no book is changed.

The closed request is `{wire, operation, world, base_packet, premises, eps}`.
`wire` is `CompanyEPSJoin/1`, `operation` is `report`, and `world` is `conversion`
or `redemption`. `base_packet` is a support record with exactly `path`, `sha256`
and `anchor`, referencing the protected CompanyComposition/1 attempt03 packet.
The packet digest is pinned to the predecessor manifest's attempt03 entry,
not calculated anew as a trusted value. The caller resolves the referenced bytes.
`premises` has exactly the fields in `premises.json`; quantities are reduced
rational strings, dates are ISO dates and findings are Booleans. Null findings
mean unresolved. A different known contract, tax-base treatment or unsupported
scope returns unsupported. Incomplete inventory/share history/consequences
remain unresolved even when explicitly false. Unknown/missing fields reject.
`record-schemas.json` provides the complete closed Request/Result schemas.
`eps` is the closed
OrderedEPS/1 request, with the complete projected amounts, context and windows.
This interface deliberately verifies a proposed projection against the company's
replayed financial records; it cannot validate arbitrary externally supplied books.

The base reference must match the exact locked P5 packet, and every protected
base/source calculator file must still match its lock. Missing bytes are
unresolved and mismatching bytes reject. Source and premise truth remains a
supplied finding. Live book freshness outside this immutable documentary context
requires the later runtime resolver.

Replay P5's independent legal calculations, then merge the new issue, accrual,
coupon and settlement chronologically. Recalculate parent second-half tax from
actual merged pretax income and the original returns timing adjustment, less tax
already paid. Preserve the subsidiary, original matured debt and original
deferred-tax effects. Consolidate the full merged books, eliminating internal
sales/receipts/payments and the parent investment; NCI uses the unchanged
20%/10% ownership periods. The EPS numerator is group profit minus NCI profit,
not the parent's separate profit or total group profit.

Construct weighted shares by replaying each day in the 365-day reporting year.
Potential shares exist July1–October1 in both worlds. Actual conversion shares
exist October1–January1 only in the conversion world. Hash the closing legal
books for the head and the complete supplied premises for the evidence view;
bind entity/group population, dates, share class/basis/currency to the same EPS
context. Compare every proposed EPS field to that independently derived request
before invoking OrderedEPS/1. A wrong numerator, date, period, head, view,
inventory or weighting therefore rejects even if its own context hash agrees.

The closed result is `{wire, request_sha256, status, company, eps, issues,
mutations, acceptance}`. Status is `conditional_complete`, `unresolved`,
`unsupported` or `rejected`. Company is the exact closing-books/financials/
timeline/cash/daily-share record written by the reference calculator, or null
when its own inputs fail. EPS is the complete OrderedEPS/1 result, or null.
Issues are reason strings. Mutations is always the empty array; acceptance is
`conditional_documentary_only`. A wrong proposed EPS projection can preserve
the independently derived company result while returning null EPS. Missing or
unsupported company premises leave both null. The canonical request digest is
SHA256 of sorted compact UTF-8 JSON with ASCII escaping and no newline.

The result is deterministic conditional arithmetic for this finite case. No
whole-profile migration, arbitrary company, early-conversion measurement,
different tax-base treatment, current-law admission or runtime result is claimed.
