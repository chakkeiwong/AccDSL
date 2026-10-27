"""Preserve the first successful review; repair visible citation spacing."""
from pathlib import Path
import importlib.util, json, hashlib, sys
H=Path(__file__).resolve().parent; R=H.parents[2]; D=H/'readability-repair-01'
spec=importlib.util.spec_from_file_location('integration',H/'integrate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
if sys.argv[1]=='prepare':
    D.mkdir(exist_ok=False)
    lock=json.loads((H/'source-preservation.json').read_text())
    target=R/lock['target']; old=(H/'funding-control-authority.tex').read_text()
    assert (target/'simulation/funding-control-authority.tex').read_text()==old
    new=old.replace('option\citep','option \citep').replace('alone\citep','alone \citep').replace('condition\citep','condition \citep')
    assert new!=old
    (D/'before.tex').write_text(old)
    (D/'funding-control-authority.tex').write_text(new)
    (D/'authority.bib').write_bytes((H/'authority.bib').read_bytes())
    (target/'simulation/funding-control-authority.tex').write_text(new)
    lock['added']['simulation/funding-control-authority.tex']=hashlib.sha256(new.encode()).hexdigest()
    (D/'source-preservation.json').write_text(json.dumps(lock,indent=2)+'\n')
    (D/'repair.md').write_text('Rendered review of main page125 and simulation page116 found three citations touching the preceding word. Inserted ordinary spaces only. Equations, claims, citations, predecessor sources and the original successful build/review records are preserved. This is a typography repair, not new scientific evidence.\n')
    print('Prepared three citation-space repairs; original successful outputs preserved.')
else:
    m.H=D;m.R=R
    if sys.argv[1]=='build':m.build('build-attempt-01')
    elif sys.argv[1]=='verify':m.verify()
    else:raise ValueError('Unknown action')
