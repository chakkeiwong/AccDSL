from pathlib import Path
import re

H = Path(__file__).resolve().parent
s = (H.parent / "joint-frontier-integration-20261027/advance.py").read_text()
changes = {
    "gap-joint-policy-integration-refresh-20261027": "gap-joint-frontier-integration-refresh-20261027",
    "gap-joint-frontier-integration-refresh-20261027": "gap-joint-domain-integration-refresh-20261027",
    "docs/plans/accounting-joint-domain-transport-20261027.md": "docs/plans/accounting-joint-financial-source-20261027.md",
    "docs/plans/accounting-joint-frontier-integration-20261027.md": "docs/plans/accounting-joint-domain-integration-20261027.md",
    "data/accounting-master/joint-temporal-frontier-20261027/result.md": "data/accounting-master/joint-observation-refinement-20261027/result.md",
    "docs/plans/accounting-joint-temporal-frontier-20261027.md": "docs/plans/accounting-joint-domain-transport-20261027.md",
    "5.40;813 pages;not_ready": "5.41;815 pages;not_ready",
    "5.41;815 pages;not_ready": "5.42;816 pages;not_ready",
    "Version 5.41 integrates checked joint continuation and partial-policy results; 5.40 preserved.": "Version 5.42 integrates joint-domain renaming and refinement; 5.41 preserved.",
    "Resumable joint source search and checked partial policies": "Joint-stage declared observation refinement",
    "4,083 original assertions plus 275 saved-result checks; 33 added corruption controls; finite logical continuation only.": "46 comparisons, 397 assertions and 14 controls; exact erasure and per-rule reached rows; unassessed cases preserved.",
    "Joint-frontier manuscript integration": "Joint-domain manuscript integration",
    "666 document checks preserve 270 sources and 108 evidence files; bounded author review, independent acceptance pending.": "694 document checks preserve 271 sources and 134 evidence files; bounded author review, independent acceptance pending.",
    "Version 5.41 integrates checked joint continuation and partial-policy conclusions; independent acceptance pending.": "Version 5.42 integrates exact joint renaming and declared refinement; independent acceptance pending.",
    "Execute accounting-joint-domain-transport-20261027.md; preserve joint-stage memory and the original source frontier.": "Execute accounting-joint-financial-source-20261027.md; retain both dated source views without inventing an economic-history splice.",
    "Joint frontier and result-witness checks integrated; exact joint-domain transport next; no whole requirement closure.": "Joint-domain relations integrated; financial-source selection and its economic-history boundary next; no whole requirement closure.",
    "Check exact joint-stage message renaming": "Check financial source corrections at both dates",
    "Version 5.41: resumable joint source search and independently checked saved-policy witnesses; 666 document checks; not_ready.": "Version 5.42: exact joint renaming and refinement; 694 document checks and repaired layout; not_ready.",
    "Updated 27 October 2026. Governing candidate **5.41**, 815 main pages, not_ready.": "Updated 27 October 2026. Governing candidate **5.42**, 816 main pages, not_ready.",
    "Simulation: 249 total / 228 body pages.": "Simulation: 250 total / 229 body pages.",
    "Joint source continuation and checked partial-policy conclusions are integrated.": "Joint-domain renaming and declared refinement are integrated.",
    "Recovery preserved the successful run and added the missing refusal-witness and": "Renaming passes 34 comparisons; refinement passes 46 comparisons, including",
    "false-feasibility controls: all 33 corruptions rejected. 666 document checks preserve": "unassessed source/domain cases. 694 document checks preserve",
    "270 sources and 108 evidence files. Bounded author review is complete; independent": "271 sources and 134 evidence files. Layout repaired; bounded author review complete. Independent",
    "## Joint continuation integrated — 27 October 2026": "## Joint-domain relations integrated — 27 October 2026",
    "Version 5.40, 813 pages": "Version 5.41, 815 pages",
    "Version 5.41, 815 pages": "Version 5.42, 816 pages",
    "**247 pages**": "**249 pages**", "**249 pages**": "**250 pages**",
    "**226 body pages**": "**228 body pages**", "**228 body pages**": "**229 body pages**",
    "joint-policy-integration-20261027/result.md": "joint-frontier-integration-20261027/result.md",
    "joint-frontier-integration-20261027/result.md": "joint-domain-integration-20261027/result.md",
    "# Full closure program after joint-frontier integration": "# Full closure program after joint-domain integration",
    "Version 5.41; all 18 packages remain open.": "Version 5.42; all 18 packages remain open.",
    "Exact source preservation, checked local mathematics and bounded rendered author review support provisional 5.41. Missing saved-result controls were repaired before integration. Exact renaming is the next bounded question; refinement requires its own relation.": "Exact source preservation, checked erasure/lift reasoning and bounded rendered author review support provisional 5.42. Financial corrections must preserve assertion history separately from economic continuity.",
    "One joint-frontier method delta and one manuscript integration delta added without duplicate credit.": "Two joint-domain method deltas and one manuscript integration delta added without duplicate credit.",
    ".v541.tmp": ".v542.tmp", ".v541-link": ".v542-link",
}
for old in changes:
    assert old in s, old
s = re.sub("|".join(re.escape(k) for k in sorted(changes, key=len, reverse=True)), lambda match: changes[match.group()], s)
anchor = "for title, evidence, disposition in ["
s = s.replace(anchor, anchor + chr(10) + '    ("Joint-stage exact message renaming", "data/accounting-master/joint-domain-transport-20261027/result.md", "34 comparisons, 388 assertions and 16 controls; exact population/witness permutation and inverse roundtrips."),')
s = s.replace('joint_frontier_result=INTERNAL', 'joint_refinement_result=INTERNAL, joint_renaming_result="data/accounting-master/joint-domain-transport-20261027/result.md"')
target = H / "advance.py"
assert not target.exists()
target.write_text(s)
print("Prepared 5.42 advancement with both method deltas")
