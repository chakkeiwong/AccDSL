from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
ms=json.loads((OUT/'manuscript-checks.json').read_text());assert ms['failures']==0 and ms['version']=='3.35'
assert not (OUT/'rendered-review.json').exists()
review=dict(status='incremental_author_inspection_complete',pdf_sha256=ms['pdf_sha256'],pages_inspected=ms['rendered_pages'],full_resolution_pages=[313,314],
    findings='Title, contents and physical pages311–316 inspected. Cash/history distinction, CSM derivations, acquisition nil and treaty origins are readable without clipping. Prior source argument remains preserved. Provisional voice; independent/domain/human acceptance pending.',human_acceptance='pending')
(OUT/'rendered-review.json').write_text(json.dumps(review,indent=2)+'\n')
(OUT/'manuscript-result.md').write_text('# Version3.35 — retrospective transition measurements\n\n'
    'Protected integration preserves all134 Version3.34 sources except the approved label/insertion. Full/modified opening measurements, distinct information views, acquisition and recovery origins are taught with complete checked calculations.\n\n'
    f"PDF: {ms['pdf']}\n\nSHA256: {ms['pdf_sha256']}\n\n{ms['pages']} pages;{ms['checks']} document checks, zero failures. Physical pages1,8,311–316 inspected;313–314 at full resolution. No material diagnostics, missing references, duplicate labels or out-of-page text.\n\n"
    'Local author inspection is not whole-document or human acceptance.436 financial checks remain conditional evidence. Readiness remains not_ready. Next:J1 sector/company composition, retaining named transition residuals.\n')
print('Recorded inspected Version3.35 manuscript')
