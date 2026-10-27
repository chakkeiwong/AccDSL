# Unpaid coupon carry evidence contract

27 October 2026. Implements accounting-coupon-carry-20261027.md. Its skeptical
audit passes. The upstream verified record is an externally identified premise;
its full bytes and verifier dependencies are locked. The selected wrapper binds
the saved record, complete report, period and all-preserve memory policy before
calling the existing carry engine. Current-record consistency is checked, not
inferred from balanced books. The zero-coupon debt contract is not reused.

Expected result: six eligible final-day cases across two charts, four June 30
refusals unassessed for carry. In receipt-6 draw/pay and draw/draw, closing removes
income -6, interest expense 181/16 and fee expense 1/4, and posts 89/16 to the
signed equity account. Cash 85/16 and coupon payable -43/8 remain; next-period
flows are empty; original flows/seen events and refusal are preserved in the
bound archive. All memory fields, especially used=true, are unchanged. Receipt-7
draw/pay supplies the settled control. Negative equity does not block a valid
book or establish legal default. No fiscal or source admission follows.

Primary criteria: independent exact closing journal, closed state, opening,
archive fields and new-opening report. Check original accepted execution and
report once per retained case, with native fallback disabled. A generic typed
reset can pass its own engine; the selected wrapper must reject it. Stale report,
changed history, changed liability, missing/reset policy, reused close ID, wrong
date and invented admission are controls. No new funding or settlement event.

At most three fresh 120-second CPU attempts, GPU hidden. Preserve failure records,
complete results, source locks and manifest. Avoid duplicating the large upstream
trace in outputs: retain its external hash and file path, and full changed states.
