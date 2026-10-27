from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'coupon-continuation-integration-20261027/advance.py').read_text()
changes={
 'gap-viability-integration-refresh-20261027':'gap-coupon-continuation-refresh-20261027',
 'gap-coupon-continuation-refresh-20261027':'gap-coupon-scope-refresh-20261027',
 'accounting-coupon-schedule-invariant-20261027.md':'accounting-coupon-program-resume-20261027.md',
 'accounting-refused-payment-reporting-20261027.md':'accounting-coupon-schedule-invariant-20261027.md',
 'accounting-coupon-continuation-integration-20261027.md':'accounting-coupon-scope-integration-20261027.md',
 'data/accounting-master/coupon-partial-settlement-20261027/result.md':'data/accounting-master/coupon-continuation-scope-20261027/result.md',
 '5.45;821 pages;not_ready':'5.46;823 pages;not_ready',
 '5.46;823 pages;not_ready':'5.47;824 pages;not_ready',
 'Version 5.46 integrates refused reporting, carry and partial payment; 5.45 preserved.':'Version 5.47 integrates schedule invariants and continuation scope; 5.46 preserved.',
 'Version 5.46 integrates refused reporting, carry and partial payment; independent acceptance pending.':'Version 5.47 integrates schedule invariants and continuation scope; independent acceptance pending.',
 'distinguish the algebraic schedule result from runtime and history compatibility.':'verify selected multi-event resume with original opening, exact prefix and cumulative budgets.',
 'After the coupon invariant, audit which future queries and methods distinguish equal balances with different dated histories; do not merge on financial totals alone.':'Retain the checked date/replay counterexamples; audit compression only for explicitly named future methods, queries and resource scope.',
 'Version 5.46 integrates all three coupon companions; continue bounded consistency repairs and independent reader/domain/whole-document review.':'Version 5.47 integrates schedule and continuation limits; continue bounded consistency repairs and independent reader/domain/whole-document review.',
 'Derive partial-payment schedule invariants':'Check bounded same-period program resumption',
 'Refused reporting, carry and partial payment integrated; general schedule invariant next; no whole requirement closure.':'Schedule invariant and continuation limits integrated; selected program resume next; no whole requirement closure.',
 'Version 5.46: refusal, carry and partial payment; 792 checks; not_ready.':'Version 5.47: schedule invariant and continuation limits; 803 checks; not_ready.',
 '**5.46**, 823 main pages':'**5.47**, 824 main pages',
 '257 total / 236 body pages':'258 total / 237 body pages',
 'Refused-payment reporting, selected year-end carry and explicit partial settlement':'Exact payment-schedule invariants and checked continuation limits',
 'are integrated. All 792 document checks pass, preserving':'are integrated. All 803 document checks pass, preserving',
 '275 sources and 224 evidence files':'276 sources and 233 evidence files',
 '## Refusal and later settlement integrated — 27 October 2026':'## Schedule and continuation scope integrated — 27 October 2026',
 'Version 5.45, 821 pages':'Version 5.46, 823 pages',
 'Version 5.46, 823 pages':'Version 5.47, 824 pages',
 '**255 pages**':'**257 pages**','**257 pages**':'**258 pages**',
 '**234 body pages**':'**236 body pages**','**236 body pages**':'**237 body pages**',
 'viability-integration-20261027/result.md':'coupon-continuation-integration-20261027/result.md',
 'coupon-continuation-integration-20261027/result.md':'coupon-scope-integration-20261027/result.md',
 '# Full closure program after coupon continuation integration':'# Full closure program after coupon scope integration',
 'Version 5.46; all 18 packages remain open.':'Version 5.47; all 18 packages remain open.',
 'Exact source preservation, complete state comparisons and bounded rendered review support provisional 5.46. Schedule generality remains unproved by the finite examples.':'Exact source preservation, checked recurrence and complete-state comparisons support provisional 5.47. General program resume remains open; the current continuation is an explicitly selected single step.',
 'Three coupon method deltas and one integration delta added without duplicate credit.':'Two schedule/scope method deltas and one integration delta added without duplicate credit.',
 '.v546.tmp':'.v547.tmp','.v546-link':'.v547-link',
 'v["checks"] == 792':'v["checks"] == 803',
 'len(audit["successor_deltas"]) == 116':'len(audit["successor_deltas"]) == 119',
}
for k in changes:assert k in s,k
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
start=s.index('for title, evidence, disposition in [');end=s.index(']:',start)+2
s=s[:start]+'''for title, evidence, disposition in [
    ("Partial-payment schedule invariant", "data/accounting-master/coupon-schedule-invariant-20261027/result.md", "20 runtime cases, 517 assertions and 8 controls; exact recurrence induction and resource limits separated."),
    ("Coupon continuation scope", INTERNAL, "24 continuation cases, 514 assertions and 10 controls; date and replay distinguish equal financial balances."),
    ("Coupon scope manuscript integration", RESULT, "803 checks preserve 276 sources and 233 evidence files; covers and added pages reviewed; independent acceptance pending.")]:'''+s[end:]
s=s.replace('coupon_partial_result=INTERNAL, coupon_carry_result="data/accounting-master/coupon-carry-20261027/result.md", refused_reporting_result="data/accounting-master/refused-payment-reporting-20261027/result.md",',
 'coupon_scope_result=INTERNAL, coupon_schedule_result="data/accounting-master/coupon-schedule-invariant-20261027/result.md",')
s=s.replace('for result in ("data/accounting-master/refused-payment-reporting-20261027/result.md", "data/accounting-master/coupon-carry-20261027/result.md", INTERNAL, RESULT):',
 'for result in ("data/accounting-master/coupon-schedule-invariant-20261027/result.md", INTERNAL, RESULT):')
assert not (H/'advance.py').exists();(H/'advance.py').write_text(s)
print('Prepared 5.47 three-delta advancement')
