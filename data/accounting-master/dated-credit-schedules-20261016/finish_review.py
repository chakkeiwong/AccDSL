from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
ms=json.loads((OUT/'manuscript-checks.json').read_text())
assert ms['failures']==0 and ms['version']=='3.33'
assert not (OUT/'rendered-review.json').exists()
review=dict(status='incremental_author_inspection_complete',pdf_sha256=ms['pdf_sha256'],pages_inspected=ms['rendered_pages'],full_resolution_pages=[255,256],
    findings='Title, contents and physical pages253–258 inspected. Dates, equations, negative allowance, cash299 and profit−1 are readable with no clipping. Provisional voice; independent technical/domain and human acceptance remain pending.',
    human_acceptance='pending')
(OUT/'rendered-review.json').write_text(json.dumps(review,indent=2)+'\n')
(OUT/'manuscript-result.md').write_text(
    '# Version3.33 — dated credit schedules\n\n'
    'The protected insertion adds dated POCI and performing-asset examples with integral fees, early financial write-offs, original-rate PV bounds and the distinct non-credit catch-up. All132 Version3.32 sources are preserved except the approved version label and one insertion.\n\n'
    f"PDF: {ms['pdf']}\n\nSHA256: {ms['pdf_sha256']}\n\n"
    f"{ms['pages']} pages; {ms['checks']} document checks, zero failures. Physical pages1,8,253–258 inspected;255–256 at full resolution. No material build diagnostics, missing references, duplicate labels or out-of-page text. This is local author typography inspection, not whole-document or human acceptance.\n\n"
    'The1231 financial checks and their finite admission limits remain separate. Mission readiness is not_ready. Next: audit and execute I1 insurance service/finance origins; retain general-rate propagation and wider B1 joins.\n')
print('Recorded inspected Version3.33 pages and manuscript result')
