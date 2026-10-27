"""Preserve the first successful build before repairing a split short example."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TARGET=ROOT/'docs/design/proposal/manuscript-method-requirements-20261024'
BACKUP=HERE/'before-layout-repair'
assert not BACKUP.exists()
BACKUP.mkdir()
source=TARGET/'sections/method-requirement-language.tex'
for p in [HERE/'build.json',HERE/'build.log',source,TARGET/'accounting-product-proposal.pdf']:
    shutil.copy2(p,BACKUP/p.name)
text=source.read_text()
anchor='Text uses named, semicolon-terminated declarations and prefix expressions.'
assert text.count(anchor)==1 and text.count('\\end{lstlisting}')==1
text=text.replace(anchor,'\\noindent\\begin{minipage}{\\linewidth}\n'+anchor)
text=text.replace('\\end{lstlisting}','\\end{lstlisting}\n\\end{minipage}\n')
source.write_text(text)
(BACKUP/'preservation.json').write_text(json.dumps({p.name:sha256(p.read_bytes()).hexdigest()
    for p in BACKUP.iterdir() if p.is_file()},indent=2)+'\n')
(HERE/'build.json').unlink()
(HERE/'layout-repair.md').write_text('The first build passed content checks but split the short authoring example across PDF pages 401–402. The complete first build, PDF and section source are preserved in before-layout-repair/. A minipage keeps the introduction and example together; no financial or semantic content changes. Rebuild and inspect the affected pages before recording acceptance.\n')
print('preserved first build; grouped short example for rendered review')
