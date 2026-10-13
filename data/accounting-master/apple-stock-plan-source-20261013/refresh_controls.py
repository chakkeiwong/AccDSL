"""Advance current pointers without rewriting historical/frozen evidence."""
import json
from pathlib import Path
U=Path(__file__).resolve().parent
R=U.parents[2]
if (U/'completion.json').exists(): raise SystemExit('Completed unit.')
h=json.loads((U/'manuscript-checks.json').read_text())['pdf_sha256']
old='80b65fd23021d3241ba7a7e6aa3642d7ef6a1b0ca44924993273202ef43042ba'
oldpdf='docs/design/proposal/manuscript-apple-settlement-paths-20261013/accounting-product-proposal.pdf'
pdf='docs/design/proposal/manuscript-apple-stock-plan-20261013/accounting-product-proposal.pdf'
nextplan='accounting-apple-performance-award-20261013.md'
summary=('The [stock-plan inquiry](../../data/accounting-master/apple-stock-plan-source-20261013/result.md)\n'
 'is delivered in Version 2.65: three exact filing exhibits retained, selected\n'
 'capacity/award/settlement clauses inspected, 75 source and 141 manuscript\n'
 'checks pass. Six final pages read; all earlier math/citations preserved.\n'
 'The frozen 40 unresolved reference labels remain unchanged; this dated\n'
 'supplement supplies three counterparts, leaving 37 without one here.\n'
 'Actual grants, current amendments, tax/expense/EPS methods and complete\n'
 'company semantics remain unresolved. Execute the\n'
 '[performance-award inquiry]('+nextplan+').\n')
p=R/'docs/plans/accounting-master-current.md';s=p.read_text()
s=s.replace('**Version 2.64, 215 pages; readiness not_ready.**','**Version 2.65, 217 pages; readiness not_ready.**',1)
s=s.replace(oldpdf,pdf,1).replace(old,h,1)
s=s.replace('Execute the [stock-plan source inquiry](accounting-apple-stock-plan-source-20261013.md).',summary)
s=s.replace('Delivered through Version 2.64; recurring','Delivered through Version 2.65; recurring')
s=s.replace('inspect the unresolved2022 employee stock-plan reference and award dependencies',
 'three2022 plan/form counterparts acquired with selected clauses; inspect performance method and grant dependencies')
s=s.replace('All five\nworkstreams remain open.','The V2.65 source/method supplement adds three exhibit counterparts and\nconditional reserve/settlement consequences without changing any acceptance\nstatus. All five workstreams remain open.')
p.write_text(s)
p=R/'docs/plans/accounting-master-checkpoint.md';s=p.read_text()
start=s.index('**Version 2.64');end=s.index('## Latest completed work')
s=s[:start]+f'**Version 2.65, 217 pages.**\nPDF: {pdf}\nSHA256: {h}.\n'+summary+'\nThis is a design candidate; readiness **not_ready**. Independent/domain/human\nacceptance remains pending while internal preparation continues.\n\n'+s[end:]
s=s.replace('creditV2.60–2.64. Execute the\n[stock-plan source inquiry](accounting-apple-stock-plan-source-20261013.md).\nThe frozen40-target remainder is preserved; do not repeat the blocked indenture routes.',
 'credit V2.60–2.64. The stock-plan source inquiry is now complete within\nscope, with three supplemental counterparts. Execute the\n[performance-award inquiry]('+nextplan+').\nThe frozen40-target list and failed indenture routes remain preserved.')
p.write_text(s)
p=R/'docs/plans/accounting-continuation-requirements-20261007.md';s=p.read_text()
entry=f'''## Current checkpoint — Version 2.65

13 October 2026. **217 pages; not_ready**.
PDF: {pdf}
SHA256: {h}.
{summary}
The following dated sections preserve prior assessments and their then-current
next actions. Their old “current” wording does not supersede this checkpoint.
The full V2.64 assessment still controls all 35 requirement and 18 gap statuses;
this addition improves evidence within those statuses.

| Obligations | New evidence | Remaining obligation |
| --- | --- | --- |
| MC01/03/04/05; G5/G11 | Three source counterparts, exact dates and selected meanings | Full material semantics, amendment chain and historical availability |
| MC08/10/11/17; G7/G15/G16 | Reserve/delivery counterexample and agreement-specific settlement | Actual grants, performance, tax/expense/EPS and complete scenario treatment |
| MC28/30/32–35 | Checked arithmetic, additive integration, source/render records | Independent/domain/human acceptance and wider research/method obligations |

'''
pos=s.index('## Current CSM');s=s[:pos]+entry+s[pos:]
s=s.replace('## Current CSM and reporting-population bridge','## Preserved CSM and reporting-population bridge',1)
s=s.replace('Version **2.59, 209 pages** is current:','Version **2.59, 209 pages** was current for that unit:',1)
p.write_text(s)
(R/'data/accounting-master/next-plan.md').write_text(f'''# Accounting proposal — direct next plan

13 October 2026. Version 2.65,217 pages; readiness **not_ready**.
PDF: {pdf}
SHA256: {h}
Implementation and historical controller remain held.

The stock-plan source inquiry is complete within scope:
data/accounting-master/apple-stock-plan-source-20261013/result.md.
75 source and141 manuscript checks pass; six final pages read.
The4March2022 filing supplies three exact exhibit counterparts. Preserve the
frozen40 unresolved labels; the dated supplement leaves37 without counterparts.

Execute docs/plans/{nextplan}.
Inspect the performance form, its unfilled schedule, rank/return definitions
and named-award proxy evidence. Do not invent thresholds, grant applicability,
percentile conventions or actual market results.

P17/P18 continue; P19 remains negative. All35 MC requirements/18 gaps and five
E workstreams remain controlling. Frozen56/136 publication dates,35 supplemental
dates and101 without supplements remain. Preserve100 unrelated staged entries.
Human acceptance blocks promotion, not internal work.
''')
print('Four current controls refreshed; all requirement statuses preserved.')
