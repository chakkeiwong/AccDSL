from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'credit-claim-integration-20261027/advance.py').read_text()
changes={
 'gap-coupon-resume-refresh-20261027':'gap-credit-claim-refresh-20261027',
 'gap-credit-claim-refresh-20261027':'gap-credit-recovery-refresh-20261027',
 'accounting-credit-claim-continuity-20261027.md':'accounting-credit-recovery-scope-20261027.md',
 'accounting-credit-recovery-scope-20261027.md':'accounting-insurance-shared-group-audit-20261027.md',
 'accounting-credit-claim-integration-20261027.md':'accounting-credit-recovery-integration-20261027.md',
 'credit-claim-continuity-20261027/result.md':'credit-recovery-intake-20261027/result.md',
 'coupon-resume-integration-20261027/result.md':'credit-claim-integration-20261027/result.md',
 'credit-claim-integration-20261027/result.md':'credit-recovery-integration-20261027/result.md',
 '5.48;825 pages;not_ready':'5.49;826 pages;not_ready',
 '5.49;826 pages;not_ready':'5.50;827 pages;not_ready',
 'Version 5.49 integrates dated nominal credit continuity; 5.48 preserved.':'Version 5.50 integrates recovery-source scope and unresolved intake; 5.49 preserved.',
 'Version 5.49 integrates dated nominal credit continuity; independent acceptance pending.':'Version 5.50 integrates recovery-source scope and unresolved intake; independent acceptance pending.',
 'Version 5.49 integrates nominal credit continuity; continue bounded consistency repairs and independent reader/domain/whole-document review.':'Version 5.50 integrates recovery-source limits; continue bounded consistency repairs and independent reader/domain/whole-document review.',
 'Inspect source-qualified recovery requirements after financial closure':'Audit issued/held insurance composition through actual report endpoints',
 'Dated nominal credit continuity integrated; source-qualified recovery scope next; no whole requirement closure.':'Recovery-source scope and unresolved intake integrated; insurance composition audit next; no whole requirement closure.',
 'Version 5.49: dated nominal credit continuity; 998 checks; not_ready.':'Version 5.50: recovery scope and unresolved intake; 617 checks; not_ready.',
 '**5.49**, 826 main pages':'**5.50**, 827 main pages',
 '260 total / 239 body pages':'261 total / 240 body pages',
 'Dated nominal credit continuity and explicit after-close limits':'Recovery-source scope and explicitly unresolved evidence intake',
 'are integrated. All 998 document checks pass, preserving':'are integrated. All 617 document checks pass, preserving',
 '278 sources and 424 evidence files':'279 sources and 41 evidence files',
 '## Dated credit continuity integrated — 27 October 2026':'## Recovery scope integrated — 27 October 2026',
 'Version 5.48, 825 pages':'Version 5.49, 826 pages',
 'Version 5.49, 826 pages':'Version 5.50, 827 pages',
 '**259 pages**':'**260 pages**','**260 pages**':'**261 pages**',
 '**238 body pages**':'**239 body pages**','**239 body pages**':'**240 body pages**',
 '# Full closure program after credit continuity integration':'# Full closure program after recovery scope integration',
 'Version 5.49; all 18 packages remain open.':'Version 5.50; all 18 packages remain open.',
 'Exact source preservation and complete dated credit reconciliation support provisional 5.49. Recovery recognition, legal assessment and general bank methods remain open; inspect primary authority before implementing a new event.':'Exact source preservation and checked source/intake boundaries support provisional 5.50. Positive recovery recognition and actual receipt evidence remain open. Independent insurance composition audit uses retained supported methods only.',
 'One dated credit continuity delta and one manuscript integration delta added without duplicate credit.':'One recovery-source delta, one unresolved-intake delta and one manuscript integration delta added without duplicate credit.',
 '.v549.tmp':'.v550.tmp','.v549-link':'.v550-link',
 'v["checks"] == 998':'v["checks"] == 617','len(audit["successor_deltas"]) == 123':'len(audit["successor_deltas"]) == 126',
 'credit_claim_result=INTERNAL':'credit_recovery_intake_result=INTERNAL',
}
for k in changes:assert k in s,k
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
a=s.index('for title, evidence, disposition in [');b=s.index(']:',a)+2
s=s[:a]+'''for title, evidence, disposition in [
    ("Recovery-source scope", "data/accounting-master/credit-recovery-scope-20261027/result.md", "Nine historical spans, four official pages and 15 checks; post-close recognition remains unadmitted."),
    ("Unresolved recovery intake", INTERNAL, "Nine histories, 239 assertions and 50 controls; no positive recovery or financial effect."),
    ("Recovery scope manuscript integration", RESULT, "617 checks preserve 279 sources and 41 evidence files; covers and added pages reviewed; independent acceptance pending.")]:'''+s[b:]
a=s.index('    if row["id"] in ["W09", "W16"]:');b=s.index('    if row["id"] == "W05":',a)
s=s[:a]+'''    if row["id"] == "W09":
        row["next_action"] = "Unresolved recovery intake is checked. Seek applicable post-derecognition recognition and actual receipt/allocation evidence before enabling positive recoveries; retain legal unknowns."
    if row["id"] in ["W10", "W16"]:
        row["next_action"] = "Execute accounting-insurance-shared-group-audit-20261027.md; verify issued/held origins and the actual reporting call chain before proposing a new supported composition."
'''+s[b:]
s=s.replace('bank_next_plan=NEXT,','insurance_next_plan=NEXT, bank_next_plan="docs/plans/accounting-credit-recovery-intake-20261027.md",')
s=s.replace('for result in (INTERNAL, RESULT):','for result in ("data/accounting-master/credit-recovery-scope-20261027/result.md", INTERNAL, RESULT):')
p=H/'advance.py';assert not p.exists();p.write_text(s)
print('Prepared 5.50 advancement with three scoped deltas and insurance continuation')
