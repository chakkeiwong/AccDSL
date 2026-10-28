"""Create an explicitly synthetic raster-only referenced covenant."""
from hashlib import sha256
import json
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

H = Path(__file__).resolve().parent
S = H / 'sources'
S.mkdir(exist_ok=False)
lines = ['SYNTHETIC TEST FIXTURE - NOT AN APPLE DOCUMENT',
         'Incorporated financing note: synthetic.note.covenant',
         'Effective for the authored 2027 borrowing example.',
         '',
         'The borrower must not incur a borrowing if total',
         'principal debt after that borrowing would exceed',
         '80 currency units. The limit applies to cumulative',
         'principal debt, not just the new borrowing amount.',
         '',
         'This is an invented test rule. It is not a real contract.']
im = Image.new('RGB', (1300, 760), 'white')
draw = ImageDraw.Draw(im)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
for i, line in enumerate(lines): draw.text((45, 45 + i * 61), line, fill='black', font=font)
im.save(S / 'covenant.png')
pdf = fitz.open()
page = pdf.new_page(width=650, height=380)
page.insert_image(page.rect, filename=str(S / 'covenant.png'))
pdf.save(S / 'covenant-scan.pdf')
pdf.close()
(S / 'transcription.txt').write_text('\n'.join(lines) + '\n')
(S / 'parent.txt').write_text('SYNTHETIC TEST FIXTURE - NOT AN APPLE DOCUMENT\n'
    'The borrowing example incorporates synthetic.note.covenant, supplied as covenant-scan.pdf.\n'
    'Inspect its restrictions before admitting a borrowing.\n')
with fitz.open(S / 'covenant-scan.pdf') as check:
    assert len(check) == 1 and check[0].get_text() == '' and len(check[0].get_images()) == 1
baseline = dict(profile='SyntheticReferencedCovenant/1', reference_ids=['synthetic.note.covenant'],
    synthetic=True, source_admission=False, accounting_admission=False,
    interpretation=dict(total_principal_after_borrowing_max='80/1', unit='book_currency',
        source_reference='synthetic.note.covenant', applies_to='cumulative_principal_after_each_borrowing'),
    files={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(S.iterdir())})
(H / 'fixture-baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
print(json.dumps(dict(baseline_sha256=sha256((H/'fixture-baseline.json').read_bytes()).hexdigest(),
                     page_count=1, extractable_text_characters=0, images=1)))
