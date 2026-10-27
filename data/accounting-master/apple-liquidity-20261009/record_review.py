"""Bind the completed author inspection to final render and source evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
if (OUT / 'completion.json').exists() or (OUT / 'render-review.json').exists():
    raise SystemExit('Preserve existing review evidence')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
r = read(OUT / 'render-manifest.json')
old = read(OUT / 'candidate-attempt-01/render-manifest.json')
unchanged = [n for n in r['page_numbers'] if
    r['rendered_pages'][str(n)]['sha256'] == old['rendered_pages'][str(n)]['sha256']]
assert unchanged == [1, 2, 3, 4, 5, 6, 7, 20, 21, 22, 24, 25]
assert r['continuous_read_pages'] == list(range(20, 26))
record = dict(recorded_at=datetime.now(timezone.utc).isoformat(),
    render_manifest_sha256=sha(OUT / 'render-manifest.json'),
    author_review_sha256=sha(OUT / 'author-review.md'),
    page_numbers=r['page_numbers'], continuous_read_pages=r['continuous_read_pages'],
    navigation_inspection_pages=list(range(1, 8)),
    prior_inspected_unchanged_images=unchanged, repaired_page_reread=[23],
    prior_render_manifest_sha256=sha(OUT / 'candidate-attempt-01/render-manifest.json'),
    independent_reader='pending', human_acceptance='pending',
    method='Author continuous normal-resolution reading 20–25; final corrected page 23 reread; other images unchanged. Navigation contact sheet only.')
(OUT / 'render-review.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))
