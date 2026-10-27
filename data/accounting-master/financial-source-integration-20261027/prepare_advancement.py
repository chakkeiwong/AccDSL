from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'joint-domain-integration-20261027/advance.py').read_text()
changes={
 'gap-joint-frontier-integration-refresh-20261027':'gap-joint-domain-integration-refresh-20261027',
 'gap-joint-domain-integration-refresh-20261027':'gap-financial-source-integration-refresh-20261027',
 'accounting-joint-financial-source-20261027.md':'accounting-revised-source-actor-messages-20261027.md',
 'accounting-joint-domain-integration-20261027.md':'accounting-financial-source-integration-20261027.md',
 'accounting-joint-domain-transport-20261027.md':'accounting-joint-financial-source-20261027.md',
 '5.41;815 pages;not_ready':'5.42;816 pages;not_ready',
 '5.42;816 pages;not_ready':'5.43;818 pages;not_ready',
 'Version 5.42 integrates joint-domain renaming and refinement; 5.41 preserved.':'Version 5.43 integrates financial sources and supplied worlds; 5.42 preserved.',
 'Version 5.42 integrates exact joint renaming and declared refinement; independent acceptance pending.':'Version 5.43 integrates financial sources and supplied worlds; independent acceptance pending.',
 'retain both dated source views without inventing an economic-history splice.':'keep dated actor messages separate from the analyst world hypothesis.',
 'Integrate later checked joint-domain changes; continue independent reader, domain and whole-document review.':'Integrate later checked actor-message evidence; continue independent reader, domain and whole-document review.',
 'Joint-domain relations integrated; financial-source selection and its economic-history boundary next; no whole requirement closure.':'Financial sources and worlds integrated; actor-message binding next; no whole requirement closure.',
 'Check financial source corrections at both dates':'Check dated actor messages across supplied worlds',
 'Version 5.42: exact joint renaming and refinement; 694 document checks and repaired layout; not_ready.':'Version 5.43: financial-source continuity and supplied-world binding; 682 checks; not_ready.',
 '## Joint-domain relations integrated — 27 October 2026':'## Financial-source interpretation integrated — 27 October 2026',
 'Version 5.41, 815 pages':'Version 5.42, 816 pages',
 'Version 5.42, 816 pages':'Version 5.43, 818 pages',
 '**249 pages**':'**250 pages**','**250 pages**':'**252 pages**',
 '**228 body pages**':'**229 body pages**','**229 body pages**':'**231 body pages**',
 'joint-frontier-integration-20261027/result.md':'joint-domain-integration-20261027/result.md',
 'joint-domain-integration-20261027/result.md':'financial-source-integration-20261027/result.md',
 '# Full closure program after joint-domain integration':'# Full closure program after financial-source integration',
 'Version 5.42; all 18 packages remain open.':'Version 5.43; all 18 packages remain open.',
 'Exact source preservation, checked erasure/lift reasoning and bounded rendered author review support provisional 5.42. Financial corrections must preserve assertion history separately from economic continuity.':'Exact source preservation, checked continuity and bounded rendered review support provisional 5.43. Actor messages must not disclose the analyst world by construction.',
 'Two joint-domain method deltas and one manuscript integration delta added without duplicate credit.':'Three financial-source method deltas and one integration delta added without duplicate credit.',
 '.v542.tmp':'.v543.tmp','.v542-link':'.v543-link',
 'data/accounting-master/joint-observation-refinement-20261027/result.md':'data/accounting-master/financial-source-world-binding-20261027/result.md',
}
for key in changes: assert key in s,key
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
start=s.index('for title, evidence, disposition in [');end=s.index(']:',start)+2
s=s[:start]+'''for title, evidence, disposition in [
    ("Joint financial-source selection", "data/accounting-master/joint-financial-source-20261027/result.md", "11 protected and 13 new cases; 341 assertions and 16 controls; no policy binding."),
    ("Financial assertion continuity", "data/accounting-master/financial-assertion-continuity-20261027/result.md", "16 symbolic cases, 112 boundary comparisons, 594 assertions and 48 rejected discontinuities."),
    ("Explicit supplied economic-world binding", INTERNAL, "20 cases, 289 assertions, 25 controls; complete world rows, no actor policy."),
    ("Financial-source manuscript integration", RESULT, "682 checks preserve 272 sources and 120 evidence files; covers and added pages reviewed; independent acceptance pending.")]:'''+s[end:]
s=s.replace('joint_refinement_result=INTERNAL, joint_renaming_result="data/accounting-master/joint-domain-transport-20261027/result.md",','financial_world_result=INTERNAL, financial_source_result="data/accounting-master/joint-financial-source-20261027/result.md", financial_continuity_result="data/accounting-master/financial-assertion-continuity-20261027/result.md",')
s=s.replace('for result in (INTERNAL, RESULT):','for result in ("data/accounting-master/joint-financial-source-20261027/result.md", "data/accounting-master/financial-assertion-continuity-20261027/result.md", INTERNAL, RESULT):')
start=s.index('summary = chr(10).join([');end=s.index('new = {paths[0]',start)
s=s[:start]+'''summary = chr(10).join([
    "Updated 27 October 2026. Governing candidate **5.43**, 818 main pages, not_ready.",
    "Simulation: 252 total / 231 body pages. Four stable PDF/TeX links select this candidate.",
    "Main SHA256: " + a["current_pdf_sha256"] + ".",
    "Simulation SHA256: " + a["standalone_pdf_sha256"] + ".", "",
    "Financial-source selection, complete-state continuity and explicit supplied",
    "economic worlds are integrated. All 682 document checks pass, preserving",
    "272 sources and 120 evidence files. Both covers and all added pages reviewed.",
    "Independent reader, domain and whole-document acceptance remain pending.", "",
    "Result: " + RESULT + ".", "Method evidence: " + INTERNAL + ".",
    "Active execution plan: " + NEXT + ".", "Financing evidence plan: " + a["financing_next_plan"] + ".",
    "Full program: " + base + "/closure-program.md.", "Remaining work: " + base + "/remaining-work.md.", "",
    "All 53 obligations, six interactions, 46 operations and 18 packages remain open.",
    "S1–S5 partial; S6 held; E3 deferred. Measured conversion-to-control remains locally",
    "evidence-blocked. Continue independent ready work; no global continuation veto.", ""])
'''+s[end:]
assert not (H/'advance.py').exists()
(H/'advance.py').write_text(s)
print('Prepared four-delta advancement')
