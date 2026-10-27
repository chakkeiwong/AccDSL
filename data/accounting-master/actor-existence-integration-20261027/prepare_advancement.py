from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'financial-source-integration-20261027/advance.py').read_text()
changes={
 'gap-joint-domain-integration-refresh-20261027':'gap-financial-source-integration-refresh-20261027',
 'gap-financial-source-integration-refresh-20261027':'gap-actor-existence-integration-refresh-20261027',
 'accounting-revised-source-actor-messages-20261027.md':'accounting-policy-failure-diagnosis-20261027.md',
 'accounting-financial-source-integration-20261027.md':'accounting-actor-existence-integration-20261027.md',
 'accounting-joint-financial-source-20261027.md':'accounting-revised-source-actor-messages-20261027.md',
 '5.42;816 pages;not_ready':'5.43;818 pages;not_ready',
 '5.43;818 pages;not_ready':'5.44;820 pages;not_ready',
 'Version 5.43 integrates financial sources and supplied worlds; 5.42 preserved.':'Version 5.44 integrates dated messages and checked existence certificates; 5.43 preserved.',
 'Version 5.43 integrates financial sources and supplied worlds; independent acceptance pending.':'Version 5.44 integrates dated messages and checked existence certificates; independent acceptance pending.',
 'keep dated actor messages separate from the analyst world hypothesis.':'diagnose economic infeasibility versus observation collisions at one exact witness.',
 'Financial sources and worlds integrated; actor-message binding next; no whole requirement closure.':'Dated messages and existence certificates integrated; exact economic failure diagnosis next; no whole requirement closure.',
 'Check dated actor messages across supplied worlds':'Diagnose the economic cause of policy contradictions',
 'Version 5.43: financial-source continuity and supplied-world binding; 682 checks; not_ready.':'Version 5.44: dated actor messages and policy certificates; 709 checks; not_ready.',
 '## Financial-source interpretation integrated — 27 October 2026':'## Actor messages and existence certificates integrated — 27 October 2026',
 'Version 5.42, 816 pages':'Version 5.43, 818 pages','Version 5.43, 818 pages':'Version 5.44, 820 pages',
 '**250 pages**':'**252 pages**','**252 pages**':'**254 pages**','**229 body pages**':'**231 body pages**','**231 body pages**':'**233 body pages**',
 'joint-domain-integration-20261027/result.md':'financial-source-integration-20261027/result.md',
 'financial-source-integration-20261027/result.md':'actor-existence-integration-20261027/result.md',
 '# Full closure program after financial-source integration':'# Full closure program after actor-existence integration',
 'Version 5.43; all 18 packages remain open.':'Version 5.44; all 18 packages remain open.',
 'Exact source preservation, checked continuity and bounded rendered review support provisional 5.43. Actor messages must not disclose the analyst world by construction.':'Exact source preservation, checked Boolean derivation and bounded rendered review support provisional 5.44. Economic versus information failure must be diagnosed at one consistent financial point.',
 'Three financial-source method deltas and one integration delta added without duplicate credit.':'Two actor-policy method deltas and one integration delta added without duplicate credit.',
 '.v543.tmp':'.v544.tmp','.v543-link':'.v544-link',
 'data/accounting-master/financial-source-world-binding-20261027/result.md':'data/accounting-master/policy-existence-certificates-20261027/result.md',
}
for key in changes:assert key in s,key
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
start=s.index('for title, evidence, disposition in [');end=s.index(']:',start)+2
s=s[:start]+'''for title, evidence, disposition in [
    ("Dated actor messages across supplied worlds", "data/accounting-master/revised-source-actor-messages-20261027/result.md", "47 cases, 394 assertions, 20 controls; protected full policy populations and explicit overflow."),
    ("Checked policy-existence certificates", INTERNAL, "47 cases and 260 formulas; 1,083 assertions, 22 controls; 13 newly assessed larger domains."),
    ("Actor-existence manuscript integration", RESULT, "709 checks preserve 273 sources and 145 evidence files; covers and added pages reviewed; independent acceptance pending.")]:'''+s[end:]
s=s.replace('financial_world_result=INTERNAL, financial_source_result="data/accounting-master/joint-financial-source-20261027/result.md", financial_continuity_result="data/accounting-master/financial-assertion-continuity-20261027/result.md",','policy_existence_result=INTERNAL, actor_message_result="data/accounting-master/revised-source-actor-messages-20261027/result.md",')
s=s.replace('for result in ("data/accounting-master/joint-financial-source-20261027/result.md", "data/accounting-master/financial-assertion-continuity-20261027/result.md", INTERNAL, RESULT):','for result in ("data/accounting-master/revised-source-actor-messages-20261027/result.md", INTERNAL, RESULT):')
s=s.replace('**5.43**, 818 main pages','**5.44**, 820 main pages').replace('252 total / 231 body pages','254 total / 233 body pages')
s=s.replace('Financial-source selection, complete-state continuity and explicit supplied','Dated actor observations and checkable policy-existence certificates')
s=s.replace('economic worlds are integrated. All 682 document checks pass, preserving','are integrated. All 709 document checks pass, preserving')
s=s.replace('272 sources and 120 evidence files','273 sources and 145 evidence files')
assert not (H/'advance.py').exists();(H/'advance.py').write_text(s)
print('Prepared three-delta version 5.44 advancement')
