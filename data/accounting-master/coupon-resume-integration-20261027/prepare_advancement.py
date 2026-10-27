from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'coupon-scope-integration-20261027/advance.py').read_text()
changes={
 'gap-coupon-continuation-refresh-20261027':'gap-coupon-scope-refresh-20261027',
 'gap-coupon-scope-refresh-20261027':'gap-coupon-resume-refresh-20261027',
 'accounting-coupon-program-resume-20261027.md':'accounting-credit-claim-continuity-20261027.md',
 'accounting-coupon-schedule-invariant-20261027.md':'accounting-coupon-program-resume-20261027.md',
 'accounting-coupon-scope-integration-20261027.md':'accounting-coupon-resume-integration-20261027.md',
 'data/accounting-master/coupon-continuation-scope-20261027/result.md':'data/accounting-master/coupon-program-resume-20261027/result.md',
 '5.46;823 pages;not_ready':'5.47;824 pages;not_ready','5.47;824 pages;not_ready':'5.48;825 pages;not_ready',
 'Version 5.47 integrates schedule invariants and continuation scope; 5.46 preserved.':'Version 5.48 integrates selected same-period resumption; 5.47 preserved.',
 'Version 5.47 integrates schedule invariants and continuation scope; independent acceptance pending.':'Version 5.48 integrates selected same-period resumption; independent acceptance pending.',
 'Version 5.47 integrates schedule and continuation limits; continue bounded consistency repairs and independent reader/domain/whole-document review.':'Version 5.48 integrates selected resumption; continue bounded consistency repairs and independent reader/domain/whole-document review.',
 'Check bounded same-period program resumption':'Check bank credit schedule continuity after write-off',
 'Schedule invariant and continuation limits integrated; selected program resume next; no whole requirement closure.':'Selected coupon resumption integrated; bank claim-component continuity next; no whole requirement closure.',
 'Version 5.47: schedule invariant and continuation limits; 803 checks; not_ready.':'Version 5.48: selected same-period resumption; 836 checks; not_ready.',
 '**5.47**, 824 main pages':'**5.48**, 825 main pages','258 total / 237 body pages':'259 total / 238 body pages',
 'Exact payment-schedule invariants and checked continuation limits':'Selected same-period resumption and supplementary prefix/resource checks',
 'are integrated. All 803 document checks pass, preserving':'are integrated. All 836 document checks pass, preserving',
 '276 sources and 233 evidence files':'277 sources and 264 evidence files',
 '## Schedule and continuation scope integrated — 27 October 2026':'## Selected program resumption integrated — 27 October 2026',
 'Version 5.46, 823 pages':'Version 5.47, 824 pages','Version 5.47, 824 pages':'Version 5.48, 825 pages',
 '**257 pages**':'**258 pages**','**258 pages**':'**259 pages**','**236 body pages**':'**237 body pages**','**237 body pages**':'**238 body pages**',
 'coupon-continuation-integration-20261027/result.md':'coupon-scope-integration-20261027/result.md',
 'coupon-scope-integration-20261027/result.md':'coupon-resume-integration-20261027/result.md',
 '# Full closure program after coupon scope integration':'# Full closure program after selected resume integration',
 'Version 5.47; all 18 packages remain open.':'Version 5.48; all 18 packages remain open.',
 'Exact source preservation, checked recurrence and complete-state comparisons support provisional 5.47. General program resume remains open; the current continuation is an explicitly selected single step.':'Exact source preservation, complete chunk comparisons and supplementary prefix/resource checks support provisional 5.48. General methods, cross-period execution and durable persistence remain open. Ready bank work now checks nominal claim components without inventing legal outcomes.',
 'Two schedule/scope method deltas and one integration delta added without duplicate credit.':'One selected resume method delta (including its audit) and one integration delta added without duplicate credit.',
 '.v547.tmp':'.v548.tmp','.v547-link':'.v548-link',
 'v["checks"] == 803':'v["checks"] == 836','len(audit["successor_deltas"]) == 119':'len(audit["successor_deltas"]) == 121',
}
for k in changes:assert k in s,k
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
start=s.index('for title, evidence, disposition in [');end=s.index(']:',start)+2
s=s[:start]+'''for title, evidence, disposition in [
    ("Selected coupon program resumption", INTERNAL, "16 cases, 48 chunk comparisons, 824 assertions and 18 controls; supplementary audit 493 assertions and 12 controls."),
    ("Selected resume manuscript integration", RESULT, "836 checks preserve 277 sources and 264 evidence files; covers and added pages reviewed; independent acceptance pending.")]:'''+s[end:]
s=s.replace('coupon_scope_result=INTERNAL, coupon_schedule_result="data/accounting-master/coupon-schedule-invariant-20261027/result.md",','coupon_resume_result=INTERNAL,')
s=s.replace('for result in ("data/accounting-master/coupon-schedule-invariant-20261027/result.md", INTERNAL, RESULT):','for result in (INTERNAL, RESULT):')
start=s.index('    if row["id"] in ["W05", "W11", "W12", "W13", "W16"]:');end=s.index('    if row["id"] == "W01":',start)
s=s[:start]+'''    if row["id"] in ["W09", "W16"]:
        row["next_action"] = "Execute accounting-credit-claim-continuity-20261027.md; reconcile every dated collection, removed portion, uncollected amount and modeled schedule revision."
    if row["id"] == "W05":
        row["next_action"] = "Selected coupon resume is checked; broader financing and cross-period methods remain open. Conversion allocation remains independently source-evidence-blocked."
    if row["id"] == "W11":
        row["next_action"] = "Retain selected resume semantics; audit other method families and explicit migration boundaries before generalizing the interface."
    if row["id"] == "W12":
        row["next_action"] = "Pure selected replay is checked; real store transactions, effect ownership and concurrent-writer recovery remain unimplemented and cannot close from this evidence."
    if row["id"] == "W13":
        row["next_action"] = "Preserve exact numerical and resource refusal distinctions; extend root/reset domains only with explicit certification and independent financial targets."
'''+s[end:]
s=s.replace('compression_next_plan=NEXT,','bank_next_plan=NEXT,')
assert not (H/'advance.py').exists();(H/'advance.py').write_text(s)
print('Prepared 5.48 two-delta advancement and bank continuation')
