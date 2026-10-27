"""Prepare a bounded successor; do not rerun completed advancement writers."""
from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'viability-integration-20261027/advance.py').read_text()
changes={
 'gap-actor-existence-integration-refresh-20261027':'gap-viability-integration-refresh-20261027',
 'gap-viability-integration-refresh-20261027':'gap-coupon-continuation-refresh-20261027',
 'accounting-refused-payment-reporting-20261027.md':'accounting-coupon-schedule-invariant-20261027.md',
 'accounting-policy-failure-diagnosis-20261027.md':'accounting-refused-payment-reporting-20261027.md',
 'accounting-viability-integration-20261027.md':'accounting-coupon-continuation-integration-20261027.md',
 'data/accounting-master/financing-viability-boundary-20261027/result.md':'data/accounting-master/coupon-partial-settlement-20261027/result.md',
 '5.44;820 pages;not_ready':'5.45;821 pages;not_ready',
 '5.45;821 pages;not_ready':'5.46;823 pages;not_ready',
 'Version 5.45 integrates economic failure and exact viability; 5.44 preserved.':'Version 5.46 integrates refused reporting, carry and partial payment; 5.45 preserved.',
 'Version 5.45 integrates economic failure and exact viability; independent acceptance pending.':'Version 5.46 integrates refused reporting, carry and partial payment; independent acceptance pending.',
 'verify retained unpaid coupon state and financial reports after refused execution.':'derive schedule invariants and check their exact selected-method correspondence.',
 'Check complete reports after refused coupon payment':'Derive partial-payment schedule invariants',
 'Economic diagnosis and exact viability integrated; refused-payment reporting next; no whole requirement closure.':'Refused reporting, carry and partial payment integrated; general schedule invariant next; no whole requirement closure.',
 'Version 5.45: economic diagnosis and exact viability; 726 checks; not_ready.':'Version 5.46: refusal, carry and partial payment; 792 checks; not_ready.',
 '**5.45**, 821 main pages':'**5.46**, 823 main pages',
 '255 total / 234 body pages':'257 total / 236 body pages',
 'Exact economic failure diagnosis and the continuous financing viability boundary':'Refused-payment reporting, selected year-end carry and explicit partial settlement',
 'are integrated. All 726 document checks pass, preserving':'are integrated. All 792 document checks pass, preserving',
 '274 sources and 160 evidence files':'275 sources and 224 evidence files',
 '## Economic diagnosis and viability integrated — 27 October 2026':'## Refusal and later settlement integrated — 27 October 2026',
 'Version 5.44, 820 pages':'Version 5.45, 821 pages',
 'Version 5.45, 821 pages':'Version 5.46, 823 pages',
 '**254 pages**':'**255 pages**','**255 pages**':'**257 pages**',
 '**233 body pages**':'**234 body pages**','**234 body pages**':'**236 body pages**',
 'actor-existence-integration-20261027/result.md':'viability-integration-20261027/result.md',
 'viability-integration-20261027/result.md':'coupon-continuation-integration-20261027/result.md',
 '# Full closure program after viability integration':'# Full closure program after coupon continuation integration',
 'Version 5.45; all 18 packages remain open.':'Version 5.46; all 18 packages remain open.',
 'Exact source preservation, checked financial derivation and bounded rendered review support provisional 5.45. Refused instructions must retain unpaid coupons and accepted financial prefixes.':'Exact source preservation, complete state comparisons and bounded rendered review support provisional 5.46. Schedule generality remains unproved by the finite examples. Stale next actions for disclosure, information and compression are restored to those packages\u0027 own closure criteria.',
 'Two viability method deltas and one integration delta added without duplicate credit.':'Three coupon method deltas and one integration delta added without duplicate credit.',
 '.v545.tmp':'.v546.tmp','.v545-link':'.v546-link',
}
for k in changes: assert k in s,k
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
start=s.index('for title, evidence, disposition in ['); end=s.index(']:',start)+2
s=s[:start]+'''for title, evidence, disposition in [
    ("Refused coupon complete reporting", "data/accounting-master/refused-payment-reporting-20261027/result.md", "10 cases, 396 assertions, 12 controls; full unpaid coupon and accepted prefix preserved."),
    ("Selected unpaid coupon year-end carry", "data/accounting-master/coupon-carry-20261027/result.md", "6 carries and 4 nonfinal refusals; 406 assertions and 16 controls; original refusal archived."),
    ("Explicit partial coupon settlement", INTERNAL, "8 cases, 446 assertions and 20 controls; cash zero, claim 1/16 and original missed decision retained."),
    ("Coupon continuation manuscript integration", RESULT, "792 checks preserve 275 sources and 224 evidence files; covers and added pages reviewed; independent acceptance pending.")]:'''+s[end:]
s=s.replace('viability_result=INTERNAL, failure_diagnosis_result="data/accounting-master/policy-failure-diagnosis-20261027/result.md",',
 'coupon_partial_result=INTERNAL, coupon_carry_result="data/accounting-master/coupon-carry-20261027/result.md", refused_reporting_result="data/accounting-master/refused-payment-reporting-20261027/result.md",')
s=s.replace('for result in ("data/accounting-master/policy-failure-diagnosis-20261027/result.md", INTERNAL, RESULT):',
 'for result in ("data/accounting-master/refused-payment-reporting-20261027/result.md", "data/accounting-master/coupon-carry-20261027/result.md", INTERNAL, RESULT):')
s=s.replace('if row["id"] in ["W01", "W03", "W04", "W11", "W12", "W13", "W16", "W17"]:',
 'if row["id"] in ["W05", "W11", "W12", "W13", "W16", "W17"]:')
start=s.index('    if row["id"] in ["W01", "W03", "W04", "W11", "W12", "W13", "W16"]:')
end=s.index('counts = read(',start)
s=s[:start]+'''    if row["id"] in ["W05", "W11", "W12", "W13", "W16"]:
        row["next_action"] = "Execute accounting-coupon-schedule-invariant-20261027.md; distinguish the algebraic schedule result from runtime and history compatibility."
    if row["id"] == "W05":
        row["next_action"] += " Conversion allocation remains independently source-evidence-blocked."
    if row["id"] == "W01":
        row["next_action"] = "Continue exact source spans, precision and dated availability; keep legal-book opening admission separate from consolidated disclosure."
    if row["id"] == "W03":
        row["next_action"] = "Extend source/message continuation only with explicit observation and permitted-policy semantics; retain unresolved histories when evidence is insufficient."
    if row["id"] == "W04":
        row["next_action"] = "After the coupon invariant, audit which future queries and methods distinguish equal balances with different dated histories; do not merge on financial totals alone."
    if row["id"] == "W17":
        row["next_action"] = "Version 5.46 integrates all three coupon companions; continue bounded consistency repairs and independent reader/domain/whole-document review."
'''+s[end:]
s=s.replace('assert audit["groups"] == protected_groups', 'assert len(audit["successor_deltas"]) == 116\nassert audit["groups"] == protected_groups')
s=s.replace('assert v["status"] == "PASS" and (H / "author-review.md").exists()', 'assert v["status"] == "PASS" and v["checks"] == 792 and (H / "author-review.md").exists()\nassert (R / NEXT).is_file() and (R / PLAN).is_file() and (R / RESULT).is_file()')
assert not (H/'advance.py').exists()
(H/'advance.py').write_text(s)
print('Prepared 5.46 advancement and package-specific next actions')
