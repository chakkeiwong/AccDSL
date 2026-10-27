"""Create bounded white-background views; original image bytes stay intact."""
import hashlib
import io
import json
from pathlib import Path
import sys
from PIL import Image, __version__ as pillow_version

U=Path(__file__).resolve().parent
rows=json.loads((U/'image-index.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
first,last=map(int,sys.argv[1:])
assert 1<=first<=last<=20 and last-first<3
(U/'views').mkdir(exist_ok=True)
for row in rows[first-1:last]:
    number=row['index']
    original=U/row['local']
    target=U/f'views/image-{number:02}-white.png'
    record=U/f'views/image-{number:02}.json'
    assert not record.exists(), 'Do not repeat recorded view preparation'
    im=Image.open(original)
    rgba=im.convert('RGBA')
    white=Image.new('RGBA',rgba.size,'white')
    white.alpha_composite(rgba)
    out=white.convert('RGB')
    out.thumbnail((1600,1200))
    buffer=io.BytesIO()
    out.save(buffer,format='PNG')
    if target.exists():
        assert number==3 and target.read_bytes()==buffer.getvalue()
    else:
        with target.open('xb') as stream:stream.write(buffer.getvalue())
    with record.open('x') as stream:
        json.dump({'image':number,'original':row['local'],'original_sha256':sha(original),
            'original_mode':im.mode,'original_dimensions':list(im.size),
            'view':str(target.relative_to(U)),'view_sha256':sha(target),
            'view_dimensions':list(out.size),'transform':'Composite on white, RGB, proportional thumbnail <=1600x1200',
            'pillow_version':pillow_version,'reading_status':'not established by view preparation'},stream,indent=2)
        stream.write('\n')
print(json.dumps({'views_prepared':list(range(first,last+1)),'reading_status':'pending actual image inspection'}))
