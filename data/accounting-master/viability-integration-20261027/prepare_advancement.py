from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'actor-existence-integration-20261027/advance.py').read_text()
changes={
 'gap-financial-source-integration-refresh-20261027':'gap-actor-existence-integration-refresh-20261027',
 'gap-actor-existence-integration-refresh-20261027':'gap-viability-integration-refresh-20261027',
 'accounting-policy-failure-diagnosis-20261027.md':'accounting-refused-payment-reporting-20261027.md',
 'accounting-actor-existence-integration-20261027.md':'accounting-viability-integration-20261027.md',
 'accounting-revised-source-actor-messages-20261027.md':'accounting-policy-failure-diagnosis-20261027.md',
 '5.43;818 pages;not_ready':'5.44;820 pages;not_ready','5.44;820 pages;not_ready':'5.45;821 pages;not_ready',
 'Version 5.44 integrates dated messages and checked existence certificates; 5.43 preserved.':'Version 5.45 integrates economic failure and exact viability; 5.44 preserved.',
 'Version 5.44 integrates dated messages and checked existence certificates; independent acceptance pending.':'Version 5.45 integrates economic failure and exact viability; independent acceptance pending.',
 'diagnose economic infeasibility versus observation collisions at one exact witness.':'verify retained unpaid coupon state and financial reports after refused execution.',
 'Dated messages and existence certificates integrated; exact economic failure diagnosis next; no whole requirement closure.':'Economic diagnosis and exact viability integrated; refused-payment reporting next; no whole requirement closure.',
 'Diagnose the economic cause of policy contradictions':'Check complete reports after refused coupon payment',
 'Version 5.44: dated actor messages and policy certificates; 709 checks; not_ready.':'Version 5.45: economic diagnosis and exact viability; 726 checks; not_ready.',
 '## Actor messages and existence certificates integrated — 27 October 2026':'## Economic diagnosis and viability integrated — 27 October 2026',
 'Version 5.43, 818 pages':'Version 5.44, 820 pages','Version 5.44, 820 pages':'Version 5.45, 821 pages',
 '**252 pages**':'**254 pages**','**254 pages**':'**255 pages**','**231 body pages**':'**233 body pages**','**233 body pages**':'**234 body pages**',
 'financial-source-integration-20261027/result.md':'actor-existence-integration-20261027/result.md',
 'actor-existence-integration-20261027/result.md':'viability-integration-20261027/result.md',
 '# Full closure program after actor-existence integration':'# Full closure program after viability integration',
 'Version 5.44; all 18 packages remain open.':'Version 5.45; all 18 packages remain open.',
 'Exact source preservation, checked Boolean derivation and bounded rendered review support provisional 5.44. Economic versus information failure must be diagnosed at one consistent financial point.':'Exact source preservation, checked financial derivation and bounded rendered review support provisional 5.45. Refused instructions must retain unpaid coupons and accepted financial prefixes.',
 'Two actor-policy method deltas and one integration delta added without duplicate credit.':'Two viability method deltas and one integration delta added without duplicate credit.',
 '.v544.tmp':'.v545.tmp','.v544-link':'.v545-link',
 'data/accounting-master/policy-existence-certificates-20261027/result.md':'data/accounting-master/financing-viability-boundary-20261027/result.md',
}
for key in changes:assert key in s,key
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
start=s.index('for title, evidence, disposition in [');end=s.index(']:',start)+2
s=s[:start]+'''for title, evidence, disposition in [
    ("Exact economic failure diagnosis", "data/accounting-master/policy-failure-diagnosis-20261027/result.md", "10 paths, 337 assertions and 7 controls; all actions fail at one exact receipt-6 point."),
    ("Continuous committed-right viability boundary", INTERNAL, "Two receipt domains, 366 guard implications, 315 assertions and 10 controls; no model domain change."),
    ("Viability manuscript integration", RESULT, "726 checks preserve 274 sources and 160 evidence files; covers and added pages reviewed; independent acceptance pending.")]:'''+s[end:]
s=s.replace('policy_existence_result=INTERNAL, actor_message_result="data/accounting-master/revised-source-actor-messages-20261027/result.md",','viability_result=INTERNAL, failure_diagnosis_result="data/accounting-master/policy-failure-diagnosis-20261027/result.md",')
s=s.replace('for result in ("data/accounting-master/revised-source-actor-messages-20261027/result.md", INTERNAL, RESULT):','for result in ("data/accounting-master/policy-failure-diagnosis-20261027/result.md", INTERNAL, RESULT):')
s=s.replace('**5.44**, 820 main pages','**5.45**, 821 main pages').replace('254 total / 233 body pages','255 total / 234 body pages')
s=s.replace('Dated actor observations and checkable policy-existence certificates','Exact economic failure diagnosis and the continuous financing viability boundary')
s=s.replace('are integrated. All 709 document checks pass, preserving','are integrated. All 726 document checks pass, preserving')
s=s.replace('273 sources and 145 evidence files','274 sources and 160 evidence files')
assert not (H/'advance.py').exists();(H/'advance.py').write_text(s)
print('Prepared three-delta version 5.45 advancement')
