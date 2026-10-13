"""Advance current assessment and next action, preserving the PDF and history."""
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'completion.json').exists():raise SystemExit('Completed assessment.')
nextplan='accounting-arelle-fact-identity-20261013.md'
block=('The [post-awards reassessment](../../data/accounting-master/post-awards-readiness-20261013/result.md)\n'
 'is complete: all35 requirements/18 gaps and statuses preserved,16/10\n'
 'descriptions updated,154 integrity checks pass. Twenty-two of26 sources\n'
 'carry prior judgments; three new transitive sections are separately credited.\n'
 'Three new counterparts are distinct from three already located forms now\n'
 'inspected. Actual grants and broader semantics remain unresolved. Execute\n'
 'the [Arelle fact-preservation inquiry]('+nextplan+').\n')
p=R/'docs/plans/accounting-master-current.md';s=p.read_text()
s=s.replace('Execute\nthe [full-program reassessment](accounting-post-awards-readiness-20261013.md).','The full-program assessment is now refreshed.\n\n'+block)
s=s.replace('Version 2.64 author refresh complete, still negative','Version 2.67 author refresh complete, still negative')
s=s.replace('select the next distinct source/method after full reassessment','actual-grant limitations preserved; continue distinct package/authority work without repeating the award chain')
s=s.replace('Extend failure/interface examples and applicable dependency/model/terms evidence','Inspect pinned Arelle fact equality, duplicate grouping and occurrence preservation; retain prior cache/controller/Docling work')
s=s.replace('../../data/accounting-master/post-apple-readiness-20261013/dispositions.md','../../data/accounting-master/post-awards-readiness-20261013/dispositions.md')
s=s.replace('The V2.65–2.66 supplements add three exhibit counterparts, conditional\nreserve/settlement/performance consequences and a source-specific timing question without changing any acceptance\nstatus.','The V2.65–2.67 supplements add three counterparts and selected\nreserve/performance/versioned-settlement consequences without changing\nacceptance statuses; the full author matrix now credits them.')
p.write_text(s)
p=R/'docs/plans/accounting-master-checkpoint.md';s=p.read_text()
s=s.replace('Execute\nthe [full-program reassessment](accounting-post-awards-readiness-20261013.md).','The full-program assessment is now refreshed.\n\n'+block)
s=s.replace('Execute the\n[post-awards reassessment](accounting-post-awards-readiness-20261013.md).','The post-awards reassessment is complete. Execute the\n[Arelle fact-preservation inquiry]('+nextplan+').')
p.write_text(s)
p=R/'docs/plans/accounting-continuation-requirements-20261007.md';s=p.read_text();a=s.index('## Current checkpoint')
s=s[:a]+'## Current whole-program assessment — Version 2.67\n\n'+block+'\nReadiness **not_ready**. This53-row assessment now controls author evidence\ndescriptions; original acceptance obligations/statuses remain unchanged.\n\n'+s[a:]
s=s.replace('## Current checkpoint — Version 2.67','## Preserved integration checkpoint — Version 2.67',1);p.write_text(s)
p=R/'data/accounting-master/next-plan.md';s=p.read_text();a=s.index('The retained award-version inquiry');z=s.index('P17/P18 continue')
s=s[:a]+'''V2.65–2.67 and the full master assessment are complete within scope:
data/accounting-master/post-awards-readiness-20261013/result.md.
All35 requirements/18 gaps preserved;16/10 descriptions updated. All154
integrity checks pass. Twenty-two source judgments carried; new sections
separately credited. Actual grant and whole-company admission stay open.

Execute docs/plans/accounting-arelle-fact-identity-20261013.md.
Inspect pinned source semantics for fact equality and duplicate grouping;
preserve occurrence, context, unit, precision and validation state. No runtime
installation/execution. Do not repeat completed cache/controller inquiries.

'''+s[z:];p.write_text(s)
print('Master assessment and next action refreshed in four controls.')
