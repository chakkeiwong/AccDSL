from pathlib import Path
from hashlib import sha256
import importlib.util,json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('current_integration',HERE/'integrate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
archive=HERE/'attempt-01';assert not archive.exists();archive.mkdir()
for name in ('build.json','build.log','verification.json'):
    shutil.move(str(HERE/name),str(archive/name))
for name in ('accounting-product-proposal.pdf','accounting-product-proposal.log','chapters/06-language.tex'):
    target=archive/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(m.TARGET/name,target)
name='chapters/06-language.tex';original=(m.SOURCE/name).read_text()
assert (m.TARGET/name).read_text()==original
revised=m.expected(name,original);assert revised!=original
(m.TARGET/name).write_text(revised)
(HERE/'repair-note.md').write_text('''# Current-language correction before advancement

The first Version 5.10 build passed preservation, references and rendering
checks (726 pages; no new warnings). Chapter 6 still described the old source
composition as current, despite the new appendix successor. That is stale
reader-facing guidance. The first build/PDF/chapter are archived in attempt-01.
The explicit preservation exception now includes a fourth file: the bounded
paragraph in Chapter 6. No earlier manuscript or simulation chapter changes.
Rebuild and inspect the corrected chapter with the new and adjacent pages.
''')
print(json.dumps(dict(archived='attempt-01',changed=name,sha256=sha256(revised.encode()).hexdigest())))
