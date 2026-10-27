"""Correct inherited cover dates without overwriting earlier verification."""
from pathlib import Path
import importlib.util,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
P=H/'readability-repair-01';D=H/'edition-date-repair-02'
spec=importlib.util.spec_from_file_location('integration',H/'integrate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prior_transform=m.transform
def transform(name,text,base,version):
    out=prior_transform(name,text,base,version)
    if name in ['accounting-product-proposal.tex','simulation-foundations.tex']:
        assert out.count('26 October 2026')==1
        out=out.replace('26 October 2026','27 October 2026')
    return out
if sys.argv[1]=='prepare':
    assert json.loads((P/'verification.json').read_text())['status']=='PASS'
    D.mkdir(exist_ok=False)
    lock=json.loads((P/'source-preservation.json').read_text());T=R/lock['target'];S=R/lock['source']
    for name in ['accounting-product-proposal.tex','simulation-foundations.tex']:
        (D/(name+'.before')).write_bytes((T/name).read_bytes())
        (T/name).write_text(transform(name,(S/name).read_text(),lock['base'],lock['version']))
    for name in ['source-preservation.json','funding-control-authority.tex','authority.bib']:
        (D/name).write_bytes((P/name).read_bytes())
    (D/'repair.md').write_text('Cover review found the inherited26 October date inconsistent with this27 October successor. Both root dates now say27 October2026. Only existing named root edits change; prior successful builds and verification remain preserved.\n')
    print('Prepared both cover dates; prior successful evidence preserved.')
else:
    m.H=D;m.R=R;m.transform=transform
    if sys.argv[1]=='build':m.build('build-attempt-01')
    elif sys.argv[1]=='verify':m.verify()
    else:raise ValueError('Unknown action')
