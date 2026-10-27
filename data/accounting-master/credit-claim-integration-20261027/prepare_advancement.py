from pathlib import Path
import re
H = Path(__file__).resolve().parent
s = (H.parent / 'coupon-resume-integration-20261027/advance.py').read_text()
changes = {
 'gap-coupon-scope-refresh-20261027':'gap-coupon-resume-refresh-20261027',
 'gap-coupon-resume-refresh-20261027':'gap-credit-claim-refresh-20261027',
 'accounting-coupon-program-resume-20261027.md':'accounting-credit-claim-continuity-20261027.md',
 'accounting-credit-claim-continuity-20261027.md':'accounting-credit-recovery-scope-20261027.md',
 'accounting-coupon-resume-integration-20261027.md':'accounting-credit-claim-integration-20261027.md',
 'coupon-program-resume-20261027/result.md':'credit-claim-continuity-20261027/result.md',
 'coupon-scope-integration-20261027/result.md':'coupon-resume-integration-20261027/result.md',
 'coupon-resume-integration-20261027/result.md':'credit-claim-integration-20261027/result.md',
 '5.47;824 pages;not_ready':'5.48;825 pages;not_ready',
 '5.48;825 pages;not_ready':'5.49;826 pages;not_ready',
 'Version 5.48 integrates selected same-period resumption; 5.47 preserved.':'Version 5.49 integrates dated nominal credit continuity; 5.48 preserved.',
 'Version 5.48 integrates selected same-period resumption; independent acceptance pending.':'Version 5.49 integrates dated nominal credit continuity; independent acceptance pending.',
 'Version 5.48 integrates selected resumption; continue bounded consistency repairs and independent reader/domain/whole-document review.':'Version 5.49 integrates nominal credit continuity; continue bounded consistency repairs and independent reader/domain/whole-document review.',
 'Check bank credit schedule continuity after write-off':'Inspect source-qualified recovery requirements after financial closure',
 'Selected coupon resumption integrated; bank claim-component continuity next; no whole requirement closure.':'Dated nominal credit continuity integrated; source-qualified recovery scope next; no whole requirement closure.',
 'Version 5.48: selected same-period resumption; 836 checks; not_ready.':'Version 5.49: dated nominal credit continuity; 998 checks; not_ready.',
 '**5.48**, 825 main pages':'**5.49**, 826 main pages',
 '259 total / 238 body pages':'260 total / 239 body pages',
 'Selected same-period resumption and supplementary prefix/resource checks':'Dated nominal credit continuity and explicit after-close limits',
 'are integrated. All 836 document checks pass, preserving':'are integrated. All 998 document checks pass, preserving',
 '277 sources and 264 evidence files':'278 sources and 424 evidence files',
 '## Selected program resumption integrated — 27 October 2026':'## Dated credit continuity integrated — 27 October 2026',
 'Version 5.47, 824 pages':'Version 5.48, 825 pages',
 'Version 5.48, 825 pages':'Version 5.49, 826 pages',
 '**258 pages**':'**259 pages**', '**259 pages**':'**260 pages**',
 '**237 body pages**':'**238 body pages**', '**238 body pages**':'**239 body pages**',
 '# Full closure program after selected resume integration':'# Full closure program after credit continuity integration',
 'Version 5.48; all 18 packages remain open.':'Version 5.49; all 18 packages remain open.',
 'Exact source preservation, complete chunk comparisons and supplementary prefix/resource checks support provisional 5.48. General methods, cross-period execution and durable persistence remain open. Ready bank work now checks nominal claim components without inventing legal outcomes.':'Exact source preservation and complete dated credit reconciliation support provisional 5.49. Recovery recognition, legal assessment and general bank methods remain open; inspect primary authority before implementing a new event.',
 'One selected resume method delta (including its audit) and one integration delta added without duplicate credit.':'One dated credit continuity delta and one manuscript integration delta added without duplicate credit.',
 '.v548.tmp':'.v549.tmp', '.v548-link':'.v549-link',
 'v["checks"] == 836':'v["checks"] == 998',
 'len(audit["successor_deltas"]) == 121':'len(audit["successor_deltas"]) == 123',
 'coupon_resume_result=INTERNAL':'credit_claim_result=INTERNAL',
}
for k in changes:
    assert k in s, k
s = re.sub('|'.join(re.escape(k) for k in sorted(changes, key=len, reverse=True)), lambda m: changes[m[0]], s)
a = s.index('for title, evidence, disposition in ['); b = s.index(']:', a) + 2
s = s[:a] + '''for title, evidence, disposition in [
    ("Dated nominal credit continuity", INTERNAL, "Nine histories, 57 stages, 999 assertions, 25 controls and nine after-close refusals; financial outputs unchanged."),
    ("Credit continuity manuscript integration", RESULT, "998 checks preserve 278 sources and 424 evidence files; covers and added pages reviewed; independent acceptance pending.")]:''' + s[b:]
s = s.replace('requirements=["MC03", "MC05", "MC11", "MC12", "MC13", "MC18", "MC24", "MC25", "MC26", "MC28", "MC32", "MC33", "MC34"]', 'requirements=["MC03", "MC05", "MC08", "MC11", "MC13", "MC15", "MC16", "MC17", "MC19", "MC24", "MC25", "MC26", "MC28", "MC33", "MC34"]')
s = s.replace('if row["id"] in ["W05", "W11", "W12", "W13", "W16", "W17"]:', 'if row["id"] in ["W07", "W09", "W11", "W12", "W16", "W17"]:')
s = s.replace('Execute accounting-credit-recovery-scope-20261027.md; reconcile every dated collection, removed portion, uncollected amount and modeled schedule revision.', 'Execute accounting-credit-recovery-scope-20261027.md; inspect recovery recognition, receipt/portion attribution and information-date requirements without inventing a recovery.')
# The predecessor template names the plan without its directory in this line.
s = s.replace('Execute accounting-credit-claim-continuity-20261027.md; reconcile every dated collection, removed portion, uncollected amount and modeled schedule revision.', 'Execute accounting-credit-recovery-scope-20261027.md; inspect recovery recognition, receipt/portion attribution and information-date requirements without inventing a recovery.')
p = H / 'advance.py'; assert not p.exists(); p.write_text(s)
print('Prepared credit continuity advancement and package-specific recovery action')
