"""Advance the four live controls; retain historical evidence."""
import json
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'completion.json').exists():raise SystemExit('Completed unit.')
h=json.loads((U/'manuscript-checks.json').read_text())['pdf_sha256']
oldh='d3c37127c7ede9648f680ff0577b9a8d33077b574611be806a6c201f2c8aa061'
oldpdf='docs/design/proposal/manuscript-apple-performance-award-20261013/accounting-product-proposal.pdf'
pdf='docs/design/proposal/manuscript-apple-award-versions-20261013/accounting-product-proposal.pdf'
nextplan='accounting-post-awards-readiness-20261013.md'
summary=('The [award-version inquiry](../../data/accounting-master/apple-award-versions-20261013/result.md)\n'
 'is delivered in Version 2.67: already retained2022 CEO and2024 general/CEO\n'
 'forms now have selected substantive clauses inspected. General prorating and\n'
 'CEO continued eligibility differ; both retain later delivery. Actual-grant\n'
 'applicability and the proxy timing description remain unresolved. All104\n'
 'source and143 manuscript checks pass; five final pages inspected. Execute\n'
 'the [full-program reassessment]('+nextplan+').\n')
p=R/'docs/plans/accounting-master-current.md';s=p.read_text()
s=s.replace('**Version 2.66, 219 pages; readiness not_ready.**','**Version 2.67, 221 pages; readiness not_ready.**',1).replace(oldpdf,pdf,1).replace(oldh,h,1)
s=s.replace('Delivered through Version 2.66; recurring','Delivered through Version 2.67; recurring')
s=s.replace('Inspect the already retained versions next:\n[award-version inquiry](accounting-apple-award-versions-20261013.md).','The retained-version comparison is now complete within scope.\n\n'+summary)
s=s.replace('inspect retained form versions and unresolved grant applicability','retained version comparison delivered; preserve unresolved actual grants and select the next distinct source/method after full reassessment')
p.write_text(s)
p=R/'docs/plans/accounting-master-checkpoint.md';s=p.read_text();a=s.index('**Version 2.66');z=s.index('## Latest completed work')
s=s[:a]+f'**Version 2.67, 221 pages.**\nPDF: {pdf}\nSHA256: {h}.\n'+summary+'\nReadiness **not_ready**. Independent/domain/human acceptance remains pending.\nThe three new stock-plan counterparts remain supplemental; the three forms\nnow inspected were already located. No additional acquisition count is added.\n\n'+s[z:]
s=s.replace('Execute the\n[award-version inquiry](accounting-apple-award-versions-20261013.md).','The version inquiry is now delivered. Execute the\n[post-awards reassessment]('+nextplan+').')
p.write_text(s)
p=R/'docs/plans/accounting-continuation-requirements-20261007.md';s=p.read_text().replace('## Current checkpoint — Version 2.66','## Preserved checkpoint — Version 2.66',1);a=s.index('## Preserved checkpoint')
entry=f'''## Current checkpoint — Version 2.67

13 October 2026. **221 pages; not_ready**.
PDF: {pdf}
SHA256: {h}.
{summary}
MC01/03–05/08/10–11/17/28/30/32–35 and G5/G7/G11/G13/G15/G16 receive
selected source-version and conditional-consequence evidence. All original
obligations/statuses remain. Source identity, general versus CEO populations,
retirement conditions and later delivery remain distinct from actual-grant
admission. The next full assessment will credit V2.65–2.67 together.

The dated entries below are historical. This checkpoint and the master next
plan control execution; old next-action wording does not supersede them.

''';p.write_text(s[:a]+entry+s[a:])
(R/'data/accounting-master/next-plan.md').write_text(f'''# Accounting proposal — direct next plan

13 October 2026. Version2.67,221 pages; **not_ready**.
PDF: {pdf}
SHA256: {h}
Implementation and historical controller remain held.

The retained award-version inquiry is complete within scope:
data/accounting-master/apple-award-versions-20261013/result.md.
104 source/arithmetic and143 manuscript checks pass; five final pages read.
General and CEO survival terms differ; both anchor later delivery. Actual
grant applicability and the proxy timing summary remain unresolved.

Execute docs/plans/{nextplan}.
Credit V2.65–2.67 across all35 MC requirements/18 gaps without changing
acceptance statuses. Select another distinct ready obligation; do not repeat
grant arithmetic, already acquired sources or exhausted access routes.

P17/P18 continue; P19 stays negative. All five E workstreams remain open.
Frozen40 unresolved references, three supplements and37 without counterparts
remain; three already located forms now have selected substantive inspection.
Publication56/136,35 supplements and101 remaining are unchanged. Preserve100
unrelated staged entries. Human acceptance blocks promotion, not preparation.
''')
print('Current controls advanced to V2.67 and full reassessment.')
