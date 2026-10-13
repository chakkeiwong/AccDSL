"""Record V2.66 and the next source-version inquiry."""
import json
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'completion.json').exists():raise SystemExit('Completed unit.')
h=json.loads((U/'manuscript-checks.json').read_text())['pdf_sha256']
oldh='92293e585a0e030e7f66647db69eb2ed26996377b4ab92d0b409fb2c972aa454'
oldpdf='docs/design/proposal/manuscript-apple-stock-plan-20261013/accounting-product-proposal.pdf'
pdf='docs/design/proposal/manuscript-apple-performance-award-20261013/accounting-product-proposal.pdf'
nextplan='accounting-apple-award-versions-20261013.md'
summary=('The [performance-award inquiry](../../data/accounting-master/apple-performance-award-20261013/result.md)\n'
 'is delivered in Version 2.66: the disclosed October2023 schedule, negative\n'
 'return cap, price-window counterexample, service fraction and cash dividend\n'
 'equivalents are integrated with explicit hypothetical inputs. All81 source\n'
 'and137 manuscript checks pass; five final pages inspected. The2022 form and\n'
 'proxy termination wording have an unresolved applicability/timing distinction.\n'
 'Inspect the already retained versions next:\n'
 '[award-version inquiry]('+nextplan+').\n')
p=R/'docs/plans/accounting-master-current.md';s=p.read_text()
s=s.replace('**Version 2.65, 217 pages; readiness not_ready.**','**Version 2.66, 219 pages; readiness not_ready.**',1).replace(oldpdf,pdf,1).replace(oldh,h,1)
s=s.replace('Delivered through Version 2.65; recurring','Delivered through Version 2.66; recurring')
s=s.replace('Execute the\n[performance-award inquiry](accounting-apple-performance-award-20261013.md).','The performance-method work is now complete within scope.\n\n'+summary)
s=s.replace('inspect performance method and grant dependencies','conditional performance method delivered; inspect retained form versions and unresolved grant applicability')
s=s.replace('The V2.65 source/method supplement adds three exhibit counterparts and\nconditional reserve/settlement consequences','The V2.65–2.66 supplements add three exhibit counterparts, conditional\nreserve/settlement/performance consequences and a source-specific timing question')
p.write_text(s)
p=R/'docs/plans/accounting-master-checkpoint.md';s=p.read_text();a=s.index('**Version 2.65');z=s.index('## Latest completed work')
s=s[:a]+f'**Version 2.66, 219 pages.**\nPDF: {pdf}\nSHA256: {h}.\n'+summary+'\nReadiness **not_ready**; independent/domain/human acceptance remains pending.\nThe three stock-plan counterparts remain supplemental;37 of the original40\nunresolved targets still lack counterparts in that supplement.\n\n'+s[z:]
s=s.replace('Execute the\n[performance-award inquiry](accounting-apple-performance-award-20261013.md).','The performance-award inquiry is also delivered. Execute the\n[award-version inquiry]('+nextplan+').')
p.write_text(s)
p=R/'docs/plans/accounting-continuation-requirements-20261007.md';s=p.read_text()
s=s.replace('## Current checkpoint — Version 2.65','## Preserved checkpoint — Version 2.65',1)
a=s.index('## Preserved checkpoint')
entry=f'''## Current checkpoint — Version 2.66

13 October 2026. **219 pages; not_ready**.
PDF: {pdf}
SHA256: {h}.
{summary}
MC01/03–05/08/10–11/17/28/30/32–35 advance within the stated source and
conditional-method scope; G5/G7/G11/G15/G16 remain open. No insurance or
new accounting-standard authority is supplied. All62 displays/426 citation
occurrences are retained in this candidate, including two displays and nine
citations added to V2.65. Exact rank conversion, dividend/corporate-action
implementation, actual grants, timing applicability and accounting valuation
remain unresolved. No requirement or readiness status is promoted.

The dated sections below preserve earlier assessments and their then-current
next actions. This checkpoint and the master next plan control execution.

'''
s=s[:a]+entry+s[a:];p.write_text(s)
(R/'data/accounting-master/next-plan.md').write_text(f'''# Accounting proposal — direct next plan

13 October 2026. Version2.66,219 pages; **not_ready**.
PDF: {pdf}
SHA256: {h}
Implementation and historical controller remain held.

The performance-award inquiry is complete within scope:
data/accounting-master/apple-performance-award-20261013/result.md.
81 source/arithmetic and137 manuscript checks pass; five final pages read.
General2022 form and2025 proxy describe different termination timing without
an established same-grant conflict. Missing numerical rank conventions and
actual award facts remain explicit; no historical payout is manufactured.

Execute docs/plans/{nextplan}.
Compare already retained2022 CEO and2024 general/CEO performance forms with
the source clauses. No acquisition is needed for these located targets.
Preserve their dates, populations, blanks and unknown applicability.

P17/P18 continue; P19 stays negative. All35 MC requirements/18 gaps and five
E workstreams remain controlling. Frozen40 unresolved references are unchanged;
three supplemental counterparts leave37 without one. Frozen56/136 publication
dates,35 supplements and101 without supplements remain. Preserve100 unrelated
staged entries. Human acceptance blocks promotion, not internal preparation.
''')
print('Four current controls advanced to V2.66.')
