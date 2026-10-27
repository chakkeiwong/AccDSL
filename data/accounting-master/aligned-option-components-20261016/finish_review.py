"""Record completed incremental render inspection before freezing evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json
OUT=Path(__file__).resolve().parent
ms=json.loads((OUT/'manuscript-checks.json').read_text())
review=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),pdf_sha256=ms['pdf_sha256'],status='incremental_author_inspection_complete',physical_pages=ms['rendered_pages'],full_resolution_pages=[202,203],findings=['Version3.32 title and contents inspected.','Actual/hypothetical strike and reserve equations are legible with no overflow.','EU source boundary is explicit within the surrounding AASB discussion.','The wrong-target example and lower-actual reversal preserve their numerical implications.'],human_acceptance='pending',independent_domain_review='pending',scope='Incremental author inspection; not full378-page review or human acceptance.')
(OUT/'rendered-review.json').write_text(json.dumps(review,indent=2)+'\n')
(OUT/'manuscript-result.md').write_text('''# Version3.32 manuscript result

16 October2026. The378-page candidate adds actual/aligned option components
through complete cash settlement and inventory basis. It passes398 checks with
131 protected Version3.31 sources. PDF SHA256:
468f6e7f9e127298e4bc5dd9be2781834101eac40832ee2339c43dd0a6560104.

Physical pages1,8,200–205 were inspected;202–203 at full resolution. No clipping,
formula collision or missing source boundary was detected. Source/equation/
citation preservation checks pass. This is incremental author inspection;
independent technical/domain and human comprehension acceptance remain pending.
The voice stays provisional and readiness remains not_ready.

Build: latexmk -lualatex -silent -g -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex.
Existing tfgpu Python/PyMuPDF/Pillow performed document checks with GPU hidden.
Script preparation encountered escaping/assertion failures before a successor
was created; explicit prepare_scripts.py corrected that transport issue.
Closeout initially stopped on the missing review record after preserving the
predecessor/controls/index; the guarded continuation verifies those unchanged
records and continues. No prior or financial evidence was overwritten.
''')
(OUT/'f2-residual-disposition.md').write_text('''# F2 after Version3.32

Delivered: component-specific instrument-only reductions retaining the item and
prior designated history; actual/aligned purchased-call intrinsic/time
components joined to premium, supplier, settlement, reserves and inventory.
Earlier item additions, acquired instruments and matched partial stopping remain.

Open: an allocation procedure for unidentified heterogeneous discontinued item
reserves, general signed/opposed-direction option/forward/collar components,
and actual valuations/qualification. The tested instrument family does not close
the stopped-item allocation question. A next source lead is the IFRS9
implementation/examples for layer designations and cost-of-hedging component
changes. Compare explicit source-origin allocation with a claimed nominal
percentage before admitting it. B1 dated schedules can proceed independently.
''')
print('Recorded completed render inspection and exact F2 residuals.')
