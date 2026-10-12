"""Extract and optionally render at most two selected source pages per call."""
import hashlib
import json
import sys
from pathlib import Path
import fitz

OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
args=sys.argv[1:];render='--render' in args;args=[a for a in args if a!='--render']
name=args[0];assert name in {'aasb108','aasb13'}
pages=[int(n) for n in args[1:]];assert 1<=len(pages)<=2
pdf=OUT/'acquisition'/(name+'.pdf');assert pdf.read_bytes().startswith(b'%PDF')
doc=fitz.open(pdf)
for n in pages:
    text=doc[n-1].get_text();p=OUT/'text'/f'{name}-{n}.txt'
    assert not p.exists();p.write_text(text)
    if render:doc[n-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(OUT/'rendered'/f'{name}-{n}.png')
    print(f'{name} PDF {n}/{len(doc)}\n{text}')
