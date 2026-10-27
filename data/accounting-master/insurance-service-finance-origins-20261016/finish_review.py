from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
ms=json.loads((OUT/'manuscript-checks.json').read_text());assert ms['failures']==0 and ms['version']=='3.34'
assert not (OUT/'rendered-review.json').exists()
review=dict(status='incremental_author_inspection_complete',pdf_sha256=ms['pdf_sha256'],pages_inspected=ms['rendered_pages'],full_resolution_pages=[288,289],
    findings='Title, contents and physical pages285–291 inspected. Loss allocation, recovery non-duplication, both frozen policy-switch directions and transfer signs are readable; no clipping or broken equations. Provisional drafting; independent/domain/human acceptance pending.',human_acceptance='pending')
(OUT/'rendered-review.json').write_text(json.dumps(review,indent=2)+'\n')
(OUT/'manuscript-result.md').write_text('# Version3.34 — insurance service and finance origins\n\n'
    'Protected integration preserves all133 Version3.33 sources except the approved label/insertion. The new passage teaches loss service/finance allocation, existing recovery-origin regression, B134 matching, frozen B135–136 switches and paragraph91 origin distinctions.\n\n'
    f"PDF: {ms['pdf']}\n\nSHA256: {ms['pdf_sha256']}\n\n{ms['pages']} pages;{ms['checks']} document checks, zero failures. Physical pages1,8,285–291 inspected,288–289 at full resolution. No material diagnostics, missing references, duplicate labels or out-of-page text.\n\n"
    'Local author inspection is not whole-document/human acceptance.477 financial checks remain conditional reference evidence. Readiness remains not_ready. Next:I2 retrospective/modified transition measurement, with original obligation and source limits preserved.\n')
print('Recorded inspected Version3.34 manuscript')
